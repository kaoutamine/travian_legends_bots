"""
Proof of Concept: Oasis Troops and Defense Power
This file is kept for reference and future development.
It demonstrates how to calculate oasis defense power from animal counts.
"""

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


def main():
    # Login to the server
    print("Logging into the server...")
    session, server_url = login()
    api = TravianAPI(session, server_url)
    
    # Test coordinates
    test_coords = [
        (36, -30),  # Example oasis
        (35, -31),  # Another example
    ]
    
    print("\n🔍 Testing Oasis Defense Power Calculation")
    print("=" * 50)
    
    for x, y in test_coords:
        try:
            print(f"\n📌 Testing oasis at ({x}, {y})...")
            
            # Get oasis HTML
            html = get_oasis_animals_html(api, x, y)
            if not html:
                print(f"❌ Failed to get HTML for oasis at ({x}, {y})")
                continue
            
            # Parse animals
            soup = BeautifulSoup(html, "html.parser")
            troop_table = soup.find("table", id="troop_info")
            
            if not troop_table:
                print("❌ No troop information found")
                continue
            
            # Calculate total power
            total_power = 0
            print("\nAnimals found:")
            for row in troop_table.find_all("tr"):
                img = row.find("img")
                cols = row.find_all("td")
                if img and len(cols) >= 2:
                    animal_name = img.get("alt", "").strip().lower()
                    count_text = cols[1].get_text(strip=True).replace("\u202d", "").replace("\u202c", "")
                    try:
                        count = int(count_text)
                        power = get_animal_power(animal_name) * count
                        total_power += power
                        print(f"  {animal_name}: {count} units (power: {power})")
                    except ValueError:
                        continue
            
            print(f"\nTotal defense power: {total_power}")
            
        except Exception as e:
            print(f"❌ Error processing oasis at ({x}, {y}): {str(e)}")
    
    print("\n✅ Oasis defense power calculation test complete!")

if __name__ == "__main__":
    main() 