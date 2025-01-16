import tkinter as tk
from tkinter import ttk
import random
import os
from automatea import AutomaTEAApp


class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.configure(bg="#87CEEB")
        self.overrideredirect(True)
        self.geometry(self.center_splash(580, 380))
        self.attributes("-topmost", True)

        splash_frame = tk.Frame(self, bg="#87CEEB", relief="solid", bd=2)
        splash_frame.place(relx=0.5, rely=0.5, anchor="center", width=560, height=360)

        title_frame = tk.Frame(splash_frame, bg="#87CEEB")
        title_frame.pack(pady=20)

        tk.Label(title_frame, text="AutomaTEA", font=("Arial", 28, "bold"), fg="white", bg="#87CEEB").pack(side="left")
        logo_path = "./assets/logo.png"
        if os.path.exists(logo_path):
            logo = tk.PhotoImage(file=logo_path).subsample(8, 8)
            tk.Label(title_frame, image=logo, bg="#87CEEB").pack(side="right")
            self.logo_image = logo

        tk.Label(splash_frame, text="Hack your Time", font=("Arial", 16, "italic"), fg="white", bg="#87CEEB").pack()

        self.phrase_var = tk.StringVar()
        self.phrases = random.sample([
            "La integridad es primero.",
            "Protege tu entorno.",
            "Evita contaminación cruzada.",
            "Mantén el enfoque.",
            "Mejora cada día.",
            "La seguridad es un hábito.",
            "Nunca subestimes los riesgos.",
            "Automatiza para optimizar.",
            "Cada segundo cuenta.",
            "Piensa antes de actuar.",
        ], 3)
        self.carousel_index = 0
        tk.Label(splash_frame, textvariable=self.phrase_var, font=("Arial", 12), fg="white", bg="#87CEEB").pack(pady=10)
        self.update_phrase()

        progress_frame = tk.Frame(splash_frame, bg="#87CEEB")
        progress_frame.pack(pady=20, fill="x", padx=40)
        self.progress = tk.IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress, maximum=100, length=480)
        self.progress_bar.pack(fill="x")

        footer = tk.Label(
            splash_frame,
            text="AutomaTEA Ticket Software | By Eduardo Valdebenito | Cybersecurity Analyst",
            font=("Arial", 10, "italic"),
            fg="white",
            bg="#87CEEB",
        )
        footer.pack(side="bottom", pady=10)

        self.after(500, self.update_progress)

    def update_phrase(self):
        if self.carousel_index < len(self.phrases):
            self.phrase_var.set(self.phrases[self.carousel_index])
            self.carousel_index += 1
            self.after(1500, self.update_phrase)

    def update_progress(self):
        current_value = self.progress.get()
        if current_value < 100:
            self.progress.set(current_value + 5)
            self.after(200, self.update_progress)
        else:
            self.destroy()
            self.start_main_app()

    def center_splash(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        return f"{width}x{height}+{x}+{y}"

    def start_main_app(self):
        app = AutomaTEAApp()
        app.state('zoomed')
        app.mainloop()


if __name__ == "__main__":
    SplashScreen().mainloop()
