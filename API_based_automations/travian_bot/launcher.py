import time
import random
import json
import os
from identity_handling.login import login
from core.travian_api import TravianAPI
from core.hero_manager import HeroManager
from core.database_helpers import load_latest_unoccupied_oases
from oasis_raiding_from_scan_list_main import run_raid_planner
from raid_list_main import run_one_farm_list_burst
from features.raiding.reset_raid_plan import reset_saved_raid_plan
from features.raiding.setup_interactive_plan import setup_interactive_raid_plan
from identity_handling.identity_manager import handle_identity_management
from identity_handling.identity_helper import load_villages_from_identity
from features.hero.hero_operations import run_hero_operations

# === CONFIG ===
WAIT_BETWEEN_CYCLES_MINUTES = 50
JITTER_MINUTES = 5
SERVER_SELECTION = 0  # 👈 update if needed

def view_identity():
    """Display the current identity information."""
    try:
        with open("database/identity.json", "r", encoding="utf-8") as f:
            identity = json.load(f)
        
        travian_identity = identity.get("travian_identity", {})
        faction = travian_identity.get("faction", "unknown").title()
        tribe_id = travian_identity.get("tribe_id", "unknown")
        
        print("\n👤 Current Identity:")
        print(f"Faction: {faction} (ID: {tribe_id})")
        print("\n🏰 Villages:")
        
        for server in travian_identity.get("servers", []):
            for village in server.get("villages", []):
                name = village.get("village_name", "Unknown")
                vid = village.get("village_id", "?")
                x = village.get("x", "?")
                y = village.get("y", "?")
                print(f"- {name} (ID: {vid}) at ({x}|{y})")
    
    except FileNotFoundError:
        print("\n❌ No identity file found. Please set up your identity first.")
    except json.JSONDecodeError:
        print("\n❌ Identity file is corrupted. Please set up your identity again.")
    except Exception as e:
        print(f"\n❌ Error reading identity: {e}")

