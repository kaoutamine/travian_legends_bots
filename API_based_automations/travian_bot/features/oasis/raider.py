import logging
import time
from random import uniform
from analysis.number_to_unit_mapping import get_unit_name
from features.oasis.validator import is_valid_unoccupied_oasis

def get_units_for_distance(distance, distance_ranges):
    """Get the appropriate unit combination for a given distance."""
    for range_data in distance_ranges:
        if range_data["start"] <= distance < range_data["end"]:
            return range_data["units"]
    return None

def run_raid_batch(api, raid_plan, faction, village_id, oases, hero_raiding=False, hero_available=False):
    """
    Execute a batch of raids on oases based on the raid plan.
    
    :param api: TravianAPI instance
    :param raid_plan: Dictionary containing raid configuration
    :param faction: Player's faction (Romans, Gauls, etc.)
    :param village_id: ID of the village sending raids
    :param oases: Dictionary of oases to raid
    :param hero_raiding: Whether hero raiding is enabled
    :param hero_available: Whether hero is available
    :return: Number of successful raids sent
    """
    sent_raids = 0
    max_raid_distance = raid_plan.get("max_raid_distance", float("inf"))
    distance_ranges = raid_plan.get("distance_ranges", [])

    # Get village coordinates from the first oasis's parent folder name
    village_coords = next(iter(oases.keys())).split("_")
    village_x, village_y = int(village_coords[0]), int(village_coords[1])
    logging.info(f"Raid origin village at ({village_x}, {village_y})")
    logging.info(f"Maximum raid distance: {max_raid_distance} tiles")

    # Get current troops
    troops_info = api.get_troops_in_village()
    if not troops_info:
        logging.error("Could not fetch troops. Exiting.")
        return sent_raids

    for coords, tile in oases.items():
        # Check distance from stored value
        distance = tile["distance"]
        if distance > max_raid_distance:
            logging.info(f"Reached maximum raid distance ({max_raid_distance} tiles). Stopping raids.")
            break

        # Get appropriate unit combination for this distance
        units = get_units_for_distance(distance, distance_ranges)
        if not units:
            logging.info(f"No unit combination defined for distance {distance:.1f}. Skipping.")
            continue

        # Check if we have enough troops for all units in the combination
        can_raid = True
        for unit in units:
            if troops_info.get(unit["unit_code"], 0) < unit["group_size"]:
                can_raid = False
                logging.info(f"Not enough {get_unit_name(unit['unit_code'], faction)} for distance {distance:.1f}. Skipping.")
                break

        if not can_raid:
            continue

        x_str, y_str = coords.split("_")
        x, y = int(x_str), int(y_str)
        
        # Validate oasis is raidable
        if not is_valid_unoccupied_oasis(api, x, y):
            continue

        # Prepare raid setup with all units in the combination
        raid_setup = {}
        for unit in units:
            raid_setup[unit["unit_code"]] = unit["group_size"]
            unit_name = get_unit_name(unit["unit_code"], faction)
            logging.info(f"Adding {unit['group_size']} {unit_name} to raid")

        logging.info(f"Launching raid on oasis at ({x}, {y})... Distance: {distance:.1f} tiles")
        attack_info = api.prepare_oasis_attack(None, x, y, raid_setup)
        success = api.confirm_oasis_attack(attack_info, x, y, raid_setup, village_id)

        if success:
            logging.info(f"✅ Raid sent to ({x}, {y}) - Distance: {distance:.1f} tiles")
            # Update available troops
            for unit in units:
                troops_info[unit["unit_code"]] -= unit["group_size"]
            sent_raids += 1
        else:
            logging.error(f"❌ Failed to send raid to ({x}, {y}) - Distance: {distance:.1f} tiles")

        time.sleep(uniform(0.5, 1.2))

    logging.info(f"\n✅ Finished sending {sent_raids} raids.")
    logging.info("Troops remaining:")
    for unit_code, amount in troops_info.items():
        if amount > 0 and unit_code != "uhero":
            unit_name = get_unit_name(unit_code, faction)
            logging.info(f"    {unit_name}: {amount} left")
            
    return sent_raids 