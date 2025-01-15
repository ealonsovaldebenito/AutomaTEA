import tkinter as tk
from tkinter import ttk

def center_window(win, width=400, height=300):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

class ManageAllWindow(tk.Toplevel):
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.title("Manage All Data")
        self.config(bg="#ECECEC")
        self.parent = parent
        self.data_manager = data_manager
        self.geometry("900x500")
        center_window(self, 900, 500)
        self.modules_map = {
            "Clients": "clients",
            "Notes": "notes",
            "OSINT": "osint",
            "Queries": "queries",
            "Templates": "templates",
            "RootCause(5w)": "template_5w",
            "Tickets": "tickets",
            "Tucs": "tucs"
        }
        self.current_module = None
        self.current_data = []
        self.create_ui()

    def create_ui(self):
        container = tk.Frame(self, bg="#ECECEC")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        self.modules_list = tk.Listbox(container, exportselection=False, bg="#DADADA")
        self.modules_list.pack(side="left", fill="y", expand=False, padx=(0, 10))
        for display_name in self.modules_map.keys():
            self.modules_list.insert(tk.END, display_name)
        self.modules_list.bind("<<ListboxSelect>>", self.on_module_select)
        right_frame = tk.Frame(container, bg="#ECECEC")
        right_frame.pack(side="right", fill="both", expand=True)
        self.tree = ttk.Treeview(right_frame, columns=("Name", "Detail"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Detail", text="Detail")
        self.tree.column("Name", width=200, stretch=False)
        self.tree.column("Detail", width=400, stretch=False)
        self.tree.pack(fill="both", expand=True, pady=(0,5))
        btn_frame = tk.Frame(right_frame, bg="#ECECEC")
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Add", command=self.add_item, bg="#A8A8A8").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Edit", command=self.edit_item, bg="#A8A8A8").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_item, bg="#A8A8A8").pack(side="left", padx=5)
        tk.Button(btn_frame, text="View in Editor", command=self.view_in_editor, bg="#A8A8A8").pack(side="left", padx=5)

    def on_module_select(self, event):
        sel = self.modules_list.curselection()
        if not sel:
            return
        idx = sel[0]
        display_name = self.modules_list.get(idx)
        self.current_module = self.modules_map[display_name]
        self.load_data()

    def load_data(self):
        if not self.current_module:
            return
        if self.current_module == "template_5w":
            self.current_data = self.data_manager._load_json("template_5w.json")
        else:
            m = f"get_{self.current_module}"
            if hasattr(self.data_manager, m):
                self.current_data = getattr(self.data_manager, m)()
            else:
                fn = self.data_manager.files.get(self.current_module, "")
                self.current_data = self.data_manager._load_json(fn) if fn else []
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for idx, item in enumerate(self.current_data):
            name_val, detail_val = self.extract_columns(item)
            self.tree.insert("", "end", iid=str(idx), values=(name_val, detail_val))

    def extract_columns(self, item):
        if isinstance(item, dict):
            main_val = item.get("name") or item.get("ticket_number") or list(item.keys())[0]
            detail_val = item.get("content") or item.get("description") or item.get("url") or ""
            return str(main_val), str(detail_val)
        return str(item), ""

    def save_data(self):
        if not self.current_module:
            return
        if self.current_module == "template_5w":
            self.data_manager._save_json("template_5w.json", self.current_data)
        else:
            fn = self.data_manager.files.get(self.current_module, "")
            if fn:
                self.data_manager._save_json(fn, self.current_data)

    def add_item(self):
        w = tk.Toplevel(self)
        w.title("Add New Item")
        w.config(bg="#ECECEC")
        w.transient(self)
        w.grab_set()
        w.resizable(True, True)
        center_window(w, 600, 400)

        lbl = tk.Label(w, text="Add a New Item", bg="#ECECEC", font=("Arial", 12, "bold"))
        lbl.pack(pady=(10, 5))

        frame = tk.Frame(w, bg="#ECECEC")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        if self.current_data:
            first_item = self.current_data[0]
            if isinstance(first_item, dict):
                keys = list(first_item.keys())
            else:
                keys = ["value"]
        else:
            keys = ["name", "content"]

        entries = {}
        row_idx = 0
        for k in keys:
            tk.Label(frame, text=k, bg="#ECECEC").grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
            var = tk.StringVar()
            tk.Entry(frame, textvariable=var).grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
            entries[k] = var
            row_idx += 1

        btn_frame = tk.Frame(w, bg="#ECECEC")
        btn_frame.pack(fill="x", pady=(0,10))

        def on_save():
            new_obj = {}
            for k, v in entries.items():
                val = v.get().strip()
                if val:
                    new_obj[k] = val
            if new_obj:
                self.current_data.append(new_obj)
                self.save_data()
                self.refresh_tree()
            w.destroy()

        def on_close():
            w.destroy()

        tk.Button(btn_frame, text="Save", bg="#A8A8A8", command=on_save).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Close", bg="#A8A8A8", command=on_close).pack(side="left", padx=5)

        self.wait_window(w)


    def edit_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        old = self.current_data[idx]
        updated = self.dynamic_edit_form(old)
        if updated is not None:
            self.current_data[idx] = updated
            self.save_data()
            self.refresh_tree()

    def delete_item(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self.current_data):
            if self.confirm_delete("Are you sure you want to delete this item?"):
                del self.current_data[idx]
                self.save_data()
                self.refresh_tree()

    def confirm_delete(self, msg):
        d = tk.Toplevel(self)
        d.title("Confirm Delete")
        d.config(bg="#ECECEC")
        d.transient(self)
        d.grab_set()
        center_window(d, 300, 150)
        tk.Label(d, text=msg, bg="#ECECEC").pack(pady=10, padx=20)
        res = []
        def on_yes():
            res.append(True)
            d.destroy()
        def on_no():
            res.append(False)
            d.destroy()
        bf = tk.Frame(d, bg="#ECECEC")
        bf.pack(pady=10)
        tk.Button(bf, text="Yes", command=on_yes, bg="#A8A8A8").pack(side="left", padx=5)
        tk.Button(bf, text="No", command=on_no, bg="#A8A8A8").pack(side="left", padx=5)
        self.wait_window(d)
        return bool(res and res[0])

    def dynamic_edit_form(self, item=None):
        w = tk.Toplevel(self)
        w.title("Edit Item")
        w.config(bg="#ECECEC")
        w.transient(self)
        w.grab_set()
        center_window(w, 400, 400)
        frame = tk.Frame(w, bg="#ECECEC")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        data = {}
        if isinstance(item, dict):
            for k, v in item.items():
                data[k] = v
        else:
            data["value"] = item if item else ""
        row_idx = 0
        entries = {}
        for k in data.keys():
            tk.Label(frame, text=k, bg="#ECECEC").grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)
            sv = tk.StringVar(value=str(data[k]))
            ent = tk.Entry(frame, textvariable=sv)
            ent.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
            entries[k] = sv
            row_idx += 1
        res = []
        def on_save():
            new_dict = {}
            for k in entries:
                val = entries[k].get().strip()
                new_dict[k] = val
            res.append(new_dict)
            w.destroy()
        tk.Button(w, text="Save", command=on_save, bg="#A8A8A8").pack(side="bottom", pady=5)
        self.wait_window(w)
        if not res:
            return None
        if "value" in res[0] and len(res[0]) == 1:
            return res[0]["value"]
        return res[0]

    def view_in_editor(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        old_item = self.current_data[idx]
        name_val, detail_val = self.extract_columns(old_item)
        editor_win = tk.Toplevel(self)
        editor_win.title(f"Editor: {name_val}")
        editor_win.config(bg="#ECECEC")
        editor_win.transient(self)
        editor_win.grab_set()
        editor_win.resizable(True, True)
        center_window(editor_win, 800, 600)
        lbl = tk.Label(editor_win, text=f"Editing detail of: {name_val}", bg="#ECECEC")
        lbl.pack(pady=(10,0))
        frame_text = tk.Frame(editor_win, bg="#ECECEC")
        frame_text.pack(fill="both", expand=True, padx=10, pady=(0,10))
        text_widget = tk.Text(frame_text, wrap="word")
        text_widget.pack(side="left", fill="both", expand=True)
        scroll = tk.Scrollbar(frame_text, command=text_widget.yview)
        scroll.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scroll.set)
        text_widget.insert("1.0", detail_val)
        bf = tk.Frame(editor_win, bg="#ECECEC")
        bf.pack(fill="x", pady=(0, 10))
        def on_save(item):
            nc = text_widget.get("1.0", "end").strip()
            if isinstance(item, dict):
                if "content" in item:
                    item["content"] = nc
                elif "description" in item:
                    item["description"] = nc
                else:
                    item["content"] = nc
            else:
                new_item = {"name": name_val, "content": nc}
                self.current_data[idx] = new_item
                item = new_item
            self.save_data()
            self.refresh_tree()
            editor_win.destroy()
        def on_close():
            editor_win.destroy()
        tk.Button(bf, text="Save", bg="#A8A8A8", command=lambda: on_save(old_item)).pack(side="left", padx=5)
        tk.Button(bf, text="Close", bg="#A8A8A8", command=on_close).pack(side="left", padx=5)
        self.wait_window(editor_win)
