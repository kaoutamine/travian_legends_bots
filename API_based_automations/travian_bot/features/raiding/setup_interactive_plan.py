import logging
import json
from core.travian_api import TravianAPI
from core.database_raid_config import save_raid_plan
from identity_handling.identity_helper import load_villages_from_identity
from identity_handling.faction_utils import get_faction_name
from analysis.number_to_unit_mapping import get_unit_name

def setup_interactive_raid_plan(api: TravianAPI, server_url: str):
    print("\n🛠️ Interactive Raid Plan Creator")

    # Load identity to get faction info
    try:
        with open("database/identity.json", "r", encoding="utf-8") as f:
            identity = json.load(f)
            faction = identity["travian_identity"]["faction"]
            print(f"Detected faction: {faction.title()}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"❌ Error loading identity: {e}")
        return

    villages = load_villages_from_identity()
    if not villages:
        print("❌ No villages found.")
        return

    print("\nAvailable villages:")
    for idx, v in enumerate(villages):
        print(f"[{idx}] {v['village_name']} at ({v['x']}, {v['y']})")

    try:
        village_index = int(input("Select village index: ").strip())
        selected = villages[village_index]
    except (IndexError, ValueError):
        print("❌ Invalid selection.")
        return

    village_id = selected["village_id"]
    print(f"\n🔍 Fetching info for '{selected['village_name']}'...")

    troops_info = api.get_troops_in_village()
    if not troops_info:
        print("❌ Could not fetch troops.")
        return

    available_units = {
        k: v for k, v in troops_info.items() if k.startswith("u") and v > 0 and k != "uhero"
    }

    if not available_units:
        print("❌ No usable troops available.")
        return

    print("\nAvailable troops:")
    indexed_units = list(available_units.items())
    for i, (code, count) in enumerate(indexed_units):
        print(f"[{i}] {get_unit_name(code, faction)} ({code}): {count}")

    selected_input = input(
        "\nSelect unit types to use (comma-separated indexes, e.g. 0,2): "
    ).strip()
    try:
        selected_indexes = [int(i.strip()) for i in selected_input.split(",")]
    except ValueError:
        print("❌ Invalid input.")
        return

    raid_plan = []
    for i in selected_indexes:
        try:
            unit_code, total_available = indexed_units[i]
        except IndexError:
            print(f"⚠️ Skipping invalid index: {i}")
            continue

        unit_name = get_unit_name(unit_code, faction)
        while True:
            try:
                group_size = int(input(f"Enter group size per raid for {unit_name}: ").strip())
                if group_size <= 0:
                    print("Must be > 0.")
                    continue
                break
            except ValueError:
                print("Invalid number.")

        raid_plan.append({
            "unit_code": unit_code,
            "unit_payload_code": unit_code,
            "group_size": group_size
        })

    # Ask for maximum raid distance
    while True:
        try:
            max_distance = int(input("\nEnter maximum raid distance in tiles (default = 25): ").strip() or "25")
            if max_distance <= 0:
                print("Distance must be > 0.")
                continue
            break
        except ValueError:
            print("Invalid number.")

    # Save raid plan with metadata
    save_raid_plan(server_url, village_index, {
        "max_raid_distance": max_distance,
        "raid_plan": raid_plan
    })
    
    print(f"\n✅ Saved raid plan for village '{selected['village_name']}' using {len(raid_plan)} unit types.")
    print(f"Maximum raid distance set to {max_distance} tiles.")
