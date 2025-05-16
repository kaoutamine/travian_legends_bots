import logging

def try_send_hero_to_oasis(api, village, oasis, min_power=50, max_power=2000, help=True):
    """
    Sends the hero to the given oasis if its attack power is under the threshold.
    Power thresholds are based on distance:
    - Extra low distance (< 3 tiles): Power < 500
    - Low distance (< 6 tiles): Power < 1000
    - Medium distance (< 20 tiles): Power < 2000

    Args:
        api (TravianAPI): the game API object
        village (dict): the current village dict (must contain 'village_id', 'x', 'y')
        oasis (dict): a single oasis dict (must contain 'x', 'y')
        min_power (int): minimum acceptable power (default: 50)
        max_power (int): maximum acceptable power (default: 2000)
        help (bool): whether to send help troops (default: True)

    Returns:
        bool: True if hero was sent, False otherwise
    """
    # Calculate distance
    distance = abs(village['x'] - oasis['x']) + abs(village['y'] - oasis['y'])
    
    # Set power threshold based on distance
    if distance < 3:
        max_power = 500  # Extra low distance
    elif distance < 6:
        max_power = 1000  # Low distance
    elif distance < 20:
        max_power = 2000  # Medium distance
    else:
        logging.info(f"⚠️ Distance too far ({distance} tiles). Skipping.")
        return False

    oasis_info = api.get_oasis_info(oasis["x"], oasis["y"])
    power = oasis_info["attack_power"]
    logging.debug(f"Checking oasis at ({oasis['x']}, {oasis['y']}) → Power: {power}, Distance: {distance}")
    
    if power > max_power or power < min_power:
        logging.info(f"⚠️ Skipping oasis at ({oasis['x']},{oasis['y']}) — Power {power} outside range {min_power}-{max_power}")
        return False

    logging.info(f"🚀 Sending hero to oasis at ({oasis['x']},{oasis['y']}) — Power: {power}, Distance: {distance}")
    raid_setup = {}
    if help:
        raid_setup = {"t5": 1, "t11": 1}  # Send help troops
    else:
        raid_setup = {"t11": 1}  # Hero only
    
    attack_info = api.prepare_oasis_attack(None, oasis["x"], oasis["y"], raid_setup)
    success = api.confirm_oasis_attack(attack_info, oasis["x"], oasis["y"], raid_setup, village["village_id"])
    return success
