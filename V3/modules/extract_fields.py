import tkinter as tk
from tkinter import ttk, messagebox
import re


class ExtractFieldsModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, editor_module):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.editor_module = editor_module  # Referencia al EditorModule

    def build(self):
        # Contenedor principal
        frame = ttk.LabelFrame(self.parent, text="Extracted Fields")
        frame.grid(
            row=self.row_start,
            column=self.col_start,
            columnspan=self.col_span,
            rowspan=self.row_span,
            sticky="nsew",
            padx=2,
            pady=2,
        )
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        # Botón para extraer campos
        ttk.Button(
            button_frame,
            text="Extract Fields",
            command=self.extract_fields,
            width=12,
        ).grid(row=0, column=0, pady=2, padx=2, sticky="w")

        # Botón para limpiar campos
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_fields,
            width=12,
        ).grid(row=0, column=1, pady=2, padx=2, sticky="e")

        # Canvas para contenido scrollable
        self.fields_canvas = tk.Canvas(frame, highlightthickness=0, height=150)  # 5 filas visibles (aproximadamente)
        self.fields_canvas.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)

        self.scrollable_frame = ttk.Frame(self.fields_canvas)
        self.scrollable_window = self.fields_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Barra de desplazamiento vertical
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.fields_canvas.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.fields_canvas.configure(yscrollcommand=scrollbar.set)

        # Vincular el canvas con la rueda del mouse, solo para este módulo
        self.fields_canvas.bind("<Enter>", self._bind_mousewheel)
        self.fields_canvas.bind("<Leave>", self._unbind_mousewheel)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.fields_canvas.configure(scrollregion=self.fields_canvas.bbox("all")),
        )

    def display_extracted_fields(self, fields):
        """
        Muestra los campos extraídos en la interfaz en columnas.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not fields:
            ttk.Label(self.scrollable_frame, text="No fields extracted.", anchor="center").pack(pady=2)
            return

        # Mostrar los campos en columnas verticales
        max_rows = 5
        row = 0
        col = 0

        for index, (key, value_list) in enumerate(fields.items(), start=1):
            for value in value_list:
                field_frame = ttk.Frame(self.scrollable_frame)
                field_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=1)

                # Viñeta con índice
                ttk.Label(
                    field_frame,
                    text=f"{index}.",
                    anchor="center",
                    width=2,
                    font=("Arial", 8),
                    foreground="blue",
                ).grid(row=0, column=0, sticky="w")

                # Etiqueta del campo
                ttk.Label(
                    field_frame,
                    text=f"{key}:",
                    anchor="w",
                    width=20,
                    font=("Arial", 8),
                ).grid(row=0, column=1, sticky="w")

                # Valor del campo
                ttk.Label(
                    field_frame,
                    text=value,
                    anchor="w",
                    wraplength=150,
                    font=("Arial", 8),
                ).grid(row=0, column=2, sticky="w")

                # Botón para copiar al portapapeles
                ttk.Button(
                    field_frame,
                    text="📋",
                    width=2,
                    command=lambda v=value: self.copy_to_clipboard(v),
                ).grid(row=0, column=3, sticky="w", padx=2)

                # Ajustar la posición de fila y columna
                row += 1
                if row >= max_rows:
                    row = 0
                    col += 1

    def extract_fields(self):
        """
        Extrae campos reales del contenido establecido usando patrones basados en ":".
        Solo analiza el contenido después de "####INVESTIGATION DETAILS####".
        """
        if not self.editor_module or not hasattr(self.editor_module, "editor_box"):
            messagebox.showerror("Error", "Editor module not configured!")
            return

        content_to_parse = self.editor_module.editor_box.get("1.0", tk.END).strip()
        if not content_to_parse:
            messagebox.showwarning("No Content", "No content in the editor to extract fields from.")
            return

        # Buscar la sección relevante
        investigation_marker = "####INVESTIGATION DETAILS####"
        if investigation_marker not in content_to_parse:
            messagebox.showwarning("No Marker Found", f"'{investigation_marker}' not found in the content.")
            return

        relevant_content = content_to_parse.split(investigation_marker, 1)[1].strip()

        # Extraer campos usando el patrón actualizado
        # Captura claves completas (incluye espacios) y múltiples valores
        pattern = r"(?P<key>.+?):\s+(?P<value>[^\s].+)"
        matches = re.findall(pattern, relevant_content)

        extracted_fields = {}
        for key, value in matches:
            key = key.strip()
            if key in extracted_fields:
                extracted_fields[key].append(value.strip())
            else:
                extracted_fields[key] = [value.strip()]

        if not extracted_fields:
            messagebox.showinfo("No Fields Found", "No fields were extracted from the content.")
        else:
            self.display_extracted_fields(extracted_fields)

    def copy_to_clipboard(self, text):
        """
        Copia el texto especificado al portapapeles.
        """
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()
        messagebox.showinfo("Copied", f"Copied to clipboard: {text}")

    def clear_fields(self):
        """
        Limpia todos los campos mostrados.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.scrollable_frame, text="Fields cleared.", anchor="center").pack(pady=2)

    def _bind_mousewheel(self, event):
        """
        Permite desplazar el canvas con la rueda del mouse cuando el puntero está sobre este módulo.
        """
        self.fields_canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        """
        Desactiva el desplazamiento con la rueda del mouse cuando el puntero sale del módulo.
        """
        self.fields_canvas.unbind("<MouseWheel>")

    def _on_mousewheel(self, event):
        """
        Maneja el desplazamiento con la rueda del mouse.
        """
        self.fields_canvas.yview_scroll(-1 * (event.delta // 120), "units")
