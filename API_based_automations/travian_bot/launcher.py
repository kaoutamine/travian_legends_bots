import time
import random
from identity_handling.login import login
from core.travian_api import TravianAPI
from oasis_raiding_from_scan_list_main import run_raid_planner
from raid_list_main import run_one_farm_list_burst

# === CONFIG ===
WAIT_BETWEEN_CYCLES_MINUTES = 50  # base time between cycles
JITTER_MINUTES = 5                # random jitter +/- 5 min

def main():
    print("""
🛡️ Travian Automation Launcher
[1] Run one farm list burst + one raid planner
[2] Run farm list + raid planner in infinite safe loop
""")
    choice = input("Select an option: ").strip()

    print("\n🔐 Logging into Travian...")
    session, server_url = login(server_selection=1, interactive=False)
    api = TravianAPI(session, server_url)

    if choice == "1":
        print("\n🚀 Starting one safe cycle (farm + raid)...\n")
        run_one_farm_list_burst(api)
        run_raid_planner(
            api=api,
            server_url=server_url,
            reuse_saved=True,
            enable_hero_raiding=True,
            interactive=False
        )

    elif choice == "2":
        print("\n🚀 Starting infinite safe cycling (farm + raid)...\n")

        while True:
            start_time = time.strftime("%H:%M:%S")
            print(f"\n⏳ Starting cycle at {start_time}")

            run_one_farm_list_burst(api)
            run_raid_planner(
                api=api,
                server_url=server_url,
                reuse_saved=True,
                enable_hero_raiding=True,
                interactive=False
            )

            # Calculate wait time with jitter
            jitter = random.randint(-JITTER_MINUTES, JITTER_MINUTES)
            total_wait_minutes = WAIT_BETWEEN_CYCLES_MINUTES + jitter
            print(f"✅ Cycle complete. Waiting {total_wait_minutes} minutes (base {WAIT_BETWEEN_CYCLES_MINUTES} ± {JITTER_MINUTES})...\n")

            time.sleep(total_wait_minutes * 60)

    else:
        print("❌ Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
