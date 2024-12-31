import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime
import pytz


class TimerModule:
    def __init__(self, parent, row_start, col_start, col_span=1, row_span=1):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.timer_running = False
        self.paused_time = 0
        self.start_time = 0
        self.timer_var = tk.StringVar(value="00:00:00")
        self.timestamp_var = tk.StringVar(value="Chile: --:-- | Canada: --:--")

    def build(self):
        ########### FRAME CONFIGURATION ###########
        frame = ttk.LabelFrame(self.parent, text="SLA Timer")
        frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            rowspan=self.row_span,
            sticky="nsew",
            padx=2,  # Reduced padding
            pady=2,  # Reduced padding
        )

        # Configure rows and columns within the Timer frame
        for i in range(3):
            frame.rowconfigure(i, weight=1)
        for i in range(3):
            frame.columnconfigure(i, weight=1)

        ########### TIMER DISPLAY ###########
        timer_label = ttk.Label(frame, textvariable=self.timer_var, font=("Arial", 14, "bold"), anchor="center")
        timer_label.grid(row=0, column=0, columnspan=3, pady=2, sticky="nsew")  # Reduced padding

        ########### BUTTONS ###########
        ttk.Button(frame, text="Start", command=self.start_timer).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(frame, text="Pause", command=self.pause_timer).grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        ttk.Button(frame, text="Reset", command=self.reset_timer).grid(row=1, column=2, padx=2, pady=2, sticky="ew")

        ########### TIMESTAMP DISPLAY ###########
        timestamp_label = ttk.Label(frame, textvariable=self.timestamp_var, font=("Arial", 9), anchor="center")
        timestamp_label.grid(row=2, column=0, columnspan=3, pady=2, sticky="nsew")  # Reduced padding

    ########### TIMER FUNCTIONALITY ###########
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time() - self.paused_time
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
