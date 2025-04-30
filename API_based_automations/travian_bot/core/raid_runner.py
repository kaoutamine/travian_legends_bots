import logging
import time
from random import uniform
from analysis.number_to_unit_mapping import get_unit_name

def run_raid_batch(api, raid_plan, faction, village_id, oases, hero_raiding=False, hero_available=False):
    sent_raids = 0

    for coords, tile in oases.items():
        for unit in raid_plan:
            if unit["available"] < unit["group_size"]:
                continue

            x_str, y_str = coords.split("_")
            x, y = int(x_str), int(y_str)

            animal_count = api.get_oasis_animal_count(x, y)
            if animal_count is None:
                continue
            if animal_count > 0:
                logging.warning(f"Skipping oasis at ({x}, {y}) — {animal_count} animals present.")
                break

            unit_name = get_unit_name(unit["unit_code"], faction)
            logging.info(f"Launching raid on oasis at ({x}, {y}) with {unit['group_size']} {unit_name}...")
            raid_setup = {unit["unit_payload_code"]: unit["group_size"]}
            raid_setup = {unit["unit_code"]: unit["group_size"]}  # 'u3': 5

            attack_info = api.prepare_oasis_attack(None, x, y, raid_setup)
            success = api.confirm_oasis_attack(attack_info, x, y, raid_setup, village_id)

            if success:
                logging.info(f"✅ Raid sent to ({x}, {y})")
                unit["available"] -= unit["group_size"]
                sent_raids += 1
            else:
                logging.error(f"❌ Failed to send raid to ({x}, {y})")

            time.sleep(uniform(0.5, 1.2))
            break

    logging.info(f"\n✅ Finished sending {sent_raids} raids.")
    logging.info("Troops remaining:")
    for unit in raid_plan:
        unit_name = get_unit_name(unit["unit_code"], faction)
        logging.info(f"    {unit_name}: {unit['available']} left")
