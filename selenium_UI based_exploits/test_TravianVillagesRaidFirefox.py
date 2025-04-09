# Modified from Selenium IDE export
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service as FirefoxService

class TestTravianvillagesraid():
    def setup_method(self, method):
        load_dotenv()
        self.driver = webdriver.Firefox(service=FirefoxService())
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_travianvillagesraid(self):
        d = self.driver
        actions = ActionChains(d)
        print("hello hello hello")

        d.get("https://www.travian.com/international#loginLobby")
        d.set_window_size(1024, 768)

        # Login
        WebDriverWait(d, 15).until(lambda x: x.find_element(By.NAME, "email")).send_keys(os.getenv("TRAVIAN_EMAIL"))
        WebDriverWait(d, 15).until(lambda x: x.find_element(By.NAME, "password")).send_keys(os.getenv("TRAVIAN_PASSWORD"))
        d.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(5)  # Adjust if login is slow

        # --- Continue original flow ---
        d.find_element(By.CSS_SELECTOR, "div:nth-child(1) > span").click()
        actions.move_to_element(d.find_element(By.CSS_SELECTOR, ".a31 path")).perform()
        actions.move_to_element(d.find_element(By.CSS_SELECTOR, ".g16 > .hoverShape > path")).perform()
        d.find_element(By.CSS_SELECTOR, ".g16 path:nth-child(2)").click()

        d.find_element(By.ID, "button67e04c1e282ff").click()
        d.find_element(By.CSS_SELECTOR, ".dropContainer:nth-child(2) .farmListHeader > .textButtonV2 > div").click()
        d.find_element(By.ID, "button67e04c209a011").click()

        print("✅ Test finished executing. Browser should be visible.")
        input("Press Enter to quit browser...")