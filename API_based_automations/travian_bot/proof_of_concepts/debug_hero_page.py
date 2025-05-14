"""
Proof of Concept: Debug Hero Page
This file is kept for reference and future development.
It demonstrates how to get hero information from the hero page.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity_handling.login import login
from core.travian_api import TravianAPI
from core.hero_manager import HeroManager

# Configure logging
logging.basicConfig(level=logging.INFO)

def debug_hero_page(api):
    """Debug hero page functionality."""
    # Create hero manager and fetch status
    hero_manager = HeroManager(api)
    status = hero_manager.fetch_hero_status()
    
    if not status:
        print("❌ Failed to fetch hero status")
        return
    
    # Print hero status
    print("\n--- HERO STATUS ---")
    print(f"Present: {'✅' if status.is_present else '❌'}")
    
    if status.is_present:
        print(f"Level: {status.level} ({status.experience_percent:.1f}% to next)")
        print(f"Health: {'✅' if status.health is not None else '❌'} {status.health}%")
        print(f"On Mission: {'✅' if status.is_on_mission else '❌'}")
        
        if status.is_on_mission:
            if status.mission_return_time:
                print(f"Return Time: {status.mission_return_time}")
            if status.mission_target:
                x, y = status.mission_target
                print(f"Target: ({x}, {y})")
        
        if status.current_village_name:
            print(f"Current Village: {status.current_village_name}")
            if not status.is_in_known_village:
                print("⚠️  Note: Hero is in a village not listed in your identity")
        else:
            print("❌ No current village information")

def main():
    # Load environment variables
    load_dotenv()
    
    # Login to the server and initialize API
    print("Logging into the server...")
    session, server_url = login()
    api = TravianAPI(session, server_url)
    
    # Debug hero page
    debug_hero_page(api)

if __name__ == "__main__":
    main() 