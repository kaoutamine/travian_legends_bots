from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity, choose_village_to_scan
from core.travian_api import TravianAPI
from core.full_map_scanner import full_map_scan
from analysis.full_scan_oasis_analysis import extract_unoccupied_oases
import time

def main():
    print("[+] Logging into Travian...")
    session, base_url = login()

    time.sleep(1)  # Small wait after login to ensure session is ready
    api_client = TravianAPI(session, base_url)

    # Try to load villages, else inform user to run identity setup
    try:
        villages = load_villages_from_identity()
    except (FileNotFoundError, Exception) as e:
        print(f"[!] Issue loading identity: {e}")
        print("[!] Please run 'python identity_handling/setup_identity.py' first to set up your identity")
        return

    # Let user choose from villages
    village_x, village_y = choose_village_to_scan(villages)

    # Ask for scan radius
    try:
        scan_radius = int(input("\n🗺️  Enter scan radius around the village (default = 25): ").strip())
    except ValueError:
        scan_radius = 25

    # Full map scan
    print(f"[+] Starting full map scan around ({village_x}, {village_y}) with radius {scan_radius}...")
    scan_path = full_map_scan(api_client, village_x, village_y, scan_radius)

    # Oasis extraction
    print("[+] Extracting unoccupied oases from scan data...")
    extract_unoccupied_oases(scan_path)

    print("\n✅ Map scanning and oasis extraction complete!")

if __name__ == "__main__":
    main()
