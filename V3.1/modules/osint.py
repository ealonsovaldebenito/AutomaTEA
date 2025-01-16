import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import subprocess
import re
import json
import os


class OSINTModule:
    def __init__(self, parent, row_start, col_start, col_span, row_span, json_path="osint.json", editor_module=None):
        self.parent = parent
        self.row_start = row_start
        self.col_start = col_start
        self.col_span = col_span
        self.row_span = row_span
        self.json_path = json_path
        self.editor_module = editor_module
        self.osint_var = tk.StringVar()
        self.param_var = tk.StringVar()
        self.osint_tools = self.load_osint_tools()

    def load_osint_tools(self):
        """Load OSINT tools from a JSON file. Create file if not exists."""
        if not os.path.exists(self.json_path):
            self.create_default_json()
        try:
            with open(self.json_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messagebox.showerror("Error", f"Error loading '{self.json_path}'. Resetting to default.")
            self.create_default_json()
            return self.load_osint_tools()

    def create_default_json(self):
        """Create a default JSON file if it doesn't exist."""
        default_data = [
            {"name": "VirusTotal", "generate_url": "https://www.virustotal.com/gui/search/"},
            {"name": "AbuseIPDB", "generate_url": "https://www.abuseipdb.com/check/"},
        ]
        try:
            with open(self.json_path, "w") as file:
                json.dump(default_data, file, indent=4)
            messagebox.showinfo("Info", f"Default JSON created at '{self.json_path}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create default JSON: {e}")

    def build(self):
        frame = ttk.LabelFrame(self.parent, text="OSINT Tools")
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
        frame.columnconfigure(1, weight=2)

        # Combobox y entradas
        ttk.Label(frame, text="Select Tool:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Combobox(
            frame,
            textvariable=self.osint_var,
            values=[tool["name"] for tool in self.osint_tools],
            state="readonly",
            width=30
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(frame, text="Parameter:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame, textvariable=self.param_var, width=30).grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Botones distribuidos en columnas
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Search", command=self.search_tool).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Manage", command=self.manage_osint_tools).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="ISP Info", command=self.fetch_isp_info).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def search_tool(self):
        """Perform a search using the selected OSINT tool."""
        selected_tool = self.osint_var.get()
        param = self.param_var.get().strip()

        if not selected_tool:
            messagebox.showwarning("Warning", "Please select a tool.")
            return

        if not param:
            messagebox.showwarning("Warning", "Please enter a parameter.")
            return

        tool = next((tool for tool in self.osint_tools if tool["name"] == selected_tool), None)
        if not tool:
            messagebox.showerror("Error", f"Tool '{selected_tool}' not found.")
            return

        webbrowser.open(tool["generate_url"] + param)

    def manage_osint_tools(self):
        """Open a manager to add, edit, and delete OSINT tools."""
        manager_window = tk.Toplevel(self.parent)
        manager_window.title("Manage OSINT Tools")
        manager_window.geometry("500x400")

        # Listbox para mostrar herramientas
        tools_listbox = tk.Listbox(manager_window, height=15)
        tools_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for tool in self.osint_tools:
            tools_listbox.insert("end", tool["name"])

        def add_tool():
            """Add a new tool."""
            name = tk.simpledialog.askstring("Add Tool", "Enter tool name:")
            url = tk.simpledialog.askstring("Add Tool", "Enter tool URL (use {0} as a placeholder):")

            if name and url:
                self.osint_tools.append({"name": name, "generate_url": url})
                tools_listbox.insert("end", name)
                self.save_tools()

        def edit_tool():
            """Edit the selected tool."""
            selected_index = tools_listbox.curselection()
            if not selected_index:
                messagebox.showwarning("Select Tool", "Please select a tool to edit.")
                return

            selected_tool = self.osint_tools[selected_index[0]]
            name = tk.simpledialog.askstring("Edit Tool", "Edit tool name:", initialvalue=selected_tool["name"])
            url = tk.simpledialog.askstring("Edit Tool", "Edit tool URL:", initialvalue=selected_tool["generate_url"])

            if name and url:
                self.osint_tools[selected_index[0]] = {"name": name, "generate_url": url}
                tools_listbox.delete(selected_index)
                tools_listbox.insert(selected_index, name)
                self.save_tools()

        def delete_tool():
            """Delete the selected tool."""
            selected_index = tools_listbox.curselection()
            if not selected_index:
                messagebox.showwarning("Select Tool", "Please select a tool to delete.")
                return

            confirm = messagebox.askyesno("Delete Tool", "Are you sure you want to delete this tool?")
            if confirm:
                tools_listbox.delete(selected_index)
                del self.osint_tools[selected_index[0]]
                self.save_tools()

        button_frame = ttk.Frame(manager_window)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Add", command=add_tool).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Edit", command=edit_tool).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=delete_tool).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=manager_window.destroy).pack(side="right", padx=5)

    def save_tools(self):
        """Save the updated tools list to the JSON file."""
        try:
            with open(self.json_path, "w") as file:
                json.dump(self.osint_tools, file, indent=4)
            messagebox.showinfo("Success", "Changes saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")

    def fetch_isp_info(self):
        """Fetch ISP information from AbuseIPDB using CURL and display results."""
        param = self.param_var.get().strip()
        if not param:
            messagebox.showwarning("Input Required", "Please enter an IP address.")
            return

        try:
            curl_command = ["curl", f"https://www.abuseipdb.com/check/{param}"]
            output = subprocess.check_output(curl_command, stderr=subprocess.STDOUT).decode("utf-8")
            info = self.parse_abuseipdb_data(output)
            if not info:
                messagebox.showinfo("No Data", f"No relevant data found for IP: {param}")
                return
            self.show_results_popup(param, info)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to fetch data for IP: {param}\n{e.output.decode('utf-8')}")

    def parse_abuseipdb_data(self, html):
        """Parse HTML data to extract ISP and related information."""
        patterns = {
            "ISP": r"<th>ISP<\/th>\s*<td>\s*(.*?)\s*<\/td>",
            "Usage Type": r"<th>Usage Type<\/th>\s*<td>\s*(.*?)\s*<\/td>",
            "ASN": r"<th>ASN<\/th>\s*<td>\s*(.*?)\s*<\/td>",
            "Domain Name": r"<th>Domain Name<\/th>\s*<td>\s*(.*?)\s*<\/td>",
            "Country": r"<th>Country<\/th>\s*<td>\s*(.*?)\s*<\/td>",
            "City": r"<th>City<\/th>\s*<td>\s*(.*?)\s*<\/td>",
        }

        parsed_data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            parsed_data[key] = match.group(1).strip() if match else "N/A"

        if all(value == "N/A" for value in parsed_data.values()):
            return None

        return parsed_data

    def show_results_popup(self, param, info):
        """Display the parsed information in a popup."""
        popup = tk.Toplevel(self.parent)
        popup.title(f"Results for {param}")
        popup.geometry("350x250")

        result_text = "\n".join([f"{key}: {value}" for key, value in info.items()])
        text_widget = tk.Text(popup, wrap="word", height=10, width=40)
        text_widget.insert("1.0", result_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(popup)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Send to Editor", command=lambda: self.send_to_editor(result_text)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(result_text)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=popup.destroy).pack(side="right", padx=5)

    def send_to_editor(self, text):
        """Send the parsed information to the editor module."""
        if self.editor_module and hasattr(self.editor_module, "editor_box") and self.editor_module.editor_box:
            self.editor_module.editor_box.insert("1.0", text)
            messagebox.showinfo("Success", "Information sent to the editor.")
        else:
            messagebox.showerror("Error", "Editor module is not properly configured.")

    def copy_to_clipboard(self, text):
        """Copy the parsed information to the clipboard."""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(text)
        self.parent.update()
        messagebox.showinfo("Copied", "Information copied to clipboard.")
