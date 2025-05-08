import logging
import json
import os
from core.travian_api import TravianAPI
from core.database_raid_config import save_raid_plan
from identity_handling.identity_helper import load_villages_from_identity
from identity_handling.faction_utils import get_faction_name
from analysis.number_to_unit_mapping import get_unit_name

def setup_interactive_raid_plan(api, server_url):
    """Set up a raid plan interactively."""
    villages = load_villages_from_identity()
    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

    # Load faction from identity.json
    try:
        with open("database/identity.json", "r", encoding="utf-8") as f:
            identity = json.load(f)
            tribe_id = identity["travian_identity"]["tribe_id"]
            faction = get_faction_name(tribe_id)
            logging.info(f"Detected faction: {faction.title()}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading identity: {e}")
        return

    # Show available villages
    print("\nAvailable villages:")
    for i, village in enumerate(villages):
        print(f"[{i}] {village['village_name']} at ({village['x']}, {village['y']})")
    print("[a] Set up for all villages")

    # Get village selection
    choice = input("\nSelect village index or 'a' for all: ").strip().lower()
    
    if choice == 'a':
        # Set up for all villages
        for i, village in enumerate(villages):
            print(f"\nSetting up raid plan for {village['village_name']}...")
            setup_raid_plan_for_village(api, server_url, village, i, faction)
    else:
        try:
            village_index = int(choice)
            if 0 <= village_index < len(villages):
                village = villages[village_index]
                setup_raid_plan_for_village(api, server_url, village, village_index, faction)
            else:
                print("Invalid village index.")
        except ValueError:
            print("Invalid input. Please enter a number or 'a'.")

def setup_raid_plan_for_village(api, server_url, village, village_index, faction):
    """Set up a raid plan for a specific village."""
    village_id = village["village_id"]
    village_x = village["x"]
    village_y = village["y"]
    logging.info(f"Selected village: {village['village_name']} ({village_x}, {village_y})")

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
        "village_index": village_index,
        "max_raid_distance": max_raid_distance,
        "distance_ranges": distance_ranges,
        "raid_plan": []
    }

    # Save the raid plan
    save_raid_plan(raid_plan, server_url, village_index)
    logging.info("✅ Raid plan setup complete!")

def create_raid_plan_from_saved(api, server_url, village_index, saved_config):
    """Create a raid plan from a saved configuration."""
    villages = load_villages_from_identity()
    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

    # Load faction from identity.json
    try:
        with open("database/identity.json", "r", encoding="utf-8") as f:
            identity = json.load(f)
            tribe_id = identity["travian_identity"]["tribe_id"]
            faction = get_faction_name(tribe_id)
            logging.info(f"Detected faction: {faction.title()}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading identity: {e}")
        return

    village = villages[village_index]
    village_id = village["village_id"]
    village_x = village["x"]
    village_y = village["y"]
    logging.info(f"Selected village: {village['village_name']} ({village_x}, {village_y})")

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

    # Create the raid plan from saved config
    raid_plan = {
        "server": server_url,
        "village_index": village_index,
        "max_raid_distance": saved_config["max_raid_distance"],
        "distance_ranges": saved_config["distance_ranges"],
        "raid_plan": []
    }

    # Save the raid plan
    save_raid_plan(raid_plan, server_url, village_index)
    logging.info("✅ Raid plan setup complete!")

    return raid_plan
