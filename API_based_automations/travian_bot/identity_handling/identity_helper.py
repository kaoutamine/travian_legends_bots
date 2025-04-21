import json
import os

def load_villages_from_identity():
    """Load all villages from the identity card located in database/."""
    current_dir = os.path.dirname(__file__)
    database_dir = os.path.join(current_dir, '..', 'database')  # Move UP one folder first
    identity_path = os.path.join(database_dir, 'identity.json')

    identity_path = os.path.abspath(identity_path)  # Make sure it's a full absolute path

    with open(identity_path, 'r') as f:
        identity = json.load(f)

    servers = identity["travian_identity"]["servers"]
    if not servers:
        raise Exception("❌ No servers found in identity!")

    villages = servers[0]["villages"]
    if not villages:
        raise Exception("❌ No villages found for the server!")

    return villages

def choose_village_to_scan(villages):
    """Prompt user to pick a village to center the scan around."""
    print("\n🏡 Available villages to scan from:")
    for idx, village in enumerate(villages):
        print(f"{idx}: {village['village_name']} ({village['x']},{village['y']})")

    while True:
        try:
            choice = int(input("\n✏️ Enter the number of the village to scan around: ").strip())
            if 0 <= choice < len(villages):
                selected = villages[choice]
                print(f"\n✅ Selected village: {selected['village_name']} at ({selected['x']},{selected['y']})")
                return selected["x"], selected["y"]
            else:
                print("❌ Invalid selection, please try again.")
        except ValueError:
            print("❌ Please enter a valid number.")
