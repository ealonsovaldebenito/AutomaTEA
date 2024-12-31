import tkinter as tk
from tkinter import ttk, messagebox


class InputModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, editor_module, data_manager):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.editor_module = editor_module
        self.data_manager = data_manager

        self.ticket_number = tk.StringVar()
        self.account = tk.StringVar()
        self.short_desc = tk.StringVar()
        self.tuc = tk.StringVar()
        self.severity = tk.IntVar(value=1)
        self.assigned_to = tk.StringVar()
        self.escalated = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Abierto")

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Ticket Inputs")
        frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            rowspan=self.row_span,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        frame.columnconfigure(0, weight=1)  # Left column
        frame.columnconfigure(1, weight=1)  # Right column

        # Input Fields Frame (Left Column)
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Ticket Number:").grid(row=0, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(input_frame, textvariable=self.ticket_number).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(input_frame, text="Account:").grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.account_combo = ttk.Combobox(input_frame, textvariable=self.account, values=[], state="normal")
        self.account_combo.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(input_frame, text="Short Description:").grid(row=2, column=0, sticky="w", padx=2, pady=2)
        ttk.Entry(input_frame, textvariable=self.short_desc).grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(input_frame, text="TUC:").grid(row=3, column=0, sticky="w", padx=2, pady=2)
        self.tuc_combo = ttk.Combobox(input_frame, textvariable=self.tuc, values=[], state="normal")
        self.tuc_combo.grid(row=3, column=1, sticky="ew", padx=2, pady=2)

        # Add Buttons
        button_row_frame = ttk.Frame(input_frame)
        button_row_frame.grid(row=4, column=1, sticky="ew", padx=2, pady=2)
        button_row_frame.columnconfigure(0, weight=1)
        button_row_frame.columnconfigure(1, weight=1)
        button_row_frame.columnconfigure(2, weight=1)

        ttk.Button(button_row_frame, text="Add TUC", command=self.add_tuc).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(button_row_frame, text="Submit", command=self.submit_inputs).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(button_row_frame, text="Clear", command=self.clear_inputs).grid(row=0, column=2, sticky="ew", padx=2, pady=2)

        # Buttons and Extra Controls Frame (Right Column)
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        buttons_frame.columnconfigure(1, weight=1)

        ttk.Label(buttons_frame, text="Severity (1-4):").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        ttk.Spinbox(buttons_frame, from_=1, to=4, textvariable=self.severity, width=10).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(buttons_frame, text="Assigned To:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        ttk.Combobox(
            buttons_frame,
            textvariable=self.assigned_to,
            values=["L1 Team", "L2 Team", "Infrastructure", "Managed Devices"],
            state="readonly",
        ).grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        ttk.Label(buttons_frame, text="Escalado:").grid(row=2, column=0, sticky="e", padx=2, pady=2)
        ttk.Checkbutton(buttons_frame, variable=self.escalated).grid(row=2, column=1, sticky="w", padx=2, pady=2)

        ttk.Label(buttons_frame, text="Estado:").grid(row=3, column=0, sticky="e", padx=2, pady=2)
        ttk.Combobox(
            buttons_frame,
            textvariable=self.status,
            values=["Abierto", "Pendiente", "Cerrado", "Escalado"],
            state="readonly",
        ).grid(row=3, column=1, sticky="ew", padx=2, pady=2)

        # Initialize input lists
        self.refresh_inputs()

    def submit_inputs(self):
        """Send inputs to the editor, formatted with required headers."""
        details = (
            "########TICKET DETAILS########\n"
            f"Ticket Number: {self.ticket_number.get()}\n"
            f"Account: {self.account.get()}\n"
            f"Short Description: {self.short_desc.get()}\n"
            f"TUC: {self.tuc.get()}\n"
            f"Severity: {self.severity.get()}\n"
            f"Assigned To: {self.assigned_to.get()}\n"
            f"Escalado: {'Sí' if self.escalated.get() else 'No'}\n"
            f"Estado: {self.status.get()}\n"
            "########INVESTIGATION DETAILS########\n\n"
        )

        if self.editor_module and hasattr(self.editor_module, "editor_box") and self.editor_module.editor_box:
            self.editor_module.editor_box.insert("1.0", details)
            messagebox.showinfo("Success", "Ticket details sent to the editor!")
        else:
            messagebox.showerror("Error", "EditorModule is not properly configured or missing.")

    def add_tuc(self):
        """Add a new TUC."""
        new_tuc = self.tuc.get().strip()
        if not new_tuc:
            messagebox.showerror("Error", "TUC field is empty.")
            return

        self.data_manager.add_tuc(new_tuc)
        self.refresh_inputs()
        messagebox.showinfo("Success", f"TUC '{new_tuc}' added successfully!")

    def clear_inputs(self):
        """Clear all input fields."""
        self.ticket_number.set("")
        self.account.set("")
        self.short_desc.set("")
        self.tuc.set("")
        self.severity.set(1)
        self.assigned_to.set("")
        self.escalated.set(False)
        self.status.set("Abierto")

    def refresh_inputs(self):
        """Refresh inputs with data from the data manager."""
        accounts = [account["name"] for account in self.data_manager.get_clients()]
        self.account_combo["values"] = accounts

        tucs = [tuc["name"] for tuc in self.data_manager.get_tucs()]
        self.tuc_combo["values"] = tucs