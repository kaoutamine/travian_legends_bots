from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity
from core.travian_api import TravianAPI
from core.database_raid_config import save_raid_plan, load_saved_raid_plan

def reset_saved_raid_plan(server_selection: int = 0):
    print("\n🛠️ Resetting Raid Plan...")
    session, server_url = login(server_selection=server_selection, interactive=True)
    api = TravianAPI(session, server_url)

    villages = load_villages_from_identity()
    if not villages:
        print("❌ No villages found. Exiting.")
        return

    print("\nAvailable villages:")
    for idx, v in enumerate(villages):
        print(f"[{idx}] {v['village_name']} at ({v['x']}, {v['y']})")

    try:
        index = int(input("\nSelect the village index to reset raid plan for: ").strip())
        selected = villages[index]
    except (IndexError, ValueError):
        print("❌ Invalid selection. Aborting.")
        return

    # Optional: show preview of current plan if it exists
    old_plan = load_saved_raid_plan()
    if old_plan and old_plan["server"] == server_url and old_plan["village_index"] == index:
        print("\n⚠️ Existing raid plan for this village:")
        for unit in old_plan["raid_plan"]:
            target = unit.get("target_coord", "Unknown")
            unit_code = unit.get("unit_code", "?")
            print(f"  - Unit {unit_code} → {target}")
        confirm = input("\nAre you sure you want to overwrite this plan? (y/N): ").strip().lower()
        if confirm != "y":
            print("❌ Aborting reset.")
            return

    # Save an empty plan with the selected village and server
    save_raid_plan(server_url, index, [])

    print(f"✅ Raid plan reset for village '{selected['village_name']}' on server {server_url}.")
    print("ℹ️ You can now re-run the planner to define a new plan.")
