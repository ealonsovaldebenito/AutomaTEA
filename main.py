import os
from ui_main import AutomaTEAApp

def main():
    # Crear carpetas necesarias si no existen
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./notes", exist_ok=True)
    os.makedirs("./tickets", exist_ok=True)

    # Iniciar la aplicación
    app = AutomaTEAApp()
    app.mainloop()

if __name__ == "__main__":
    main()
