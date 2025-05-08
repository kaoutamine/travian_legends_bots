import os
import json
import logging

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RAID_PLAN_FILE = os.path.join(CURRENT_DIR, "..", "database", "saved_raid_plan.json")
RAID_PLAN_FILE = os.path.abspath(RAID_PLAN_FILE)

def load_saved_raid_plan(village_index):
    """Load the saved raid plan from JSON file."""
    try:
        filename = f"database/raid_plans/raid_plan_village_{village_index}.json"
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"⚠️ No saved raid plan found for village {village_index}")
        return None
    except Exception as e:
        logging.error(f"❌ Failed to load raid plan: {e}")
        return None

def save_raid_plan(raid_plan, server_url=None, village_index=None):
    """Save the raid plan to a JSON file."""
    try:
        # Create a directory for raid plans if it doesn't exist
        os.makedirs("database/raid_plans", exist_ok=True)
        
        # Save the raid plan with village index in the filename
        filename = f"database/raid_plans/raid_plan_village_{village_index}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(raid_plan, f, indent=4)
        logging.info(f"✅ Raid plan saved to {filename}")
    except Exception as e:
        logging.error(f"❌ Failed to save raid plan: {e}")
