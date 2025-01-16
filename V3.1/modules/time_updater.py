from datetime import datetime
from pytz import timezone
from tkinter import ttk



class TimeUpdater:
    def __init__(self, parent, row_start, col_start, col_span):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span

        self.time_labels = {}

    def build(self):
        frame = ttk.Frame(self.parent)
        frame.grid(row=self.row_start, column=self.col_start, columnspan=self.col_span, sticky="nsew", padx=5)

        ttk.Label(frame, text="Hora Chile:", font=("Arial", 10)).pack(side="left", padx=5)
        self.time_labels["chile"] = ttk.Label(frame, text="", font=("Arial", 10, "italic"))
        self.time_labels["chile"].pack(side="left", padx=5)

        ttk.Label(frame, text="Hora Canada EST:", font=("Arial", 10)).pack(side="left", padx=5)
        self.time_labels["canada"] = ttk.Label(frame, text="", font=("Arial", 10, "italic"))
        self.time_labels["canada"].pack(side="left", padx=5)

    def update_time(self):
        try:
            chile_time = datetime.now(timezone("America/Santiago")).strftime("%Y-%m-%d %H:%M:%S")
            canada_time = datetime.now(timezone("America/Toronto")).strftime("%Y-%m-%d %H:%M:%S")

            self.time_labels["chile"].config(text=chile_time)
            self.time_labels["canada"].config(text=canada_time)

            self.parent.after(1000, self.update_time)
        except Exception as e:
            print(f"Error al actualizar las horas: {e}")
