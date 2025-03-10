import tkinter as tk
from tkinter import ttk
import json
from utils import make_request, BASE_URL
import logging

# Setup logging for debugging
logging.basicConfig(filename="player_tab_debug.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")

class PlayerTab:
    def __init__(self, notebook, api_key, raw_mode, last_api_call, search_history, status_label, item_list):
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Player")
        self.player_frame = ttk.Frame(self.tab, padding=10)
        self.player_frame.pack(fill="both", expand=1)
        
        input_frame = ttk.Frame(self.player_frame)
        input_frame.pack(fill="x", pady=5)
        ttk.Label(input_frame, text="Player Name:").pack(side=tk.LEFT, padx=5)
        self.player_name_combobox = ttk.Combobox(input_frame, values=search_history["players"], width=40)
        self.player_name_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Search Profile", command=self.search_player).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="View Logs", command=self.view_player_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Clear", command=lambda: self.player_result_tree.delete(*self.player_result_tree.get_children())).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Export", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.Frame(self.player_frame)
        result_frame.pack(fill="both", expand=1)
        self.player_result_tree = ttk.Treeview(result_frame, columns=("Category", "Detail"), show="headings", height=25)
        self.player_result_tree.heading("Category", text="Category")
        self.player_result_tree.heading("Detail", text="Detail")
        self.player_result_tree.column("Category", width=200, anchor="w")
        self.player_result_tree.column("Detail", width=500, anchor="w")
        self.player_result_tree.pack(side=tk.LEFT, fill="both", expand=1)
        player_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.player_result_tree.yview)
        player_scroll.pack(side=tk.RIGHT, fill="y")
        self.player_result_tree.configure(yscrollcommand=player_scroll.set)
        
        self.api_key = api_key
        self.raw_mode = raw_mode
        self.last_api_call = last_api_call
        self.search_history = search_history
        self.status_label = status_label
        self.tabs = None
        self.item_list = item_list  # Store item_list for equipment name lookup

        # Debug: Log the initial item_list contents
        logging.debug(f"Initial item_list keys: {list(self.item_list.keys())}")

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

    def search_player(self):
        name = self.player_name_combobox.get().strip()
        if not name:
            self.player_result_tree.delete(*self.player_result_tree.get_children())
            self.player_result_tree.insert("", "end", values=("Error", "Please enter a player name."))
            return
        self.status_label.config(text="Fetching player profile...")
        self.update_comboboxes(name, "players")
        try:
            profile = make_request(f"{BASE_URL}/api/Player/profile/{name}", api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.player_result_tree.delete(*self.player_result_tree.get_children())
            if self.raw_mode.get():
                self.player_result_tree.insert("", "end", values=("Raw Data", json.dumps(profile, indent=2)))
            else:
                self.player_result_tree.insert("", "end", values=("Username", profile.get('username', 'N/A')))
                self.player_result_tree.insert("", "end", values=("Game Mode", profile.get('gameMode', 'N/A')))
                self.player_result_tree.insert("", "end", values=("Guild", profile.get('guildName', 'None')))
                self.player_result_tree.insert("", "end", values=("", ""))  # Separator
                self.player_result_tree.insert("", "end", values=("Skills", ""))
                for skill, exp in profile.get('skillExperiences', {}).items():
                    self.player_result_tree.insert("", "end", values=(skill.capitalize(), f"{exp:,.2f} XP"))
                self.player_result_tree.insert("", "end", values=("", ""))  # Separator
                self.player_result_tree.insert("", "end", values=("Equipment", ""))
                for slot, item_id in profile.get('equipment', {}).items():
                    # Convert item_id to string for lookup and handle potential None or invalid values
                    item_id_str = str(item_id) if item_id is not None else "None"
                    # Check if item_id is -1 and display as "N/A"
                    if item_id == -1:
                        item_name = "N/A"
                    else:
                        item_name = self.item_list.get(item_id_str, f"Unknown Item (ID: {item_id_str})")
                        # Temporary workaround: Capitalize and replace underscores for readability
                        if item_name != f"Unknown Item (ID: {item_id_str})":
                            item_name = item_name.replace("_", " ").title()
                    logging.debug(f"Looking up item_id: {item_id_str}, found: {item_name}")
                    self.player_result_tree.insert("", "end", values=(slot.capitalize(), item_name))
                self.player_result_tree.insert("", "end", values=("", ""))  # Separator
                self.player_result_tree.insert("", "end", values=("Enchantment Boosts", ""))
                for skill, boost in profile.get('enchantmentBoosts', {}).items():
                    self.player_result_tree.insert("", "end", values=(skill.capitalize(), f"{boost}% boost"))
                self.player_result_tree.insert("", "end", values=("", ""))  # Separator
                self.player_result_tree.insert("", "end", values=("Upgrades", ""))
                for upgrade, level in profile.get('upgrades', {}).items():
                    self.player_result_tree.insert("", "end", values=(upgrade, f"Level {level}"))
                self.player_result_tree.insert("", "end", values=("", ""))  # Separator
                self.player_result_tree.insert("", "end", values=("PvM Stats (Kills)", ""))
                for monster, kills in profile.get('pvmStats', {}).items():
                    self.player_result_tree.insert("", "end", values=(monster, str(kills)))
            self.status_label.config(text="Profile loaded successfully")
        except Exception as e:
            self.player_result_tree.delete(*self.player_result_tree.get_children())
            self.player_result_tree.insert("", "end", values=("Error", str(e)))
            self.status_label.config(text="Error fetching profile")
            logging.error(f"Error in search_player: {e}")

    def view_player_logs(self):
        name = self.player_name_combobox.get().strip()
        if not name:
            self.player_result_tree.delete(*self.player_result_tree.get_children())
            self.player_result_tree.insert("", "end", values=("Error", "Please enter a player name."))
            return
        self.status_label.config(text="Fetching player logs...")
        self.update_comboboxes(name, "players")
        try:
            logs = make_request(f"{BASE_URL}/api/Player/clan-logs/{name}", params={"limit": 50}, api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.player_result_tree.delete(*self.player_result_tree.get_children())
            if self.raw_mode.get():
                self.player_result_tree.insert("", "end", values=("Raw Data", json.dumps(logs, indent=2)))
            else:
                for log in logs:
                    self.player_result_tree.insert("", "end", values=("Log", f"{log['timestamp']}: [{log['clanName']}] {log['message']}"))
            self.status_label.config(text="Logs loaded successfully")
        except Exception as e:
            self.player_result_tree.delete(*self.player_result_tree.get_children())
            self.player_result_tree.insert("", "end", values=("Error", str(e)))
            self.status_label.config(text="Error fetching logs")

    def export_results(self):
        try:
            with open("player_results.txt", "w") as f:
                for item in self.player_result_tree.get_children():
                    values = self.player_result_tree.item(item, "values")
                    f.write(f"{values[0]}: {values[1]}\n")
            self.status_label.config(text="Results exported to player_results.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

def create_player_tab(notebook, api_key, raw_mode, last_api_call, search_history, status_label, item_list):
    tab = PlayerTab(notebook, api_key, raw_mode, last_api_call, search_history, status_label, item_list)
    return tab