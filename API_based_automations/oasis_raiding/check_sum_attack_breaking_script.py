import requests
import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# === SETTINGS ===
SERVER_INDEX = 0  # 0 = Asia 3
VILLAGE_INDEX = 0  # 0 = Rafale
TROOP_SETUP = {
    "t5": 60,  # Send 60 Equites Imperatoris
}
OASIS_X = -64
OASIS_Y = -8

load_dotenv()

def login():
    print("[+] Logging in...")
    servers = [
        "https://ts3.x1.asia.travian.com/",
    ]
    server_url = servers[SERVER_INDEX]

    session = requests.Session()

    login_page = session.get(server_url + "login.php")
    if login_page.status_code != 200:
        raise Exception("[-] Failed to load login page.")

    # Direct POST login (no parsing needed)
    res = session.post(server_url + "login.php", data={
        "name": os.getenv("TRAVIAN_EMAIL"),
        "password": os.getenv("TRAVIAN_PASSWORD"),
        "s1": "Login",
    })

    if "dorf1.php" not in res.text:
        raise Exception("[-] Login failed.")

    print(f"[+] Successfully logged into {server_url}")
    return session, server_url

def extract_action_and_checksum(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # Find the confirm button
    button = soup.find("button", id="confirmSendTroops")
    if not button:
        raise Exception("[-] Confirm button not found.")

    onclick = button.get("onclick")
    if not onclick:
        raise Exception("[-] Confirm button has no onclick attribute.")

    checksum_match = re.search(r"value\s*=\s*'([a-f0-9]+)'", onclick)
    if not checksum_match:
        raise Exception("[-] Failed to extract checksum from onclick.")

    checksum = checksum_match.group(1)

    # Find the hidden action input
    action_input = soup.select_one('input[name="action"]')
    if not action_input:
        raise Exception("[-] Failed to find action input.")

    action = action_input.get("value")

    print(f"[+] Found action={action}, checksum={checksum}")
    return action, checksum

def main():
    session, server_url = login()

    print("[+] Fetching villages...")
    res = session.post(server_url + "/api/v1/graphql", json={
        "query": """
        query {
            ownPlayer {
                villages {
                    id
                    name
                }
            }
        }
        """
    })

    villages = res.json()["data"]["ownPlayer"]["villages"]
    selected_village = villages[VILLAGE_INDEX]
    village_id = selected_village["id"]
    print(f"[+] Selected village: {selected_village['name']} (ID {village_id})")

    print("[+] Step 1: Get oasis tile details...")
    tile_detail_res = session.post(server_url + "/api/v1/map/tile-details", json={"x": OASIS_X, "y": OASIS_Y})
    tile_detail_res.raise_for_status()
    tile_html = tile_detail_res.json()["html"]

    # Find targetMapId in HTML
    match = re.search(r"targetMapId=(\d+)", tile_html)
    if not match:
        raise Exception("[-] Failed to find targetMapId.")

    target_map_id = match.group(1)
    print(f"[+] Found targetMapId: {target_map_id}")

    print("[+] Step 2: Open raid page...")
    raid_page_res = session.get(f"{server_url}/build.php?gid=16&tt=2&eventType=4&targetMapId={target_map_id}")
    raid_page_res.raise_for_status()

    print("[+] Step 3: Prepare troops to get checksum...")
    prepare_data = {
        "troop[t1]": "",
        "troop[t2]": "",
        "troop[t3]": "",
        "troop[t4]": "",
        "troop[t5]": str(TROOP_SETUP.get("t5", "")),
        "troop[t6]": "",
        "villagename": "",
        "x": OASIS_X,
        "y": OASIS_Y,
        "eventType": 4,
        "ok": "ok",
    }
    preparation_res = session.post(f"{server_url}/build.php?gid=16&tt=2", data=prepare_data)
    preparation_res.raise_for_status()

    print("[+] Step 4: Extract checksum and action...")
    action, checksum = extract_action_and_checksum(preparation_res.text)

    print("[+] Step 5: Confirm the raid...")
    final_attack_payload = {
        "action": action,
        "eventType": 4,
        "villagename": "",
        "x": OASIS_X,
        "y": OASIS_Y,
        "redeployHero": "",
        "checksum": checksum,
    }

    # Add the troop setup
    for troop_id in range(1, 11):
        final_attack_payload[f"troops[0][t{troop_id}]"] = 0
    final_attack_payload[f"troops[0][t5]"] = TROOP_SETUP.get("t5", 0)
    final_attack_payload["troops[0][villageId]"] = village_id

    confirm_res = session.post(f"{server_url}/build.php?gid=16&tt=2", data=final_attack_payload)
    confirm_res.raise_for_status()

    if "Rally point" in confirm_res.text or "returning" in confirm_res.text or "underway" in confirm_res.text:
        print("✅ Attack launched successfully!")
    else:
        print("❌ Failed to launch the attack.")

if __name__ == "__main__":
    main()
