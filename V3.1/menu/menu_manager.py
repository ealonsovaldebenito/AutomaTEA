import tkinter as tk
from menu.manage_all_window import ManageAllWindow

class MenuManager:
    def __init__(self, parent):
        self.parent = parent
        self.data_manager = parent.data_manager
        self.menu_bar = tk.Menu(self.parent)

    def create_menu(self):
        file_menu = tk.Menu(self.menu_bar, tearoff=False)
        file_menu.add_command(label="Exit", command=self.parent.destroy)

        manage_menu = tk.Menu(self.menu_bar, tearoff=False)
        manage_menu.add_command(label="Manage All", command=self.manage_all)

        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.menu_bar.add_cascade(label="Manage", menu=manage_menu)
        self.parent.config(menu=self.menu_bar)

    def manage_all(self):
        ManageAllWindow(self.parent, self.data_manager)
