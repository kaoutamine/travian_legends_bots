# proof_of_concepts/get_troops_simple.py

from oasis_raiding.core.travian_api import TravianAPI
from oasis_raiding.identity_handling.login import login
from bs4 import BeautifulSoup




def get_village_troops(api: TravianAPI) -> dict:
    """
    Fetches and returns current troops stationed in the selected village.
    """
    url = f"{api.server_url}/dorf1.php"
    response = api.session.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    troops_table = soup.find("table", id="troops")
    if not troops_table:
        print("[-] No troops table found.")
        return {}

    troops = {}
    for row in troops_table.find_all("tr"):
        num_cell = row.find("td", class_="num")
        name_cell = row.find("td", class_="un")
        if not num_cell or not name_cell:
            continue

        try:
            unit_name = name_cell.text.strip()
            unit_count = int(num_cell.text.strip())

            if unit_name:
                troops[unit_name] = unit_count
        except Exception as e:
            print(f"[!] Skipping row due to error: {e}")

    return troops

def main():
    print("[+] Logging into Travian...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Fetching troops...")
    troops = get_village_troops(api)

    if troops:
        print("[+] Troops stationed in the village:")
        for unit, count in troops.items():
            print(f"  - {unit}: {count}")
    else:
        print("[!] No troops found or parsing failed.")

if __name__ == "__main__":
    main()
