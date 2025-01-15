import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os


class QueriesModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager, queries_path="data/queries.json", tuc_path="data/tucs.json"):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.queries_path = queries_path
        self.tuc_path = tuc_path
        self.queries = []
        self.filtered_queries = []
        self.categories = ["All", "Interactive Login", "Non-Interactive Login", "Network Device Info", "Identity Info", "Risk Identity", "Network Info"]
        self.siems = ["All", "Sentinel Azure", "Splunk", "QRadar", "SolarWinds", "GoogleSecOps", "Otros"]

    def build(self):
        # Main frame
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

        # Filters and Buttons
        controls_frame = ttk.Frame(frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=2)

        # Search bar
        ttk.Label(controls_frame, text="Search:").grid(row=0, column=0, sticky="w", padx=2)
        self.search_entry = ttk.Entry(controls_frame, width=30)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(controls_frame, text="Search", command=self.filter_queries).grid(row=0, column=2, sticky="w", padx=2)

        # Category filter
        ttk.Label(controls_frame, text="Category:").grid(row=0, column=3, sticky="w", padx=2)
        self.category_filter = tk.StringVar(value="All")
        self.category_menu = ttk.OptionMenu(controls_frame, self.category_filter, *self.categories, command=lambda _: self.filter_queries())
        self.category_menu.grid(row=0, column=4, sticky="ew", padx=2)

        # SIEM filter
        ttk.Label(controls_frame, text="SIEM:").grid(row=0, column=5, sticky="w", padx=2)
        self.siem_filter = tk.StringVar(value="All")
        self.siem_menu = ttk.OptionMenu(controls_frame, self.siem_filter, *self.siems, command=lambda _: self.filter_queries())
        self.siem_menu.grid(row=0, column=6, sticky="ew", padx=2)

        # Reset filters button
        ttk.Button(controls_frame, text="Reset", command=self.reset_filters).grid(row=0, column=7, sticky="e", padx=2)

        # Treeview for Queries
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=2)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("name", "siem", "category", "objective"), show="headings", height=10)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.config(yscrollcommand=scrollbar.set)

        # Configure Treeview Columns
        self.tree.heading("name", text="Name")
        self.tree.heading("siem", text="SIEM")
        self.tree.heading("category", text="Category")
        self.tree.heading("objective", text="Objective")

        self.tree.column("name", width=150, anchor="w")
        self.tree.column("siem", width=120, anchor="center")
        self.tree.column("category", width=150, anchor="center")
        self.tree.column("objective", width=150, anchor="w")

        self.load_queries()
        self.tree.bind("<Double-1>", self.open_query_details)  # Doble clic para abrir detalles

    def load_queries(self):
        """Load queries from the JSON file."""
        try:
            if os.path.exists(self.queries_path):
                with open(self.queries_path, "r", encoding="utf-8") as file:
                    self.queries = json.load(file)
                    self.filtered_queries = self.queries[:]
                    self.update_queries_tree()
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", "Failed to load queries file.")
            self.queries = []
            self.filtered_queries = []

    def update_queries_tree(self):
        """Update the Treeview with filtered queries."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for query in self.filtered_queries:
            self.tree.insert(
                "",
                "end",
                values=(query["name"], query["platform"], query["category"], query["objective"]),
            )

    def filter_queries(self):
        """Filter queries based on the filters."""
        search_text = self.search_entry.get().lower()
        category = self.category_filter.get()
        siem = self.siem_filter.get()

        self.filtered_queries = [
            query for query in self.queries
            if (
                any(search_text in str(query.get(field, "")).lower() for field in ["name", "description", "content", "objective", "tuc", "ticket_number"])
            )
            and (category == "All" or query["category"] == category)
            and (siem == "All" or query["platform"] == siem)
        ]
        self.update_queries_tree()

    def reset_filters(self):
        """Reset filters and show all queries."""
        self.search_entry.delete(0, tk.END)
        self.category_filter.set("All")
        self.siem_filter.set("All")
        self.filtered_queries = self.queries[:]
        self.update_queries_tree()

    def open_query_details(self, event):
        """Open query details and allow editing."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        query_values = self.tree.item(selected_item, "values")
        query_name = query_values[0]
        query_data = next((query for query in self.filtered_queries if query["name"] == query_name), None)

        if query_data:
            self.edit_query_window(query_data)

    def edit_query_window(self, query_data):
        """Open a window to edit a query."""
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"Query: {query_data['name']}")
        details_window.geometry("600x500")
        details_window.resizable(False, False)

        ttk.Label(details_window, text="Edit Query", font=("Arial", 14, "bold")).pack(pady=5)

        # Editable fields
        fields = ["name", "category", "platform", "objective", "description", "content", "tuc", "ticket_number"]
        entries = {}

        for field in fields:
            ttk.Label(details_window, text=field.replace("_", " ").capitalize()).pack(pady=2, anchor="w")
            entry = ttk.Entry(details_window)
            entry.insert(0, str(query_data.get(field, "")))
            entry.pack(fill="x", padx=5, pady=2)
            entries[field] = entry

        def save_changes():
            for field, entry in entries.items():
                query_data[field] = entry.get()
            self.save_queries()
            messagebox.showinfo("Success", "Query updated successfully!")
            details_window.destroy()
            self.update_queries_tree()

        ttk.Button(details_window, text="Save Changes", command=save_changes).pack(pady=5)

    def save_queries(self):
        """Save queries to JSON file."""
        try:
            with open(self.queries_path, "w", encoding="utf-8") as file:
                json.dump(self.queries, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save queries: {e}")
