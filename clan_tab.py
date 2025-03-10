import tkinter as tk
from tkinter import ttk
import json
from utils import make_request, BASE_URL
import os

class ClanTab:
    def __init__(self, notebook, api_key, raw_mode, last_api_call, search_history, status_label):
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Clan")
        self.clan_notebook = ttk.Notebook(self.tab)
        self.clan_notebook.pack(expand=1, fill="both")

        # Recruitment Sub-Tab
        self.clan_recruitment_frame = ttk.Frame(self.clan_notebook)
        self.clan_notebook.add(self.clan_recruitment_frame, text="Recruitment")
        rec_input_frame = ttk.Frame(self.clan_recruitment_frame)
        rec_input_frame.pack(fill="x", pady=5)
        ttk.Label(rec_input_frame, text="Clan Name:").pack(side=tk.LEFT, padx=5)
        self.clan_rec_name_combobox = ttk.Combobox(rec_input_frame, values=search_history["clans"], width=40)
        self.clan_rec_name_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(rec_input_frame, text="Search", command=self.search_recruitment).pack(side=tk.LEFT, padx=5)
        ttk.Button(rec_input_frame, text="Clear", command=lambda: self.clan_rec_result_tree.delete(*self.clan_rec_result_tree.get_children())).pack(side=tk.LEFT, padx=5)
        ttk.Button(rec_input_frame, text="Export", command=self.export_recruitment).pack(side=tk.LEFT, padx=5)
        rec_result_frame = ttk.Frame(self.clan_recruitment_frame)
        rec_result_frame.pack(fill="both", expand=1)
        self.clan_rec_result_tree = ttk.Treeview(rec_result_frame, columns=("Category", "Detail"), show="headings", height=25)
        self.clan_rec_result_tree.heading("Category", text="Category")
        self.clan_rec_result_tree.heading("Detail", text="Detail")
        self.clan_rec_result_tree.column("Category", width=200, anchor="w")
        self.clan_rec_result_tree.column("Detail", width=500, anchor="w")
        self.clan_rec_result_tree.pack(side=tk.LEFT, fill="both", expand=1)
        clan_rec_scroll = ttk.Scrollbar(rec_result_frame, orient="vertical", command=self.clan_rec_result_tree.yview)
        clan_rec_scroll.pack(side=tk.RIGHT, fill="y")
        self.clan_rec_result_tree.configure(yscrollcommand=clan_rec_scroll.set)

        # Logs Sub-Tab
        self.clan_logs_frame = ttk.Frame(self.clan_notebook)
        self.clan_notebook.add(self.clan_logs_frame, text="Logs")
        logs_input_frame = ttk.Frame(self.clan_logs_frame)
        logs_input_frame.pack(fill="x", pady=5)
        ttk.Label(logs_input_frame, text="Clan Name:").pack(side=tk.LEFT, padx=5)
        self.clan_logs_name_combobox = ttk.Combobox(logs_input_frame, values=search_history["clans"], width=40)
        self.clan_logs_name_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Label(logs_input_frame, text="Keyword:").pack(side=tk.LEFT, padx=5)
        self.keyword_combobox = ttk.Combobox(logs_input_frame, values=search_history["keywords"], width=40)
        self.keyword_combobox.pack(side=tk.LEFT, padx=5)
        self.keyword_combobox.bind("<KeyRelease>", lambda event: self.filter_logs())
        ttk.Button(logs_input_frame, text="Search Logs", command=self.search_clan_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(logs_input_frame, text="Clear", command=lambda: self.clan_logs_tree.delete(*self.clan_logs_tree.get_children())).pack(side=tk.LEFT, padx=5)
        logs_result_frame = ttk.Frame(self.clan_logs_frame)
        logs_result_frame.pack(fill="both", expand=1)
        self.clan_logs_tree = ttk.Treeview(logs_result_frame, columns=("Viewed", "Timestamp", "Message"), show="headings", height=20)
        self.clan_logs_tree.heading("Viewed", text="Viewed")
        self.clan_logs_tree.heading("Timestamp", text="Timestamp")
        self.clan_logs_tree.heading("Message", text="Message")
        self.clan_logs_tree.column("Viewed", width=50, anchor="center")
        self.clan_logs_tree.column("Timestamp", width=150)
        self.clan_logs_tree.column("Message", width=600)
        self.clan_logs_tree.pack(side=tk.LEFT, fill="both", expand=1)
        clan_logs_scroll = ttk.Scrollbar(logs_result_frame, orient="vertical", command=self.clan_logs_tree.yview)
        clan_logs_scroll.pack(side=tk.RIGHT, fill="y")
        self.clan_logs_tree.configure(yscrollcommand=clan_logs_scroll.set)
        self.viewed_logs = self.load_viewed_logs()
        self.clan_logs_tree.bind("<Button-1>", self.toggle_viewed)

        # Cup Standings Sub-Tab
        self.clan_standings_frame = ttk.Frame(self.clan_notebook)
        self.clan_notebook.add(self.clan_standings_frame, text="Cup Standings")
        stand_input_frame = ttk.Frame(self.clan_standings_frame)
        stand_input_frame.pack(fill="x", pady=5)
        ttk.Label(stand_input_frame, text="Clan Name:").pack(side=tk.LEFT, padx=5)
        self.clan_stand_name_combobox = ttk.Combobox(stand_input_frame, values=search_history["clans"], width=40)
        self.clan_standings_frame.clan_stand_name_combobox = self.clan_stand_name_combobox
        self.clan_stand_name_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Label(stand_input_frame, text="Game Mode:").pack(side=tk.LEFT, padx=5)
        self.game_mode_combo = ttk.Combobox(stand_input_frame, values=["Default", "Ironman"], width=20)
        self.clan_standings_frame.game_mode_combo = self.game_mode_combo
        self.game_mode_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(stand_input_frame, text="View Standings", command=self.view_standings).pack(side=tk.LEFT, padx=5)
        ttk.Button(stand_input_frame, text="Clear", command=lambda: self.clan_stand_result_tree.delete(*self.clan_stand_result_tree.get_children())).pack(side=tk.LEFT, padx=5)
        ttk.Button(stand_input_frame, text="Export", command=self.export_standings).pack(side=tk.LEFT, padx=5)
        stand_result_frame = ttk.Frame(self.clan_standings_frame)
        stand_result_frame.pack(fill="both", expand=1)
        self.clan_stand_result_tree = ttk.Treeview(stand_result_frame, columns=("Objective", "Details"), show="headings", height=20)
        self.clan_stand_result_tree.heading("Objective", text="Objective")
        self.clan_stand_result_tree.heading("Details", text="Details")
        self.clan_stand_result_tree.column("Objective", width=200, anchor="w")
        self.clan_stand_result_tree.column("Details", width=500, anchor="w")
        self.clan_stand_result_tree.pack(side=tk.LEFT, fill="both", expand=1)
        clan_stand_scroll = ttk.Scrollbar(stand_result_frame, orient="vertical", command=self.clan_stand_result_tree.yview)
        clan_stand_scroll.pack(side=tk.RIGHT, fill="y")
        self.clan_stand_result_tree.configure(yscrollcommand=clan_stand_scroll.set)

        self.api_key = api_key
        self.raw_mode = raw_mode
        self.last_api_call = last_api_call
        self.search_history = search_history
        self.status_label = status_label
        self.tabs = None
        self.all_logs = []

    def set_tabs(self, tabs):
        self.tabs = tabs

    def update_comboboxes(self, name, category):
        if name and name not in self.search_history[category]:
            self.search_history[category].insert(0, name)
            if len(self.search_history[category]) > 50:
                self.search_history[category].pop()
            for tab in self.tabs:
                if category == "players" and hasattr(tab, "player_name_combobox"):
                    tab.player_name_combobox["values"] = self.search_history["players"]
                if category == "clans":
                    if hasattr(tab, "clan_rec_name_combobox"):
                        tab.clan_rec_name_combobox["values"] = self.search_history["clans"]
                    if hasattr(tab, "clan_logs_name_combobox"):
                        tab.clan_logs_name_combobox["values"] = self.search_history["clans"]
                    if hasattr(tab, "clan_stand_name_combobox"):
                        tab.clan_stand_name_combobox["values"] = self.search_history["clans"]
                if category == "keywords" and hasattr(tab, "keyword_combobox"):
                    tab.keyword_combobox["values"] = self.search_history["keywords"]

    def search_recruitment(self):
        name = self.clan_rec_name_combobox.get().strip()
        if not name:
            self.clan_rec_result_tree.delete(*self.clan_rec_result_tree.get_children())
            self.clan_rec_result_tree.insert("", "end", values=("Error", "Please enter a clan name."))
            return
        self.status_label.config(text="Fetching recruitment data...")
        self.update_comboboxes(name, "clans")
        try:
            data = make_request(f"{BASE_URL}/api/Clan/recruitment/{name}", api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.clan_rec_result_tree.delete(*self.clan_rec_result_tree.get_children())
            if self.raw_mode.get():
                self.clan_rec_result_tree.insert("", "end", values=("Raw Data", json.dumps(data, indent=2)))
            else:
                self.clan_rec_result_tree.insert("", "end", values=("Clan", data.get('clanName', 'N/A')))
                self.clan_rec_result_tree.insert("", "end", values=("Activity Score", str(data.get('activityScore', 'N/A'))))
                self.clan_rec_result_tree.insert("", "end", values=("Minimum Total Level", str(data.get('minimumTotalLevelRequired', 'N/A'))))
                self.clan_rec_result_tree.insert("", "end", values=("Member Count", str(data.get('memberCount', 'N/A'))))
                self.clan_rec_result_tree.insert("", "end", values=("Recruiting", str(data.get('isRecruiting', False))))
                self.clan_rec_result_tree.insert("", "end", values=("Language", data.get('language', 'N/A')))
                self.clan_rec_result_tree.insert("", "end", values=("Category", data.get('category', 'N/A')))
                self.clan_rec_result_tree.insert("", "end", values=("Recruitment Message", data.get('recruitmentMessage', 'N/A')))
                self.clan_rec_result_tree.insert("", "end", values=("House ID", str(data.get('houseId', 'N/A'))))
                self.clan_rec_result_tree.insert("", "end", values=("", ""))  # Separator
                self.clan_rec_result_tree.insert("", "end", values=("Members", ""))
                for member in data.get('memberlist', []):
                    self.clan_rec_result_tree.insert("", "end", values=("Member", f"{member['memberName']} (Rank: {member['rank']})"))
                self.clan_rec_result_tree.insert("", "end", values=("", ""))  # Separator
                self.clan_rec_result_tree.insert("", "end", values=("Serialized Skills", ""))
                skills = json.loads(data.get('serializedSkills', '{}'))
                for skill, exp in skills.items():
                    self.clan_rec_result_tree.insert("", "end", values=(skill, f"{exp:,.2f} XP"))
                self.clan_rec_result_tree.insert("", "end", values=("", ""))  # Separator
                self.clan_rec_result_tree.insert("", "end", values=("Serialized Upgrades", ""))
                upgrades = data.get('serializedUpgrades', '[]')
                self.clan_rec_result_tree.insert("", "end", values=("Upgrades", str(upgrades)))
            self.status_label.config(text="Recruitment data loaded")
        except Exception as e:
            self.clan_rec_result_tree.delete(*self.clan_rec_result_tree.get_children())
            self.clan_rec_result_tree.insert("", "end", values=("Error", str(e)))
            self.status_label.config(text="Error fetching recruitment data")

    def search_clan_logs(self):
        name = self.clan_logs_name_combobox.get().strip()
        keyword = self.keyword_combobox.get().strip()
        if not name:
            self.clan_logs_tree.delete(*self.clan_logs_tree.get_children())
            return
        self.status_label.config(text="Fetching clan logs...")
        self.update_comboboxes(name, "clans")
        if keyword:
            self.update_comboboxes(keyword, "keywords")
        try:
            self.all_logs = make_request(f"{BASE_URL}/api/Clan/logs/clan/{name}", params={"limit": 100}, api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.filter_logs()
            self.status_label.config(text="Logs loaded successfully")
        except Exception as e:
            self.clan_logs_tree.delete(*self.clan_logs_tree.get_children())
            self.clan_logs_tree.insert("", "end", values=("", "Error", str(e)))
            self.status_label.config(text="Error fetching logs")

    def filter_logs(self):
        keyword = self.keyword_combobox.get().lower()
        filtered_logs = [log for log in self.all_logs if not keyword or keyword in log.get('message', '').lower()]
        self.clan_logs_tree.delete(*self.clan_logs_tree.get_children())
        if self.raw_mode.get():
            self.clan_logs_tree.insert("", "end", values=("", "Raw Data", json.dumps(filtered_logs, indent=2)))
        else:
            for log in filtered_logs:
                log_id = f"{log['timestamp']}-{log['message']}"
                viewed = log_id in self.viewed_logs
                checkbox = "☑" if viewed else "◻"
                self.clan_logs_tree.insert("", "end", iid=log_id, values=(checkbox, log['timestamp'], log['message']), tags=("viewed" if viewed else "unviewed"))
            self.clan_logs_tree.tag_configure("viewed", font=("Arial", 10, "overstrike"))

    def toggle_viewed(self, event):
        item = self.clan_logs_tree.identify_row(event.y)
        if not item:
            return
        column = self.clan_logs_tree.identify_column(event.x)
        if column == "#1":
            current_values = self.clan_logs_tree.item(item, "values")
            log_id = item
            if current_values[0] == "☑":
                self.clan_logs_tree.item(item, values=("◻", current_values[1], current_values[2]), tags="unviewed")
                if log_id in self.viewed_logs:
                    del self.viewed_logs[log_id]
            else:
                self.clan_logs_tree.item(item, values=("☑", current_values[1], current_values[2]), tags="viewed")
                self.viewed_logs[log_id] = True
            self.save_viewed_logs()

    def load_viewed_logs(self):
        try:
            if os.path.exists("viewed_logs.json"):
                with open("viewed_logs.json", "r") as f:
                    return json.load(f)
        except Exception:
            return {}
        return {}

    def save_viewed_logs(self):
        try:
            with open("viewed_logs.json", "w") as f:
                json.dump(self.viewed_logs, f)
        except Exception as e:
            self.status_label.config(text=f"Error saving viewed logs: {e}")

    def view_standings(self):
        name = self.clan_stand_name_combobox.get().strip()
        mode = self.game_mode_combo.get()
        if not name:
            self.clan_stand_result_tree.delete(*self.clan_stand_result_tree.get_children())
            self.clan_stand_result_tree.insert("", "end", values=("Error", "Please enter a clan name."))
            return
        self.status_label.config(text="Fetching standings...")
        self.update_comboboxes(name, "clans")
        try:
            standings = make_request(f"{BASE_URL}/api/ClanCup/standings/{name}", params={"gameMode": mode}, api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.clan_stand_result_tree.delete(*self.clan_stand_result_tree.get_children())
            if self.raw_mode.get():
                self.clan_stand_result_tree.insert("", "end", values=("Raw Data", json.dumps(standings, indent=2)))
            else:
                self.clan_stand_result_tree.insert("", "end", values=("Clan", f"{name} ({mode})"))
                for standing in standings:
                    if 'bestTime' in standing:
                        time = standing['bestTime'].get('time', 'N/A')
                        achieved_at = standing['bestTime'].get('achievedAt', 'N/A')
                        self.clan_stand_result_tree.insert("", "end", values=(standing['objective'], f"Best Time {time} (Achieved at {achieved_at}), Rank: {standing['rank']}"))
                    else:
                        self.clan_stand_result_tree.insert("", "end", values=(standing['objective'], f"Score {standing['score']}, Rank: {standing['rank']}"))
            self.status_label.config(text="Standings loaded successfully")
        except Exception as e:
            self.clan_stand_result_tree.delete(*self.clan_stand_result_tree.get_children())
            self.clan_stand_result_tree.insert("", "end", values=("Error", str(e)))
            self.status_label.config(text="Error fetching standings")

    def export_recruitment(self):
        try:
            with open("clan_recruitment.txt", "w") as f:
                for item in self.clan_rec_result_tree.get_children():
                    values = self.clan_rec_result_tree.item(item, "values")
                    f.write(f"{values[0]}: {values[1]}\n")
            self.status_label.config(text="Recruitment exported to clan_recruitment.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

    def export_standings(self):
        try:
            with open("clan_standings.txt", "w") as f:
                for item in self.clan_stand_result_tree.get_children():
                    values = self.clan_stand_result_tree.item(item, "values")
                    f.write(f"{values[0]}: {values[1]}\n")
            self.status_label.config(text="Standings exported to clan_standings.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

def create_clan_tab(notebook, api_key, raw_mode, last_api_call, search_history, status_label):
    tab = ClanTab(notebook, api_key, raw_mode, last_api_call, search_history, status_label)
    return tab