import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestTravianoasisraid():
    def setup_method(self, method):
        load_dotenv()
        options = Options()
        # Uncomment to run headless
        # options.add_argument("--headless=new")
        options.add_argument("start-maximized")

        service = Service("/usr/local/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_travianoasisraid(self):
        d = self.driver
        actions = ActionChains(d)

        d.get("https://www.travian.com/de")
        d.set_window_size(1024, 768)

        d.find_element(By.NAME, "name").click()
        d.find_element(By.NAME, "name").send_keys(os.getenv("TRAVIAN_EMAIL"))
        d.find_element(By.NAME, "password").click()
        d.find_element(By.NAME, "password").send_keys(os.getenv("TRAVIAN_PASSWORD"))
        d.find_element(By.CSS_SELECTOR, ".withLoadingIndicator > div").click()
        time.sleep(3)

        d.find_element(By.CSS_SELECTOR, "section").click()
        d.find_element(By.CSS_SELECTOR, ".gameworldButton").click()
        actions.move_to_element(d.find_element(By.CSS_SELECTOR, ".gameworldButton")).perform()
        actions.move_to_element(d.find_element(By.CSS_SELECTOR, "body"), 0, 0).perform()
        d.find_element(By.CSS_SELECTOR, ".action div").click()

        elements = [
            ".buildingSlot2 > .labelLayer",
            ".buildingSlot6:nth-child(6)",
            ".buildingSlot3:nth-child(3)",
            ".buildingSlot2:nth-child(2)",
            ".buildingSlot9 > .labelLayer",
            ".map",
            ".buildingView",
            ".a31 path",
            "#villageContent"
        ]
        for selector in elements:
            el = d.find_element(By.CSS_SELECTOR, selector)
            actions.move_to_element(el).perform()
            actions.move_to_element(d.find_element(By.CSS_SELECTOR, "body"), 0, 0).perform()

        d.find_element(By.CSS_SELECTOR, ".buildingView").click()
        actions.click_and_hold(d.find_element(By.ID, "villageContent")).perform()
        actions.release().perform()
        d.find_element(By.ID, "villageContent").click()

        el = d.find_element(By.CSS_SELECTOR, ".aid39 > .labelLayer")
        actions.move_to_element(el).click().perform()

        d.find_element(By.ID, "button67df3e2481b72").click()
        d.find_element(By.NAME, "selectAll").click()

        d.execute_script("window.scrollTo(0,918)")
        d.find_element(By.CSS_SELECTOR, ".dropContainer:nth-child(2) .farmListFooter div").click()
        d.find_element(By.CSS_SELECTOR, ".dropContainer:nth-child(3) tfoot input").click()
        d.find_element(By.CSS_SELECTOR, ".dropContainer:nth-child(3) .farmListFooter div").click()

        input("✅ Done. Press Enter to close...")

# Run directly
if __name__ == "__main__":
    test = TestTravianoasisraid()
    test.setup_method(None)
    try:
        test.test_travianoasisraid()
    finally:
        test.teardown_method(None)
