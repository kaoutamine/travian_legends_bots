import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from identity_handling.login import login
from core.travian_api import TravianAPI
from bs4 import BeautifulSoup
from analysis.animal_to_power_mapping import get_animal_power


def get_oasis_animals_html(api: TravianAPI, x: int, y: int):
    url = f"{api.server_url}/api/v1/map/tile-details"
    payload = {"x": x, "y": y}
    response = api.session.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("html", "")


def print_oasis_defense_power(api: TravianAPI, x: int, y: int):
    html = get_oasis_animals_html(api, x, y)
    if not html:
        print("No oasis data found.")
        return

    soup = BeautifulSoup(html, "html.parser")
    troop_table = soup.find("table", id="troop_info")
    if not troop_table:
        print("No troops found in this oasis.")
        return

    total_power = 0
    print(f"\n🐾 Animals in oasis at ({x}, {y}):")
    for row in troop_table.find_all("tr"):
        img = row.find("img")
        cols = row.find_all("td")
        if img and len(cols) >= 2:
            animal_name = img.get("alt", "").strip().lower()
            count_text = cols[1].get_text(strip=True).replace("\u202d", "").replace("\u202c", "")
            try:
                count = int(count_text)
            except ValueError:
                continue

            power = get_animal_power(animal_name) * count
            total_power += power
            print(f" - {animal_name}: {count} × {get_animal_power(animal_name)} = {power}")

    print(f"\n🛡️ Total estimated defense power: {int(total_power)}")


if __name__ == "__main__":
    session, server_url = login()
    api = TravianAPI(session, server_url)

    # Example oasis coords
    test_x, test_y = 17, -49  # Replace with coords near you
    print_oasis_defense_power(api, test_x, test_y)
