import requests
import re
import json
import time
import logging

BASE_URL = "https://query.idleclans.com"
ITEM_LIST_URL = "https://idleclans.uraxys.dev/api/items/all"

def make_request(url, params=None, api_key=None, last_api_call=None, retries=3):
    headers = {"X-Api-Key": api_key} if api_key else {}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)  # Added timeout for reliability
            response.raise_for_status()
            if last_api_call:
                last_api_call.set(f"Last API Call: {url}")
            fixed_text = re.sub(r'ObjectId\("([0-9a-fA-F]{24})"\)', r'"\1"', response.text)
            if not fixed_text.strip():
                raise ValueError("Empty response")
            return json.loads(fixed_text)
        except (requests.exceptions.RequestException, ValueError) as e:
            logging.error(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt == retries - 1:
                raise Exception(f"API request failed after {retries} attempts: {e}")
            time.sleep(1)

def fetch_item_list(last_api_call=None):
    try:
        item_list = make_request(ITEM_LIST_URL, last_api_call=last_api_call)
        # Map internal_id to name_id (reverting to original behavior)
        result = {str(item['internal_id']): item['name_id'] for item in item_list if 'internal_id' in item and 'name_id' in item}
        logging.debug(f"Fetched item_list with keys: {list(result.keys())}")
        return result
    except Exception as e:
        logging.error(f"Failed to fetch item list: {e}")
        return {}

def fetch_initial_data(api_key=None, last_api_call=None):
    try:
        game_data = make_request(f"{BASE_URL}/api/Configuration/game-data", api_key=api_key, last_api_call=last_api_call)
        prices = make_request(f"{BASE_URL}/api/PlayerMarket/items/prices/latest", api_key=api_key, last_api_call=last_api_call)
        item_list = fetch_item_list(last_api_call)
        return game_data, prices, item_list
    except Exception as e:
        logging.error(f"Failed to fetch initial data: {e}")
        return None, None, {}