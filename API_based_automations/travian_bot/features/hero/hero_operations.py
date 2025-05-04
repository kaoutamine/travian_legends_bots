import logging
from core.hero_manager import HeroManager
from core.database_helpers import load_latest_unoccupied_oases
from identity_handling.identity_helper import load_villages_from_identity

def run_hero_operations(api):
    """Run hero-specific operations including checking status and sending to suitable oases."""
    print("\n🦸 Hero Operations")
    
    # Load villages and let user select one
    villages = load_villages_from_identity()
    if not villages:
        print("❌ No villages found in identity. Exiting.")
        return
    
    print("\nAvailable villages:")
    for idx, v in enumerate(villages):
        print(f"[{idx}] {v['village_name']} at ({v['x']}, {v['y']})")
    
    try:
        village_idx = int(input("\nSelect village index: ").strip())
        selected_village = villages[village_idx]
    except (ValueError, IndexError):
        print("❌ Invalid village selection.")
        return
    
    # Check hero status
    hero_manager = HeroManager(api)
    troops_info = api.get_troops_in_village()
    if not troops_info:
        print("❌ Could not fetch troops. Exiting.")
        return
    
    is_present, health = hero_manager.get_hero_status(troops_info)
    if not is_present:
        print("❌ Hero is not present in the village.")
        return
    
    print(f"✅ Hero is present in {selected_village['village_name']}")
    if health is not None:
        print(f"Hero health: {health}%")
    
    # Load oases and filter by power range
    oases = load_latest_unoccupied_oases(f"({selected_village['x']}_{selected_village['y']})")
    suitable_oases = []
    
    for coord_key, oasis_data in oases.items():
        x_str, y_str = coord_key.split("_")
        oasis = {"x": int(x_str), "y": int(y_str)}
        power = api.get_oasis_attack_power(oasis["x"], oasis["y"])
        
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