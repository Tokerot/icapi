# chat_tab.py
import tkinter as tk
from tkinter import ttk
import json
from utils import make_request, BASE_URL
import re

class ChatTab:
    def __init__(self, notebook, api_key, raw_mode, last_api_call, status_label):
        self.tab = ttk.Frame(notebook)
        notebook.add(self.tab, text="Chat")
        self.chat_frame = ttk.Frame(self.tab, padding=10)
        self.chat_frame.pack(fill="both", expand=1)
        
        # Input frame
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill="x", pady=5)
        ttk.Label(input_frame, text="Channel:").pack(side=tk.LEFT, padx=5)
        self.channel_combobox = ttk.Combobox(input_frame, values=["All", "General", "Trade", "Help", "ClanHub", "CombatLFG", "RaidLFG"], width=20)
        self.channel_combobox.pack(side=tk.LEFT, padx=5)
        self.channel_combobox.set("All")
        ttk.Button(input_frame, text="Fetch Chat", command=self.fetch_chat).pack(side=tk.LEFT, padx=5)
        self.auto_refresh = tk.BooleanVar(value=False)
        ttk.Checkbutton(input_frame, text="Auto-Refresh", variable=self.auto_refresh, command=self.toggle_auto_refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Clear", command=self.clear_chat).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Export", command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Result frame with Treeview
        result_frame = ttk.Frame(self.chat_frame)
        result_frame.pack(fill="both", expand=1)
        self.chat_tree = ttk.Treeview(result_frame, columns=("Timestamp", "Channel", "Sender", "Message"), show="headings", height=25)
        self.chat_tree.heading("Timestamp", text="Time")
        self.chat_tree.heading("Channel", text="Channel")
        self.chat_tree.heading("Sender", text="Sender")
        self.chat_tree.heading("Message", text="Message")
        self.chat_tree.column("Timestamp", width=80, anchor="center")
        self.chat_tree.column("Channel", width=80, anchor="center")
        self.chat_tree.column("Sender", width=120, anchor="w")
        self.chat_tree.column("Message", width=500, anchor="w")
        self.chat_tree.pack(side=tk.LEFT, fill="both", expand=1)
        chat_scroll = ttk.Scrollbar(result_frame, orient="vertical", command=self.chat_tree.yview)
        chat_scroll.pack(side=tk.RIGHT, fill="y")
        self.chat_tree.configure(yscrollcommand=chat_scroll.set)
        
        # Styling tags for Treeview
        self.chat_tree.tag_configure("premium", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_tree.tag_configure("gilded", foreground="gold", font=("Arial", 10, "bold"))
        self.chat_tree.tag_configure("normal", foreground="black", font=("Arial", 10))
        
        self.api_key = api_key
        self.raw_mode = raw_mode
        self.last_api_call = last_api_call
        self.status_label = status_label
        self.raw_text = None  # For raw mode display

    def fetch_chat(self):
        self.status_label.config(text="Fetching chat...")
        try:
            # Map selected channel to query parameters
            selected_channel = self.channel_combobox.get()
            params = {
                "generalDisabled": "true" if selected_channel != "All" and selected_channel != "General" else "false",
                "tradeDisabled": "true" if selected_channel != "All" and selected_channel != "Trade" else "false",
                "helpDisabled": "true" if selected_channel != "All" and selected_channel != "Help" else "false",
                "clanHubDisabled": "true" if selected_channel != "All" and selected_channel != "ClanHub" else "false",
                "combatLFGDisabled": "true" if selected_channel != "All" and selected_channel != "CombatLFG" else "false",
                "raidLFGDisabled": "true" if selected_channel != "All" and selected_channel != "RaidLFG" else "false"
            }
            
            data = make_request(f"{BASE_URL}/api/Chat/recent", params=params, api_key=self.api_key.get(), last_api_call=self.last_api_call)
            self.clear_chat()  # Clear previous content
            
            if self.raw_mode.get():
                # Display raw JSON in a Text widget
                if self.chat_tree.winfo_exists():
                    self.chat_tree.pack_forget()
                if not self.raw_text:
                    self.raw_text = tk.Text(self.chat_frame, height=25, width=90)
                    self.raw_text.pack(fill="both", expand=1)
                    scroll = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.raw_text.yview)
                    scroll.pack(side=tk.RIGHT, fill="y")
                    self.raw_text.configure(yscrollcommand=scroll.set)
                self.raw_text.delete(1.0, tk.END)
                self.raw_text.insert(tk.END, json.dumps(data, indent=2))
            else:
                # Switch back to Treeview for readable mode
                if self.raw_text and self.raw_text.winfo_exists():
                    self.raw_text.pack_forget()
                    self.raw_text = None
                self.chat_tree.pack(side=tk.LEFT, fill="both", expand=1)
                
                for channel, messages in data.items():
                    for message in messages:
                        msg_text = message.get("Message", "N/A")
                        timestamp_match = re.match(r"\[(\d{2}:\d{2}:\d{2})\] (.*)", msg_text)
                        if timestamp_match:
                            timestamp = timestamp_match.group(1)
                            content = timestamp_match.group(2)
                        else:
                            timestamp = "N/A"
                            content = msg_text
                        
                        sender = message.get("Sender", "N/A")
                        premium = message.get("Premium", False)
                        gilded = message.get("Gilded", False)
                        
                        # Determine tag based on user status
                        tag = "gilded" if gilded else "premium" if premium else "normal"
                        self.chat_tree.insert("", "end", values=(timestamp, channel, sender, content), tags=(tag,))
            self.status_label.config(text="Chat loaded successfully")
        except Exception as e:
            self.clear_chat()
            self.chat_tree.insert("", "end", values=("N/A", "Error", "N/A", str(e)))
            self.status_label.config(text="Error fetching chat")

    def toggle_auto_refresh(self):
        if self.auto_refresh.get():
            self.auto_refresh_chat()
        else:
            try:
                self.chat_frame.after_cancel(self.auto_refresh_chat)
            except ValueError:  # If no after call is scheduled
                pass

    def auto_refresh_chat(self):
        self.fetch_chat()
        if self.auto_refresh.get():
            self.chat_frame.after(30000, self.auto_refresh_chat)

    def clear_chat(self):
        self.chat_tree.delete(*self.chat_tree.get_children())
        if self.raw_text and self.raw_text.winfo_exists():
            self.raw_text.delete(1.0, tk.END)

    def export_results(self):
        try:
            with open("chat_results.txt", "w") as f:
                if self.raw_mode.get() and self.raw_text:
                    f.write(self.raw_text.get(1.0, tk.END))
                else:
                    for item in self.chat_tree.get_children():
                        values = self.chat_tree.item(item, "values")
                        f.write(f"{values[0]}: [{values[1]}] {values[2]}: {values[3]}\n")
            self.status_label.config(text="Results exported to chat_results.txt")
        except Exception as e:
            self.status_label.config(text=f"Export failed: {e}")

def create_chat_tab(notebook, api_key, raw_mode, last_api_call, status_label):
    tab = ChatTab(notebook, api_key, raw_mode, last_api_call, status_label)
    return tab