import requests
import re
from bs4 import BeautifulSoup
from login import login  # Use your existing login function

# === CONFIG ===
OASIS_X = -90
OASIS_Y = 3
TROOP_SETUP = {
    "t5": 60  # 60 Equites Imperatoris
}
VILLAGE_INDEX = 0  # Which village to send from

def main():
    print("[+] Logging in...")
    session, server_url = login()
    print("[+] Logged in successfully.")

    print("[+] Fetching player info...")
    payload = {
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
    }
    res = session.post(f"{server_url}/api/v1/graphql", json=payload)
    res.raise_for_status()
    player_info = res.json()["data"]["ownPlayer"]

    selected_village = player_info["villages"][VILLAGE_INDEX]
    village_id = selected_village["id"]
    print(f"[+] Selected village: {selected_village['name']} (ID {village_id})")

    print(f"[+] Getting target oasis details at ({OASIS_X}, {OASIS_Y})...")
    res = session.post(server_url + "/api/v1/map/tile-details", json={"x": OASIS_X, "y": OASIS_Y})
    res.raise_for_status()
    html = res.json()["html"]

    match = re.search(r"targetMapId=(\d+)", html)
    if not match:
        raise Exception("[-] Failed to find targetMapId in tile details.")
    target_map_id = match.group(1)
    print(f"[+] Found targetMapId: {target_map_id}")

    print("[+] Opening raid preparation page...")
    raid_page = session.get(f"{server_url}/build.php?gid=16&tt=2&eventType=4&targetMapId={target_map_id}")
    raid_page.raise_for_status()

    print("[+] Sending initial POST to prepare troops...")
    prepare_data = {
        "villagename": "",
        "x": OASIS_X,
        "y": OASIS_Y,
        "eventType": 4,
        "ok": "ok",
    }

    # Force full troop fields t1..t11
    for troop_id in range(1, 12):  # t1 to t11
        prepare_data[f"troop[t{troop_id}]"] = TROOP_SETUP.get(f"t{troop_id}", 0)
    # Add scout/catapult fields even if empty
    prepare_data["troop[scoutTarget]"] = ""
    prepare_data["troop[catapultTarget1]"] = ""
    prepare_data["troop[catapultTarget2]"] = ""

    preparation_res = session.post(f"{server_url}/build.php?gid=16&tt=2", data=prepare_data)
    preparation_res.raise_for_status()

    print("[+] Preparation page content preview:")
    print(preparation_res.text[:2000])  # Check if the confirm button appears

    print("[+] Parsing action and checksum...")
    soup = BeautifulSoup(preparation_res.text, "html.parser")

    # Extract action
    action_input = soup.select_one('input[name="action"]')
    if not action_input:
        raise Exception("[-] No action input found.")
    action = action_input["value"]

    # Extract checksum
    button = soup.find("button", id="confirmSendTroops")
    if not button:
        raise Exception("[-] Confirm button not found.")

    onclick = button.get("onclick")
    checksum_match = re.search(r"value\s*=\s*'([a-f0-9]+)'", onclick)
    if not checksum_match:
        raise Exception("[-] Checksum not found in onclick.")
    checksum = checksum_match.group(1)

    print(f"[+] Found action: {action}, checksum: {checksum}")

    print("[+] Sending final attack confirmation...")
    final_attack_payload = {
        "action": action,
        "eventType": 4,
        "villagename": "",
        "x": OASIS_X,
        "y": OASIS_Y,
        "redeployHero": "",
        "checksum": checksum,
    }

    for troop_id in range(1, 12):  # t1 to t11
        final_attack_payload[f"troops[0][t{troop_id}]"] = TROOP_SETUP.get(f"t{troop_id}", 0)

    final_attack_payload["troops[0][scoutTarget]"] = ""
    final_attack_payload["troops[0][catapultTarget1]"] = ""
    final_attack_payload["troops[0][catapultTarget2]"] = ""
    final_attack_payload["troops[0][villageId]"] = village_id

    confirm_res = session.post(f"{server_url}/build.php?gid=16&tt=2", data=final_attack_payload, allow_redirects=False)
    confirm_res.raise_for_status()

    # Check based on 302 redirect
    if confirm_res.status_code == 302 and confirm_res.headers.get("Location") == "/build.php?gid=16&tt=1":
        print("✅ Attack launched successfully!")
    else:
        print(f"❌ Attack may have failed. Status: {confirm_res.status_code}")
        print(confirm_res.text[:1000])  # Print small debug info

if __name__ == "__main__":
    main()
