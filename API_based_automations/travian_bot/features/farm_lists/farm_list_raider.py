import json
import os
import sys
import logging
import time
from random import uniform

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def load_farm_lists(server_url):
    """Load farm lists configuration for a server."""
    filename = os.path.join("database/farm_lists", f"{server_url.replace('/', '_').replace(':', '_')}.json")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return None

def run_farm_list_raids(api, server_url, village_id):
    """Run raids for all enabled farm lists in a village."""
    # Load farm lists configuration
    config = load_farm_lists(server_url)
    if not config:
        logging.error("❌ No farm lists configuration found.")
        return

    # Get village's farm lists
    village_config = config["villages"].get(str(village_id))
    if not village_config:
        logging.error(f"❌ No farm lists found for village ID {village_id}")
        return

    # Get enabled farm lists
    enabled_lists = [fl for fl in village_config["farm_lists"] if fl["enabled"]]
    if not enabled_lists:
        logging.info(f"ℹ️ No enabled farm lists for village {village_config['name']}")
        return

    logging.info(f"\n{'='*40}")
    logging.info(f"🏰 Processing farm lists for {village_config['name']}")
    logging.info(f"{'='*40}")
    
    # For each enabled farm list
    for farm_list in enabled_lists:
        logging.info(f"\n📋 Farm List: {farm_list['name']}")
        logging.info(f"   🎯 Slots: {farm_list['slots']}")
        logging.info(f"   ⏳ Preparing to launch...")
        
        # Launch the farm list
        success = api.send_farm_list(farm_list["id"])
        
        if success:
            logging.info(f"   ✨ Successfully launched!")
            logging.info(f"   🎉 Raids are on their way!")
        else:
            logging.error(f"   💥 Failed to launch!")
            logging.error(f"   ⚠️ Please check your connection")

        # Random delay between launches
        delay = uniform(1.5, 2.5)
        logging.info(f"   ⏱️ Waiting {delay:.1f}s before next launch...")
        time.sleep(delay)

def main():
    """Main entry point for farm list raiding."""
    from identity_handling.login import login
    from core.travian_api import TravianAPI
    
    print("\n" + "="*40)
    print("🚀 Starting Farm List Raider")
    print("="*40)
    
    print("\n🔐 Logging in...")
    session, server_url = login(server_selection=0, interactive=False)
    api = TravianAPI(session, server_url)
    
    # Load villages
    from identity_handling.identity_helper import load_villages_from_identity
    villages = load_villages_from_identity()
    
    if not villages:
        print("❌ No villages found in identity. Exiting.")
        return

    print(f"\n🏰 Found {len(villages)} villages to process")
    print("="*40)

    # Process each village
    for i, village in enumerate(villages, 1):
        print(f"\n📌 Processing village {i}/{len(villages)}")
        run_farm_list_raids(api, server_url, village["village_id"])
    
    print("\n" + "="*40)
    print("✨ Farm List Raider completed!")
    print("="*40)

if __name__ == "__main__":
    main() 