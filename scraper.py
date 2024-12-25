from seleniumwire import webdriver
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

proxies = {
    "http": 'http://'+os.environ['USER']+':'+os.environ['PASS']+'@'+os.environ['PROXY'],
    "https": 'http://'+os.environ['USER']+':'+os.environ['PASS']+'@'+os.environ['PROXY']
}


# Function to scrape top 5 trending topics from Twitter


def scrape_trending_topics():
    # Set up the Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(
        # seleniumwire_options={'proxy': proxies},
        options=chrome_options
    )

    try:

        # Open X.com (Twitter)
        driver.get(url=os.environ['BASE_URL'])

        driver.maximize_window()

        # Wait for the login page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='text']"))
        ).send_keys(os.environ['USERNAME'])

        # Click the next button
        next_button = driver.find_element(
            By.XPATH, "//span[contains(text(), 'Next')]")

        next_button.click()

        time.sleep(2)

        # Wait for the password field to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='password']"))
        ).send_keys(os.environ['PASSWORD'])

        time.sleep(2)

        # Click the login button
        login_button = driver.find_element(
            By.XPATH, "//span[contains(text(), 'Log in')]").click()

        # Wait for the main page to load
        time.sleep(5)

        # Navigate to the explore page to fetch trends
        driver.get("https://x.com/explore")

        # Wait for the trending topics section to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//span[contains(text(), 'Trending')]"))
        )

        time.sleep(5)

        # Get the trending topics
        trending_topics = driver.find_elements(
            By.XPATH, "//span[contains(text(), '#')]")

        trending_topics_list = []

        for topic in trending_topics[:5]:
            trending_topics_list.append(topic.text)

        return trending_topics_list

    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        driver.quit()


# generate unique id for each scrape


def generate_unique_id():
    return datetime.now().strftime("%Y%m%d%H%M%S")


# Function to save data to MongoDB


def save_data_to_mongo(data):

    # Connect to MongoDB
    client = MongoClient(os.environ['MONGO_URI'])
    db = client['twitter_scraper']
    collection = db['trends_scraped']

    # Insert data
    collection.insert_one(data)

# Function to run the scraper


def run_scraper():
    try:
        # Scrape trending topics from Twitter
        trends = scrape_trending_topics()

        # Get the IP address of the client
        ip_address = requests.get(
            'https://api64.ipify.org?format=json').json()['ip']

        # Get the current date and time
        datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Data to return in JSON format
        result = {
            'id': generate_unique_id(),
            'datetime': datetime_now,
            'trends': trends,
            'ip_address': ip_address
        }

        # Save the data to MongoDB
        save_data_to_mongo(result)

        return result

    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == '__main__':

    print(run_scraper())
