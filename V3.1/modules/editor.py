import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import json
from datetime import datetime


class EditorModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager, history_module, timer_module, json_path="tickets.json"):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.history_module = history_module
        self.timer_module = timer_module
        self.editor_box = None
        self.template_combo = None
        self.json_path = json_path

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Ticket Editor")
        frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            rowspan=self.row_span,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Combo de Plantillas
        ttk.Label(frame, text="Template:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        template_list = [tmpl.get("name", "Unnamed") for tmpl in self.data_manager.get_templates()]
        self.template_combo = ttk.Combobox(frame, values=template_list, state="readonly")
        self.template_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.template_combo.bind("<<ComboboxSelected>>", self.load_template_content)

        # Cuadro de Texto
        self.editor_box = tk.Text(frame, wrap="word", undo=True)
        self.editor_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame, command=self.editor_box.yview)
        self.editor_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns")

        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Save", command=self.save_ticket).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_ticket).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_editor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Load", command=self.load_ticket).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Defang", command=self.apply_defang).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Undo Defang", command=self.undo_defang).pack(side="left", padx=5)

    def load_template_content(self, event):
        templates = self.data_manager.get_templates()
        content = next((tmpl["content"] for tmpl in templates if tmpl.get("name") == self.template_combo.get()), "")
        self.editor_box.delete("1.0", tk.END)
        self.editor_box.insert("1.0", content)

    def save_ticket(self):
        content = self.editor_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Editor is empty!")
            return

        extracted_data = self.extract_fields(content)
        time_worked = self.get_time_worked()

        ticket_data = {
            "ticket_number": extracted_data.get("Ticket Number"),
            "client": extracted_data.get("Account"),
            "short_description": extracted_data.get("Short Description"),
            "tuc": extracted_data.get("TUC"),
            "severity": int(extracted_data.get("Severity", 1)),
            "assigned_to": extracted_data.get("Assigned To"),
            "timezone": extracted_data.get("Timezone"),
            "time_worked": time_worked,
            "content": content,
            "created_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_timestamp": None,
        }

        if not ticket_data["ticket_number"] or not ticket_data["client"]:
            messagebox.showerror("Error", "Ticket Number and Client are required fields!")
            return

        if self.is_ticket_duplicate(ticket_data):
            messagebox.showerror("Error", f"Ticket {ticket_data['ticket_number']} already exists!")
            return

        # Save the ticket
        self.save_to_json(ticket_data)

        # Refresh the history module
        self.history_module.load_tickets()  # Reload tickets from JSON
        self.history_module.update_history_list()  # Refresh the UI

        # Pause the timer and open checklist
        self.pause_timer()
        self.open_checklist_window(ticket_data)

        messagebox.showinfo("Success", "Ticket saved successfully!")


    def update_ticket(self):
        content = self.editor_box.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Editor is empty!")
            return

        extracted_data = self.extract_fields(content)
        time_worked = self.get_time_worked()

        ticket_data = {
            "ticket_number": extracted_data.get("Ticket Number"),
            "client": extracted_data.get("Account"),
            "short_description": extracted_data.get("Short Description"),
            "tuc": extracted_data.get("TUC"),
            "severity": int(extracted_data.get("Severity", 1)),
            "assigned_to": extracted_data.get("Assigned To"),
            "timezone": extracted_data.get("Timezone"),
            "time_worked": time_worked,
            "content": content,
            "updated_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if not self.is_ticket_duplicate(ticket_data):
            messagebox.showerror("Error", f"Ticket {ticket_data['ticket_number']} does not exist for updating!")
            return

        self.overwrite_ticket(ticket_data)
        self.history_module.update_history_list()
        messagebox.showinfo("Success", "Ticket updated successfully!")

    def is_ticket_duplicate(self, ticket_data):
        tickets = self.data_manager.get_tickets()
        for ticket in tickets:
            if (
                ticket.get("ticket_number") == ticket_data["ticket_number"]
                and ticket.get("client") == ticket_data["client"]
            ):
                return True
        return False

    def open_checklist_window(self, ticket_data):
        checklist_window = tk.Toplevel(self.parent)
        checklist_window.title("Checklist")
        checklist_window.geometry("600x600")
        checklist_window.transient(self.parent)
        checklist_window.grab_set()
        checklist_window.update_idletasks()
        
        screen_width = checklist_window.winfo_screenwidth()
        screen_height = checklist_window.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (600 // 2)
        checklist_window.geometry(f"600x600+{x}+{y}")
        checklist_window.attributes("-alpha", 0.0)
        checklist_window.after(50, lambda: checklist_window.attributes("-alpha", 1.0))

        frame = ttk.Frame(checklist_window, padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Checklist Options", font=("Arial", 16, "bold")).pack(pady=10)

        options = [
            "Pull Logs",
            "Triage",
            "Investigation",
            "Historical Search",
            "Additional Search",
            "Osint",
            "Escalated",
            "Email",
            "Phone Call",
        ]

        selected_options = []

        def toggle_option(option):
            if option in selected_options:
                selected_options.remove(option)
            else:
                selected_options.append(option)
            summary_var.set(", ".join(selected_options))

        checklist_frame = ttk.Frame(frame)
        checklist_frame.pack(fill="both", expand=True, pady=10)

        col1_frame = ttk.Frame(checklist_frame)
        col1_frame.pack(side="left", fill="y", padx=5, expand=True)

        col2_frame = ttk.Frame(checklist_frame)
        col2_frame.pack(side="left", fill="y", padx=5, expand=True)

        for i, option in enumerate(options):
            target_frame = col1_frame if i % 2 == 0 else col2_frame
            ttk.Checkbutton(target_frame, text=option, command=lambda opt=option: toggle_option(opt)).pack(anchor="w", pady=2)

        summary_var = tk.StringVar(value="")
        summary_frame = ttk.LabelFrame(frame, text="Summary", labelanchor="n")
        summary_frame.pack(fill="x", padx=10, pady=10)

        summary_box = ttk.Entry(summary_frame, textvariable=summary_var, state="readonly", font=("Arial", 10))
        summary_box.pack(fill="x", padx=10, pady=5)

        ttk.Button(summary_frame, text="Copy", command=lambda: self.copy_to_clipboard(summary_var.get())).pack(side="right", padx=10)

        details_frame = ttk.LabelFrame(frame, text="Ticket Details", labelanchor="n")
        details_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(details_frame, text="Ticket Number:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(details_frame, text=ticket_data.get("ticket_number", "N/A"), font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=10)

        ttk.Label(details_frame, text="Client:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(details_frame, text=ticket_data.get("client", "N/A"), font=("Arial", 10)).grid(row=1, column=1, sticky="w", padx=10)

        ttk.Label(details_frame, text="Short Description:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(details_frame, text=ticket_data.get("short_description", "N/A"), font=("Arial", 10)).grid(row=2, column=1, sticky="w", padx=10)

        ttk.Label(details_frame, text="Time Worked:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(details_frame, text=ticket_data.get("time_worked", "00:00:00"), font=("Arial", 10, "bold")).grid(row=3, column=1, sticky="w", padx=10)

        ttk.Button(frame, text="Submit", command=lambda: checklist_window.destroy()).pack(side="bottom", pady=10)

    def copy_to_clipboard(self, text):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()
        messagebox.showinfo("Copied", "Summary copied to clipboard!")

    def save_to_json(self, ticket_data):
        tickets = self.data_manager.get_tickets()
        tickets.append(ticket_data)
        self.data_manager._save_json(self.json_path, tickets)

    def overwrite_ticket(self, ticket_data):
        tickets = self.data_manager.get_tickets()
        for index, ticket in enumerate(tickets):
            if (
                ticket.get("ticket_number") == ticket_data["ticket_number"]
                and ticket.get("client") == ticket_data["client"]
            ):
                tickets[index].update(ticket_data)
                self.data_manager._save_json(self.json_path, tickets)
                return

    def pause_timer(self):
        if self.timer_module and self.timer_module.timer_running:
            self.timer_module.pause_timer()

    def get_time_worked(self):
        return self.timer_module.get_time_worked() if self.timer_module else "00:00:00"

    def extract_fields(self, content):
        pattern = r"(?P<key>[\w\s]+):\s*(?P<value>[^\n]+)"
        matches = re.findall(pattern, content)
        return {key.strip(): value.strip() for key, value in matches}

    def clear_editor(self):
        self.editor_box.delete("1.0", tk.END)

    def load_ticket(self):
        file_path = filedialog.askopenfilename(initialdir="./tickets/")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.editor_box.delete("1.0", tk.END)
                self.editor_box.insert("1.0", file.read())
    def apply_defang(self):
        try:
            # Obtener el rango seleccionado
            start = self.editor_box.index("sel.first")
            end = self.editor_box.index("sel.last")
            selected_text = self.editor_box.get(start, end)

            # Reemplazar los patrones en el texto seleccionado
            defanged_text = selected_text.replace(".", "[.]").replace("http", "hxxp")
            
            # Reemplazar el texto seleccionado con el texto defanged
            self.editor_box.delete(start, end)
            self.editor_box.insert(start, defanged_text)
        except tk.TclError:
            messagebox.showwarning("Warning", "No text selected! Please select a portion of text to apply defang.")

    def undo_defang(self):
        try:
            # Obtener el rango seleccionado
            start = self.editor_box.index("sel.first")
            end = self.editor_box.index("sel.last")
            selected_text = self.editor_box.get(start, end)

            # Revertir los patrones en el texto seleccionado
            undefanged_text = selected_text.replace("[.]", ".").replace("hxxp", "http")
            
            # Reemplazar el texto seleccionado con el texto undefanged
            self.editor_box.delete(start, end)
            self.editor_box.insert(start, undefanged_text)
        except tk.TclError:
            messagebox.showwarning("Warning", "No text selected! Please select a portion of text to undo defang.")

    def center_window(self, window, width, height):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
