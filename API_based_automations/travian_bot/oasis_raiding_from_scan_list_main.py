import os
import json
import logging
from random import uniform
import time

from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity
from core.travian_api import TravianAPI
from analysis.number_to_unit_mapping import get_unit_name
from core.database_helpers import load_latest_unoccupied_oases
from core.database_raid_config import load_saved_raid_plan, save_raid_plan
from features.oasis.raider import run_raid_batch
from core.hero_runner import try_send_hero_to_oasis  # ✅ Hero logic
from identity_handling.faction_utils import get_faction_name
from dotenv import load_dotenv

class NoTimestampFormatter(logging.Formatter):
    def format(self, record):
        return f"[{record.levelname}] {record.getMessage()}"

console_handler = logging.StreamHandler()
console_handler.setFormatter(NoTimestampFormatter())
logging.basicConfig(level=logging.INFO, handlers=[console_handler])

def save_raid_plan(raid_plan, server_url, village_index):
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

def run_raid_planner(
    api,
    server_url,
    reuse_saved=True,
    selected_village_index=None,
    units_to_use=None,
    enable_hero_raiding=True,
    interactive=False,
    multi_village=False,  # New parameter to control multi-village mode
    run_farm_lists=False  # New parameter to control whether to run farm lists
):
    villages = load_villages_from_identity()
    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

    # Load faction from identity using the helper function
    try:
        current_dir = os.path.dirname(__file__)
        database_dir = os.path.join(current_dir, 'database')
        identity_path = os.path.join(database_dir, 'identity.json')
        identity_path = os.path.abspath(identity_path)

        with open(identity_path, "r", encoding="utf-8") as f:
            identity = json.load(f)
            tribe_id = identity["travian_identity"]["tribe_id"]
            faction = get_faction_name(tribe_id)
            logging.info(f"Detected faction: {faction.title()}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading identity: {e}")
        return

    # Determine which villages to process
    if multi_village:
        villages_to_process = list(enumerate(villages))
        logging.info(f"Running in multi-village mode. Will process {len(villages)} villages.")
    else:
        village_index = 0
        villages_to_process = [(village_index, villages[village_index])]
        logging.info("Running in single-village mode.")

    # Process selected villages
    for village_index, selected_village in villages_to_process:
        logging.info(f"\n{'='*50}")
        logging.info(f"Processing village {village_index + 1}/{len(villages)}: {selected_village['village_name']}")
        logging.info(f"{'='*50}")

        village_id = selected_village["village_id"]
        village_x = selected_village["x"]
        village_y = selected_village["y"]
        logging.info(f"Village coordinates: ({village_x}, {village_y})")

        # Switch to the correct village
        logging.info(f"\nSwitching to village {village_id}")
        url = f"{api.server_url}/dorf1.php?newdid={village_id}"
        response = api.session.get(url)
        response.raise_for_status()

        # Get troops info for this village
        troops_info = api.get_troops_in_village()
        if not troops_info:
            logging.error("Could not fetch troops. Skipping village.")
            continue

        logging.info("Current troops in village:")
        for unit_code, amount in troops_info.items():
            unit_name = get_unit_name(unit_code, faction)
            logging.info(f"    {unit_name} ({unit_code}): {amount} units")

        # Run farm lists only if explicitly requested
        if run_farm_lists:
            logging.info("\nRunning farm lists...")
            from features.farm_lists.farm_list_raider import run_farm_list_raids
            run_farm_list_raids(api, server_url, village_id)
        else:
            logging.info("\nSkipping farm lists as requested.")

        # Then check if this village has a raid plan for oases
        saved_data = load_saved_raid_plan(village_index)
        if reuse_saved and saved_data and saved_data["server"] == server_url:
            # This village has a saved raid plan
            raid_plan = saved_data  # Use the entire saved data as the raid plan
        else:
            # No raid plan for this village
            logging.warning(f"⚠️ No raid plan found for {selected_village['village_name']}. Skipping oasis raids.")
            continue

        oases = load_latest_unoccupied_oases(f"({village_x}_{village_y})")
        if not oases:
            logging.info("No unoccupied oases found for this village. Skipping oasis raids.")
            continue

        # --- HERO LOGIC START ---
        hero_available = troops_info.get("uhero", 0) >= 1
        hero_sent = False

        if enable_hero_raiding and hero_available:
            for coord_key, oasis_data in oases.items():
                x_str, y_str = coord_key.split("_")
                oasis = {"x": int(x_str), "y": int(y_str)}
                if try_send_hero_to_oasis(api, selected_village, oasis):
                    hero_sent = True
                    break
        # --- HERO LOGIC END ---

        run_raid_batch(api, raid_plan, faction, village_id, oases)

    logging.info("\n✅ Finished processing all selected villages.")

