import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import uuid
from datetime import datetime


class NotesModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager, json_path="data/notes.json"):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.json_path = json_path
        self.notes = []
        self.filtered_notes = []

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Notes")
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

        controls_frame = ttk.Frame(frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=2)
        controls_frame.columnconfigure(0, weight=1)

        ttk.Label(controls_frame, text="Search:").grid(row=0, column=0, sticky="w", padx=2)
        self.search_entry = ttk.Entry(controls_frame, width=30)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(controls_frame, text="Search", command=self.filter_notes).grid(row=0, column=2, sticky="w", padx=2)

        ttk.Button(controls_frame, text="New Note", command=self.new_note, width=12).grid(row=0, column=3, sticky="e", padx=2)
        ttk.Button(controls_frame, text="Delete Note", command=self.delete_note, width=12).grid(row=0, column=4, sticky="e", padx=2)

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("name", "timestamp", "tags"), show="headings", height=10)
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.config(yscrollcommand=scrollbar.set)

        self.tree.heading("name", text="Name")
        self.tree.heading("timestamp", text="Date and Time")
        self.tree.heading("tags", text="Tags")
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("timestamp", width=120, anchor="center")
        self.tree.column("tags", width=150, anchor="center")

        self.load_notes()
        self.tree.bind("<Double-1>", self.open_note_details)

    def load_notes(self):
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, "r", encoding="utf-8") as file:
                    self.notes = json.load(file)
                    self.filtered_notes = self.notes[:]
                    self.update_notes_tree()
        except:
            self.notes = []
            self.filtered_notes = []

    def update_notes_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for note in self.filtered_notes:
            self.tree.insert(
                "",
                "end",
                values=(
                    note["name"],
                    note["timestamp"],
                    ", ".join(note.get("tags", [])),
                ),
            )

    def filter_notes(self):
        search_text = self.search_entry.get().lower()
        self.filtered_notes = [
            note
            for note in self.notes
            if search_text in note["name"].lower()
            or search_text in note["content"].lower()
            or any(search_text in tag.lower() for tag in note.get("tags", []))
        ]
        self.update_notes_tree()

    def new_note(self):
        new_note = {
            "id": str(uuid.uuid4()),
            "name": "New Note",
            "content": "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tags": [],
        }
        self.notes.append(new_note)
        self.filtered_notes.append(new_note)
        self.save_notes_to_file()
        self.update_notes_tree()
        self.open_note_editor(new_note)

    def delete_note(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "No note selected!")
            return

        note_values = self.tree.item(selected_item, "values")
        note_name = note_values[0]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{note_name}'?")
        if not confirm:
            return

        self.notes = [note for note in self.notes if note["name"] != note_name]
        self.filtered_notes = [note for note in self.filtered_notes if note["name"] != note_name]
        self.save_notes_to_file()
        self.update_notes_tree()
        messagebox.showinfo("Success", f"Note '{note_name}' deleted successfully!")

    def open_note_details(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        note_values = self.tree.item(selected_item, "values")
        note_name = note_values[0]
        note_data = next((note for note in self.notes if note["name"] == note_name), None)

        if note_data:
            self.open_note_editor(note_data)

    def open_note_editor(self, note_data):
        editor_window = tk.Toplevel(self.parent)
        editor_window.title(f"Note: {note_data['name']}")
        editor_window.geometry("700x500")
        editor_window.resizable(False, False)

        ttk.Button(editor_window, text="Save Changes", command=lambda: self.save_changes(note_data, editor_window)).pack(fill="x", pady=5)

        ttk.Label(editor_window, text="Note Name:").pack(pady=2)
        self.name_entry = ttk.Entry(editor_window)
        self.name_entry.insert(0, note_data["name"])
        self.name_entry.pack(fill="x", padx=5, pady=2)

        ttk.Label(editor_window, text="Tags (comma-separated):").pack(pady=2)
        self.tags_entry = ttk.Entry(editor_window)
        self.tags_entry.insert(0, ", ".join(note_data.get("tags", [])))
        self.tags_entry.pack(fill="x", padx=5, pady=2)

        text_frame = ttk.Frame(editor_window)
        text_frame.pack(fill="both", expand=True, padx=5, pady=2)
        self.content_text = tk.Text(text_frame, wrap="word")
        self.content_text.insert("1.0", note_data["content"])
        self.content_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(text_frame, command=self.content_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.content_text.config(yscrollcommand=scrollbar.set)

    def save_changes(self, note_data, editor_window):
        new_name = self.name_entry.get().strip()
        new_tags = [tag.strip() for tag in self.tags_entry.get().split(",") if tag.strip()]
        new_content = self.content_text.get("1.0", "end").strip()
        new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        note_data["name"] = new_name
        note_data["tags"] = new_tags
        note_data["content"] = new_content
        note_data["timestamp"] = new_timestamp

        self.save_notes_to_file()
        self.update_notes_tree()
        messagebox.showinfo("Success", "Changes saved successfully!")
        editor_window.destroy()

    def save_notes_to_file(self):
        with open(self.json_path, "w", encoding="utf-8") as file:
            json.dump(self.notes, file, indent=4)
