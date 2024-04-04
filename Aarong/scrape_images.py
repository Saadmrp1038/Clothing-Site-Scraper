import json
import time
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import sys

# Set recursion limit to a higher value
sys.setrecursionlimit(10**6)

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)

def get_image_links(url):
    """Scrape image links from a given URL."""
    driver.get(url)
    
    time.sleep(2)
    
    html_content = driver.page_source

    soup = BeautifulSoup(html_content, "lxml")
    shaft_div = soup.find('div', class_='fotorama__stage__shaft')
    image_links = []

    if shaft_div:
        img_tags = shaft_div.find_all('img')
        image_links = [img['src'] for img in img_tags if 'src' in img.attrs]
    
    return image_links

def main():
    file_name = "Men_NEW ARRIVALS.json"
    # Load product links from JSON file
    with open(f'Aarong/{file_name}', 'r') as file:
        products = json.load(file)


    index = 0
    for product in products:
        image_links = get_image_links(product["Link"])
        product['image_links'] = image_links
        index += 1
        print(f"Product {index} done")
        
    #Write the updated data to a new JSON file
    with open(f'New_{file_name}', 'w') as file:
        json.dump(products, file, indent=4)

if __name__ == "__main__":
    main()
    driver.quit()
