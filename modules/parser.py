import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET


class ParserModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, data_manager):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.data_manager = data_manager
        self.input_text = tk.StringVar()
        self.selected_method = tk.StringVar(value="JSON")

    def build_auto_parser(self):
        frame = ttk.LabelFrame(self.parent, text="Parser Module")
        frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            rowspan=self.row_span,
            sticky="nsew",
            padx=5,
            pady=5,
        )
        frame.columnconfigure(1, weight=1)

        # Input text area
        ttk.Label(frame, text="Input Text:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        input_box = ttk.Entry(frame, textvariable=self.input_text, width=60)
        input_box.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Parse method selection
        ttk.Label(frame, text="Parse Method:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        methods = ["JSON", "CSV", "XML"]
        method_combo = ttk.Combobox(frame, values=methods, textvariable=self.selected_method, state="readonly")
        method_combo.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Parse button
        parse_button = ttk.Button(frame, text="Parse", command=self.parse_input)
        parse_button.grid(row=2, column=0, columnspan=3, pady=10)

    def parse_input(self):
        text = self.input_text.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Input text is empty!")
            return

        method = self.selected_method.get()
        if method == "JSON":
            self.parse_json(text)
        elif method == "CSV":
            self.parse_csv(text)
        elif method == "XML":
            self.parse_xml(text)

    def parse_json(self, text):
        try:
            import json
            data = json.loads(text)
            keys = ', '.join(data.keys())
            messagebox.showinfo("Parsed JSON", f"Keys: {keys}")
        except Exception as e:
            messagebox.showerror("JSON Parse Error", str(e))

    def parse_csv(self, text):
        try:
            rows = text.splitlines()
            headers = rows[0].split(",")
            messagebox.showinfo("Parsed CSV", f"Headers: {', '.join(headers)}")
        except Exception as e:
            messagebox.showerror("CSV Parse Error", str(e))

    def parse_xml(self, text):
        try:
            root = ET.fromstring(text)
            elements = {elem.tag for elem in root.iter()}
            messagebox.showinfo("Parsed XML", f"Elements: {', '.join(elements)}")
        except Exception as e:
            messagebox.showerror("XML Parse Error", str(e))
