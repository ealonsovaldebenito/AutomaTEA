import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from datetime import datetime


class QueriesModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager, queries_path="data/queries.json"):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.queries_path = queries_path
        self.search_var = tk.StringVar()

        self.queries = []
        self.sort_order = {}

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Queries")
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
        frame.rowconfigure(1, weight=1)

        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(search_frame, text="Search", command=self.update_queries_list).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Add Query", command=self.new_query).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Delete Query", command=self.delete_query).pack(side="left", padx=5)

        columns = ("name", "platform", "category", "objective", "timestamp")
        self.queries_tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.queries_tree.heading(
                col,
                text=col.replace("_", " ").title(),
                anchor="center",
                command=lambda c=col: self.sort_by_column(c),
            )
            self.queries_tree.column(col, width=120, anchor="center")

        self.queries_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.queries_tree.bind("<Double-1>", self.on_query_double_click)

        self.load_queries()
        self.update_queries_list()

    def load_queries(self):
        try:
            with open(self.queries_path, "r", encoding="utf-8") as file:
                self.queries = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.queries = []

    def update_queries_list(self):
        self.queries_tree.delete(*self.queries_tree.get_children())
        query = self.search_var.get().lower()

        for query_data in self.queries:
            if any(
                query in str(value).lower()
                for value in query_data.values()
            ):
                self.queries_tree.insert(
                    "",
                    "end",
                    values=(
                        query_data.get("name", ""),
                        query_data.get("platform", ""),
                        query_data.get("category", ""),
                        query_data.get("objective", ""),
                        query_data.get("timestamp", ""),
                    ),
                )

    def sort_by_column(self, col):
        if col not in self.sort_order:
            self.sort_order[col] = False  # False means ascending order

        self.queries.sort(
            key=lambda x: x.get(col, ""),
            reverse=self.sort_order[col],
        )
        self.sort_order[col] = not self.sort_order[col]
        self.update_queries_list()

    def new_query(self):
        new_query = {
            "id": str(uuid.uuid4()),
            "name": "New Query",
            "platform": "",
            "category": "",
            "objective": "",
            "description": "",
            "content": "",
            "tuc": "",
            "ticket_number": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.open_query_editor(new_query, is_new=True)

    def delete_query(self):
        selected_item = self.queries_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No query selected!")
            return

        query_values = self.queries_tree.item(selected_item[0], "values")
        query_name = query_values[0]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{query_name}'?")
        if not confirm:
            return

        self.queries = [query for query in self.queries if query.get("name") != query_name]
        self.save_queries()
        self.update_queries_list()
        messagebox.showinfo("Success", f"Query '{query_name}' deleted successfully!")

    def on_query_double_click(self, event):
        selected_item = self.queries_tree.selection()
        if not selected_item:
            return

        query_data = self.queries_tree.item(selected_item[0], "values")
        query_name = query_data[0]

        query = next((q for q in self.queries if q.get("name") == query_name), None)
        if query:
            self.open_query_editor(query)

    def open_query_editor(self, query, is_new=False):
        editor_window = tk.Toplevel(self.parent)
        editor_window.title(f"Edit Query: {query.get('name')}")
        editor_window.geometry("700x500")
        editor_window.resizable(True, True)

        main_frame = ttk.Frame(editor_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        save_button = ttk.Button(
            main_frame,
            text="Save Changes",
            command=lambda: self.save_changes(query, editor_window, is_new),
        )
        save_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left_frame.columnconfigure(1, weight=1)

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_frame.columnconfigure(1, weight=1)

        fields_left = ["name", "platform", "category", "objective"]
        fields_right = ["tuc", "ticket_number", "description"]

        self.entry_widgets = {}

        for idx, field in enumerate(fields_left):
            ttk.Label(left_frame, text=field.capitalize()).grid(row=idx, column=0, sticky="e", pady=5)
            entry = ttk.Entry(left_frame)
            entry.grid(row=idx, column=1, sticky="ew", pady=5)
            entry.insert(0, query.get(field, ""))
            self.entry_widgets[field] = entry

        for idx, field in enumerate(fields_right):
            ttk.Label(right_frame, text=field.capitalize()).grid(row=idx, column=0, sticky="e", pady=5)
            entry = ttk.Entry(right_frame)
            entry.grid(row=idx, column=1, sticky="ew", pady=5)
            entry.insert(0, query.get(field, ""))
            self.entry_widgets[field] = entry

        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        content_frame.columnconfigure(0, weight=1)

        ttk.Label(content_frame, text="Content").grid(row=0, column=0, sticky="w")
        self.content_text = tk.Text(content_frame, wrap="word", height=8)
        self.content_text.grid(row=1, column=0, sticky="nsew")
        self.content_text.insert("1.0", query.get("content", ""))

        scrollbar = ttk.Scrollbar(content_frame, command=self.content_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.content_text.config(yscrollcommand=scrollbar.set)

    def save_changes(self, query, editor_window, is_new):
        for field, entry in self.entry_widgets.items():
            query[field] = entry.get()

        query["content"] = self.content_text.get("1.0", "end").strip()
        query["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_new:
            self.queries.append(query)

        self.save_queries()
        self.update_queries_list()
        messagebox.showinfo("Success", "Query saved successfully!")
        editor_window.destroy()

    def save_queries(self):
        with open(self.queries_path, "w", encoding="utf-8") as file:
            json.dump(self.queries, file, indent=4)
