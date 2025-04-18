# main.py

from login import login
from farm_list import (
    fetch_villages_and_farm_lists,
    fetch_farm_lists_with_ids,
    fetch_farm_list,
    parse_farm_list
)
from oasis import filter_oases, sort_oases_by_loot

def main():
    session, server_url = login()
    print(f"[+] Connected to {server_url}")

    player_data = fetch_villages_and_farm_lists(session)
    villages = player_data["villages"]

    # Select village
    for idx, village in enumerate(villages):
        print(f"[{idx}] {village['name']} (ID: {village['id']})")
    selected_village = villages[int(input("\nSelect a village: "))]

    farm_lists = fetch_farm_lists_with_ids(session, selected_village["id"])

    # Select farm list
    for idx, farm_list in enumerate(farm_lists):
        print(f"[{idx}] {farm_list['name']} — ID: {farm_list['id']} (Slots: {farm_list['slots_amount']})")
    selected_farm_list = farm_lists[int(input("\nSelect a farm list: "))]

    raw_farm_list_data = fetch_farm_list(session, selected_farm_list["id"])
    farms = parse_farm_list(raw_farm_list_data)

    oases = filter_oases(farms)

    if not oases:
        print("[-] No oases found.")
        return

    oases = sort_oases_by_loot(oases)

    print("\nOasis Targets (sorted by best loot):")
    for idx, oasis in enumerate(oases):
        print(f"[{idx}] {oasis['target_name']} at ({oasis['x']},{oasis['y']}) — Loot: {oasis['total_loot']}")

if __name__ == "__main__":
    main()
