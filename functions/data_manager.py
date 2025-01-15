import json
import os


class DataManager:
    def __init__(self):
        self.data_folder = "./data/"
        self.files = {
            "osint": "osint.json",
            "queries": "queries.json",
            "templates": "templates.json",
            "tucs": "tucs.json",
            "clients": "clients.json",
            "notes": "notes.json",
            "tickets": "tickets.json",
        }

    def _load_json(self, filename):
        path = os.path.join(self.data_folder, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def _save_json(self, filename, data):
        path = os.path.join(self.data_folder, filename)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # Métodos para cargar datos
    def get_templates(self):
        return self._load_json(self.files["templates"])

    def get_osint(self):
        return self._load_json(self.files["osint"])

    def get_queries(self):
        return self._load_json(self.files["queries"])

    def get_notes(self):
        return self._load_json(self.files["notes"])

    def get_tickets(self):
        return self._load_json(self.files["tickets"])

    def get_clients(self):
        return self._load_json(self.files["clients"])

    def get_tucs(self):
        return self._load_json(self.files["tucs"])

    # Métodos para agregar datos
    def add_ticket(self, ticket):
        tickets = self.get_tickets()
        tickets.append(ticket)
        self._save_json(self.files["tickets"], tickets)

    def add_note(self, note):
        notes = self.get_notes()
        notes.append(note)
        self._save_json(self.files["notes"], notes)

    def add_client(self, client_name):
        clients = self.get_clients()
        if client_name not in [client["name"] for client in clients]:
            clients.append({"name": client_name})
            self._save_json(self.files["clients"], clients)

    def add_tuc(self, tuc_name):
        tucs = self.get_tucs()
        if tuc_name not in [tuc["name"] for tuc in tucs]:
            tucs.append({"name": tuc_name})
            self._save_json(self.files["tucs"], tucs)

    def add_osint_tool(self, tool_name, tool_url):
        tools = self.get_osint()
        if tool_name not in [tool["name"] for tool in tools]:
            tools.append({"name": tool_name, "url": tool_url})
            self._save_json(self.files["osint"], tools)

    def add_template(self, template_name, content):
        templates = self.get_templates()
        if template_name not in [template["name"] for template in templates]:
            templates.append({"name": template_name, "content": content})
            self._save_json(self.files["templates"], templates)
    