import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Para cargar y manejar imágenes


class AppTitleModule:
    def __init__(self, parent, row_start, col_start, col_span):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.logo_path = "assets/logo.png"
        self.time_labels = {}

    def build(self):
        # Frame principal para el título
        title_frame = ttk.Frame(self.parent)
        title_frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        title_frame.columnconfigure(0, weight=1)

        # Logo y título
        header_frame = ttk.Frame(title_frame)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(1, weight=1)  # Título expansible

        # Cargar y mostrar el logo
        try:
            logo_image = Image.open(self.logo_path).resize((50, 50), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            ttk.Label(header_frame, image=self.logo_photo).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        except FileNotFoundError:
            ttk.Label(header_frame, text="[Logo Missing]", font=("Arial", 10, "italic"), foreground="red").grid(
                row=0, column=0, padx=5, pady=5, sticky="w"
            )

        # Título
        title_label = ttk.Label(
            header_frame,
            text="AutomaTEA Ticket Software",
            font=("Arial", 20, "bold"),
            anchor="center",
            foreground="#0F4C75",  # Color azul
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=10)

        # Línea divisoria
        ttk.Separator(title_frame, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=5)

        # Tiempo (placeholder para uso futuro)
        time_frame = ttk.Frame(title_frame)
        time_frame.grid(row=2, column=0, sticky="ew")
        ttk.Label(time_frame, text="Hack your time!", font=("Arial", 10, "italic")).pack()


# Ejemplo de uso:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AutomaTEA")
    root.geometry("600x200")

    app_title = AppTitleModule(root, 0, 0, 3)
    app_title.build()

    root.mainloop()
