import tkinter as tk
from tkinter import ttk
import json
from utils import make_request, BASE_URL

class LeaderboardsTab:
    def __init__(self, notebook, api_key, raw_mode, last_api_call, status_label):
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Leaderboards")
        self.lb_frame = ttk.Frame(self.tab, padding=10)
        self.lb_frame.pack(fill="both", expand=1)
        
        # Input Frame
        input_frame = ttk.Frame(self.lb_frame)
        input_frame.pack(fill="x", pady=5)
        
        # Mode selection
        ttk.Label(input_frame, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value="clan_top")
        ttk.Radiobutton(input_frame, text="Clan Top", variable=self.mode_var, value="clan_top", command=self.update_ui).pack(side=tk.LEFT)
        ttk.Radiobutton(input_frame, text="Clan Details", variable=self.mode_var, value="clan_detail", command=self.update_ui).pack(side=tk.LEFT)
        ttk.Radiobutton(input_frame, text="Player", variable=self.mode_var, value="player", command=self.update_ui).pack(side=tk.LEFT)
        
        # Common inputs
        self.game_mode_label = ttk.Label(input_frame, text="Game Mode:")
        self.game_mode_combobox = ttk.Combobox(input_frame, values=["Default", "Ironman"], width=15)
        self.game_mode_combobox.set("Default")
        
        # Clan Top inputs
        self.category_label = ttk.Label(input_frame, text="Category:")
        category_options = ["totalPoints", "Woodcutting", "Fishing", "Cooking", "Carpentry", "Foraging",
                          "DevilKills", "GriffinKills", "HadesKills", "OtherworldlyGolemKills"]
        self.category_combobox = ttk.Combobox(input_frame, values=category_options, width=20)
        self.category_combobox.set("totalPoints")
        
        # Clan Detail/Player input
        self.name_label = ttk.Label(input_frame, text="Name:")
        self.name_entry = ttk.Entry(input_frame, width=20)
        
        # Limit
        self.limit_label = ttk.Label(input_frame, text="Limit:")
        self.limit_combobox = ttk.Combobox(input_frame, values=[10, 25, 50, 100], width=5)
        self.limit_combobox.set(10)
        
        # Buttons
        self.view_button = ttk.Button(input_frame, text="View", command=self.view_leaderboard)
        ttk.Button(input_frame, text="Clear", command=lambda: self.lb_result_tree.delete(*self.lb_result_tree.get_children())).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Export", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Result Frame
        result_frame = ttk.Frame(self.lb_frame)
        result_frame.pack(fill="both", expand=1)
        self.lb_result_tree = ttk.Treeview(result_frame, columns=("Rank", "Name", "Value"), show="headings", height=25)
        self.lb_result_tree.pack(side=tk.LEFT, fill="both", expand=1)
        lb_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.lb_result_tree.yview)
        lb_scroll.pack(side=tk.RIGHT, fill="y")
        self.lb_result_tree.configure(yscrollcommand=lb_scroll.set)
        
        self.api_key = api_key
        self.raw_mode = raw_mode
        self.last_api_call = last_api_call
        self.status_label = status_label
        
        self.update_ui()  # Initial UI setup

    def update_ui(self):
        mode = self.mode_var.get()
        
        # Clear current widgets
        for widget in [self.game_mode_label, self.game_mode_combobox, self.category_label, 
                      self.category_combobox, self.name_label, self.name_entry, 
                      self.limit_label, self.limit_combobox, self.view_button]:
            widget.pack_forget()
            
        # Update Treeview columns
        if mode == "clan_top":
            self.lb_result_tree["columns"] = ("Rank", "Clan", "Points")
            self.lb_result_tree.heading("Rank", text="Rank")
            self.lb_result_tree.heading("Clan", text="Clan Name")
            self.lb_result_tree.heading("Points", text="Points")
            self.lb_result_tree.column("Rank", width=50, anchor="center")
            self.lb_result_tree.column("Clan", width=200, anchor="w")
            self.lb_result_tree.column("Points", width=300, anchor="w")
            
            self.game_mode_label.pack(side=tk.LEFT, padx=5)
            self.game_mode_combobox.pack(side=tk.LEFT, padx=5)
            self.category_label.pack(side=tk.LEFT, padx=5)
            self.category_combobox.pack(side=tk.LEFT, padx=5)
            self.limit_label.pack(side=tk.LEFT, padx=5)
            self.limit_combobox.pack(side=tk.LEFT, padx=5)
            self.view_button.pack(side=tk.LEFT, padx=5)
            
        elif mode == "clan_detail":
            self.lb_result_tree["columns"] = ("Category", "Points")
            self.lb_result_tree.heading("Category", text="Category")
            self.lb_result_tree.heading("Points", text="Points")
            self.lb_result_tree.column("Category", width=200, anchor="w")
            self.lb_result_tree.column("Points", width=350, anchor="w")
            
            self.game_mode_label.pack(side=tk.LEFT, padx=5)
            self.game_mode_combobox.pack(side=tk.LEFT, padx=5)
            self.name_label.pack(side=tk.LEFT, padx=5)
            self.name_entry.pack(side=tk.LEFT, padx=5)
            self.view_button.pack(side=tk.LEFT, padx=5)
            
        elif mode == "player":
            self.lb_result_tree["columns"] = ("Stat", "Score", "Rank")
            self.lb_result_tree.heading("Stat", text="Stat")
            self.lb_result_tree.heading("Score", text="Score")
            self.lb_result_tree.heading("Rank", text="Rank")
            self.lb_result_tree.column("Stat", width=200, anchor="w")
            self.lb_result_tree.column("Score", width=200, anchor="w")
            self.lb_result_tree.column("Rank", width=100, anchor="center")
            
            self.name_label.pack(side=tk.LEFT, padx=5)
            self.name_entry.pack(side=tk.LEFT, padx=5)
            self.view_button.pack(side=tk.LEFT, padx=5)

    def view_leaderboard(self):
        mode = self.mode_var.get()
        game_mode = self.game_mode_combobox.get().strip()
        self.lb_result_tree.delete(*self.lb_result_tree.get_children())
        
        self.status_label.config(text="Fetching data...")
        try:
            if mode == "clan_top":
                category = self.category_combobox.get().strip()
                limit = int(self.limit_combobox.get())
                if not game_mode or not category:
                    raise ValueError("Please select game mode and category")
                endpoint = f"{BASE_URL}/api/ClanCup/leaderboard/{game_mode}/{category}"
                data = make_request(endpoint, params={"limit": limit}, api_key=self.api_key.get(), last_api_call=self.last_api_call)
                
                if self.raw_mode.get():
                    self.lb_result_tree.insert("", "end", values=("Raw Data", "", json.dumps(data, indent=2)))
                else:
                    for rank, entry in enumerate(data, 1):
                        clan_name = entry.get('clanName', 'N/A')
                        points = entry.get('points', 'N/A')
                        self.lb_result_tree.insert("", "end", values=(rank, clan_name, f"{points:,}"))
                        
            elif mode == "clan_detail":
                clan_name = self.name_entry.get().strip()
                if not game_mode or not clan_name:
                    raise ValueError("Please enter game mode and clan name")
                endpoint = f"{BASE_URL}/api/ClanCup/leaderboard/{game_mode}/clans/{clan_name}"
                data = make_request(endpoint, api_key=self.api_key.get(), last_api_call=self.last_api_call)
                
                if self.raw_mode.get():
                    self.lb_result_tree.insert("", "end", values=("Raw Data", json.dumps(data, indent=2)))
                else:
                    self.lb_result_tree.insert("", "end", values=("Total Points", f"{data.get('totalPoints', 'N/A'):,}"))
                    for category, points in data.get('categoryPoints', {}).items():
                        self.lb_result_tree.insert("", "end", values=(category, f"{points:,}"))
                        
            elif mode == "player":
                player_name = self.name_entry.get().strip()
                if not player_name:
                    raise ValueError("Please enter player name")
                endpoint = f"{BASE_URL}/api/Leaderboard/profile/players:default/{player_name}"
                data = make_request(endpoint, api_key=self.api_key.get(), last_api_call=self.last_api_call)
                
                if self.raw_mode.get():
                    self.lb_result_tree.insert("", "end", values=("Raw Data", "", json.dumps(data, indent=2)))
                else:
                    total = data.get('totalLevelResult', {})
                    self.lb_result_tree.insert("", "end", values=("Total Level", f"{total.get('score', 'N/A'):,}", total.get('rank', 'N/A')))
                    for stat, values in data.get('fields', {}).items():
                        self.lb_result_tree.insert("", "end", values=(stat, f"{values.get('score', 'N/A'):,}", values.get('rank', 'N/A')))
            
            self.status_label.config(text="Data loaded successfully")
        except Exception as e:
            self.lb_result_tree.insert("", "end", values=("Error", str(e), ""))
            self.status_label.config(text="Error fetching data")

    def export_results(self):
        try:
            with open("leaderboard_results.txt", "w") as f:
                for item in self.lb_result_tree.get_children():
                    values = self.lb_result_tree.item(item, "values")
                    f.write(f"{' - '.join(str(v) for v in values)}\n")
            self.status_label.config(text="Results exported to leaderboard_results.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

def create_leaderboards_tab(notebook, api_key, raw_mode, last_api_call, status_label):
    tab = LeaderboardsTab(notebook, api_key, raw_mode, last_api_call, status_label)
    return tab