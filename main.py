import tkinter as tk
from tkinter import ttk
from player_tab import create_player_tab
from clan_tab import create_clan_tab
from item_tab import create_item_tab
from chat_tab import create_chat_tab
from leaderboards_tab import create_leaderboards_tab
from market_tab import create_market_tab
from utils import fetch_initial_data
import json
import os
import logging

# Setup logging
logging.basicConfig(filename="errors.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

# Create the root window but keep it hidden initially
root = tk.Tk()
root.title("icapi - The IdleClan Api Tool - by Tokerot")
root.geometry("1200x600")
root.withdraw()  # Hide the main window until fully loaded

# Create a splash screen
splash = tk.Toplevel()
splash.title("Loading...")
splash.geometry("300x100")
splash.resizable(False, False)
# Center the splash screen
splash.update_idletasks()
width = splash.winfo_width()
height = splash.winfo_height()
x = (splash.winfo_screenwidth() // 2) - (width // 2)
y = (splash.winfo_screenheight() // 2) - (height // 2)
splash.geometry(f"{width}x{height}+{x}+{y}")
splash_label = ttk.Label(splash, text="Loading IdleClans Data.", font=("Helvetica", 12))
splash_label.pack(pady=20)
splash.transient()
splash.grab_set()

# Function to animate the dots
def animate_dots():
    current_text = splash_label.cget("text")
    if current_text.endswith("..."):
        new_text = "Loading IdleClans Data."
    elif current_text.endswith(".."):
        new_text = "Loading IdleClans Data..."
    elif current_text.endswith("."):
        new_text = "Loading IdleClans Data.."
    else:
        new_text = "Loading IdleClans Data."
    splash_label.config(text=new_text)
    if splash.winfo_exists():
        splash.after(500, animate_dots)

# Start the animation
animate_dots()
splash.update()  # Ensure the splash screen renders immediately

# Main window setup
style = ttk.Style()
style.theme_use("clam")

# Top frame
top_frame = ttk.Frame(root)
top_frame.pack(side=tk.TOP, fill="x", pady=5)

api_key = tk.StringVar()
ttk.Label(top_frame, text="API Key (optional):").pack(side=tk.LEFT, padx=5)
api_key_entry = tk.Entry(top_frame, textvariable=api_key, width=30)
api_key_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(top_frame, text="?", command=lambda: tk.messagebox.showinfo("API Key", "Enter your Idle Clans API key here.")).pack(side=tk.LEFT, padx=2)

raw_mode = tk.BooleanVar(value=False)
ttk.Checkbutton(top_frame, text="Raw", variable=raw_mode).pack(side=tk.LEFT, padx=10)

dark_mode = tk.BooleanVar(value=False)
ttk.Checkbutton(top_frame, text="Dark Mode", variable=dark_mode, command=lambda: toggle_theme(dark_mode.get())).pack(side=tk.LEFT, padx=10)

last_api_call = tk.StringVar(value="Last API Call: None")
ttk.Label(top_frame, textvariable=last_api_call, wraplength=500, justify="right").pack(side=tk.RIGHT, padx=5)

# Status bar
status_frame = ttk.Frame(root)
status_frame.pack(side=tk.BOTTOM, fill="x")
status_label = ttk.Label(status_frame, text="Fetching initial data...", font=("Arial", 8))
status_label.pack(side=tk.LEFT, padx=5)

notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

def load_search_history():
    try:
        if os.path.exists("search_history.json"):
            with open("search_history.json", "r") as f:
                data = json.load(f)
                return {"players": data.get("players", []), "clans": data.get("clans", []), "keywords": data.get("keywords", [])}
    except Exception as e:
        logging.error(f"Failed to load search history: {e}")
    return {"players": [], "clans": [], "keywords": []}

def save_search_history(history):
    try:
        with open("search_history.json", "w") as f:
            json.dump(history, f)
    except Exception as e:
        logging.error(f"Failed to save search history: {e}")

search_history = load_search_history()

# Fetch initial data
game_data, item_data, item_list = fetch_initial_data(api_key.get(), last_api_call)

tabs = []
player_tab = create_player_tab(notebook, api_key, raw_mode, last_api_call, search_history, status_label, item_list)
tabs.append(player_tab)
clan_tab = create_clan_tab(notebook, api_key, raw_mode, last_api_call, search_history, status_label)
tabs.append(clan_tab)
tabs.append(create_item_tab(notebook, api_key, raw_mode, last_api_call, item_data, item_list, status_label))
tabs.append(create_chat_tab(notebook, api_key, raw_mode, last_api_call, status_label))
tabs.append(create_leaderboards_tab(notebook, api_key, raw_mode, last_api_call, status_label))
tabs.append(create_market_tab(notebook, api_key, raw_mode, last_api_call, item_list, status_label))

for tab in tabs:
    if hasattr(tab, "set_tabs"):
        tab.set_tabs(tabs)

def toggle_theme(dark):
    if dark:
        style.configure("TFrame", background="#333333")
        style.configure("TLabel", background="#333333", foreground="white")
        style.configure("TButton", background="#555555", foreground="white")
        style.configure("TCombobox", fieldbackground="#555555", background="#555555", foreground="white")
        style.configure("Treeview", background="#444444", foreground="white", fieldbackground="#444444")
        style.configure("Treeview.Heading", background="#555555", foreground="white")
        style.configure("TNotebook", background="#333333")
        style.configure("TNotebook.Tab", background="#555555", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#777777")])
        style.configure("Vertical.TScrollbar", background="#555555", troughcolor="#333333", arrowcolor="white")
        root.configure(bg="#333333")
        
        for tab in tabs:
            for widget in tab.tab.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(bg="#444444", fg="white", insertbackground="white")
                elif isinstance(widget, tk.Entry):
                    widget.configure(bg="#555555", fg="white", insertbackground="white")
        
        for tab in tabs:
            if hasattr(tab, "chat_tree"):
                tab.chat_tree.tag_configure("premium", foreground="#87CEEB")
                tab.chat_tree.tag_configure("gilded", foreground="#FFD700")
                tab.chat_tree.tag_configure("normal", foreground="white")
            if hasattr(tab, "clan_logs_tree"):
                tab.clan_logs_tree.tag_configure("viewed", foreground="white", font=("Arial", 10, "overstrike"))
                tab.clan_logs_tree.tag_configure("unviewed", foreground="white")
    else:
        style.configure("TFrame", background="SystemButtonFace")
        style.configure("TLabel", background="SystemButtonFace", foreground="black")
        style.configure("TButton", background="SystemButtonFace", foreground="black")
        style.configure("TCombobox", fieldbackground="white", background="SystemButtonFace", foreground="black")
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        style.configure("Treeview.Heading", background="SystemButtonFace", foreground="black")
        style.configure("TNotebook", background="SystemButtonFace")
        style.configure("TNotebook.Tab", background="SystemButtonFace", foreground="black")
        style.map("TNotebook.Tab", background=[("selected", "SystemButtonFace")])
        style.configure("Vertical.TScrollbar", background="SystemButtonFace", troughcolor="SystemButtonFace", arrowcolor="black")
        root.configure(bg="SystemButtonFace")
        
        for tab in tabs:
            for widget in tab.tab.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.configure(bg="white", fg="black", insertbackground="black")
                elif isinstance(widget, tk.Entry):
                    widget.configure(bg="white", fg="black", insertbackground="black")
        
        for tab in tabs:
            if hasattr(tab, "chat_tree"):
                tab.chat_tree.tag_configure("premium", foreground="blue")
                tab.chat_tree.tag_configure("gilded", foreground="gold")
                tab.chat_tree.tag_configure("normal", foreground="black")
            if hasattr(tab, "clan_logs_tree"):
                tab.clan_logs_tree.tag_configure("viewed", foreground="black", font=("Arial", 10, "overstrike"))
                tab.clan_logs_tree.tag_configure("unviewed", foreground="black")
    
    status_label.configure(background="#333333" if dark else "SystemButtonFace", foreground="white" if dark else "black")

def update_all_comboboxes():
    for tab in tabs:
        if hasattr(tab, "update_comboboxes"):
            tab.update_comboboxes("", "players")
            tab.update_comboboxes("", "clans")
            tab.update_comboboxes("", "keywords")

ttk.Button(top_frame, text="Clear History", command=lambda: [search_history.update({"players": [], "clans": [], "keywords": []}), save_search_history(search_history), update_all_comboboxes()]).pack(side=tk.LEFT, padx=5)

def on_closing():
    save_search_history(search_history)
    root.destroy()

# Apply initial theme and finalize setup
toggle_theme(dark_mode.get())
status_label.config(text="Ready")
splash.destroy()
root.deiconify()  # Show the main window now that loading is complete

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()