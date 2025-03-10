Ai generated readme

# IdleClans API Tool

## Overview
The **IdleClans API Tool** is a graphical user interface (GUI) application that interacts with the IdleClans API. It allows users to fetch and display various game-related data, such as player stats, clan details, item prices, market trends, and chat logs. The tool is built using **Python** and **Tkinter** for the UI.

## Features
- **Player Tab**: Search for player profiles, view skill levels, equipment, and PvM stats.
- **Clan Tab**: View clan recruitment details, logs, and cup standings.
- **Item Tab**: Fetch item details, price history, and market trends.
- **Chat Tab**: Retrieve recent in-game chat messages and export chat logs.
- **Leaderboards Tab**: View rankings for clans and players.
- **Market Tab**: Analyze market trends for various in-game items.
- **Dark Mode Support**: Toggle between light and dark themes.
- **Export Data**: Save search results to text files.

## Installation
### Prerequisites
Ensure you have **Python 3.x** installed on your system. You will also need the following dependencies:

```sh
pip install requests tk matplotlib
```

### Running the Application
Clone the repository and run:

```sh
python main.py
```

## Usage
1. Launch the application.
2. Enter an **API key** (if required).
3. Navigate through tabs to access different game features.
4. Use search fields to fetch data.
5. Export results as needed.

## Files & Modules
- **`main.py`** - The main entry point, initializing the UI.
- **`player_tab.py`** - Handles player-related queries.
- **`clan_tab.py`** - Fetches clan-related data.
- **`item_tab.py`** - Retrieves item prices and history.
- **`chat_tab.py`** - Displays in-game chat logs.
- **`leaderboards_tab.py`** - Provides leaderboard rankings.
- **`market_tab.py`** - Analyzes market trends.
- **`utils.py`** - Contains API request functions and utility methods.

## API Integration
The tool communicates with **IdleClans API** endpoints to retrieve and display data. Requests are managed through `utils.py`, which handles error logging and retries.

## License
This project is open-source under the **MIT License**.

![Screenshot 2025-03-10 130003](https://github.com/user-attachments/assets/fe89dde0-7982-44bb-aef0-006d57f3169a)
![Screenshot 2025-03-10 125945](https://github.com/user-attachments/assets/5281c282-cfa0-4734-9a11-42685f68def2)
![Screenshot 2025-03-10 125906](https://github.com/user-attachments/assets/17bda515-7308-4f7d-a9af-c2a920fc4084)
![Screenshot 2025-03-10 125849](https://github.com/user-attachments/assets/83168f0d-0ece-4817-a451-d98f1dac38e7)
![Screenshot 2025-03-10 125822](https://github.com/user-attachments/assets/10fd7d66-924d-4d71-974a-f5de2e4aaca4)
![Screenshot 2025-03-10 125717](https://github.com/user-attachments/assets/051e1a08-59cb-426a-8925-08d801be4351)
![Screenshot 2025-03-10 125701](https://github.com/user-attachments/assets/d4a7b8ee-43d8-4afc-ba40-d84aaf69b1af)
![Screenshot 2025-03-10 125655](https://github.com/user-attachments/assets/db089805-3d17-464f-9b3e-2895916ca314)
