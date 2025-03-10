import tkinter as tk
from tkinter import ttk
import json
from utils import make_request, BASE_URL
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import logging

# Setup logging for debugging
logging.basicConfig(filename="item_tab_debug.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")

class ItemTab:
    def __init__(self, notebook, api_key, raw_mode, last_api_call, item_data, item_list, status_label):
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Item")
        self.item_frame = ttk.Frame(self.tab, padding=10)
        self.item_frame.pack(fill="both", expand=1)
        
        # Input frame for Entry and buttons
        self.input_frame = ttk.Frame(self.item_frame)
        self.input_frame.pack(fill="x", pady=5)
        ttk.Label(self.input_frame, text="Item Name:").pack(side=tk.LEFT, padx=5)
        
        # Entry setup
        # Format the item_list values for display (same as PlayerTab and MarketTab)
        self.item_list = {item_id: name_id.replace("_", " ").title() for item_id, name_id in item_list.items()}
        self.full_item_list = list(self.item_list.values())  # Store formatted list for filtering
        self.item_entry = ttk.Entry(self.input_frame, width=40)
        self.item_entry.pack(side=tk.LEFT, padx=5)
        self.item_entry.bind("<KeyRelease>", self.update_listbox_values)
        
        # Separate frame for Listbox to control its position
        self.dropdown_frame = ttk.Frame(self.item_frame)
        self.item_listbox = tk.Listbox(self.dropdown_frame, height=10, width=40)
        self.item_listbox.bind("<<ListboxSelect>>", self.on_listbox_select)
        self.item_listbox.pack()
        self.dropdown_frame.pack_forget()  # Hidden initially
        
        self.last_after_id = None  # For debouncing
        ttk.Button(self.input_frame, text="Latest Price", command=self.search_item_latest).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.input_frame, text="Price History", command=self.search_item_history).pack(side=tk.LEFT, padx=5)
        self.toggle_graph_button = ttk.Button(self.input_frame, text="Toggle Graph", command=self.toggle_graph)
        self.toggle_graph_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.input_frame, text="Clear", command=lambda: self.item_result_tree.delete(*self.item_result_tree.get_children())).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.input_frame, text="Export", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        self.result_frame = ttk.Frame(self.item_frame)
        self.result_frame.pack(fill="both", expand=1, pady=(0, 10))
        self.item_result_tree = ttk.Treeview(self.result_frame, columns=("Field", "Value"), show="headings", height=10)
        self.item_result_tree.heading("Field", text="Field")
        self.item_result_tree.heading("Value", text="Value")
        self.item_result_tree.column("Field", width=200, anchor="w")
        self.item_result_tree.column("Value", width=500, anchor="w")
        self.item_result_tree.pack(side=tk.LEFT, fill="both", expand=1)
        item_scroll = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.item_result_tree.yview)
        item_scroll.pack(side=tk.RIGHT, fill="y")
        self.item_result_tree.configure(yscrollcommand=item_scroll.set)
        
        self.api_key = api_key
        self.raw_mode = raw_mode
        self.last_api_call = last_api_call
        self.status_label = status_label
        self.graph_visible = False
        self.canvas = None

        # Debug: Log the formatted item_list
        logging.debug(f"Formatted item_list: {self.item_list}")

    def update_listbox_values(self, event):
        """Dynamically filter listbox values based on typed input"""
        if event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Up', 'Down', 'Left', 'Right', 'Return'):
            return
        
        if self.last_after_id is not None:
            self.item_frame.after_cancel(self.last_after_id)
        
        self.last_after_id = self.item_frame.after(100, self._filter_listbox)

    def _filter_listbox(self):
        """Perform the actual filtering and listbox update"""
        typed = self.item_entry.get().strip().lower()
        self.item_listbox.delete(0, tk.END)
        
        if typed:
            filtered_items = [item for item in self.full_item_list if typed in item.lower()]
        else:
            filtered_items = self.full_item_list
        
        for item in filtered_items:
            self.item_listbox.insert(tk.END, item)
        
        if filtered_items:
            self.dropdown_frame.place(x=self.item_entry.winfo_x(), y=self.input_frame.winfo_y() + self.input_frame.winfo_height())
            self.dropdown_frame.lift()
        else:
            self.dropdown_frame.place_forget()

    def on_listbox_select(self, event):
        """Handle selection from the listbox"""
        if self.item_listbox.curselection():
            selected = self.item_listbox.get(self.item_listbox.curselection()[0])
            self.item_entry.delete(0, tk.END)
            self.item_entry.insert(0, selected)
            self.dropdown_frame.place_forget()

    def get_item_id_from_name(self, item_name):
        """Convert item name to item ID"""
        item_name = item_name.strip()  # Remove leading/trailing spaces
        logging.debug(f"Searching for item_name: '{item_name}'")
        for item_id, name in self.item_list.items():
            if name == item_name:
                logging.debug(f"Found match: item_id={item_id}, name={name}")
                return item_id
        logging.debug(f"No match found for item_name: '{item_name}'")
        return None

    def search_item_latest(self):
        item_name = self.item_entry.get().strip()
        item_id = self.get_item_id_from_name(item_name)
        if not item_id:
            self.item_result_tree.delete(*self.item_result_tree.get_children())
            self.item_result_tree.insert("", "end", values=("Error", "Invalid item name or no matching item found."))
            return
        self.status_label.config(text="Fetching latest price and history...")
        try:
            latest_data = make_request(f"{BASE_URL}/api/PlayerMarket/items/prices/latest/{item_id}", api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.item_result_tree.delete(*self.item_result_tree.get_children())
            if self.raw_mode.get():
                self.item_result_tree.insert("", "end", values=("Raw Data", json.dumps(latest_data, indent=2)))
            else:
                self.item_result_tree.insert("", "end", values=("Item Name", f"{item_name} (ID: {item_id})"))
                low_sell = float(latest_data.get('lowestSellPrice', latest_data.get('lowesSellPrice', 'N/A'))) if latest_data.get('lowestSellPrice', latest_data.get('lowesSellPrice', 'N/A')) != 'N/A' else 'N/A'
                low_vol = float(latest_data.get('lowestPriceVolume', 'N/A')) if latest_data.get('lowestPriceVolume', 'N/A') != 'N/A' else 'N/A'
                high_buy = float(latest_data.get('highestBuyPrice', 'N/A')) if latest_data.get('highestBuyPrice', 'N/A') != 'N/A' else 'N/A'
                high_vol = float(latest_data.get('highestPriceVolume', 'N/A')) if latest_data.get('highestPriceVolume', 'N/A') != 'N/A' else 'N/A'
                self.item_result_tree.insert("", "end", values=("Lowest Sell Price", f"{low_sell:,.0f}" if low_sell != 'N/A' else "N/A"))
                self.item_result_tree.insert("", "end", values=("Lowest Price Volume", f"{low_vol:,.0f}" if low_vol != 'N/A' else "N/A"))
                self.item_result_tree.insert("", "end", values=("Highest Buy Price", f"{high_buy:,.0f}" if high_buy != 'N/A' else "N/A"))
                self.item_result_tree.insert("", "end", values=("Highest Price Volume", f"{high_vol:,.0f}" if high_vol != 'N/A' else "N/A"))

            history_data = make_request(f"{BASE_URL}/api/PlayerMarket/items/prices/history/{item_id}", api_key=self.api_key.get(), last_api_call=self.last_api_call)
            if self.graph_visible and self.canvas:
                self.canvas.get_tk_widget().pack_forget()
            timestamps = [datetime.strptime(entry['timestamp'], "%Y-%m-%dT%H:%M:%SZ") for entry in history_data]
            low_sell_prices = [float(entry.get('lowestSellPrice', entry.get('lowesSellPrice', 0))) if entry.get('lowestSellPrice', entry.get('lowesSellPrice', 'N/A')) != 'N/A' else 0 for entry in history_data]
            high_sell_prices = [float(entry.get('highestSellPrice', 0)) if entry.get('highestSellPrice', 'N/A') != 'N/A' else 0 for entry in history_data]
            avg_prices = [float(entry.get('averagePrice', 0)) if entry.get('averagePrice', 'N/A') != 'N/A' else 0 for entry in history_data]
            volumes = [float(entry.get('tradeVolume', 0)) / 3 if entry.get('tradeVolume', 'N/A') != 'N/A' else 0 for entry in history_data]

            all_prices = low_sell_prices + high_sell_prices + avg_prices
            min_price = min(all_prices)
            max_price = max(all_prices)
            price_range = max_price - min_price
            padding = price_range * 0.1 if price_range > 0 else 5
            y_min = max(0, min_price - padding)
            y_max = max_price + padding

            fig, ax1 = plt.subplots(figsize=(10, 4))
            ax2 = ax1.twinx()
            ax2.bar(timestamps, volumes, color='red', alpha=0.5, width=0.01, label='Trade Volume')
            ax2.set_ylabel('Volume (Scaled)', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.set_ylim(0, max(volumes) * 1.2)
            ax1.plot(timestamps, low_sell_prices, 'b-', label='Lowest Sell Price', zorder=10)
            ax1.plot(timestamps, high_sell_prices, 'orange', label='Highest Sell Price', zorder=10)
            ax1.plot(timestamps, avg_prices, 'g-', label='Average Price', zorder=10)
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Price', color='black')
            ax1.tick_params(axis='y', labelcolor='black')
            ax1.set_ylim(y_min, y_max)
            ax1.legend(loc='upper left')
            ax1.set_zorder(ax2.get_zorder() + 1)
            ax1.patch.set_visible(False)
            plt.title(f"Price History for {item_name}")
            fig.tight_layout()

            self.canvas = FigureCanvasTkAgg(fig, master=self.item_frame)
            if self.graph_visible:
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill="both", expand=1)

            self.status_label.config(text="Latest price and history loaded successfully")
        except Exception as e:
            self.item_result_tree.delete(*self.item_result_tree.get_children())
            self.item_result_tree.insert("", "end", values=("Error", str(e)))
            self.status_label.config(text="Error fetching price or history")

    def search_item_history(self):
        item_name = self.item_entry.get().strip()
        item_id = self.get_item_id_from_name(item_name)
        if not item_id:
            self.item_result_tree.delete(*self.item_result_tree.get_children())
            self.item_result_tree.insert("", "end", values=("Error", "Invalid item name or no matching item found."))
            return
        self.status_label.config(text="Fetching price history...")
        try:
            data = make_request(f"{BASE_URL}/api/PlayerMarket/items/prices/history/{item_id}", api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.item_result_tree.delete(*self.item_result_tree.get_children())
            if self.raw_mode.get():
                self.item_result_tree.insert("", "end", values=("Raw Data", json.dumps(data, indent=2)))
            else:
                self.item_result_tree.insert("", "end", values=("Item Name", f"{item_name} (ID: {item_id})"))
                for entry in data[:10]:
                    timestamp = entry.get('timestamp', 'N/A')
                    low_sell = float(entry.get('lowestSellPrice', entry.get('lowesSellPrice', 'N/A'))) if entry.get('lowestSellPrice', entry.get('lowesSellPrice', 'N/A')) != 'N/A' else 'N/A'
                    high_sell = float(entry.get('highestSellPrice', 'N/A')) if entry.get('highestSellPrice', 'N/A') != 'N/A' else 'N/A'
                    avg_price = float(entry.get('averagePrice', 'N/A')) if entry.get('averagePrice', 'N/A') != 'N/A' else 'N/A'
                    volume = float(entry.get('tradeVolume', 'N/A')) if entry.get('tradeVolume', 'N/A') != 'N/A' else 'N/A'
                    self.item_result_tree.insert("", "end", values=(timestamp, f"Lowest Sell: {low_sell:,.0f}, Highest Sell: {high_sell:,.0f}, Avg: {avg_price:,.0f}, Volume: {volume:,.0f}" if low_sell != 'N/A' else "N/A"))
            
            if self.graph_visible and self.canvas:
                self.canvas.get_tk_widget().pack_forget()
            timestamps = [datetime.strptime(entry['timestamp'], "%Y-%m-%dT%H:%M:%SZ") for entry in data]
            low_sell_prices = [float(entry.get('lowestSellPrice', entry.get('lowesSellPrice', 0))) if entry.get('lowestSellPrice', entry.get('lowesSellPrice', 'N/A')) != 'N/A' else 0 for entry in data]
            high_sell_prices = [float(entry.get('highestSellPrice', 0)) if entry.get('highestSellPrice', 'N/A') != 'N/A' else 0 for entry in data]
            avg_prices = [float(entry.get('averagePrice', 0)) if entry.get('averagePrice', 'N/A') != 'N/A' else 0 for entry in data]
            volumes = [float(entry.get('tradeVolume', 0)) / 3 if entry.get('tradeVolume', 'N/A') != 'N/A' else 0 for entry in data]

            all_prices = low_sell_prices + high_sell_prices + avg_prices
            min_price = min(all_prices)
            max_price = max(all_prices)
            price_range = max_price - min_price
            padding = price_range * 0.1 if price_range > 0 else 5
            y_min = max(0, min_price - padding)
            y_max = max_price + padding

            fig, ax1 = plt.subplots(figsize=(10, 4))
            ax2 = ax1.twinx()
            ax2.bar(timestamps, volumes, color='red', alpha=0.5, width=0.01, label='Trade Volume')
            ax2.set_ylabel('Volume (Scaled)', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            ax2.set_ylim(0, max(volumes) * 1.2)
            ax1.plot(timestamps, low_sell_prices, 'b-', label='Lowest Sell Price', zorder=10)
            ax1.plot(timestamps, high_sell_prices, 'orange', label='Highest Sell Price', zorder=10)
            ax1.plot(timestamps, avg_prices, 'g-', label='Average Price', zorder=10)
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Price', color='black')
            ax1.tick_params(axis='y', labelcolor='black')
            ax1.set_ylim(y_min, y_max)
            ax1.legend(loc='upper left')
            ax1.set_zorder(ax2.get_zorder() + 1)
            ax1.patch.set_visible(False)
            plt.title(f"Price History for {item_name}")
            fig.tight_layout()

            self.canvas = FigureCanvasTkAgg(fig, master=self.item_frame)
            if self.graph_visible:
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill="both", expand=1)

            self.status_label.config(text="History loaded successfully")
        except Exception as e:
            self.item_result_tree.delete(*self.item_result_tree.get_children())
            self.item_result_tree.insert("", "end", values=("Error", str(e)))
            self.status_label.config(text="Error fetching history")

    def toggle_graph(self):
        self.graph_visible = not self.graph_visible
        if self.canvas:
            if self.graph_visible:
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill="both", expand=1)
            else:
                self.canvas.get_tk_widget().pack_forget()
        self.status_label.config(text=f"Graph {'shown' if self.graph_visible else 'hidden'}")

    def export_results(self):
        try:
            with open("item_results.txt", "w") as f:
                for item in self.item_result_tree.get_children():
                    values = self.item_result_tree.item(item, "values")
                    f.write(f"{values[0]}: {values[1]}\n")
            self.status_label.config(text="Results exported to item_results.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

def create_item_tab(notebook, api_key, raw_mode, last_api_call, item_data, item_list, status_label):
    tab = ItemTab(notebook, api_key, raw_mode, last_api_call, item_data, item_list, status_label)
    return tab