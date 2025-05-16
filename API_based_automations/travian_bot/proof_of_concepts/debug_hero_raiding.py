"""
Proof of Concept: Debug Hero Raiding
Tests the hero raiding functionality with all necessary checks and validations.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import time
import random

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity_handling.login import login
from core.travian_api import TravianAPI
from core.hero_manager import HeroManager
from core.database_helpers import load_latest_unoccupied_oases
from core.hero_runner import try_send_hero_to_oasis

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_oasis_liking_rating(oasis_data):
    """
    Calculate a liking rating for an oasis based on its animal composition.
    Small animals (rats, spiders, bats) = 1 point
    Medium animals (boars, wolves) = 2 points
    Large animals (bears, elephants, crocodiles) = 3 points
    """
    rating = 0
    
    # Get animals from raw title
    raw_title = oasis_data.get("raw_title", "").lower()
    if not raw_title:
        return 0
        
    # Parse animal counts from title
    # Example: "Unoccupied oasis (3 rats, 2 wolves, 1 bear)"
    animals = {}
    parts = raw_title.replace("unoccupied oasis", "").strip("() ").split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            count, animal = part.split(" ", 1)
            count = int(count)
            animal = animal.strip().lower()
            animals[animal] = count
        except ValueError:
            continue
    
    # Small animals (1 point)
    small_animals = ["rat", "spider", "bat"]
    for animal in small_animals:
        rating += animals.get(animal, 0)
    
    # Medium animals (2 points)
    medium_animals = ["boar", "wolf"]
    for animal in medium_animals:
        rating += animals.get(animal, 0) * 2
    
    # Large animals (3 points)
    large_animals = ["bear", "elephant", "crocodile"]
    for animal in large_animals:
        rating += animals.get(animal, 0) * 3
    
    return rating

def find_suitable_oases(api, village, oases):
    """
    Find suitable oases based on power and distance thresholds.
    Returns a list of (oasis, power, distance, liking_rating) tuples, sorted by liking_rating/distance ratio.
    """
    suitable = []
    
    for coord_key, oasis_data in oases.items():
        x_str, y_str = coord_key.split("_")
        oasis = {"x": int(x_str), "y": int(y_str)}
        
        # Calculate distance
        distance = abs(village['x'] - oasis['x']) + abs(village['y'] - oasis['y'])
        
        # Skip if too far
        if distance >= 20:
            continue
        
        # Query live animal data for the oasis
        oasis_info = api.get_oasis_info(oasis["x"], oasis["y"])
        animal_info = oasis_info["animals"]
        power = oasis_info["attack_power"]
        
        # Check if the oasis is occupied
        if oasis_info["is_occupied"]:
            continue  # Skip occupied oases
        
        # Set power threshold based on distance
        max_power = 2000  # Default for medium distance
        if distance < 3:
            max_power = 500  # Extra low distance
        elif distance < 6:
            max_power = 1000  # Low distance
        
        # Check if power is within acceptable range
        if 50 <= power <= max_power:
            # Calculate liking rating based on animal count
            liking_rating = sum(count for _, count in animal_info)
            # Calculate efficiency (higher is better)
            efficiency = liking_rating / distance
            suitable.append((oasis, power, distance, liking_rating, efficiency))
    
    # Sort by efficiency (liking_rating/distance ratio)
    suitable.sort(key=lambda x: x[4], reverse=True)
    return suitable

def test_hero_raiding(api):
    """Test hero raiding functionality with all necessary checks."""
    print("\n🦸 Testing Hero Raiding")
    print("=" * 30)
    
    while True:
        # Get hero status
        hero_manager = HeroManager(api)
        status = hero_manager.fetch_hero_status()
        if not status:
            print("❌ Failed to fetch hero status")
            return
        
        hero_can_be_sent = True
        if not status.is_present:
            print("❌ Hero is not present (but running oasis debug anyway)")
            hero_can_be_sent = False
        elif status.health is not None and status.health < 20:
            print(f"⚠️ Hero health too low ({status.health}%) (but running oasis debug anyway)")
            hero_can_be_sent = False
        elif status.is_on_mission:
            print("❌ Hero is on a mission (but running oasis debug anyway)")
            hero_can_be_sent = False
        
        # Get hero's current village
        if not status.current_village_id:
            print("❌ No current village information")
            return
        
        # Load villages from identity to get village coordinates
        from identity_handling.identity_helper import load_villages_from_identity
        villages = load_villages_from_identity()
        current_village = None
        
        for village in villages:
            if str(village["village_id"]) == status.current_village_id:
                current_village = village
                break
        
        if not current_village:
            print(f"⚠️ Hero is in village {status.current_village_id} which is not in your identity")
            return
        
        print(f"\n📍 Hero is in {status.current_village_name} at ({current_village['x']}, {current_village['y']})")
        
        # Load unoccupied oases around the village
        oases = load_latest_unoccupied_oases(f"({current_village['x']}_{current_village['y']})")
        if not oases:
            print("❌ No unoccupied oases found in latest scan")
            return
        
        print(f"\n🔍 Found {len(oases)} unoccupied oases")
        
        # Print raw_title for first 10 oases for debugging
        print("\n[DEBUG] raw_title for first 10 oases:")
        for idx, (coord_key, oasis_data) in enumerate(oases.items()):
            if idx >= 10:
                break
            print(f"{coord_key}: {oasis_data.get('raw_title', '')}")
        
        # Find suitable oases
        suitable = find_suitable_oases(api, current_village, oases)
        if not suitable:
            print("❌ No suitable oases found (based on power and distance thresholds)")
            return
        
        print("\n🎯 Suitable oases found:")
        for idx, (oasis, power, distance, liking_rating, efficiency) in enumerate(suitable[:5]):  # Show top 5
            print(f"[{idx}] Oasis at ({oasis['x']}, {oasis['y']})")
            print(f"    Power: {power}, Distance: {distance}")
            print(f"    Liking Rating: {liking_rating} (Efficiency: {efficiency:.2f})")
        
        # Ask user if they want to send hero
        if hero_can_be_sent:
            choice = input("\nSend hero to the best oasis? (y/n): ").strip().lower()
            if choice != 'y':
                print("Operation cancelled.")
                return
            # Send hero to the best oasis
            best_oasis = suitable[0][0]
            if try_send_hero_to_oasis(api, current_village, best_oasis):
                print(f"✅ Hero sent to oasis at ({best_oasis['x']}, {best_oasis['y']})")
                # Calculate return time and resend
                return_time = (distance / 14) * 3600  # Convert to seconds
                print(f"Hero will return in {return_time / 3600:.2f} hours.")
                time.sleep(return_time + random.randint(60, 120))  # Add a slight delay
                print("Resending hero...")
                continue  # Continue the loop to resend
            else:
                print("❌ Failed to send hero.")
        else:
            print("(Hero cannot be sent, but oasis selection logic ran successfully.)")
            time.sleep(60)  # Wait for 60 seconds before checking again

def main():
    # Load environment variables
    load_dotenv()
    
    # Login to the server and initialize API
    print("Logging into the server...")
    session, server_url = login()
    api = TravianAPI(session, server_url)
    
    # Test hero raiding
    test_hero_raiding(api)

if __name__ == "__main__":
    main() 