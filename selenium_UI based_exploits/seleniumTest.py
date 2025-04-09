from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
# Comment this out to see the browser
# options.add_argument('--headless=new')

driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options)
driver.get("https://www.travian.com/international#loginLobby")




# Wait for the login form to load
email_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "email"))
)
password_field = driver.find_element(By.NAME, "password")


print("Available iframes:")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
for iframe in iframes:
    print("iframe name/id:", iframe.get_attribute("name"), iframe.get_attribute("id"))

    
# Fill in credentials
email_field.send_keys("your_email@example.com")
password_field.send_keys("your_password")

# Click the login button
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
login_button.click()

# Optional pause to observe
input("Press Enter to quit...")
driver.quit()