def update_village_coordinates():
    """Update coordinates for existing villages."""
    try:
        # Read current identity
        with open("database/identity.json", "r", encoding="utf-8") as f:
            identity = json.load(f)
        
        travian_identity = identity.get("travian_identity", {})
        servers = travian_identity.get("servers", [])
        
        if not servers:
            print("\n❌ No servers found in identity file.")
            return
        
        # For each server's villages
        for server in servers:
            villages = server.get("villages", [])
            print("\n🏰 Your villages:")
            for i, village in enumerate(villages):
                name = village.get("village_name", "Unknown")
                current_x = village.get("x", "?")
                current_y = village.get("y", "?")
                print(f"[{i}] {name} - Current coordinates: ({current_x}|{current_y})")
            
            while True:
                try:
                    choice = input("\nEnter village number to update (or 'q' to quit): ").strip()
                    if choice.lower() == 'q':
                        break
                    
                    village_idx = int(choice)
                    if village_idx < 0 or village_idx >= len(villages):
                        print("❌ Invalid village number.")
                        continue
                    
                    coords = input(f"Enter new coordinates for {villages[village_idx]['village_name']} (format: x y): ").strip().split()
                    if len(coords) != 2:
                        print("❌ Invalid format. Please enter two numbers separated by space.")
                        continue
                    
                    x, y = map(int, coords)
                    villages[village_idx]["x"] = x
                    villages[village_idx]["y"] = y
                    print(f"✅ Updated coordinates to ({x}|{y})")
                
                except ValueError:
                    print("❌ Invalid input. Please enter valid numbers.")
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        # Save updated identity
        with open("database/identity.json", "w", encoding="utf-8") as f:
            json.dump(identity, f, indent=4, ensure_ascii=False)
        print("\n✅ Successfully saved updated coordinates.")
    
    except FileNotFoundError:
        print("\n❌ No identity file found. Please set up your identity first.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def handle_identity_management():
    """Handle identity management sub-menu."""
    print("""
👤 Identity Management
[1] Set up new identity
[2] View current identity
[3] Update village coordinates
[4] Back to main menu
""")
    choice = input("Select an option: ").strip()
    
    if choice == "1":
        print("\nℹ️ Running identity setup...")
        os.system("python setup_identity.py")
    elif choice == "2":
        view_identity()
    elif choice == "3":
        update_village_coordinates()
    elif choice == "4":
        return
    else:
        print("❌ Invalid choice.")

def run_hero_operations(api: TravianAPI):
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

def setup_interactive_raid_plan(api, server_url):
    """Set up a raid plan interactively."""
    print("\n🎯 Interactive Raid Plan Creator")
    print("[1] Set up new raid plan")
    print("[2] Use saved configuration")
    
    choice = input("\nSelect an option: ").strip()
    
    if choice == "1":
        from features.raiding.setup_interactive_plan import setup_interactive_raid_plan
        setup_interactive_raid_plan(api, server_url)
    elif choice == "2":
        # Load saved configuration
        try:
            with open("database/saved_raid_plan.json", "r", encoding="utf-8") as f:
                saved_config = json.load(f)
            
            # Create raid plans for all villages
            from features.raiding.setup_interactive_plan import create_raid_plan_from_saved
            from identity_handling.identity_helper import load_villages_from_identity
            
            villages = load_villages_from_identity()
            if not villages:
                print("❌ No villages found in identity. Exiting.")
                return
            
            for i, village in enumerate(villages):
                print(f"\nSetting up raid plan for {village['village_name']}...")
                create_raid_plan_from_saved(api, server_url, i, saved_config)
            
            print("\n✅ Finished setting up raid plans for all villages.")
        except FileNotFoundError:
            print("❌ No saved raid plan found. Please set up a new raid plan first.")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("❌ Invalid option.")

def main():
    print("\n🛡️ Travian Automation Launcher")
    print("[1] Run one farm list burst + one raid planner")
    print("[2] Run farm list + Oasis raid planner in infinite safe loop")
    print("[3] Reset saved raid plan")
    print("[4] Setup new raid plan interactively")
    print("[5] Update identity, villages, etc")
    print("[6] Hero Operations")
    print("[7] Run oasis raiding (single village - for testing)")
    print("[8] Run multi-village raid planner (full automation)")

    choice = input("\nSelect an option: ").strip()

    # Login first
    print("\n🔐 Logging into Travian...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    if choice == "1":
        run_one_farm_list_burst(api)
        run_raid_planner(api, server_url)
    elif choice == "2":
        print("\n🔁 Starting infinite safe loop with recovery...")
        while True:
            try:
                print(f"\n⏳ Starting cycle at {time.strftime('%H:%M:%S')}")
                run_one_farm_list_burst(api)
                run_raid_planner(api, server_url)
                
                # Calculate next cycle time with jitter
                jitter = random.randint(-JITTER_MINUTES, JITTER_MINUTES)
                total_wait_minutes = WAIT_BETWEEN_CYCLES_MINUTES + jitter
                print(f"✅ Cycle complete. Waiting {total_wait_minutes} minutes...")
                time.sleep(total_wait_minutes * 60)
            except Exception as e:
                print(f"⚠️ Error during cycle: {e}")
                print("🔁 Attempting re-login and retry...")
                session, server_url = login()
                api = TravianAPI(session, server_url)
                print("✅ Re-login successful.")
    elif choice == "3":
        reset_saved_raid_plan()
    elif choice == "4":
        setup_interactive_raid_plan(api, server_url)
    elif choice == "5":
        handle_identity_management()
    elif choice == "6":
        run_hero_operations(api)
    elif choice == "7":
        print("\n🎯 Starting single-village oasis raiding (testing mode)...")
        run_raid_planner(api, server_url, multi_village=False)
    elif choice == "8":
        print("\n🎯 Starting multi-village raid planner (full automation)...")
        run_raid_planner(api, server_url, reuse_saved=True, multi_village=True)
    else:
        print("❌ Invalid option selected.")

if __name__ == "__main__":
    main()
