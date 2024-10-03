import time
import os
import pickle
import csv
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException,NoSuchElementException

with open('linkedin_scraper/config.json') as config_file:
    config = json.load(config_file)

# LinkedIn credentials
LINKEDIN_USERNAME = config['username']
LINKEDIN_PASSWORD = config['password']

# Output files
CONNECTIONS_FILE = config['connections_file']
COOKIES_FILE = config['cookies_file']
OUTPUT_FILE = config['output_file']
LOG_FILE = config['log_file']

# Delay between actions
DELAY = config['delay']

# Setup Chrome options for Selenium
options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-extensions')

# Add delay between actions to avoid detection

def log_action(action):
    """Logs actions in a log file."""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")

def load_cookies(driver):
    """Loads cookies if they exist."""
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

def save_cookies(driver):
    """Saves cookies for future sessions."""
    with open(COOKIES_FILE, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def login(driver):
    """Logs into LinkedIn."""
    driver.get("https://www.linkedin.com/login")
    driver.find_element(By.ID, 'username').send_keys(LINKEDIN_USERNAME)
    driver.find_element(By.ID, 'password').send_keys(LINKEDIN_PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    log_action("Logged in")

    # Handle 2FA if necessary
    try:
        wait = WebDriverWait(driver, 10)
        otp_input = wait.until(EC.presence_of_element_located((By.ID, "input__email_verification_pin"))) # //input[contains(@name, 'otp')]
        otp_code = input("Enter your OTP code: ")
        otp_input.send_keys(otp_code)
        driver.find_element(By.ID, "email-pin-submit-button").click()
        log_action("2FA completed")
    except TimeoutException:
        log_action("2FA not required")

def scrape_profile(driver, profile_url):
    """Scrapes a LinkedIn profile."""
    driver.get(profile_url)
    log_action(f"Scraping profile {profile_url}")

    # Add delays to avoid detection
    time.sleep(DELAY)

    top_panel = driver.find_element(By.XPATH, "//*[@class='mt2 relative']")
    name = top_panel.find_element(By.TAG_NAME, "h1").text
    location = top_panel.find_element(By.XPATH, "//*[@class='text-body-small inline t-black--light break-words']").text

    try:
        about = driver.find_element(By.ID,"about").find_element(By.XPATH,"..").find_element(By.CLASS_NAME,"display-flex").text
    except NoSuchElementException :
        about=None

    try:
        open_to_work = "#OPEN_TO_WORK" in driver.find_element(By.CLASS_NAME,"pv-top-card-profile-picture").find_element(By.TAG_NAME,"img").get_attribute("title")
    except:
        open_to_work =  False

    profile_data ={
        'name':name,
        'location':location,
        'about':about,
        'is_open_to_work':open_to_work
    }
    return profile_data

def append_to_csv(data, filename):
    """Appends scraped profile data to a CSV file."""
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def save_to_excel(data_list):
    """Saves all scraped data to an Excel file."""
    df = pd.DataFrame(data_list)
    df.to_excel(OUTPUT_FILE, index=False)
    log_action(f"Saved data to {OUTPUT_FILE}")

def scrape_connections(driver):
    """Scrapes all connections."""
    if os.path.exists(CONNECTIONS_FILE):
        with open(CONNECTIONS_FILE, 'r') as file:
            scraped_profiles = [line.strip() for line in file.readlines()]
    else:
        scraped_profiles = []

    connections = [
        # Add your list of profile URLs here for scraping
        'https://www.linkedin.com/in/sample-profile-1/',
        'https://www.linkedin.com/in/sample-profile-2/'
    ]

    scraped_data = []
    for profile in connections:
        if profile not in scraped_profiles:
            profile_data = scrape_profile(driver, profile)
            scraped_data.append(profile_data)
            append_to_csv({"URL": profile}, CONNECTIONS_FILE)
            log_action(f"Profile scraped: {profile}")
            time.sleep(DELAY)

    save_to_excel(scraped_data)

def main():
    # Setup WebDriver
    driver = webdriver.Chrome(options=options)

    try:
        driver.get('https://www.linkedin.com')
        load_cookies(driver)

        if "feed" not in driver.current_url:
            login(driver)
            save_cookies(driver)

        scrape_connections(driver)
    except (WebDriverException, TimeoutException) as e:
        log_action(f"Error: {str(e)}")
        if "internet" in str(e).lower():
            while True:
                try:
                    time.sleep(60)  # Wait for internet reconnection
                    driver.get("https://www.linkedin.com")
                    break
                except Exception:
                    continue
        else:
            raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()


