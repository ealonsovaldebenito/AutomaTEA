import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid


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
        self.preview_text = tk.StringVar()

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
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=1)

        self.load_templates()

        # Input Fields Frame
        input_frame = ttk.Frame(frame)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Template:").grid(row=0, column=0, sticky="w", padx=2, pady=1)
        self.template_combo = ttk.Combobox(
            input_frame,
            textvariable=self.selected_template,
            values=[tmpl["name"] for tmpl in self.templates],
            state="readonly",
            height=5,
        )
        self.template_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=1)
        if self.templates:
            self.template_combo.set(self.templates[0]["name"])

        fields = [("What", self.what), ("When", self.when), ("Where", self.where), ("Why", self.why), ("Who", self.who)]
        for idx, (label, var) in enumerate(fields, start=1):
            ttk.Label(input_frame, text=f"{label}:").grid(row=idx, column=0, sticky="w", padx=2, pady=1)
            ttk.Entry(input_frame, textvariable=var, width=25).grid(row=idx, column=1, sticky="ew", padx=2, pady=1)

        # Buttons Frame
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        buttons_frame.columnconfigure(0, weight=1)

        ttk.Button(buttons_frame, text="Preview", command=self.preview_template).pack(fill="x", padx=2, pady=2)
        ttk.Button(buttons_frame, text="Submit", command=self.submit_to_editor).pack(fill="x", padx=2, pady=2)
        ttk.Button(buttons_frame, text="Clear", command=self.clear_fields).pack(fill="x", padx=2, pady=2)
        ttk.Button(buttons_frame, text="Add Template", command=self.add_template).pack(fill="x", padx=2, pady=2)

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
            what=self.what.get(),
            when=self.when.get(),
            where=self.where.get(),
            why=self.why.get(),
            who=self.who.get(),
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

    def clear_fields(self):
        """Clear all input fields."""
        self.what.set("")
        self.when.set("")
        self.where.set("")
        self.why.set("")
        self.who.set("")
        self.preview_label.delete("1.0", tk.END)

    def center_window(self, window, width, height):
        """Center a window on the screen."""
        window.withdraw()  # Ocultar la ventana mientras se posiciona
        window.update_idletasks()  # Forzar el cálculo de geometría
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.deiconify()  # Mostrar la ventana una vez que esté posicionada


    def add_template(self):
        """Open a dialog to add a new template with a base format."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Template")
        self.center_window(dialog, 400, 300)  # Asegurarse de que esté centrada
        dialog.transient(self.parent)
        dialog.grab_set()

        ttk.Label(dialog, text="Template Name:").pack(pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var)
        name_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(dialog, text="Template Format:").pack(pady=5)
        format_text = tk.Text(dialog, wrap="word", height=8)
        format_text.insert(
            "1.0",
            "Root Cause Analysis:\n"
            "{what}\n"
            "{when}\n"
            "{where}\n"
            "{why}\n"
            "{who}\n",
        )
        format_text.pack(fill="both", expand=True, padx=10, pady=5)

        def save_template():
            name = name_var.get().strip()
            template_format = format_text.get("1.0", "end").strip()
            if not name or not template_format:
                messagebox.showerror("Error", "Both fields are required!")
                return

            new_template = {"name": name, "format": template_format}
            self.templates.append(new_template)
            with open(self.json_path, "w", encoding="utf-8") as file:
                json.dump(self.templates, file, indent=4)
            self.template_combo["values"] = [tmpl["name"] for tmpl in self.templates]
            messagebox.showinfo("Success", "Template added successfully!")
            dialog.destroy()

        ttk.Button(dialog, text="Save", command=save_template).pack(side="left", padx=10, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side="right", padx=10, pady=10)

