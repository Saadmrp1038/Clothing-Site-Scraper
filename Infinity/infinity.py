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

men_url = "https://infinitymegamall.com/product-category/men/"
men_ethnic_url = "https://infinitymegamall.com/product-category/ethnic-wear/"
women_url = "https://infinitymegamall.com/product-category/women/"

def save_to_file(product_details_list, filename):
    with open(filename, "w") as file:
        json.dump(product_details_list, file, indent=4)

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

    while attempt < max_attempt:
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
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

def scrape_product(driver, link, gender, index):
    
    driver.get(link)
    time.sleep(2)
    product_page = driver.page_source
    
    if not product_page:
        print(f"Not Found: {link}")
        return
    
    product_soup = BeautifulSoup(product_page , "lxml")
    
    # Extracting product details
    product_name_div = product_soup.find("h1", class_="product_title entry-title")
    
    if product_name_div:
        product_name = product_name_div.text.strip()
    else:
        print(f"Product name not found for {link}")
        return
    
    price_tag = product_soup.find("p", class_="price")
    
    if price_tag:
        product_price = price_tag.find("bdi").get_text(strip=True)
        product_price = product_price.replace("\u09f3","Tk ")
    else:
        print(f"Product price not found for {link}")
        return
    
    img_div = product_soup.find("div", class_="woocommerce-product-gallery__wrapper")
    
    if img_div:
        a_tag = img_div.find("a")
        image_link = a_tag["href"]
    else:
        print(f"Product image not found for {link}")
        return
    
    nav_div = product_soup.find("nav", class_="woocommerce-breadcrumb site-breadcrumb")
    
    if nav_div:
        nav_tags = nav_div.find_all("a")
        category = nav_tags[-1].text.strip()
    else:
        print(f"Product navbar not found for {link}")
        return
    
    short_description_div = product_soup.find("div", class_="woocommerce-product-details__short-description")
    
    if short_description_div:
        short_description = short_description_div.text.strip()
    else:
        short_description = None
        # print(f"Product short description not found for {link}")
    
    description_div = product_soup.find("div", class_="woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab")
    
    if description_div:
        description = description_div.text.strip()
    else:
        description = None
        # print(f"Product description not found for {link}")
    
    if description and short_description: 
        combinded_description = short_description + "\n" + description
    elif description:
        combinded_description = description
    elif short_description:
        combinded_description = short_description
    else:
        combinded_description = None
    
    product_details = {
        "Name": product_name,
        "Price": product_price,
        "Image_link": image_link,
        "Link": link,
        "Description": combinded_description,
        "Company": "Infinity",
        "Category": category,
        "Gender": gender
    }
    
    print(f"Product {index} scraped.")
    
    return product_details

def main():
    
    url = women_url
    gender = "Woman"
    category = "Women"
    
    # html_content = fetch_webpage(url)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    print("Driver Start")

    driver.get(url)
    scroll_down(driver)
    html_content = driver.page_source
    
    print("Driver End")
    
    soup = BeautifulSoup(html_content, "lxml")
    
    div_tags = soup.find_all("div", class_="product-thumbnail")
    
    product_links = []
    
    for div in div_tags:
        a_tag = div.find("a", class_="woocommerce-LoopProduct-link woocommerce-loop-product__link")
        link = a_tag["href"]
        
        product_links.append(link)
    
    print(f"Products found {len(product_links)}")
    
    product_details_list = []
    
    index = 1
    for link in product_links:
        product_details = scrape_product(driver, link, gender, index)
        if product_details:
            product_details_list.append(product_details)
        index += 1
    
    print(f"Total products scraped {len(product_details_list)}")
    
    save_to_file(product_details_list, f"Infinity/Infinity_{category}.json") 
    
    driver.quit()
    
if __name__ == "__main__":
    main()