import json
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.travian_api import TravianAPI
from identity_handling.identity_helper import load_villages_from_identity

FARM_LISTS_DIR = "database/farm_lists"

def load_farm_lists(server_url):
    """Load farm lists configuration from file."""
    filename = os.path.join(FARM_LISTS_DIR, f"{server_url.replace('/', '_').replace(':', '_')}.json")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None

def save_farm_lists(config, server_url):
    """Save farm lists configuration to file."""
    os.makedirs(FARM_LISTS_DIR, exist_ok=True)
    filename = os.path.join(FARM_LISTS_DIR, f"{server_url.replace('/', '_').replace(':', '_')}.json")
    with open(filename, "w") as f:
        json.dump(config, f, indent=4)

def update_farm_lists(api, server_url):
    """Update farm lists configuration interactively."""
    print("\n🔄 Updating farm lists configuration...")
    
    # Load villages
    villages = load_villages_from_identity()
    if not villages:
        print("❌ No villages found in identity. Exiting.")
        return

    # Load existing config or create new one
    config = load_farm_lists(server_url) or {
        "server_url": server_url,
        "villages": {}
    }

    # For each village
    for village in villages:
        village_id = str(village["village_id"])  # Convert to string for JSON
        print(f"\n🏰 Village: {village['village_name']} (ID: {village_id})")
        
        # Get farm lists
        farm_lists = api.get_village_farm_lists(int(village_id))
        
        # Initialize village in config if not exists
        if village_id not in config["villages"]:
            config["villages"][village_id] = {
                "name": village["village_name"],
                "farm_lists": []
            }

        # Update farm lists
        if farm_lists:
            print("\nAvailable farm lists:")
            for i, fl in enumerate(farm_lists):
                # Find existing config for this farm list
                existing_config = next(
                    (f for f in config["villages"][village_id]["farm_lists"] if f["id"] == fl["id"]),
                    None
                )
                enabled = existing_config["enabled"] if existing_config else True
                
                print(f"[{i}] {fl['name']}")
                print(f"    Slots: {fl['slotsAmount']}")
                print(f"    Running raids: {fl['runningRaidsAmount']}")
                print(f"    Currently {'enabled' if enabled else 'disabled'} for automation")
                
                while True:
                    choice = input(f"    Enable this farm list for automation? (y/n) [{('y' if enabled else 'n')}]: ").strip().lower()
                    if choice in ['y', 'n', '']:
                        break
                    print("    Please enter 'y' or 'n'")
                
                enabled = choice == 'y' if choice else enabled
                
                # Update config
                new_config = {
                    "id": fl["id"],
                    "name": fl["name"],
                    "slots": fl["slotsAmount"],
                    "enabled": enabled
                }
                
                # Replace or append
                if existing_config:
                    idx = config["villages"][village_id]["farm_lists"].index(existing_config)
                    config["villages"][village_id]["farm_lists"][idx] = new_config
                else:
                    config["villages"][village_id]["farm_lists"].append(new_config)
        else:
            print("  No farm lists found")
            config["villages"][village_id]["farm_lists"] = []

    # Save updated config
    save_farm_lists(config, server_url)
    print("\n✅ Farm lists configuration updated successfully!")

def main():
    """Main entry point for farm list management."""
    from identity_handling.login import login
    
    print("[+] Logging in...")
    session, server_url = login(server_selection=0, interactive=False)
    api = TravianAPI(session, server_url)
    
    update_farm_lists(api, server_url)

if __name__ == "__main__":
    main() 