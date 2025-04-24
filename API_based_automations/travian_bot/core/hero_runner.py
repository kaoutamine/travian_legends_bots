import logging

def try_send_hero_to_oasis(api, village, oasis, min_power = 50, max_power=150):
    """
    Sends the hero to the given oasis if its attack power is under the threshold.

    Args:
        api (TravianAPI): the game API object
        village (dict): the current village dict (must contain 'village_id', 'x', 'y')
        oasis (dict): a single oasis dict (must contain 'x', 'y')
        max_power (int): maximum acceptable power to send hero

    Returns:
        bool: True if hero was sent, False otherwise
    """
    power = api.get_oasis_attack_power(oasis["x"], oasis["y"])

    logging.debug(f"Checking oasis at ({oasis['x']}, {oasis['y']}) → Power: {power}")
    if power > max_power or power < min_power:
        logging.info(f"⚠️ Skipping oasis at ({oasis['x']},{oasis['y']}) — Power too high ({power})")
        return False

    logging.info(f"🚀 Sending hero to oasis at ({oasis['x']},{oasis['y']}) — Estimated power: {power}")
    raid_setup = {"t11": 1}
    attack_info = api.prepare_oasis_attack(None, oasis["x"], oasis["y"], raid_setup)
    success = api.confirm_oasis_attack(attack_info, oasis["x"], oasis["y"], raid_setup, village["village_id"])
    return True
