import tkinter as tk
from tkinter import ttk, messagebox


class HistoryModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.search_var = tk.StringVar()

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

        # Search bar
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_button = ttk.Button(search_frame, text="Filter", command=self.update_history_list)
        search_button.pack(side="left", padx=5)

        # Treeview for tickets
        # Definir las columnas
        columns = ("ticket_number", "account", "tuc", "short_description")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        # Configurar los encabezados y las columnas con alineación centrada
        for col in columns:
            self.history_tree.heading(col, text=col.replace("_", " ").title(), anchor='center')  # Centrar el encabezado
            self.history_tree.column(col, width=150, anchor='center')  # Centrar el contenido de la columna

        # Ubicar el Treeview en la cuadrícula
        self.history_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Vincular el evento de doble clic
        self.history_tree.bind("<Double-1>", self.on_ticket_double_click)

        # Populate tickets
        self.update_history_list()

    def update_history_list(self):
        self.history_tree.delete(*self.history_tree.get_children())
        query = self.search_var.get().lower()
        tickets = self.data_manager.get_tickets()

        for ticket in tickets:
            if query in ticket.get("ticket_number", "").lower() or \
               query in ticket.get("client", "").lower() or \
               query in ticket.get("tuc", "").lower() or \
               query in ticket.get("short_description", "").lower():
                self.history_tree.insert(
                    "",
                    "end",
                    values=(ticket.get("ticket_number", ""), ticket.get("client", ""),ticket.get("tuc", ""), ticket.get("short_description", "")),
                )

    def on_ticket_double_click(self, event):
        selected_item = self.history_tree.selection()
        if not selected_item:
            return

        ticket_data = self.history_tree.item(selected_item[0], "values")
        ticket_number = ticket_data[0]

        tickets = self.data_manager.get_tickets()
        ticket = next((t for t in tickets if t.get("ticket_number") == ticket_number), None)
        if ticket:
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"Ticket {ticket_number} Details")
            detail_window.geometry("600x400")

            text_area = tk.Text(detail_window, wrap="word", state="normal")
            text_area.insert("1.0", f"Ticket Number: {ticket.get('ticket_number')}\n")
            text_area.insert("2.0", f"Account: {ticket.get('client')}\n")
            text_area.insert("3.0", f"Short Description: {ticket.get('short_description')}\n\n")
            text_area.insert("4.0", f"TUC: {ticket.get('tuc')}\n\n")
            text_area.insert("5.0", f"Severity: {ticket.get('severity')}\n\n")
            text_area.insert("6.0", f"Assigned To: {ticket.get('assigned_to')}\n\n")
            text_area.insert("7.0", f"Time: {ticket.get('timestamp')}\n\n")
            text_area.insert("8.0", f"Content:\n{ticket.get('content', 'No Content')}")
            text_area.config(state="disabled")
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
