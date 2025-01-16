import tkinter as tk
import os
from functions.data_manager import DataManager
from modules.timer import TimerModule
from modules.editor import EditorModule
from modules.osint import OSINTModule
from modules.queries import QueriesModule
from modules.parser import ParserModule
from modules.notes import NotesModule
from modules.history import HistoryModule
from modules.extract_fields import ExtractFieldsModule
from modules.input import InputModule
from modules.root_cause import RootCauseModule
from modules.app_title import AppTitleModule
from modules.footer import FooterModule
from modules.time_updater import TimeUpdater
from menu.menu_manager import MenuManager


class AutomaTEAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        icon_path = "./assets/icon.ico"
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.title("AutomaTEA Ticket Software")
        self.minsize(1280, 720)
        self.data_manager = DataManager()
        self.time_updater = None

        try:
            self.create_main_layout()
            self.create_menu()
        except Exception as e:
            print(f"Error creating the main layout: {e}")
            self.destroy()

        if self.time_updater:
            self.time_updater.update_time()

    def create_main_layout(self):
        rows, cols = 21, 20
        for r in range(rows):
            if r == 0:
                self.rowconfigure(r, weight=0, minsize=50)
            elif r == 21:
                self.rowconfigure(r, weight=0, minsize=50)
            elif 4 <= r <= 13:
                self.rowconfigure(r, weight=3)
            else:
                self.rowconfigure(r, weight=1)
        for c in range(cols):
            if c <= 3:
                self.columnconfigure(c, weight=0)
            elif 4 <= c <= 15:
                self.columnconfigure(c, weight=0)
            else:
                self.columnconfigure(c, weight=0)

        AppTitleModule(self, row_start=0, col_start=0, col_span=20).build()
        timer_mod = TimerModule(self, row_start=1, col_start=0, col_span=1, row_span=6)
        timer_mod.build()

        history = HistoryModule(self, row_start=17, col_start=2, col_span=12, row_span=1, data_manager=self.data_manager)
        history.build()

        NotesModule(self, row_start=17, col_start=0, col_span=1, row_span=1, data_manager=self.data_manager).build()

        editor = EditorModule(
            self,
            row_start=1,
            col_start=2,
            col_span=12,
            row_span=15,
            data_manager=self.data_manager,
            history_module=history,
            timer_module=timer_mod,  # Asegurarse de pasar el TimerModule
        )
        editor.build()

        InputModule(self, row_start=1, col_start=16, col_span=4, row_span=6,
                    editor_module=editor, data_manager=self.data_manager, timer_module=timer_mod).build()

        QueriesModule(self, row_start=10, col_start=0, col_span=1, row_span=5,
                      data_manager=self.data_manager).build()

        OSINTModule(self, row_start=8, col_start=16, col_span=4, row_span=4, json_path="data/osint.json").build()

        ExtractFieldsModule(self, row_start=14, col_start=16, col_span=4, row_span=3, editor_module=editor).build()

        RootCauseModule(self, row_start=17, col_start=16, col_span=4, row_span=1,
                        editor_module=editor, json_path="data/template_5w.json").build()

        FooterModule(self, row_start=20, col_start=0, col_span=20).build()

        self.time_updater = TimeUpdater(self, row_start=19, col_start=0, col_span=20)
        self.time_updater.build()

    def create_menu(self):
        self.menu_manager = MenuManager(self)
        self.menu_manager.create_menu()


if __name__ == "__main__":
    app = AutomaTEAApp()
    app.mainloop()
