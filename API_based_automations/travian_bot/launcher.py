import time
import random
from identity_handling.login import login
from core.travian_api import TravianAPI
from oasis_raiding_from_scan_list_main import run_raid_planner
from raid_list_main import run_one_farm_list_burst
from features.raiding.reset_raid_plan import reset_saved_raid_plan
from features.raiding.setup_interactive_plan import setup_interactive_raid_plan  # ✅ New import

# === CONFIG ===
WAIT_BETWEEN_CYCLES_MINUTES = 50
JITTER_MINUTES = 5
SERVER_SELECTION = 0  # 👈 update if needed

def main():
    print("""
🛡️ Travian Automation Launcher
[1] Run one farm list burst + one raid planner
[2] Run farm list + raid planner in infinite safe loop (with auto-recovery)
[3] Reset saved raid plan
[4] Setup new raid plan interactively
""")
    choice = input("Select an option: ").strip()

    if choice == "3":
        reset_saved_raid_plan(server_selection=SERVER_SELECTION)
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
