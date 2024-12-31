import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime
import pytz


class TimerModule:
    def __init__(self, parent, row_start, col_start, col_span=1, row_span=1, editor_module=None):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.editor_module = editor_module
        self.timer_running = False
        self.paused_time = 0
        self.start_time = 0
        self.timer_var = tk.StringVar(value="00:00:00")
        self.timestamp_var = tk.StringVar(value="Chile: --:-- | Canada: --:--")
        self.start_time_chile = None

    def build(self):
        # Frame principal
        frame = ttk.LabelFrame(self.parent, text="SLA Timer")
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
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(0, weight=1)

        # Display del Timer
        timer_label = ttk.Label(frame, textvariable=self.timer_var, font=("Arial", 18, "bold"), anchor="center")
        timer_label.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        # Botones de control
        ttk.Button(frame, text="Start", command=self.start_timer).grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ttk.Button(frame, text="Pause", command=self.pause_timer).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(frame, text="Reset", command=self.reset_timer).grid(row=1, column=2, padx=5, pady=2, sticky="ew")

        # Botón para enviar hora de inicio
        ttk.Button(frame, text="Submit Start Time", command=self.submit_start_time).grid(
            row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew"
        )

        # Display de Timestamp
        timestamp_label = ttk.Label(frame, textvariable=self.timestamp_var, font=("Arial", 10), anchor="center")
        timestamp_label.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time() - self.paused_time
            self.start_time_chile = self.get_chile_time()
            self.update_timer()
            self.update_timestamps()

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.paused_time = time.time() - self.start_time

    def reset_timer(self):
        self.timer_running = False
        self.paused_time = 0
        self.timer_var.set("00:00:00")
        self.timestamp_var.set("Chile: --:-- | Canada: --:--")
        self.start_time_chile = None

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_var.set(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
            self.parent.after(500, self.update_timer)

    def update_timestamps(self):
        chile_tz = pytz.timezone("America/Santiago")
        canada_tz = pytz.timezone("America/Toronto")

        now_utc = datetime.now(pytz.utc)
        chile_time = now_utc.astimezone(chile_tz).strftime("%H:%M:%S")
        canada_time = now_utc.astimezone(canada_tz).strftime("%H:%M:%S")

        self.timestamp_var.set(f"Chile: {chile_time} | Canada: {canada_time}")

    def get_chile_time(self):
        """Obtain the current time in Chile's timezone."""
        chile_tz = pytz.timezone("America/Santiago")
        now_utc = datetime.now(pytz.utc)
        return now_utc.astimezone(chile_tz).strftime("%H:%M:%S")

    def submit_start_time(self):
        """Send the start time in Chilean format to the editor module."""
        if not self.start_time_chile:
            messagebox.showwarning("No Start Time", "Timer has not been started.")
            return

        details = f"######## TICKET DETAILS ########\nStart Time (Chile): {self.start_time_chile}\n"
        details += "######## INVESTIGATION DETAILS ########\n\n"

        if self.editor_module and hasattr(self.editor_module, "editor_box") and self.editor_module.editor_box:
            self.editor_module.editor_box.insert("1.0", details)
            messagebox.showinfo("Success", "Start time sent to the editor!")
        else:
            messagebox.showerror("Error", "Editor module is not properly configured or missing.")
