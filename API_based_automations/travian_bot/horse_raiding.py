import requests
import time
import random
from datetime import datetime, timedelta

# === CONFIGURATION ===
FARM_LIST_ID = 48
TARGET_IDS = [
    844, 849, 1544, 882, 845, 842, 846, 1001,
    850, 1211, 851, 843, 1409, 1115, 883, 848,
    847, 853, 1410, 881, 1546, 1545, 1212, 852
]

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://ts4.x1.arabics.travian.com",
    "Referer": "https://ts4.x1.arabics.travian.com/build.php?id=39&gid=16&tt=99",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "X-Version": "135.12",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}

COOKIES = {
    "__cmpconsentx17155": "CQQXdzAQQXdzAAfSDBENBmFsAP_gAELAAAYgLENX_G__bXlv-T736ftkeY1f99h77sQxBgbJs-4FzLvW_JwX32E7NEz6tqYKmRIAu3TBIQNtHJjURVChaogVrTDsaEyUoTtKJ-BkiHMRY2dYCFxvm4tjeQCZ5vr_91d52T-t7dr-3dzyy5hnv3a9_-S1WJidKYetHfv8bBOT-_Ie9_x-_4v4_N7pE2-eS1t_tWvt739-4tv_9__99_77_f7_____3_-_X__f__________wWFAJMNCogjLIkBCJQMIIEAKgrCAigQBAAAkDRAQAmDApyBgAusJEAIAUAAwQAgABBgACAAASABCIAKACgQAAQCBQABgAQDAQAMDAAGACwEAgABAdAxTAggECwASMyKDTAlAASCAlsqEEgCBBXCEIs8AgAREwUAAAIABQAAIDwWAxJICViQQBcQTQAAEAAAQQIFCKTswBBAGbLUXgyfRlaYFg-YJmlMAyAIgjIyTYhN-0w8AA",
    "__cmpcccx17155": "aCQQXen0gAqWFh3PmzD3nPt3jTGMHvVqYLLDDg8Ixlqa1WtMsGNMBmaWDI0Go1YLQ0hpMDJgvK8sLIYRpBoWZYZYGFoGmBNYxMmrLGsSysjQxmDFoyGVkGExGU0yYcXowamazNWatA155DGV2zDLTKxrDDFgJlRikZWADIYlqy5eatYnE8ymaBqwasGZMmRqyYGhmrMGLk8waGAwGOvWGBjTQ1GMqtZgEKUhZCaSDKqsRQoNUpGCIDQUqGA",
    "active_rallypoint_sub_filters_2": "4,4",
    "active_rallypoint_sub_filters_1": "1,1",
    "JWT": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJKVGZIY0VYT3NuWmFZMUdMbTFaNzVQTHNMMWhJRjRVaSIsImF1ZCI6IjdiNzVlMDAwLTIwM2EtMTFmMC02NjA0LTAxMDAwMDAwMDAxYSIsImV4cCI6MTc0NTU0NDE1NiwicHJvcGVydGllcyI6eyJoYXNoIjoiZjAzMGExMDBhMTAwYTEwMEN5Nkx4VE9zNHNBZ1A5dDQiLCJtb2JpbGVPcHRpbWl6YXRpb25zIjp0cnVlLCJsb2dpbklkIjoxMDc5NywibGFuZ3VhZ2UiOiJlbi1VUyIsInZpbGxhZ2VQZXJzcGVjdGl2ZSI6InBlcnNwZWN0aXZlQnVpbGRpbmdzIiwicHciOiJHb3RCNTNHZllvdFgxa3FoWnB4eVF3M3ZLQ0VrbDZLNCIsImRpZCI6MTk5ODN9fQ.Nxhg7ha1H-ALr9gw8ac99LCfujfWaOrxyd8b9rdsSdKWZl0RrMjJtnTTeOaar7E2xiZuFSMTGf-3pQ7lGQ5DT63sIKLo6uUaOhXGiWB56YT8fTyW8xL6SSEMgrYr0-1_k77822TFxMCFOjTcfQBiLVy0fr0uUTCMym_NhQ9CJhuZKsfyQF9M4Ihi0SkD369CrgQDUgXvi7SMVZMduCGrYzVVoxxgwon-K_7uj2P7L7ovut4m4o8UDdEanZBEgcc4AqrgAyPkiMnjfeDIZS5JqGWUUdVdkt7c1PolhhKzGOh74TtS3Io1yqdJIciLNnmOhKaw04LOF6wbDGK0Tcobcg"
}

URL = "https://ts4.x1.arabics.travian.com/api/v1/farm-list/send"

# === FUNCTIONS ===

def create_payload():
    return {
        "action": "farmList",
        "lists": [{
            "id": FARM_LIST_ID,
            "targets": TARGET_IDS
        }]
    }

def send_farm_list():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending farm list...")
    try:
        response = requests.post(URL, json=create_payload(), headers=HEADERS, cookies=COOKIES)
        print(f"→ Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("→ Success:", result.get("lists", [{}])[0].get("error", "OK"))
        else:
            print("→ Error response:", response.text)
    except Exception as e:
        print("→ Request failed:", e)

def run_until_630():
    end_time = datetime.now().replace(hour=6, minute=30, second=0, microsecond=0)
    if datetime.now() > end_time:
        print("▶ It’s already past 6:30 AM. Exiting.")
        return

    while True:
        now = datetime.now()
        if now >= end_time:
            print("⏹️  It's 6:30 AM. Stopping.")
            break

        send_farm_list()

        wait_minutes = random.randint(40, 50)
        wait_seconds = random.randint(0, 59)
        total_wait = wait_minutes * 60 + wait_seconds

        next_time = now + timedelta(seconds=total_wait)
        if next_time >= end_time:
            print(f"▶ Next cycle would be after 6:30 AM. Stopping now.")
            break

        print(f"→ Next run in {wait_minutes} min {wait_seconds} sec (at {next_time.strftime('%H:%M:%S')})\n")
        time.sleep(total_wait)

# === RUN SCRIPT ===
if __name__ == "__main__":
    run_until_630()
