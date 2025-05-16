import time
import random
import threading
from core.hero_manager import HeroManager
from core.database_helpers import load_latest_unoccupied_oases
from core.hero_runner import try_send_hero_to_oasis
from identity_handling.identity_helper import load_villages_from_identity

# Create a lock for printing
print_lock = threading.Lock()

def safe_print(message):
    """Thread-safe printing function."""
    with print_lock:
        print(message)

def run_hero_raiding_thread(api):
    """Background thread for adaptive hero raiding."""
    safe_print("[HeroRaider] Hero raiding thread started.")
    safe_print("[HeroRaider] Thread ID: " + str(threading.get_ident()))
    
    while True:
        try:
            safe_print("[HeroRaider] Checking hero status...")
            hero_manager = HeroManager(api)
            status = hero_manager.fetch_hero_status()
            
            if not status:
                safe_print("[HeroRaider] ❌ Failed to fetch hero status")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            if not status.is_present:
                safe_print("[HeroRaider] ❌ Hero is not present.")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            if status.health is not None and status.health < 20:
                safe_print(f"[HeroRaider] ⚠️ Hero health too low ({status.health}%)")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            if status.is_on_mission:
                safe_print("[HeroRaider] ❌ Hero is on a mission.")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            if not status.current_village_id:
                safe_print("[HeroRaider] ❌ No current village information.")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            safe_print("[HeroRaider] Loading villages from identity...")
            villages = load_villages_from_identity()
            current_village = None
            for village in villages:
                if str(village["village_id"]) == str(status.current_village_id):
                    current_village = village
                    break

            if not current_village:
                safe_print(f"[HeroRaider] ⚠️ Hero is in village {status.current_village_id} which is not in your identity.")
                safe_print("[HeroRaider] Available villages in identity:")
                for v in villages:
                    safe_print(f"[HeroRaider] - {v['village_name']} (ID: {v['village_id']})")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            # Debug: Print hero status and current village details
            safe_print(f"[HeroRaider] DEBUG: Hero status: {status.__dict__}")
            safe_print(f"[HeroRaider] DEBUG: Current village: {current_village}")

            safe_print("[HeroRaider] Loading unoccupied oases...")
            oases = load_latest_unoccupied_oases(f"({current_village['x']}_{current_village['y']})")
            if not oases:
                safe_print("[HeroRaider] ❌ No unoccupied oases found in latest scan.")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            safe_print("[HeroRaider] Finding suitable oases...")
            # Find suitable oases (using the latest logic from debug_hero_raiding.py)
            suitable = []
            for coord_key, oasis_data in oases.items():
                x_str, y_str = coord_key.split("_")
                oasis = {"x": int(x_str), "y": int(y_str)}
                distance = abs(current_village['x'] - oasis['x']) + abs(current_village['y'] - oasis['y'])
                if distance >= 20:
                    continue
                oasis_info = api.get_oasis_info(oasis["x"], oasis["y"])
                if oasis_info["is_occupied"]:
                    continue
                animal_info = oasis_info["animals"]
                power = oasis_info["attack_power"]
                max_power = 2000
                if distance < 3:
                    max_power = 500
                elif distance < 6:
                    max_power = 1000
                if 50 <= power <= max_power:
                    liking_rating = sum(count for _, count in animal_info)
                    efficiency = liking_rating / distance
                    suitable.append((oasis, power, distance, liking_rating, efficiency))
            suitable.sort(key=lambda x: x[4], reverse=True)

            if not suitable:
                safe_print("[HeroRaider] ❌ No suitable oases found (based on power and distance thresholds)")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            best_oasis = suitable[0][0]
            safe_print(f"[HeroRaider] Sending hero to oasis at ({best_oasis['x']}, {best_oasis['y']})")
            if try_send_hero_to_oasis(api, current_village, best_oasis):
                safe_print(f"[HeroRaider] ✅ Hero sent to oasis at ({best_oasis['x']}, {best_oasis['y']})")
                distance = suitable[0][2]
                return_time = (distance / 14) * 3600
                safe_print(f"[HeroRaider] Hero will return in {return_time / 3600:.2f} hours.")
                time.sleep(return_time + random.randint(60, 120))
            else:
                safe_print("[HeroRaider] ❌ Failed to send hero.")
                wait_time = 300 + random.randint(-30, 30)
                safe_print(f"[HeroRaider] Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        except Exception as e:
            safe_print(f"[HeroRaider] Exception: {e}")
            safe_print("[HeroRaider] Waiting 300 seconds before retry...")
            time.sleep(300) 