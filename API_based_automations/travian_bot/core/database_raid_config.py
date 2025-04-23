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
        logging.info(f"✅ Loaded saved raid config from {os.path.abspath(RAID_PLAN_FILE)}")
        return data
    return None

def save_raid_plan(server_url, village_index, raid_plan):
    data = {
        "server": server_url,
        "village_index": village_index,
        "raid_plan": raid_plan
    }
    os.makedirs(os.path.dirname(RAID_PLAN_FILE), exist_ok=True)
    with open(RAID_PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logging.info(f"✅ Saved raid config to {os.path.abspath(RAID_PLAN_FILE)}")
