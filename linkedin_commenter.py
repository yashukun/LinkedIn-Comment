import requests
import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import random
import re
from typing import List, Optional
import caption_to_comment
# Load environment variables from .env file
load_dotenv()

# Placeholders for your LinkedIn and OpenAI API credentials
LINKEDIN_EMAIL = os.environ.get('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASSWORD', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
HuggingFACE_API_KEY = os.environ.get('HuggingFACE_API_KEY', '')


# LinkedIn profile URLs (placeholders)
LINKEDIN_PROFILE_URLS = [
    'jadonharsh',
    'arpit-rajpoot-a48b2a246'
]

# OpenAI API endpoint
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

# Output CSV file
OUTPUT_CSV = 'linkedin_comments.csv'


def linkedin_login(driver):
    driver.get('https://www.linkedin.com/login')
    time.sleep(2)
    email_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')
    email_input.send_keys(LINKEDIN_EMAIL)
    password_input.send_keys(LINKEDIN_PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(3)


def fetch_latest_post_selenium(driver, profile_url):
    driver.get(profile_url)
    time.sleep(3000)
    try:
        # Try to find the first post in the feed
        post = driver.find_element(
            By.CSS_SELECTOR, 'ul.display-flex.flex-wrap.list-style-none.justify-center > li:first-child')

        post_text = post.text.strip()
        # button click

        # ...existing code...

        three_dots = driver.find_element(
            By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/div/section/div[2]/div/div/div[1]/ul/li[1]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div/button"
        )
        time.sleep(3)
        three_dots.click()

        time.sleep(2)
        copy_linkBtn = driver.find_element(
            By.XPATH, "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/div/section/div[2]/div/div/div[1]/ul/li[1]/div/div/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div/div/div/ul/li[2]"
        )
        copy_linkBtn.click()
        time.sleep(3)

        post_link_elem = driver.find_element(
            By.XPATH, "/html/body/div[1]/section/div/div[1]/div/p/a")
        post_link = post_link_elem.get_attribute('href')
        # Get the post link (click on the timestamp or similar element)

        return post_text, post_link
    except NoSuchElementException:
        return None, None


def generate_comment(post_text):

    if not OPENAI_API_KEY:
        generator = caption_to_comment.LinkedInCommentGenerator()
        return generator.generate_linkedin_comment(
            f"LinkedIn post: '{post_text}'\n\nComment that amplifies the core message in a fresh way:"
        )
    else:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are a professional LinkedIn user.'},
                {'role': 'user', 'content': f'Write a small and elegant comment for this LinkedIn post: "{post_text}"'},
            ],
            'max_tokens': 60,
            'temperature': 0.7,
        }
        try:
            response = requests.post(
                OPENAI_API_URL, headers=headers, json=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                print(
                    f"OpenAI API error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            print(f"OpenAI API request failed: {e}")
        return ''


def main():
    # Set up Selenium WebDriver (headless Chrome)
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Failed to start Chrome WebDriver: {e}")
        return
    try:
        linkedin_login(driver)
        results = []
        for profile_url in LINKEDIN_PROFILE_URLS:
            try:
                post_text, post_link = fetch_latest_post_selenium(
                    driver, f'https://www.linkedin.com/in/{profile_url}/recent-activity/all/')
                print(f"Fetched post_text: {post_text}")
                print(f"Fetched post_link: {post_link}")
                if post_text and post_link:
                    comment = generate_comment(post_text)
                    print(f"Generated comment: {comment}")
                    results.append(
                        {'post_link': post_link, 'comment': comment})
                    print(f'Processed: {post_link}')
                else:
                    print(f'No post found for profile {profile_url}')
            except Exception as e:
                print(f"Error processing profile {profile_url}: {e}")
            time.sleep(2)
    finally:
        driver.quit()
    # Save to CSV
    print(f"Results to be written: {results}")
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                                    'post_link', 'comment'])
            writer.writeheader()
            for row in results:
                print(f"Writing row: {row}")
                writer.writerow(row)
        print(f'Comments saved to {OUTPUT_CSV}')
    except Exception as e:
        print(f"Failed to write CSV: {e}")


if __name__ == '__main__':
    main()
