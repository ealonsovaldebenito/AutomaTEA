import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import re
import json
from datetime import datetime


class EditorModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager, history_module, json_path="tickets.json"):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.history_module = history_module  # Referencia al módulo de historial
        self.editor_box = None
        self.template_combo = None
        self.extract_fields_module = None
        self.json_path = json_path

    def set_extract_fields_module(self, extract_fields_module):
        """Enlaza el módulo ExtractFieldsModule al EditorModule."""
        self.extract_fields_module = extract_fields_module

    def build(self):
        # Crear el marco principal
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
        ttk.Button(button_frame, text="Clear", command=self.clear_editor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Load", command=self.load_ticket).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Defang", command=self.apply_defang).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Undo Defang", command=self.undo_defang).pack(side="left", padx=5)

    def load_template_content(self, event):
        """Carga el contenido de una plantilla seleccionada."""
        try:
            templates = self.data_manager.get_templates()
            content = next((tmpl["content"] for tmpl in templates if tmpl.get("name") == self.template_combo.get()), "")
            self.editor_box.delete("1.0", tk.END)
            self.editor_box.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template content: {e}")

    def save_ticket(self):
        """Guarda un ticket en formato JSON y opcionalmente como archivo TXT."""
        try:
            content = self.editor_box.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Warning", "Editor is empty!")
                return

            # Extraer automáticamente los parámetros del contenido
            extracted_data = self.extract_fields(content)
            if not extracted_data:
                messagebox.showerror("Error", "Failed to extract required fields from content!")
                return

            # Completar ticket_data con los parámetros extraídos
            ticket_data = {
                "ticket_number": extracted_data.get("Ticket Number"),
                "client": extracted_data.get("Account"),
                "short_description": extracted_data.get("Short Description"),
                "tuc": extracted_data.get("TUC"),
                "severity": int(extracted_data.get("Severity", 1)),
                "assigned_to": extracted_data.get("Assigned To"),
                "content": content,  # Guardar el contenido completo sin eliminar datos
                "parsed_info": "\n".join([f"{k}: {v}" for k, v in extracted_data.items() if v]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Validar campos requeridos
            if not ticket_data["ticket_number"] or not ticket_data["client"]:
                messagebox.showerror("Error", "Ticket Number and Client are required fields!")
                return

            # Validar si ya existe el ticket
            if self.is_ticket_duplicate(ticket_data):
                # Preguntar si desea sobrescribir
                overwrite = messagebox.askyesno(
                    "Overwrite Ticket",
                    f"Ticket '{ticket_data['ticket_number']}' for client '{ticket_data['client']}' already exists.\nDo you want to overwrite it?",
                )
                if overwrite:
                    self.overwrite_ticket(ticket_data)
                else:
                    return
            else:
                # Guardar en JSON
                self.save_to_json(ticket_data)

            # Actualizar el módulo de historial
            self.history_module.update_history_list()

            # Guardar como TXT
            if messagebox.askyesno("Save as TXT", "Do you want to save this ticket as a .txt file?"):
                self.save_to_txt(content)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ticket: {e}")

    def is_ticket_duplicate(self, ticket_data):
        """Verifica si un ticket ya existe basado en número y cliente."""
        existing_tickets = self.data_manager.get_tickets()
        for ticket in existing_tickets:
            if (
                ticket.get("ticket_number") == ticket_data["ticket_number"]
                and ticket.get("client") == ticket_data["client"]
            ):
                return True
        return False

    def overwrite_ticket(self, ticket_data):
        """Sobrescribe un ticket existente con nuevos datos."""
        tickets = self.data_manager.get_tickets()
        for index, ticket in enumerate(tickets):
            if (
                ticket.get("ticket_number") == ticket_data["ticket_number"]
                and ticket.get("client") == ticket_data["client"]
            ):
                tickets[index] = ticket_data
                self.data_manager._save_json(self.json_path, tickets)
                messagebox.showinfo("Success", "Ticket overwritten successfully!")
                return

    def extract_fields(self, content):
        """Extrae campos clave del contenido del editor."""
        try:
            pattern = r"(?P<key>[\w\s]+):\s*(?P<value>[^\n]+)"
            matches = re.findall(pattern, content)
            return {key.strip(): value.strip() for key, value in matches}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract fields: {e}")
            return {}

    def save_to_json(self, ticket_data):
        """Guarda el ticket en un archivo JSON."""
        try:
            tickets = self.data_manager.get_tickets()
            tickets.append(ticket_data)
            self.data_manager._save_json(self.json_path, tickets)
            messagebox.showinfo("Success", "Ticket saved to JSON successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ticket to JSON: {e}")

    def save_to_txt(self, content):
        """Guarda el contenido del ticket como archivo TXT."""
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir="./tickets/")
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Success", "Ticket saved as TXT successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ticket as TXT: {e}")

    def clear_editor(self):
        """Limpia el contenido del editor."""
        self.editor_box.delete("1.0", tk.END)

    def load_ticket(self):
        """Carga un archivo de texto en el editor."""
        file_path = filedialog.askopenfilename(initialdir="./tickets/")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.editor_box.delete("1.0", tk.END)
                    self.editor_box.insert("1.0", file.read())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ticket: {e}")

    def apply_defang(self):
        """Aplica defang al contenido del editor."""
        self._transform_text(lambda x: x.replace(".", "[.]").replace("http", "hxxp"))

    def undo_defang(self):
        """Revierte defang en el contenido del editor."""
        self._transform_text(lambda x: x.replace("[.]", ".").replace("hxxp", "http"))

    def _transform_text(self, transform_func):
        """Transforma el contenido del editor usando una función dada."""
        content = self.editor_box.get("1.0", tk.END).strip()
        self.editor_box.delete("1.0", tk.END)
        self.editor_box.insert("1.0", transform_func(content))
