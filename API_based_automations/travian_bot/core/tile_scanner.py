# tile_scanner.py

from API_based_automations.travian_bot.core.db_manager import save_json
from API_based_automations.oasis_raiding.identity_handling.login import login
from API_based_automations.oasis_raiding.travian_api import fetch_map_data

def classify_tile(tile_data):
    """Simple classifier based on resources"""
    resources = tile_data.get("resources", {})
    if resources == {"wood": 3, "clay": 3, "iron": 3, "crop": 9}:
        return "9c"
    elif resources == {"wood": 1, "clay": 1, "iron": 1, "crop": 15}:
        return "15c"
    else:
        return "regular"

def scan_and_classify(session, base_url, coordinates):
    print(f"🔍 Scanning {len(coordinates)} tiles for classification...")
    classified_data = {}

    for x, y in coordinates:
        tile_data = fetch_map_data(session, base_url, x, y)
        tile_type = classify_tile(tile_data)
        classified_data[f"{x}_{y}"] = {
            "tile_type": tile_type,
            "tile_data": tile_data
        }

    print(f"✅ Classified {len(classified_data)} tiles.")
    return classified_data

def main():
    session, base_url = login()

    # Coordinates to classify
    coordinates = [
        (100, 100),
        (101, 101),
        (102, 102),
        (103, 103),
        (104, 104)
    ]

    classified_tiles = scan_and_classify(session, base_url, coordinates)

    print("\nSample classified tiles:")
    for coord, info in classified_tiles.items():
        print(f"{coord}: {info['tile_type']}")

    # Ask to save
    should_save = input("\n💾 Save classified tile results to database? [y/n]: ").strip().lower()
    if should_save == 'y':
        metadata = {
            "description": "Tile classification",
            "tiles_classified": len(classified_tiles)
        }
        save_json({"metadata": metadata, "classified_tiles": classified_tiles}, filename="tile_classification.json", with_timestamp=True)
    else:
        print("❌ Classification not saved.")

if __name__ == "__main__":
    main()
