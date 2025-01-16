import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class HistoryModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.search_var = tk.StringVar()
        self.tickets = []
        self.sort_by = None
        self.sort_reverse = False

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="History")
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

        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_button = ttk.Button(search_frame, text="Filter", command=self.update_history_list)
        search_button.pack(side="left", padx=5)

        columns = ("ticket_number", "account", "tuc", "short_description", "timezone")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.history_tree.heading(
                col,
                text=col.replace("_", " ").title(),
                anchor="center",
                command=lambda c=col: self.sort_history(c),
            )
            self.history_tree.column(col, width=120, anchor="center")

        self.history_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.history_tree.bind("<Double-1>", self.on_ticket_double_click)

        self.load_tickets()
        self.update_history_list()

    def load_tickets(self):
        self.tickets = self.data_manager.get_tickets()

    def update_history_list(self):
        self.history_tree.delete(*self.history_tree.get_children())
        query = self.search_var.get().lower()

        filtered_tickets = [
            ticket
            for ticket in self.tickets
            if (
                query in ticket.get("ticket_number", "").lower()
                or query in ticket.get("client", "").lower()
                or query in ticket.get("tuc", "").lower()
                or query in ticket.get("short_description", "").lower()
                or query in ticket.get("timezone", "").lower()
            )
        ]

        if self.sort_by:
            filtered_tickets.sort(
                key=lambda x: x.get(self.sort_by, ""),
                reverse=self.sort_reverse,
            )

        for ticket in filtered_tickets:
            self.history_tree.insert(
                "",
                "end",
                values=(
                    ticket.get("ticket_number", ""),
                    ticket.get("client", ""),
                    ticket.get("tuc", ""),
                    ticket.get("short_description", ""),
                    ticket.get("timezone", ""),
                ),
            )

    def sort_history(self, column):
        if self.sort_by == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_by = column
            self.sort_reverse = False

        self.update_history_list()

    def on_ticket_double_click(self, event):
        selected_item = self.history_tree.selection()
        if not selected_item:
            return

        ticket_data = self.history_tree.item(selected_item[0], "values")
        ticket_number = ticket_data[0]

        ticket = next((t for t in self.tickets if t.get("ticket_number") == ticket_number), None)
        if ticket:
            self.open_ticket_editor(ticket)

    def open_ticket_editor(self, ticket):
        editor_window = tk.Toplevel(self.parent)
        editor_window.title(f"Edit Ticket: {ticket.get('ticket_number')}")
        editor_window.geometry("900x600")  # Larger default size
        editor_window.resizable(True, True)

        self.center_window(editor_window, 900, 600)

        main_frame = ttk.Frame(editor_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.columnconfigure(1, weight=1)

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(1, weight=1)

        ttk.Label(left_frame, text="Ticket Number:").grid(row=0, column=0, sticky="e", pady=2)
        self.entry_ticket_number = ttk.Entry(left_frame, width=20)
        self.entry_ticket_number.grid(row=0, column=1, sticky="w", pady=2)
        self.entry_ticket_number.insert(0, ticket.get("ticket_number", ""))

        ttk.Label(left_frame, text="Client/Account:").grid(row=1, column=0, sticky="e", pady=2)
        self.entry_client = ttk.Entry(left_frame, width=20)
        self.entry_client.grid(row=1, column=1, sticky="w", pady=2)
        self.entry_client.insert(0, ticket.get("client", ""))

        ttk.Label(left_frame, text="Short Desc:").grid(row=2, column=0, sticky="e", pady=2)
        self.entry_short_desc = ttk.Entry(left_frame, width=20)
        self.entry_short_desc.grid(row=2, column=1, sticky="w", pady=2)
        self.entry_short_desc.insert(0, ticket.get("short_description", ""))

        ttk.Label(left_frame, text="TUC:").grid(row=3, column=0, sticky="e", pady=2)
        self.entry_tuc = ttk.Entry(left_frame, width=20)
        self.entry_tuc.grid(row=3, column=1, sticky="w", pady=2)
        self.entry_tuc.insert(0, ticket.get("tuc", ""))

        ttk.Label(right_frame, text="Severity:").grid(row=0, column=0, sticky="e", pady=2)
        self.entry_severity = ttk.Entry(right_frame, width=5)
        self.entry_severity.grid(row=0, column=1, sticky="w", pady=2)
        self.entry_severity.insert(0, str(ticket.get("severity", 1)))

        ttk.Label(right_frame, text="Assigned To:").grid(row=1, column=0, sticky="e", pady=2)
        self.entry_assigned = ttk.Entry(right_frame, width=20)
        self.entry_assigned.grid(row=1, column=1, sticky="w", pady=2)
        self.entry_assigned.insert(0, str(ticket.get("assigned_to", "")))

        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        ttk.Label(content_frame, text="Content:").grid(row=0, column=0, sticky="w")
        text_subframe = ttk.Frame(content_frame)
        text_subframe.grid(row=1, column=0, sticky="nsew")
        text_subframe.rowconfigure(0, weight=1)
        text_subframe.columnconfigure(0, weight=1)

        self.content_text = tk.Text(text_subframe, wrap="word")
        self.content_text.grid(row=0, column=0, sticky="nsew")
        self.content_text.insert("1.0", ticket.get("content", ""))

        scrollbar = ttk.Scrollbar(text_subframe, command=self.content_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.content_text.config(yscrollcommand=scrollbar.set)

        save_btn = ttk.Button(editor_window, text="Save Changes",
                              command=lambda: self.save_changes(ticket, editor_window))
        save_btn.pack(fill="x", padx=10, pady=10)

    def save_changes(self, ticket, editor_window):
        new_ticket_number = self.entry_ticket_number.get().strip()
        new_client = self.entry_client.get().strip()
        new_short_desc = self.entry_short_desc.get().strip()
        new_tuc = self.entry_tuc.get().strip()
        try:
            new_severity = int(self.entry_severity.get().strip())
        except ValueError:
            new_severity = 1

        new_assigned = self.entry_assigned.get().strip()
        new_content = self.content_text.get("1.0", "end").strip()

        ticket["ticket_number"] = new_ticket_number
        ticket["client"] = new_client
        ticket["short_description"] = new_short_desc
        ticket["tuc"] = new_tuc
        ticket["severity"] = new_severity
        ticket["assigned_to"] = new_assigned
        ticket["updated_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticket["content"] = new_content

        filename = self.data_manager.files.get("tickets", "")
        self.data_manager._save_json(filename, self.tickets)

        self.load_tickets()  # Reload tickets from updated data
        self.update_history_list()
        messagebox.showinfo("Success", "Ticket updated successfully!")
        editor_window.destroy()

    def center_window(self, window, width, height):
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
