from login import login
from travian_api import TravianAPI
import re
from bs4 import BeautifulSoup

# === CONFIG ===
OASIS_X = -64
OASIS_Y = -8
TROOP_SETUP = {
    "t5": 60  # 60 Equites Imperatoris
}
VILLAGE_INDEX = 0  # auto-select village index

def extract_action_and_checksum(html: str):
    soup = BeautifulSoup(html, "html.parser")
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

    action_input = soup.select_one('input[name="action"]')
    if not action_input:
        raise Exception("[-] Failed to find action input.")

    action = action_input.get("value")

    print(f"[+] Found action: {action}, checksum: {checksum}")
    return action, checksum

def main():
    print("[+] Logging in...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Fetching villages...")
    player_info = api.get_player_info()
    villages = player_info["villages"]

    selected_village = villages[VILLAGE_INDEX]
    village_id = selected_village["id"]
    print(f"[+] Selected village: {selected_village['name']} (ID {village_id})")

    print("[+] Step 1: Get oasis tile details...")
    res = session.post(server_url + "/api/v1/map/tile-details", json={"x": OASIS_X, "y": OASIS_Y})
    res.raise_for_status()
    html = res.json()["html"]

    match = re.search(r"targetMapId=(\d+)", html)
    if not match:
        raise Exception("[-] Failed to find targetMapId in tile details.")
    target_map_id = match.group(1)
    print(f"[+] Found targetMapId: {target_map_id}")

    print("[+] Step 2: Open raid preparation page...")
    raid_page = session.get(f"{server_url}/build.php?gid=16&tt=2&eventType=4&targetMapId={target_map_id}")
    raid_page.raise_for_status()

    print("[+] Step 3: Prepare the attack to trigger checksum...")
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

    print("[+] Step 4: Extract action and checksum...")
    action, checksum = extract_action_and_checksum(preparation_res.text)

    print("[+] Step 5: Send final attack!")
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
        print("❌ Attack failed.")

if __name__ == "__main__":
    main()
