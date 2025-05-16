"""
Hero Operations Module
Handles hero-related operations including status checks and sending to oases.
"""

import logging
from core.hero_manager import HeroManager
from core.database_helpers import load_latest_unoccupied_oases
from identity_handling.identity_helper import load_villages_from_identity

def print_hero_status_summary(status):
    print("\n🦸 Hero Status Summary")
    print("=" * 30)
    if not status.is_present:
        print("❌ Hero is not present")
        return
    print(f"✅ Hero is present")
    print(f"📊 Level {status.level} ({status.experience_percent:.1f}% to next level)")
    if status.health is not None:
        print(f"❤️ Health: {status.health}%")
    if status.is_on_mission:
        print("\n🚀 On Mission")
        if status.mission_return_time:
            print(f"⏰ Return time: {status.mission_return_time}")
        if status.mission_target:
            x, y = status.mission_target
            print(f"🎯 Target: ({x}, {y})")
    else:
        print("\n🏠 At Home")
        if status.current_village_name:
            print(f"📍 Village: {status.current_village_name}")
            if not status.is_in_known_village:
                print("⚠️  Note: Hero is in a village not listed in your identity")
        if status.current_village_id:
            print(f"   ID: {status.current_village_id}")

def run_hero_operations(api):
    """Run hero-specific operations including checking status and sending to suitable oases."""
    print("\n🦸 Hero Operations")
    
    # Get hero status
    hero_manager = HeroManager(api)
    status = hero_manager.fetch_hero_status()
    if not status:
        print("❌ Failed to fetch hero status.")
        return
    
    # Print hero status
    print_hero_status_summary(status)
    
    # Load villages and let user select one
    villages = load_villages_from_identity()
    if not villages:
        print("❌ No villages found in identity. Exiting.")
        return
    
    # If hero is in a known village, select that village by default
    selected_village = None
    if status.is_in_known_village and status.current_village_id:
        for village in villages:
            if str(village["village_id"]) == status.current_village_id:
                selected_village = village
                print(f"\n✅ Hero is in {village['village_name']}")
                break
    
    # If hero is not in a known village or village not found, let user select
    if not selected_village:
        print("\nAvailable villages:")
        for idx, v in enumerate(villages):
            print(f"[{idx}] {v['village_name']} at ({v['x']}, {v['y']})")
        
        try:
            village_idx = int(input("\nSelect village index: ").strip())
            selected_village = villages[village_idx]
        except (ValueError, IndexError):
            print("❌ Invalid village selection.")
            return
    
    # Load oases and filter by power range
    oases = load_latest_unoccupied_oases(f"({selected_village['x']}_{selected_village['y']})")
    suitable_oases = []
    
    for coord_key, oasis_data in oases.items():
        x_str, y_str = coord_key.split("_")
        oasis = {"x": int(x_str), "y": int(y_str)}
        oasis_info = api.get_oasis_info(oasis["x"], oasis["y"])
        power = oasis_info["attack_power"]
        
        if 500 <= power <= 2000:
            suitable_oases.append((oasis, power))
    
    if not suitable_oases:
        print("❌ No suitable oases found (power between 500-2000).")
        return
    
    # Display suitable oases
    print("\nSuitable oases found:")
    for idx, (oasis, power) in enumerate(suitable_oases):
        print(f"[{idx}] Oasis at ({oasis['x']}, {oasis['y']}) - Power: {power}")
    
    # Ask user if they want to send hero
    choice = input("\nSend hero to attack? (y/n): ").strip().lower()
    if choice != 'y':
        print("Operation cancelled.")
        return
    
    # Send hero to first suitable oasis
    if hero_manager.send_hero_with_escort(selected_village, suitable_oases[0][0]):
        print(f"✅ Hero sent to oasis at ({suitable_oases[0][0]['x']}, {suitable_oases[0][0]['y']})")
    else:
        print("❌ Failed to send hero.") 