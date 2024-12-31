import tkinter as tk
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
from data_manager import DataManager
import os



class AutomaTEAApp(tk.Tk):
    def __init__(self):
        super().__init__()
        icon_path = "./assets/icon.ico"
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        self.title("AutomaTEA Ticket Software")
        self.geometry("1920x1080")
        self.minsize(1280, 720)

        self.data_manager = DataManager()
        self.time_updater = None

        try:
            self.create_main_layout()
        except Exception as e:
            print(f"Error creating the main layout: {e}")
            self.destroy()

        if self.time_updater:
            self.time_updater.update_time()

    ########### MAIN LAYOUT CONFIGURATION ###########
    def create_main_layout(self):
        ########### ROW AND COLUMN CONFIGURATION ###########
        rows, cols = 21, 20
        for r in range(rows):
            if r == 0:  # Title row (always visible)
                self.rowconfigure(r, weight=0, minsize=50)
            elif r == 19:  # Footer row (always visible)
                self.rowconfigure(r, weight=0, minsize=50)
            elif 4 <= r <= 13:  # Center rows (Editor/Input)
                self.rowconfigure(r, weight=3)  # Highest priority
            else:  # Other rows
                self.rowconfigure(r, weight=1)

        for c in range(cols):
            if c <= 3:  # Left columns (1-4)
                self.columnconfigure(c, weight=0)  # Narrower left section with minimum size
            elif 4 <= c <= 15:  # Center columns (5-16)
                self.columnconfigure(c, weight=0)  # Wider center section with minimum size
            else:  # Right columns (17-20)
                self.columnconfigure(c, weight=0)
        ########### ROW 0: TITLE ###########
        AppTitleModule(self, row_start=0, col_start=0, col_span=20).build()

        ########### COLUMN 0-3: LEFT ###########
        # Timer Module (Top Left)
        TimerModule(self, row_start=1, col_start=0, col_span=4, row_span=6).build()

        # History Module (Below Timer)
        history_instance = HistoryModule(
            self,
            row_start=10,
            col_start=0,
            col_span=4,
            row_span=5,
            data_manager=self.data_manager,
        )
        history_instance.build()

        # Notes Module (Bottom Left)
        NotesModule(self, row_start=17, col_start=0, col_span=4, row_span=1, data_manager=self.data_manager).build()

        ########### COLUMN 4-15: CENTER ###########
        # Editor Module
        editor_instance = EditorModule(
            self,
            row_start=1,
            col_start=4,
            col_span=12,
            row_span=15,
            data_manager=self.data_manager,
            history_module=history_instance,
        )
        editor_instance.build()

        # Input Module
        InputModule(
            self, row_start=1, col_start=16, col_span=4, row_span=6, editor_module=editor_instance, data_manager=self.data_manager
        ).build()

        # Queries Module (Below Editor)
        QueriesModule(
            self, row_start=17, col_start=4, col_span=12, row_span=1, data_manager=self.data_manager
        ).build()

        ########### COLUMN 16-19: RIGHT ###########
        # OSINT Module
        OSINTModule(self, row_start=8, col_start=16, col_span=4, row_span=4, json_path="data/osint.json").build()

        # Extract Fields Module
        extract_fields_instance = ExtractFieldsModule(
            self,
            row_start=14,
            col_start=16,
            col_span=4,
            row_span=3,
            editor_module=editor_instance,
        )
        extract_fields_instance.build()
        editor_instance.set_extract_fields_module(extract_fields_instance)

        # Root Cause Module
        RootCauseModule(
            self,
            row_start=17,
            col_start=16,
            col_span=4,
            row_span=3,
            editor_module=editor_instance,
            json_path="data/template_5w.json",
        ).build()

        ########### ROW 19: FOOTER ###########
        FooterModule(self, row_start=20, col_start=0, col_span=20).build()

        ########### TIME UPDATER ###########
        self.time_updater = TimeUpdater(self, row_start=19, col_start=0, col_span=20)
        self.time_updater.build()


if __name__ == "__main__":
    app = AutomaTEAApp()
    app.mainloop()
