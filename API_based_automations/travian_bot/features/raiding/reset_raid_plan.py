# features/raid/reset_raid_plan.py

from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity
from core.database_raid_config import save_raid_plan
from core.travian_api import TravianAPI

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

    # Save an empty plan with the selected village and server
    save_raid_plan({
        "server": server_url,
        "village_index": index,
        "raid_plan": []
    })

    print(f"✅ Raid plan reset for village '{selected['village_name']}' on server {server_url}.")
    print("ℹ️ You can now re-run the planner to define a new plan.")
