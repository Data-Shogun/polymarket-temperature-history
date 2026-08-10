from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time

STREAMLIT_URL_LIST = [
    "https://polymarket-temperature-history.streamlit.app/",
    "https://polymarket-temperature.streamlit.app/"
]

def get_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def process_url(driver, url):
    print(f"\nChecking: {url}")
    driver.get(url)

    wait = WebDriverWait(driver, 25)
    # Broader matching for the wake-up button text
    wake_button_xpath = "//button[contains(., 'get this app back up')]"

    try:
        button = wait.until(EC.element_to_be_clickable((By.XPATH, wake_button_xpath)))
        print("Wake-up button found. Clicking...")
        button.click()

        wait.until(EC.invisibility_of_element_located((By.XPATH, wake_button_xpath)))
        print("Button clicked. Keeping session open for container boot...")
        time.sleep(15)
        print("Wake-up request sent successfully! ✅")
        return

    except TimeoutException:
        print("Wake-up button not found. Checking if app UI is loaded...")

    # Fallback check: Verify if the main Streamlit container or root div rendered
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAppViewContainer'], .stApp, #root")))
        print("App is already awake and running ✅")
    except TimeoutException:
        print("App failed to load or wake up ❌")

def main():
    for url in STREAMLIT_URL_LIST:
        driver = get_driver()
        try:
            process_url(driver, url)
        except Exception as e:
            print(f"Error processing {url}: {e}")
        finally:
            driver.quit()
            print("Browser session closed.")

if __name__ == "__main__":
    main()