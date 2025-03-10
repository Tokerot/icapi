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

