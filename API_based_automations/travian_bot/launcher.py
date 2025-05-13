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
from features.hero.hero_operations import run_hero_operations as run_hero_ops, print_hero_status_summary

# === CONFIG ===
WAIT_BETWEEN_CYCLES_MINUTES = 44
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
        os.system("python3 setup_identity.py")
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
    run_hero_ops(api)

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

def run_map_scan(api: TravianAPI):
    """Run map scanning operations."""
    print("\n🗺️ Map Scanning")
    print("[1] Scan for unoccupied oases")
    print("[2] View latest scan results")
    print("[3] Back to main menu")
    
    choice = input("\nSelect an option: ").strip()
    
    if choice == "1":
        from features.map_scanning.scan_map import scan_map_for_oases
        print("\n🔍 Starting map scan...")
        scan_map_for_oases(api)
        print("✅ Map scan complete!")
    elif choice == "2":
        from core.database_helpers import load_latest_unoccupied_oases
        villages = load_villages_from_identity()
        if not villages:
            print("❌ No villages found in identity. Exiting.")
            return
        
        print("\nAvailable villages:")
        for idx, v in enumerate(villages):
            print(f"[{idx}] {v['village_name']} at ({v['x']}, {v['y']})")
        
        try:
            village_idx = int(input("\nSelect village to view oases for: ").strip())
            selected_village = villages[village_idx]
            oases = load_latest_unoccupied_oases(f"({selected_village['x']}_{selected_village['y']})")
            
            if not oases:
                print("❌ No oases found in latest scan.")
                return
            
            print(f"\n📊 Found {len(oases)} unoccupied oases near {selected_village['village_name']}:")
            for coord_key, oasis_data in oases.items():
                x_str, y_str = coord_key.split("_")
                print(f"- Oasis at ({x_str}, {y_str})")
        except (ValueError, IndexError):
            print("❌ Invalid village selection.")
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice.")

def main():
    print("\n" + "="*40)
    print("🎮 TRAVIAN AUTOMATION LAUNCHER")
    print("="*40)
    
    print("\n🌾 FARM LIST:")
    print("1) Farm burst")
    print("2) Configure farm lists")
    print("3) Run farm from config")
    
    print("\n🏰 OASIS RAID:")
    print("4) Setup raid plan")
    print("5) Reset raid plan")
    print("6) Test raid (single village)")
    
    print("\n🤖 AUTOMATION:")
    print("7) 👑 FULL AUTO MODE 👑")
    print("   • Farm lists + Oasis raids")
    print("   • Multi-village loop")
    
    print("\n🗺️ MAP SCANNING:")
    print("8) Scan & View Oases")
    
    print("\n👤 ACCOUNT:")
    print("9) Hero Operations")
    print("10) Identity & Villages")
    
    print("\n" + "="*40)

    choice = input("\n👉 Select an option: ").strip()

    # Login first
    print("\n🔐 Logging into Travian...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    if choice == "1":
        run_one_farm_list_burst(api)
    elif choice == "2":
        from features.farm_lists.manage_farm_lists import update_farm_lists
        update_farm_lists(api, server_url)
    elif choice == "3":
        from features.farm_lists.farm_list_raider import run_farm_list_raids
        villages = load_villages_from_identity()
        if not villages:
            print("❌ No villages found in identity. Exiting.")
            return
        for village in villages:
            run_farm_list_raids(api, server_url, village["village_id"])
    elif choice == "4":
        setup_interactive_raid_plan(api, server_url)
    elif choice == "5":
        reset_saved_raid_plan()
    elif choice == "6":
        print("\n🎯 Starting single-village oasis raiding (testing mode)...")
        run_raid_planner(api, server_url, multi_village=False, run_farm_lists=False)
    elif choice == "7":
        print("\n🤖 Starting full automation mode...")
        # Ask for delay
        while True:
            try:
                delay_input = input("\nWould you like to delay the start? (y/N): ").strip().lower()
                if delay_input == 'y':
                    delay_minutes = int(input("Enter delay in minutes: "))
                    if delay_minutes > 0:
                        print(f"\n⏳ Waiting {delay_minutes} minutes before starting...")
                        time.sleep(delay_minutes * 60)
                        break
                    else:
                        print("Delay must be greater than 0 minutes.")
                else:
                    print("\nStarting immediately...")
                    break
            except ValueError:
                print("Please enter a valid number of minutes.")

        while True:
            try:
                print(f"\n⏳ Starting cycle at {time.strftime('%H:%M:%S')}")
                run_raid_planner(api, server_url, reuse_saved=True, multi_village=True, run_farm_lists=True)
                
                # Print hero status summary at the end of the cycle
                hero_manager = HeroManager(api)
                status = hero_manager.fetch_hero_status()
                if status:
                    print_hero_status_summary(status)
                else:
                    print("❌ Could not fetch hero status summary.")
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
    elif choice == "8":
        run_map_scan(api)
    elif choice == "9":
        run_hero_operations(api)
    elif choice == "10":
        handle_identity_management()
    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
