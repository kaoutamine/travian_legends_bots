import sys
import os

# Add the project's root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
import time
import json
from random import uniform
from analysis.number_to_unit_mapping import get_unit_name
from features.oasis.validator import is_valid_unoccupied_oasis
from identity_handling.identity_helper import load_villages_from_identity
from core.database_helpers import load_latest_unoccupied_oases

def load_troop_config():
    """Load troop configuration from analysis file."""
    config_path = os.path.join("analysis", "oasis_raiding_with_possible_losses_troop_config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading troop config: {e}")
        return None

def get_aggressive_units_for_faction(faction):
    """Get the aggressive unit types for a faction."""
    config = load_troop_config()
    if not config:
        return []
    return config["aggressive_units"].get(faction.lower(), [])

def get_required_troops_for_power(power, faction, troops_info):
    """
    Calculate required troops based on animal power and available aggressive units.
    Returns troop combination or None if too powerful.
    """
    config = load_troop_config()
    if not config:
        return None

    # Get available aggressive units for this faction
    aggressive_units = get_aggressive_units_for_faction(faction)
    
    # Filter to only units we actually have
    available_aggressive = {
        unit: count for unit, count in troops_info.items() 
        if unit in aggressive_units and count > 0
    }
    
    if not available_aggressive:
        return None  # No aggressive units available
    
    # Determine how many units to send based on power
    thresholds = config["oasis_power_thresholds"]
    if power < thresholds["weak"]["max_power"]:
        total_units_needed = thresholds["weak"]["total_units"]
        max_per_type = thresholds["weak"]["max_per_type"]
        prefer_pairs = False
    elif power < thresholds["medium"]["max_power"]:
        total_units_needed = thresholds["medium"]["total_units"]
        min_units = thresholds["medium"]["min_units"]
        max_per_type = thresholds["medium"]["max_per_type"]
        prefer_pairs = thresholds["medium"]["prefer_unit_pairs"]
    else:
        return None  # Skip strong oases for now
    
    # If we prefer unit pairs, try to use them first
    if prefer_pairs:
        unit_pairs = config["unit_pairs"].get(faction.lower(), [])
        required_troops = {}
        
        # Try each pair
        for pair in unit_pairs:
            if len(pair) != 2:
                continue
                
            unit1, unit2 = pair
            if unit1 in available_aggressive and unit2 in available_aggressive:
                # Calculate how many of each unit we can take
                units1 = min(max_per_type, available_aggressive[unit1])
                units2 = min(max_per_type, available_aggressive[unit2])
                
                # If we have enough units in this pair to meet minimum
                if units1 + units2 >= min_units:
                    required_troops[unit1] = units1
                    required_troops[unit2] = units2
                    return required_troops
        
        # If we couldn't find a suitable pair, fall back to regular distribution
        if not required_troops:
            logging.info("No suitable unit pairs found, falling back to regular distribution")
    
    # Regular distribution if no pairs or fallback
    required_troops = {}
    remaining_units = total_units_needed
    
    # Sort units by their code to ensure consistent distribution
    for unit in sorted(available_aggressive.keys()):
        if remaining_units <= 0:
            break
        # Take up to max_per_type units of each type, or whatever's left
        units_to_take = min(max_per_type, available_aggressive[unit], remaining_units)
        if units_to_take > 0:
            required_troops[unit] = units_to_take
            remaining_units -= units_to_take
    
    # For medium oases, check if we meet minimum requirements
    if power >= thresholds["medium"]["max_power"] and sum(required_troops.values()) < min_units:
        return None  # Not enough units to meet minimum requirement
    
    return required_troops if required_troops else None

