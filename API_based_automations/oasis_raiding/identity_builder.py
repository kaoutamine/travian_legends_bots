import os
import json
import time
import random
from login import login
from travian_api import TravianAPI

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IDENTITY_FILE = os.path.join(SCRIPT_DIR, "identity.json")

def load_identity():
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "travian_identity": {
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "servers": []
            }
        }

def save_identity(identity_data):
    with open(IDENTITY_FILE, "w") as f:
        json.dump(identity_data, f, indent=4)

def village_already_recorded(server_url, village_id, identity_data):
    for server in identity_data["travian_identity"]["servers"]:
        if server["server_url"] == server_url:
            for village in server["villages"]:
                if village["village_id"] == village_id:
                    return True
    return False

def add_village_to_identity(identity_data, server_name, server_url, village_name, village_id, x, y):
    # Find or create server entry
    for server in identity_data["travian_identity"]["servers"]:
        if server["server_url"] == server_url:
            break
    else:
        server = {"server_name": server_name, "server_url": server_url, "villages": []}
        identity_data["travian_identity"]["servers"].append(server)

    server["villages"].append({
        "village_name": village_name,
        "village_id": village_id,
        "x": x,
        "y": y
    })

def build_identity():
    print("[+] Logging in to build identity...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    identity_data = load_identity()

    print("[+] Fetching player info...")
    player_info = api.get_player_info()
    server_name = server_url.split("//")[1]  # crude server name from URL

    for village in player_info["villages"]:
        village_name = village["name"]
        village_id = village["id"]

        if village_already_recorded(server_url, village_id, identity_data):
            print(f"[-] Village '{village_name}' (ID {village_id}) already recorded, skipping...")
            continue

        print(f"[?] Village '{village_name}' (ID {village_id}) needs coordinates.")
        try:
            x = int(input("    Enter X coordinate: ").strip())
            y = int(input("    Enter Y coordinate: ").strip())
        except ValueError:
            print("[!] Invalid coordinates entered. Skipping this village.")
            continue

        add_village_to_identity(identity_data, server_name, server_url, village_name, village_id, x, y)
        save_identity(identity_data)

        # Small random sleep to make it feel more human
        time.sleep(random.uniform(0.8, 1.5))

    print("[+] Identity building complete!")

if __name__ == "__main__":
    build_identity()
