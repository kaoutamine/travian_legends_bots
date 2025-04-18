from login import login
from travian_api import TravianAPI

def main():
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Fetching your villages...")
    player_data = api.get_villages_and_farm_lists()

    villages = player_data["villages"]
    farm_lists = player_data["farmLists"]

    if not villages:
        print("[!] No villages found.")
        return

    # Show villages
    print("\nYour villages:")
    for idx, village in enumerate(villages):
        print(f"[{idx}] {village['name']} (ID {village['id']})")

    selected_idx = int(input("\nSelect your village: "))
    selected_village = villages[selected_idx]
    village_id = selected_village["id"]

    print(f"\n[+] You selected {selected_village['name']} (ID {village_id})")

    # Now find farm lists that belong to this village
    print("\nFarm Lists belonging to this village:")
    village_farm_lists = [fl for fl in farm_lists if fl["ownerVillage"]["id"] == village_id]

    if not village_farm_lists:
        print("[!] No farm lists found for this village.")
        return

    for idx, fl in enumerate(village_farm_lists):
        print(f"[{idx}] {fl['name']}")

    selected_list_idx = int(input("\nSelect the farm list you want to scan: "))
    selected_list_name = village_farm_lists[selected_list_idx]["name"]

    print(f"\n[+] Scanning farm list: {selected_list_name}")

    # Fetch details about that farm list
    print("[+] Fetching full farm list details for this village...")
    full_farm_lists = api.get_farm_lists(village_id)
    matching_lists = [fl for fl in full_farm_lists if fl["name"] == selected_list_name]

    if not matching_lists:
        print("[!] No detailed info found for this farm list.")
        return

    farm_list_id = matching_lists[0]["id"]
    farm_list_detail = api.get_farm_list_detail(farm_list_id)

    slots = farm_list_detail["data"]["farmList"]["slots"]

    # Now check each slot (target) for monsters if it's an oasis
    print("\nScanning each target for monsters...")
    for slot in slots:
        target = slot["target"]
        if target["type"] != 2:  # 2 = Oasis type
            continue

        x, y = target["x"], target["y"]
        oasis_info = api.get_oasis_info(x, y)
        animals = oasis_info["data"]["mapDetails"]["oasis"]["animals"]

        if not animals:
            print(f"[EMPTY] Oasis at ({x}|{y}) named '{target['name']}' has no monsters.")
        else:
            total_animals = sum(a["count"] for a in animals)
            print(f"[MONSTERS] Oasis at ({x}|{y}) named '{target['name']}' has {total_animals} monsters.")

if __name__ == "__main__":
    main()
