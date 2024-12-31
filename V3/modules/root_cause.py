import tkinter as tk
from tkinter import ttk, messagebox
import json


class RootCauseModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, editor_module, json_path="data/template_5w.json"):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.editor_module = editor_module
        self.json_path = json_path
        self.templates = []
        self.selected_template = tk.StringVar()
        self.what = tk.StringVar()
        self.when = tk.StringVar()
        self.where = tk.StringVar()
        self.why = tk.StringVar()
        self.who = tk.StringVar()
        self.preview_text = tk.StringVar()  # Para previsualización

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="Root Cause (5W's)")
        frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            rowspan=self.row_span,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        frame.columnconfigure(0, weight=2)  # Inputs column
        frame.columnconfigure(1, weight=1)  # Buttons column

        # Load templates
        self.load_templates()

        # Input Fields Frame
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Template:").grid(row=0, column=0, sticky="w", padx=2, pady=1)
        self.template_combo = ttk.Combobox(
            input_frame, textvariable=self.selected_template, values=[tmpl["name"] for tmpl in self.templates], state="readonly", height=5
        )
        self.template_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=1)
        if self.templates:
            self.template_combo.set(self.templates[0]["name"])

        ttk.Label(input_frame, text="What:").grid(row=1, column=0, sticky="w", padx=2, pady=1)
        ttk.Entry(input_frame, textvariable=self.what, width=25).grid(row=1, column=1, sticky="ew", padx=2, pady=1)

        ttk.Label(input_frame, text="When:").grid(row=2, column=0, sticky="w", padx=2, pady=1)
        ttk.Entry(input_frame, textvariable=self.when, width=25).grid(row=2, column=1, sticky="ew", padx=2, pady=1)

        ttk.Label(input_frame, text="Where:").grid(row=3, column=0, sticky="w", padx=2, pady=1)
        ttk.Entry(input_frame, textvariable=self.where, width=25).grid(row=3, column=1, sticky="ew", padx=2, pady=1)

        ttk.Label(input_frame, text="Why:").grid(row=4, column=0, sticky="w", padx=2, pady=1)
        ttk.Entry(input_frame, textvariable=self.why, width=25).grid(row=4, column=1, sticky="ew", padx=2, pady=1)

        ttk.Label(input_frame, text="Who:").grid(row=5, column=0, sticky="w", padx=2, pady=1)
        ttk.Entry(input_frame, textvariable=self.who, width=25).grid(row=5, column=1, sticky="ew", padx=2, pady=1)

        # Buttons Frame
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        buttons_frame.columnconfigure(0, weight=1)

        ttk.Button(buttons_frame, text="Preview", command=self.preview_template).pack(fill="x", padx=2, pady=2)
        ttk.Button(buttons_frame, text="Submit", command=self.submit_to_editor).pack(fill="x", padx=2, pady=2)

        # Preview Section
        preview_frame = ttk.LabelFrame(frame, text="Preview")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)
        preview_frame.columnconfigure(0, weight=1)

        self.preview_label = tk.Text(preview_frame, wrap="word", height=6, font=("Arial", 10))
        self.preview_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_label.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.preview_label.config(yscrollcommand=scrollbar.set)

    def load_templates(self):
        """Load templates from the JSON file."""
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                self.templates = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", "Failed to load 5W templates. Please check the JSON file.")

    def preview_template(self):
        """Generate preview from the selected template."""
        template_name = self.selected_template.get()
        template = next((tmpl for tmpl in self.templates if tmpl["name"] == template_name), None)
        if not template:
            messagebox.showerror("Error", "Please select a valid template.")
            return

        formatted_text = template["format"].format(
            what=f"[{self.what.get()}]",
            when=f"[{self.when.get()}]",
            where=f"[{self.where.get()}]",
            why=f"[{self.why.get()}]",
            who=f"[{self.who.get()}]",
        )
        self.preview_label.delete("1.0", tk.END)
        self.preview_label.insert("1.0", formatted_text)

    def submit_to_editor(self):
        """Submit the preview text to the editor."""
        if not self.editor_module or not hasattr(self.editor_module, "editor_box"):
            messagebox.showerror("Error", "Editor module not configured!")
            return

        preview_content = self.preview_label.get("1.0", tk.END).strip()
        if not preview_content:
            messagebox.showerror("Error", "Please generate a preview before submitting.")
            return

        self.editor_module.editor_box.insert(tk.END, f"\n\nROOT CAUSE\n\n{preview_content}")
        messagebox.showinfo("Success", "5W details added to the editor!")
