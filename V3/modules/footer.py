from tkinter import ttk


class FooterModule:
    def __init__(self, parent, row_start, col_start, col_span):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span


    def build(self):
        footer_frame = ttk.Frame(self.parent)
        footer_frame.grid(row=self.row_start, column=self.col_start, columnspan=self.col_span, sticky="ew")
        footer_label = ttk.Label(
            footer_frame,
            text="AutomaTEA Ticket Software | By Eduardo Valdebenito | December, 2024 | V3.0.1",
            font=("Arial", 10, "italic"),
            anchor="center",
        )
        footer_label.pack()
