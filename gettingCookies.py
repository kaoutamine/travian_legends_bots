import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Setup
options = Options()
driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options)
driver.get("https://www.travian.com/international#loginLobby")

# Give yourself time to log in manually (or automate it before this part)
print("You have 60 seconds to log in manually...")
time.sleep(30)

# Save cookies
cookies = driver.get_cookies()
with open("travian_cookies.json", "w") as f:
    json.dump(cookies, f, indent=2)


print("Cookies saved ✅")
driver.quit()
