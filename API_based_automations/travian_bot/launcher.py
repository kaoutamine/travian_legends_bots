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

def main():
    print("""
🛡️ Travian Automation Launcher
[1] Run one farm list burst + one raid planner
[2] Run farm list + Oasis raid planner in infinite safe loop
[3] Reset saved raid plan
[4] Setup new raid plan interactively
[5] Update identity, villages, etc
[6] Hero Operations
""")
    choice = input("Select an option: ").strip()

    if choice == "3":
        reset_saved_raid_plan(server_selection=SERVER_SELECTION)
        return
    
    if choice == "5":
        handle_identity_management()
        return
    
    if choice == "6":
        print("\n🔐 Logging into Travian...")
        session, server_url = login(server_selection=SERVER_SELECTION, interactive=False)
        api = TravianAPI(session, server_url)
        run_hero_operations(api)
        return

    print("\n🔐 Logging into Travian...")
    session, server_url = login(server_selection=SERVER_SELECTION, interactive=False)
    api = TravianAPI(session, server_url)

    if choice == "1":
        print("\n🚀 Starting one safe cycle (farm + raid)...\n")
        run_one_farm_list_burst(api)
        time.sleep(3)
        run_raid_planner(
            api=api,
            server_url=server_url,
            reuse_saved=True,
            enable_hero_raiding=True,
            interactive=False
        )

    elif choice == "2":
        print("\n🔁 Starting infinite safe loop with recovery...\n")

        while True:
            start_time = time.strftime("%H:%M:%S")
            print(f"\n⏳ Starting cycle at {start_time}")

            try:
                run_one_farm_list_burst(api)
                time.sleep(3)
                run_raid_planner(
                    api=api,
                    server_url=server_url,
                    reuse_saved=True,
                    enable_hero_raiding=True,
                    interactive=False
                )
            except Exception as e:
                print(f"⚠️ Error during cycle: {e}")
                print("🔁 Attempting re-login and retry...")

                try:
                    session, server_url = login(server_selection=SERVER_SELECTION, interactive=False)
                    api = TravianAPI(session, server_url)
                    print("✅ Re-login successful.")

                except Exception as login_error:
                    print(f"❌ Re-login failed: {login_error}")
                    print("💤 Will retry after 1 hour...")
                    time.sleep(60 * 60)
                    continue

            jitter = random.randint(-JITTER_MINUTES, JITTER_MINUTES)
            total_wait_minutes = WAIT_BETWEEN_CYCLES_MINUTES + jitter
            print(f"✅ Cycle complete. Waiting {total_wait_minutes} minutes...\n")
            time.sleep(total_wait_minutes * 60)

    elif choice == "4":
        setup_interactive_raid_plan(api=api, server_url=server_url)

    else:
        print("❌ Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
