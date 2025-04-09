import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestTravianvillagesraid():
    def setup_method(self, method):
        load_dotenv()
        options = Options()
        # Comment this if you want to see the browser
        # options.add_argument("--headless=new")
        options.add_argument("start-maximized")
        self.driver = webdriver.Chrome(service=ChromeService("/usr/local/bin/chromedriver"), options=options)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_travianvillagesraid(self):
        d = self.driver
        wait = WebDriverWait(d, 15)
        actions = ActionChains(d)

        # Go to login page
        d.get("https://www.travian.com/international#loginLobby")
        wait = WebDriverWait(d, 15)

        # Click login button to open modal
        login_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "js-login-button")))
        login_btn.click()

        # Wait for modal to load
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.click()
        email_field.send_keys(os.getenv("TRAVIAN_EMAIL"))

        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.click()
        password_field.send_keys(os.getenv("TRAVIAN_PASSWORD"))

        # Submit the form
        submit_btn = d.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()


        # Wait for login to finish
        time.sleep(5)

        # Start your raid flow (copy-pasted from your original logic)
        d.find_element(By.CSS_SELECTOR, "div:nth-child(1) > span").click()
        actions.move_to_element(d.find_element(By.CSS_SELECTOR, ".a31 path")).perform()
        actions.move_to_element(d.find_element(By.CSS_SELECTOR, ".g16 > .hoverShape > path")).perform()
        d.find_element(By.CSS_SELECTOR, ".g16 path:nth-child(2)").click()

        d.find_element(By.ID, "button67e04c1e282ff").click()
        d.find_element(By.CSS_SELECTOR, ".dropContainer:nth-child(2) .farmListHeader > .textButtonV2 > div").click()
        d.find_element(By.ID, "button67e04c209a011").click()

        print("✅ Test finished executing.")
        input("Press Enter to quit browser...")

# Run directly
if __name__ == "__main__":
    test = TestTravianvillagesraid()
    test.setup_method(None)
    try:
        test.test_travianvillagesraid()
    finally:
        test.teardown_method(None)
