import os
import json
import logging

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RAID_PLAN_FILE = os.path.join(CURRENT_DIR, "..", "database", "saved_raid_plan.json")
RAID_PLAN_FILE = os.path.abspath(RAID_PLAN_FILE)

def load_saved_raid_plan():
    if os.path.exists(RAID_PLAN_FILE):
        with open(RAID_PLAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle old format (just raid_plan array) by wrapping it in new format
            if isinstance(data, list):
                data = {
                    "max_raid_distance": 25,  # Default for old format
                    "raid_plan": data
                }
            logging.info(f"✅ Loaded saved raid config from {os.path.abspath(RAID_PLAN_FILE)}")
            return data
    return None

def save_raid_plan(server_url, village_index, raid_plan_data):
    """
    Save raid plan configuration.
    
    Args:
        server_url (str): The server URL
        village_index (int): Index of the village in the identity file
        raid_plan_data (dict): Dictionary containing:
            - max_raid_distance (int): Maximum distance for raids
            - raid_plan (list): List of unit configurations
    """
    data = {
        "server": server_url,
        "village_index": village_index,
        "max_raid_distance": raid_plan_data.get("max_raid_distance", 25),  # Default to 25 if not specified
        "raid_plan": raid_plan_data.get("raid_plan", [])  # Default to empty list if not specified
    }

    os.makedirs(os.path.dirname(RAID_PLAN_FILE), exist_ok=True)
    with open(RAID_PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logging.info(f"✅ Saved raid config to {os.path.abspath(RAID_PLAN_FILE)}")
