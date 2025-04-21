# main_scripts/map_scan_and_oasis_extract_main.py

from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity, choose_village_to_scan
from core.travian_api import TravianAPI
from core.full_map_scanner import full_map_scan
from analysis.full_scan_oasis_analysis import extract_unoccupied_oases

def main():
    session, base_url = login()
    api_client = TravianAPI(session, base_url)

    villages = load_villages_from_identity()
    village_x, village_y = choose_village_to_scan(villages)

    try:
        scan_radius = int(input("\n🗺️  Enter scan radius around the village (default = 25): ").strip())
    except ValueError:
        scan_radius = 25

    # Full map scan
    scan_path = full_map_scan(api_client, village_x, village_y, scan_radius)

    # Oasis extraction
    extract_unoccupied_oases(scan_path)

if __name__ == "__main__":
    main()
