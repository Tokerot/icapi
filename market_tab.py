import tkinter as tk
from tkinter import ttk
import json
from utils import make_request, BASE_URL

class MarketTab:
    def __init__(self, notebook, api_key, raw_mode, last_api_call, item_list, status_label):
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Market")
        self.market_frame = ttk.Frame(self.tab, padding=10)
        self.market_frame.pack(fill="both", expand=1)
        
        input_frame = ttk.Frame(self.market_frame)
        input_frame.pack(fill="x", pady=5)
        ttk.Button(input_frame, text="View Market Trends", command=self.view_market_trends).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Clear", command=lambda: self.market_result_tree.delete(*self.market_result_tree.get_children())).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Export", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.Frame(self.market_frame)
        result_frame.pack(fill="both", expand=1)
        self.market_result_tree = ttk.Treeview(result_frame, columns=("Type", "Item", "Value"), show="headings", height=25)
        self.market_result_tree.heading("Type", text="Type")
        self.market_result_tree.heading("Item", text="Item")
        self.market_result_tree.heading("Value", text="Value")
        self.market_result_tree.column("Type", width=150, anchor="w")
        self.market_result_tree.column("Item", width=300, anchor="w")
        self.market_result_tree.column("Value", width=200, anchor="w")
        self.market_result_tree.pack(side=tk.LEFT, fill="both", expand=1)
        market_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.market_result_tree.yview)
        market_scroll.pack(side=tk.RIGHT, fill="y")
        self.market_result_tree.configure(yscrollcommand=market_scroll.set)
        
        self.api_key = api_key
        self.raw_mode = raw_mode
        self.last_api_call = last_api_call
        self.item_list = item_list
        self.status_label = status_label

    def view_market_trends(self):
        self.status_label.config(text="Fetching market trends...")
        try:
            value_history = make_request(f"{BASE_URL}/api/PlayerMarket/items/prices/history/value", params={"limit": 5}, api_key=self.api_key.get(), last_api_call=self.last_api_call)
            volume_history = make_request(f"{BASE_URL}/api/PlayerMarket/items/volume/history", params={"limit": 5}, api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.market_result_tree.delete(*self.market_result_tree.get_children())
            if self.raw_mode.get():
                self.market_result_tree.insert("", "end", values=("Raw Data", "", json.dumps({"value_history": value_history, "volume_history": volume_history}, indent=2)))
            else:
                self.market_result_tree.insert("", "end", values=("Type", "Item", "Value"))  # Header
                for entry in value_history:
                    # Convert itemId to string for lookup
                    item_id_str = str(entry['itemId'])
                    item_name = self.item_list.get(item_id_str, f"Unknown Item (ID: {item_id_str})")
                    # Temporary workaround: Capitalize and replace underscores for readability
                    if item_name != f"Unknown Item (ID: {item_id_str})":
                        item_name = item_name.replace("_", " ").title()
                    self.market_result_tree.insert("", "end", values=("Value", item_name, f"{entry['tradePrice']:,}"))
                for entry in volume_history:
                    # Convert itemId to string for lookup
                    item_id_str = str(entry['itemId'])
                    item_name = self.item_list.get(item_id_str, f"Unknown Item (ID: {item_id_str})")
                    # Temporary workaround: Capitalize and replace underscores for readability
                    if item_name != f"Unknown Item (ID: {item_id_str})":
                        item_name = item_name.replace("_", " ").title()
                    self.market_result_tree.insert("", "end", values=("Volume", item_name, f"{entry['volume']:,}"))
            self.status_label.config(text="Trends loaded successfully")
        except Exception as e:
            self.market_result_tree.delete(*self.market_result_tree.get_children())
            self.market_result_tree.insert("", "end", values=("Error", "", str(e)))
            self.status_label.config(text="Error fetching trends")

    def export_results(self):
        try:
            with open("market_results.txt", "w") as f:
                for item in self.market_result_tree.get_children():
                    values = self.market_result_tree.item(item, "values")
                    f.write(f"{values[0]}: {values[1]} - {values[2]}\n")
            self.status_label.config(text="Results exported to market_results.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

def create_market_tab(notebook, api_key, raw_mode, last_api_call, item_list, status_label):
    tab = MarketTab(notebook, api_key, raw_mode, last_api_call, item_list, status_label)
    return tab