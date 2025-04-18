from login import login
from travian_api import TravianAPI

def main():
    session, server_url = login()
    api = TravianAPI(session, server_url)

    player_info = api.get_player_info()

    villages = player_info["villages"]
    farm_lists = player_info["farmLists"]

    print("\nYour villages:")
    for idx, village in enumerate(villages):
        print(f"[{idx}] {village['name']} (ID {village['id']})")

    village_idx = int(input("\nSelect your village: "))
    selected_village = villages[village_idx]
    village_id = selected_village["id"]

    print(f"\n[+] Selected village: {selected_village['name']} (ID {village_id})\n")

    available_lists = [fl for fl in farm_lists if fl["ownerVillage"]["id"] == village_id]

    if not available_lists:
        print("No farm lists found for this village.")
        return

    print("\nFarm lists in this village:")
    for idx, fl in enumerate(available_lists):
        print(f"[{idx}] {fl['name']} (ID {fl['id']})")

    list_idx = int(input("\nSelect farm list to scan: "))
    selected_list = available_lists[list_idx]

    farm_list_details = api.get_farm_list_details(selected_list["id"])
    slots = farm_list_details["slots"]

    print(f"\n[+] Total targets in '{farm_list_details['name']}': {len(slots)}\n")

    for idx, slot in enumerate(slots):
        target = slot["target"]
        troop = slot.get("troop", {})
        monster_count = sum(troop.get(f"t{i}", 0) for i in range(1, 11))

        if target["type"] == 1:  # 1 = Village
            print(f"[{idx}] Village '{target['name']}' at ({target['x']},{target['y']}) - No monsters (village)")
        elif target["type"] == 2:  # 2 = Oasis
            print(f"[{idx}] Oasis '{target['name']}' at ({target['x']},{target['y']}) - Monsters: {monster_count}")
        else:
            print(f"[{idx}] Unknown type at ({target['x']},{target['y']})")

if __name__ == "__main__":
    main()
