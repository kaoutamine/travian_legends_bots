import requests
import re
from bs4 import BeautifulSoup
from login import login  # Assuming your login() function still works

# === CONFIG ===
OASIS_X = -90
OASIS_Y = 3
TROOP_SETUP = {
    "t5": 60  # number of Equites Imperatoris
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

    # Here's where we will debug step-by-step:
    print("[+] Opening raid preparation page...")
    raid_page = session.get(f"{server_url}/build.php?gid=16&tt=2&eventType=4&targetMapId={target_map_id}")
    raid_page.raise_for_status()

    print("[+] Sending initial POST to prepare troops...")
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

    print("[+] Parsing action and checksum...")
    soup = BeautifulSoup(preparation_res.text, "html.parser")

    action_input = soup.select_one('input[name="action"]')
    checksum_input = soup.select_one('input[name="checksum"]')

    if not action_input or not checksum_input:
        print(preparation_res.text[:2000])  # Print first 2000 chars to debug
        raise Exception("[-] Failed to extract action/checksum.")

    action = action_input.get("value")
    checksum = checksum_input.get("value")
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
    for troop_id in range(1, 11):
        final_attack_payload[f"troops[0][t{troop_id}]"] = 0
    final_attack_payload[f"troops[0][t5]"] = TROOP_SETUP.get("t5", 0)
    final_attack_payload["troops[0][villageId]"] = village_id

    confirm_res = session.post(f"{server_url}/build.php?gid=16&tt=2", data=final_attack_payload)
    confirm_res.raise_for_status()

    if "Rally point" in confirm_res.text or "returning" in confirm_res.text or "underway" in confirm_res.text:
        print("✅ Attack launched successfully!")
    else:
        print("⚠️ Could not confirm success, please check manually.")
        print(confirm_res.text[:2000])  # Print part of the response for debug

if __name__ == "__main__":
    main()
