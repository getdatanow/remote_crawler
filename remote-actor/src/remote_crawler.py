import requests
import json
import csv
import random
import time
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
# Load XPath configurations from config file
config = {
    "job_title": {
        "value": "Receptionist / Secretary",
        "xpath": "//h1[@class='sc-a6d70f3d-0 eNLOtt']"
    },
    "company_name": {
        "value": "RePrime group",
        "xpath": "//span[@class='sc-a6d70f3d-0 cWvlWe']"
    },
    "salary": {
        "value": "4 - 8 USD/hour",
        "xpath": "//span[@class='sc-a6d70f3d-0 ercMyp']"
    },
    "job_type": {
        "value": "Remote",
        "xpath": "//span[@class='sc-a6d70f3d-0 bXFXwo']"
    },
    "employment_type": {
        "value": "Full-time",
        "xpath": "//span[@class='sc-a6d70f3d-0 jvFZgN' and text()='Full-time']"
    },
    "description": {
        "value": "Looking for a secretary and receptionist, fluent English verbal and written skills are a must.",
        "xpath": "/html/body/div[2]/main/div/div/div/div[2]/div/div[2]/section/div/div/div"
    },
    "location": {
        "value": "Anywhere",
        "xpath": "//dt[.//span[contains(text(), 'Location')]]/following-sibling::dd//span"
    },
    "published_date": {
        "value": "Jul 12, 2024",
        "xpath": "//aside[contains(@class, 'sc-506be909-0')]//dt[contains(text(), 'Published on')]/following-sibling::dd/span[contains(@class, 'bXFXwo')]"
    }
}

# List of URLs to scrape
urls = [
    "https://remote.com/jobs/reprime-group-c1trkilo/receptionist-secretary-j19wdo6b"
]

# Headers with random user agents
ua = UserAgent()

# Function to fetch and parse a URL
def fetch_url(url):
    retries = 5
    for _ in range(retries):
        try:
            headers = {'User-Agent': ua.random}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            tree = html.fromstring(response.content)
            return tree
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            time.sleep(random.choice([4, 7]))  # Random sleep between retries
    return None

# Function to scrape job details from a parsed HTML tree
def scrape_job_details(tree):
    job_details = {}
    for key, value in config.items():
        try:
            element = tree.xpath(value['xpath'])
            job_details[key] = element[0].text_content().strip() if element else None
        except Exception as e:
            print(f"Error extracting {key}: {e}")
            job_details[key] = None
    return job_details

# Main function to handle threading and CSV output
def crawl(keyword="python"):
    urls = listing_page(keyword=keyword)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_url, urls))
    
    job_details_list = [scrape_job_details(tree) for tree in results if tree is not None]
    
    # Output to CSV
    return job_details_list
def listing_page(keyword):
    page_number = 0
    total_urls = list()
    while True:
        url = f'https://remote.com/jobs/all?query={keyword}&page={page_number}'
        response = fetch_url(url)
        items = response.xpath("//article/div//a/@href")

        if items:
            items = list(set(items))
            urls = [f'https://remote.com{item}' for item in items]
            total_urls.extend(urls)
        else:
            print("No urls found >>>")
            return
        if response.xpath("//a[@rel='next']/text()"):
            next_number = int(response.xpath("//a[@rel='next']/text()")[0])
            if next_number == page_number:
                break
            page_number = next_number
        else:
            break
    
    return total_urls
if __name__ == "__main__":
   print(crawl())
