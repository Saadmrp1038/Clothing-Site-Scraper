import time
import json
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from multiprocessing import Pool, Manager

import sys
# Set recursion limit to a higher value
sys.setrecursionlimit(10**6)

# Set Chrome options for headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# Variables
men_urls = [
    "https://www.apex4u.com/category/men-formal-shoes",
    "https://www.apex4u.com/category/men-casual-shoes",
    "https://www.apex4u.com/category/men-boots",
    "https://www.apex4u.com/category/men-canvas",
    "https://www.apex4u.com/category/men-sports-shoes",
    "https://www.apex4u.com/category/men-sandals",
    "https://www.apex4u.com/category/men-sports-sandals"
]

men_categories = [
    "Formal Shoes",
    "Casual Shoes",
    "Boots",
    "Canvas",
    "Sports Shoes",
    "Sandals",
    "Sports Sandals"
]

women_urls = [
    "https://www.apex4u.com/category/women-heels",
    "https://www.apex4u.com/category/women-sandals",
    "https://www.apex4u.com/category/women-sports-shoe",
    "https://www.apex4u.com/category/women-canvas",
    "https://www.apex4u.com/category/women-jutti",
    "https://www.apex4u.com/category/women-pumpies"
]

women_categories = [
    "Heels",
    "Sandals",
    "Sports Shoes",
    "Canvas",
    "Jutti",
    "Pumpies"
]

apex_link = "https://www.apex4u.com"

def fetch_webpage(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return None

def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    scroll_count = 0
    max_attempt = 3
    attempt = 0
    
    max_scroll = 5

    while attempt < max_attempt and scroll_count < max_scroll:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            attempt += 1
            print(f"Attempt Count: {attempt}")
            continue
        
        attempt = 0
        last_height = new_height
        
        scroll_count += 1
        print(f"Scoll Count: {scroll_count}")

def save_to_file(product_details_list, filename):
    with open(filename, "w") as file:
        json.dump(product_details_list, file, indent=4)

def scrape_product(link, category, count, lock):
    product_page = fetch_webpage(link)
    
    if not product_page:
        print(link)
        return
    
    product_soup = BeautifulSoup(product_page , "lxml")
    
    # Extracting product details
    product_name = product_soup.find('h3', class_='page-heading').text.strip()
    sku_and_style = product_soup.find('div', class_='mb-2 text-lg').text.strip()
    sku_and_style_split = sku_and_style.split(',')
    
    if len(sku_and_style_split) > 1:
        style = sku_and_style_split[1]
        
        style_split = style.split(': ')
    
        if len(style_split) > 1:
            style = style_split[1]
        else:
            style = None
    else:
        style = None
    
    price = product_soup.find('div', class_='price').text.strip()
    price = price.replace("\u09f3", "Tk ")
    image_urls = [img['src'] for img in product_soup.select('.magnifier-image')]

    # Extract description
    description_div = product_soup.find('div', class_='jsx-8b75180699e75b20 mx-6 text-justify md:mx-0 md:ml-6')
    
    if description_div:
        description = description_div.text.strip()
        
        # Extract features
        features_ul = description_div.find_next('ul')
        
        if features_ul:
            features = [li.text.strip() for li in features_ul.find_all('li')]
        else:
            features = None
    else:
        description = None
        features = None

   # Extract materials
    materials_section = product_soup.find('section', class_='jsx-1c470a0c6aa7181 group relative my-5 materials open')

    if materials_section:
        materials_div = materials_section.find('div', class_='jsx-8b75180699e75b20')
        
        if materials_div:
            materials = [p.text.strip() for p in materials_div.find_all('p')]
        else:
            materials = None
    else:
        materials = None
    
    specifications = {
        "Style" : style,
        "Features" : features,
        "Materials" : materials
    }

    # Create a dictionary to hold the product details
    product_details = {
        "Name": product_name,
        "Price": price,
        "Image_links": image_urls,
        "Link": link,
        "Description": description,
        "Specifications": specifications,
        "Company": "Apex",
        "Category": category,
        "Gender": "Male"   
    }
    
    # Increment count
    lock.acquire()
    count.value += 1
    lock.release()
    
    print(f"Product {count.value} scraped.")
    
    return product_details

def scrape_products(product_links, category):
    # Multiprocessing Pool with Manager for shared count
    with Pool() as pool, Manager() as manager:
        count = manager.Value('i', 0) 
        lock = manager.Lock()
        chunk_results = [pool.apply_async(scrape_product, (link, category, count, lock)) for link in product_links]
        product_details_list = [result.get() for result in chunk_results]
            
    return product_details_list

def main():
    index = 5
    limit = 140
    
    url = women_urls[index]
    category = women_categories[index]

    print("Driver Start")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    scroll_down(driver)
    html_content = driver.page_source
    driver.quit()
    
    print("Driver End")
    
    product_links = []
    
    soup = BeautifulSoup(html_content, "lxml")
    div_tags = soup.find_all("div", class_="jsx-b61f055fbb3ae7c7 group flex w-full")
    
    for div_tag in div_tags:
        a_tag = div_tag.find('a', class_="absolute inset-0")
    
        if a_tag:
            link = apex_link + a_tag['href']
            product_links.append(link)
        else:
            print("No <a> tag found within the div.")
    
    print(len(product_links))
    if len(product_links) > limit:
        product_links = product_links[:limit]
    
    product_details_list = scrape_products(product_links, category)
    
    save_to_file(product_details_list, f"Apex/Apex_Women_{category}.json")

if __name__ == "__main__":
    main()
