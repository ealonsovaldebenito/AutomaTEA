import tkinter as tk
from tkinter import ttk
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
        self.start_time_canada = None
        self.time_worked_seconds = 0 

    def build(self):
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

        timer_label = ttk.Label(frame, textvariable=self.timer_var, font=("Arial", 18, "bold"), anchor="center")
        timer_label.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        ttk.Button(frame, text="Start", command=self.start_timer).grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ttk.Button(frame, text="Pause", command=self.pause_timer).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(frame, text="Reset", command=self.reset_timer).grid(row=1, column=2, padx=5, pady=2, sticky="ew")

        timestamp_label = ttk.Label(frame, textvariable=self.timestamp_var, font=("Arial", 10), anchor="center")
        timestamp_label.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time() - self.paused_time
            self.start_time_chile, self.start_time_canada = self.get_start_timestamps()
            self.timestamp_var.set(f"Chile: {self.start_time_chile} | Canada: {self.start_time_canada}")
            self.update_timer()

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            elapsed_time = time.time() - self.start_time
            self.time_worked_seconds += elapsed_time  
            self.paused_time = self.time_worked_seconds  
            self.timer_var.set(self.format_time(self.time_worked_seconds))

    def reset_timer(self):
        self.timer_running = False
        self.time_worked_seconds = 0
        self.paused_time = 0
        self.start_time = 0
        self.timer_var.set("00:00:00")
        self.timestamp_var.set("Chile: --:-- | Canada: --:--")
        self.start_time_chile = None
        self.start_time_canada = None

    def update_timer(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            total_time = self.time_worked_seconds + elapsed_time
            self.timer_var.set(self.format_time(total_time))
            self.parent.after(500, self.update_timer)

    def get_start_timestamps(self):
        chile_tz = pytz.timezone("America/Santiago")
        canada_tz = pytz.timezone("America/Toronto")

        now_utc = datetime.now(pytz.utc)
        chile_time = now_utc.astimezone(chile_tz).strftime("%H:%M:%S")
        canada_time = now_utc.astimezone(canada_tz).strftime("%H:%M:%S")

        return chile_time, canada_time

    def get_time_worked(self):
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            total_time = self.time_worked_seconds + elapsed_time
            return self.format_time(total_time)
        return self.format_time(self.time_worked_seconds)

    def format_time(self, total_seconds):
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
