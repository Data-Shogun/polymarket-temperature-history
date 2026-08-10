from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import os

# STREAMLIT_URL = os.environ.get("STREAMLIT_APP_URL", "https://polymarket-temperature-history.streamlit.app/")
STREAMLIT_URL_LIST = ["https://polymarket-temperature-history.streamlit.app/", "https://polymarket-temperature.streamlit.app/"]

def main():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    # Standard User-Agent prevents headless blocking
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for STREAMLIT_URL in STREAMLIT_URL_LIST:
        try:
            driver.get(STREAMLIT_URL)
            print(f"Opened {STREAMLIT_URL}")

            wait = WebDriverWait(driver, 20)
            
            # Matches button content across child tags
            wake_button_xpath = "//button[contains(., 'Yes, get this app back up')]"
            
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, wake_button_xpath)))
                print("Wake-up button found. Clicking...")
                button.click()

                wait.until(EC.invisibility_of_element_located((By.XPATH, wake_button_xpath)))
                print("Button clicked. Keeping browser open for container boot...")
                
                # Pause to keep session alive while Streamlit initializes
                time.sleep(15)
                print("Wake-up request sent successfully! ✅")

            except TimeoutException:
                print("Wake-up button not found. Checking if app main UI is present...")
                # Verify actual Streamlit app container before declaring success
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAppViewContainer'], .stApp")))
                    print("App is already awake and running ✅")
                except TimeoutException:
                    print("App failed to load or wake up ❌")
                    # exit(1)
                    continue

        except Exception as e:
            print(f"Unexpected error: {e}")
            exit(1)
        finally:
            driver.quit()
            print("Script finished.")

if __name__ == "__main__":
    main()