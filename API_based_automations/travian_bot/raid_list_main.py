import time
import random
from datetime import datetime, timedelta
from identity_handling.login import login
from core.travian_api import TravianAPI

# === CONFIGURATION ===
LIST_DELAYS_MINUTES = {
    190: (60, 1),  # (base delay in minutes, number of sends per burst)
}

RANDOM_JITTER_MINUTES = 3  # +/- jitter in minutes
SLEEP_INTERVAL = 14        # seconds between checks
STOP_HOUR = 9              # Stop at 9AM
STOP_MINUTE = 0

# === FUNCTIONS ===
def send_farm_list(api, list_id):
    payload = {
        "action": "farmList",
        "lists": [{"id": list_id}]
    }
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛫 Sending farm list: {list_id}")
    response = api.session.post(f"{api.server_url}/api/v1/farm-list/send", json=payload)

    if response.status_code == 200:
        print("✅ Farm list sent successfully.")
        return True
    elif response.status_code in (401, 403):
        print("⚠️ Session expired! Need to re-login.")
        return False
    else:
        print(f"❌ Error sending farm list: {response.status_code}", response.text)
        return True

def calculate_next_delay(base_minutes):
    jitter = random.randint(-RANDOM_JITTER_MINUTES, RANDOM_JITTER_MINUTES)
    return (base_minutes + jitter) * 60  # seconds

def safe_relogin():
    original_input = __builtins__.input
    try:
        __builtins__.input = lambda prompt='': '0'
        session, server_url = login()
        api = TravianAPI(session, server_url)
        print("🔄 Re-login successful.")
        return api
    finally:
        __builtins__.input = original_input

def run_farmlist_runner():
    print("[+] Auto logging in (feeding 1)...")
    original_input = __builtins__.input
    try:
        __builtins__.input = lambda prompt='': '1'
        session, server_url = login()
        api = TravianAPI(session, server_url)
    finally:
        __builtins__.input = original_input

    # Set stop time properly (even across midnight)
    end_time = datetime.now().replace(hour=STOP_HOUR, minute=STOP_MINUTE, second=0, microsecond=0)
    if end_time <= datetime.now():
        end_time += timedelta(days=1)

    print(f"▶ Will stop at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    next_send_times = {}
    now = datetime.now()
    for list_id, (base_delay, burst_count) in LIST_DELAYS_MINUTES.items():
        next_send_times[list_id] = now  # Start immediately

    while True:
        now = datetime.now()

        if now >= end_time:
            print("⏹️ It's 9:00 AM. Stopping.")
            break

        due_lists = [list_id for list_id, send_time in next_send_times.items() if now >= send_time]

        if not due_lists:
            next_time = min(next_send_times.values())
            sleep_seconds = (next_time - now).total_seconds()
            if sleep_seconds > 0:
                time.sleep(min(sleep_seconds, SLEEP_INTERVAL))
            continue

        for list_id in due_lists:
            base_delay, burst_count = LIST_DELAYS_MINUTES[list_id]

            for i in range(burst_count):
                success = send_farm_list(api, list_id)
                if not success:
                    api = safe_relogin()
                    success = send_farm_list(api, list_id)
                    if not success:
                        print(f"❌ Failed again after relogin for list {list_id}. Will retry later.")
                        next_send_times[list_id] = now + timedelta(minutes=1)
                        break  # Break out of burst sends
                if i < burst_count - 1:
                    time.sleep(2)  # Short pause between sends in a burst

            delay_seconds = calculate_next_delay(base_delay)
            next_send_times[list_id] = now + timedelta(seconds=delay_seconds)
            print(f"⏩ Next send for list {list_id} scheduled at {next_send_times[list_id].strftime('%H:%M:%S')}\n")

def run_one_farm_list_burst(api):
    now = datetime.now()

    for list_id, (base_delay, burst_count) in LIST_DELAYS_MINUTES.items():
        for i in range(burst_count):
            success = send_farm_list(api, list_id)
            if not success:
                api = safe_relogin()
                send_farm_list(api, list_id)
            if i < burst_count - 1:
                time.sleep(2)  # short pause between bursts

    print("✅ Finished one farm list burst.")


# === MAIN ===

if __name__ == "__main__":
    run_farmlist_runner()