def run_oasis_raiding_thread(api, faction, multi_village=False):
    """
    Main thread function for oasis raiding.
    Can be run standalone or integrated into the launcher.
    """
    # Load configuration
    config = load_troop_config()
    if not config:
        logging.error("Failed to load troop configuration")
        return
        
    # Get settings from config
    raid_settings = config.get("raid_settings", {})
    max_raid_distance = raid_settings.get("max_raid_distance", 8)  # Default to 8 if not specified
    wait_time = raid_settings.get("wait_time_seconds", 60)
    wait_jitter = raid_settings.get("wait_time_jitter_seconds", 10)
    
    logging.info(f"Using max raid distance: {max_raid_distance}")
    
    while True:
        try:
            # Load all villages from identity
            villages = load_villages_from_identity()
            if not villages:
                logging.error("No villages found in identity. Exiting.")
                return

            # Determine which villages to process
            if multi_village:
                villages_to_process = list(enumerate(villages))
                logging.info(f"Running in multi-village mode. Will process {len(villages)} villages.")
            else:
                village_index = 0
                villages_to_process = [(village_index, villages[village_index])]
                logging.info("Running in single-village mode.")

            # Process each village
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
                    logging.info(f"    {unit_name}: {amount} units")

                # Get oases in range
                oases = load_latest_unoccupied_oases(f"({village_x}_{village_y})")
                if not oases:
                    logging.info("No oases found in range")
                    continue

                sent_raids = 0
                for coord_key, oasis in oases.items():
                    x_str, y_str = coord_key.split("_")
                    x, y = int(x_str), int(y_str)
                    
                    # Calculate distance to oasis
                    distance = abs(x - village_x) + abs(y - village_y)
                    if distance > max_raid_distance:
                        logging.info(f"Skipping oasis at ({x}, {y}) - Distance {distance} exceeds max {max_raid_distance}")
                        continue
                    
                    # Get oasis info
                    oasis_info = api.get_oasis_info(x, y)
                    animal_info = oasis_info["animals"]
                    power = oasis_info["attack_power"]
                    
                    if not animal_info or power is None:
                        continue

                    # Calculate required troops based on power and available troops
                    required_troops = get_required_troops_for_power(power, faction, troops_info)
                    if not required_troops:
                        logging.info(f"Skipping oasis at ({x}, {y}) - Too powerful or no suitable troops")
                        continue

                    # Send the raid
                    logging.info(f"Launching raid on oasis at ({x}, {y})... Power: {power}, Distance: {distance}")
                    attack_info = api.prepare_oasis_attack(None, x, y, required_troops)
                    success = api.confirm_oasis_attack(attack_info, x, y, required_troops, village_id)

                    if success:
                        logging.info(f"✅ Raid sent to ({x}, {y}) - Power: {power}, Distance: {distance}")
                        # Update available troops
                        for unit_code, amount in required_troops.items():
                            troops_info[unit_code] -= amount
                        sent_raids += 1
                    else:
                        logging.error(f"❌ Failed to send raid to ({x}, {y})")

                    time.sleep(uniform(0.5, 1.2))

                logging.info(f"\n✅ Finished sending {sent_raids} raids for village {selected_village['village_name']}.")
            
            # Wait before next cycle with jitter
            jitter = uniform(-wait_jitter, wait_jitter)
            total_wait = wait_time + jitter
            logging.info(f"Waiting {total_wait:.1f} seconds before next cycle...")
            time.sleep(total_wait)

        except Exception as e:
            logging.error(f"Error in oasis raiding thread: {e}")
            time.sleep(wait_time)  # Wait on error
            continue

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Test the thread
    from identity_handling.login import login
    from core.travian_api import TravianAPI
    
    print("🔐 Logging into Travian...")
    session, server_url = login()
    api = TravianAPI(session, server_url)
    
    # Get faction from identity
    import json
    with open("database/identity.json", "r") as f:
        identity = json.load(f)
        faction = identity["travian_identity"]["faction"].lower()
    
    print(f"\n🤖 Starting oasis raiding thread for {faction.title()}...")
    run_oasis_raiding_thread(api, faction, multi_village=False) 