def setup_raid_plan_interactive(api, server_url, selected_village_index=None):
    """Set up a raid plan interactively."""
    villages = load_villages_from_identity()
    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

    # Load faction from identity using the helper function
    try:
        current_dir = os.path.dirname(__file__)
        database_dir = os.path.join(current_dir, '..', 'database')
        identity_path = os.path.join(database_dir, 'identity.json')
        identity_path = os.path.abspath(identity_path)

        with open(identity_path, "r", encoding="utf-8") as f:
            identity = json.load(f)
            tribe_id = identity["travian_identity"]["tribe_id"]
            faction = get_faction_name(tribe_id)
            logging.info(f"Detected faction: {faction.title()}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading identity: {e}")
        return

    # Determine which village to use
    if selected_village_index is None:
        # Show available villages
        print("\nAvailable villages:")
        for i, village in enumerate(villages):
            print(f"[{i}] {village['village_name']} ({village['x']}, {village['y']})")
        
        # Get village selection
        while True:
            try:
                selected_village_index = int(input("\nSelect a village (enter number): "))
                if 0 <= selected_village_index < len(villages):
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

    selected_village = villages[selected_village_index]
    village_id = selected_village["village_id"]
    village_x = selected_village["x"]
    village_y = selected_village["y"]
    logging.info(f"Selected village: {selected_village['village_name']} ({village_x}, {village_y})")

    # Switch to the correct village
    logging.info(f"\nSwitching to village {village_id}")
    url = f"{api.server_url}/dorf1.php?newdid={village_id}"
    response = api.session.get(url)
    response.raise_for_status()

    # Get troops info
    troops_info = api.get_troops_in_village()
    if not troops_info:
        logging.error("Could not fetch troops. Exiting.")
        return

    logging.info("Current troops in village:")
    for unit_code, amount in troops_info.items():
        unit_name = get_unit_name(unit_code, faction)
        logging.info(f"    {unit_name} ({unit_code}): {amount} units")

    # Get max raid distance
    while True:
        try:
            max_raid_distance = int(input("\nEnter maximum raid distance (1-15): "))
            if 1 <= max_raid_distance <= 15:
                break
            print("Distance must be between 1 and 15.")
        except ValueError:
            print("Please enter a valid number.")

    # Get distance ranges and unit combinations
    distance_ranges = []
    current_start = 0

    while current_start < max_raid_distance:
        print(f"\nSetting up raid group for distance {current_start}+")
        
        # Get end distance for this range
        while True:
            try:
                end_distance = int(input(f"Enter end distance for this group (max {max_raid_distance}): "))
                if current_start < end_distance <= max_raid_distance:
                    break
                print(f"End distance must be between {current_start + 1} and {max_raid_distance}.")
            except ValueError:
                print("Please enter a valid number.")

        # Get unit combinations for this range
        units = []
        while True:
            print("\nAvailable units:")
            for unit_code, amount in troops_info.items():
                unit_name = get_unit_name(unit_code, faction)
                print(f"    {unit_name} ({unit_code}): {amount} units")

            unit_code = input("\nEnter unit code to add (or press Enter to finish this range): ").strip()
            if not unit_code:
                break

            if unit_code not in troops_info:
                print("Invalid unit code. Please try again.")
                continue

            while True:
                try:
                    group_size = int(input(f"Enter group size for {get_unit_name(unit_code, faction)}: "))
                    if 1 <= group_size <= troops_info[unit_code]:
                        break
                    print(f"Group size must be between 1 and {troops_info[unit_code]}.")
                except ValueError:
                    print("Please enter a valid number.")

            units.append({
                "unit_code": unit_code,
                "unit_payload_code": unit_code,
                "group_size": group_size
            })

        if units:
            distance_ranges.append({
                "start": current_start,
                "end": end_distance,
                "units": units
            })
            current_start = end_distance
        else:
            print("No units added for this range. Please add at least one unit.")

    # Create the raid plan
    raid_plan = {
        "server": server_url,
        "village_index": selected_village_index,
        "max_raid_distance": max_raid_distance,
        "distance_ranges": distance_ranges,
        "raid_plan": []
    }

    # Save the raid plan
    save_raid_plan(raid_plan, server_url, selected_village_index)
    logging.info("✅ Raid plan setup complete!")

    return raid_plan

def main():
    """Main entry point for the oasis raiding script."""
    # Load environment variables
    load_dotenv()
    
    # Get server URL from environment
    server_url = os.getenv('TRAVIAN_SERVER_URL')
    if not server_url:
        print("❌ Error: TRAVIAN_SERVER_URL not found in .env file")
        return
    
    # Login to server
    print("\n🔐 Logging into Travian...")
    api = login(server_url)
    if not api:
        print("❌ Failed to login")
        return
    
    print("\n🎯 Starting multi-village raid planner (full automation)...")
    
    while True:
        try:
            # Get all villages
            villages = api.get_villages()
            if not villages:
                print("❌ No villages found")
                return
            
            # Process each village
            for i, village in enumerate(villages, 1):
                village_id = village['id']
                village_name = village['name']
                village_coords = (village['x'], village['y'])
                
                print(f"\n{'='*50}")
                print(f"Processing village {i}/{len(villages)}: {village_name}")
                print(f"{'='*50}")
                print(f"Village coordinates: {village_coords}")
                
                # Switch to village
                print(f"\nSwitching to village {village_id}")
                api.switch_village(village_id)
                
                # Get current troops
                troops = api.get_troops_in_village()
                if troops:
                    print("Current troops in village:")
                    for unit_id, amount in troops.items():
                        unit_name = api.get_unit_name(unit_id)
                        print(f"    {unit_name}: {amount} units")
                print()
                
                # First run farm lists
                print("Running farm lists...")
                run_farm_list_raids(api, server_url, village_id)
                
                # Then run oasis raids
                run_raid_planner(api, village_id)
            
            print("\n⏳ Waiting 50 minutes before next raid cycle...")
            time.sleep(50 * 60)  # 50 minutes in seconds
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Raid planner stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error during raid cycle: {str(e)}")
            print("⏳ Waiting 5 minutes before retrying...")
            time.sleep(5 * 60)  # 5 minutes in seconds
            continue

if __name__ == "__main__":
    main()
