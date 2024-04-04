import random
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
import config

import sys
# Set recursion limit to a higher value
sys.setrecursionlimit(10**6)

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# print(config.ips[3])
# proxy_server_url = config.ips[1]
# chrome_options.add_argument(f'--proxy-server={proxy_server_url}')

# Variables
men_categories = [
    "Casual Shoes",
    "Formal Shoes",
    "Sandals",
    "Mocassino",
    "Sports"
]

men_urls = [
    "https://www.batabd.com/collections/casual-shoes",
    "https://www.batabd.com/collections/formal-shoes",
    "https://www.batabd.com/collections/mens-sandal",
    "https://www.batabd.com/collections/mocassino-1?constraint=men",
    "https://www.batabd.com/collections/sports"
]

women_categories = [
    "Sandals",
    "Heels",
    "Sports Shoes",
    "Casual & Formal Closed Shoes"
]

women_urls = [
    "https://www.batabd.com/collections/sandals",
    "https://www.batabd.com/collections/ladies-heel",
    "https://www.batabd.com/collections/ladies-sports",
    "https://www.batabd.com/collections/closed-shoes"
]

bata_link = "https://www.batabd.com"

def fetch_webpage(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return None

def save_to_file(product_details_list, filename):
    # Check if the file already exists
    if os.path.exists(filename):
        # Load existing data from the file
        with open(filename, "r") as file:
            existing_data = json.load(file)
        
        # Append new product details to existing data
        existing_data.extend(product_details_list)
        
        print(f"Total Itmes: {len(existing_data)}")
        
        # Save updated data back to the file
        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)
    else:
        # If the file doesn't exist, simply save the new data
        with open(filename, "w") as file:
            json.dump(product_details_list, file, indent=4)
            
        print(f"Total Itmes: {len(product_details_list)}")


# def save_to_file(product_details_list, filename):
#     with open(filename, "w") as file:
#         json.dump(product_details_list, file, indent=4)

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
    index = 0
    start = 14
    
    url = men_urls[index]
    category = men_categories[index]
    
    print(f"Category: {category}")
    
    page_number = 1
    product_links = []
    
    while True:
        page_url = url + f"?page={page_number}" 
        html_content = fetch_webpage(page_url)
        
        soup = BeautifulSoup(html_content, "lxml")
        div_tags = soup.find_all("div", class_="product-image image-swap")

        print(len(div_tags))
        if len(div_tags) == 0:
            break
        
        for div_tag in div_tags:
            a_tag = div_tag.find('a', class_="product-grid-image")
        
            if a_tag:
                link = bata_link + a_tag['href']
                product_links.append(link)
            else:
                print("No <a> tag found within the div.")
        
        print(f"Page {page_number} Done")
        page_number += 1
    
    print(len(product_links))
    
    product_details_list = []
    
    driver = webdriver.Chrome(options=chrome_options)
    
    count = 1
    for link in product_links[start:]:
        driver.get(link)
        time.sleep(2)
        html_content = driver.page_source
        
        if not html_content:
            break
        
        product_soup = BeautifulSoup(html_content , "lxml")
        
        #Extart product details
        product_name_div = product_soup.find('h1', class_='product-title')
        
        if product_name_div:
            product_name = product_name_div.text.strip()
        else:
            print(f"Product Name Not Found: {link}")
            break
        
        vendor_span = product_soup.find('div', class_='vendor-product').find('span')
        
        if vendor_span:
            vendor_name = vendor_span.get_text(strip=True)
        else:
            print(f"Product Vendor Not Found: {link}")
            break
        
        price_span = product_soup.find('div', class_='prices').find('span',class_="compare-price")
        
        if price_span:
            price = price_span.get_text(strip=True)
        else:
            print(f"Product Price Not Found: {link}")
            break
        
        product_image_div = product_soup.find("div",class_="product-photo-container slider-for slick-initialized slick-slider")
        slick_divs = product_image_div.find_all("div", class_="slick-slide")

        image_links = []
        
        for slick_div in slick_divs:
            image_a_tag = slick_div.find('a')
            image_link = image_a_tag['href']
            
            image_link = "https:" + image_link
            image_link = image_link.split('?')[0]
            
            image_links.append(image_link)
        
        text_element = product_soup.find('div', class_='tab-content active')
        
        text = text_element.text.strip()
        
        if "FEATURES:" in text:
            ar1 = text.split("FEATURES:")
        elif "Features:" in text:
            ar1 = text.split("Features:")
        
        description = ar1[0]
        
        if "STYLE TIPS:" in text:
            ar2 = ar1[1].split("STYLE TIPS:")
        elif "Style Tips:" in text:
            ar2 = ar1[1].split("Style Tips:")

        features = ar2[0].split("- ")
        
        if len(features) > 1:
            features = features[1:]
        else:
            features_string = features[0]
            # Split the string based on the feature separator (": ")
            features_list = features_string.split(":")

            # Remove any leading or trailing whitespace from each feature and filter out empty strings
            features_list = [feature.strip() for feature in features_list if feature.strip()]
            
            features = features_list
        
        style_tips = ar2[1]
   
        specifications = {
            "Vendor" : vendor_name,
            "Features" : features,
            "Style_Tips" : style_tips
        }
        
        product_details = {
            "Name": product_name,
            "Price": price,
            "Image_links": image_links,
            "Link": link,
            "Description": description,
            "Specifications": specifications,
            "Company": "Bata",
            "Category": category,
            "Gender": "Male"   
        }
    
        product_details_list.append(product_details)
        
        print(f"Product {count} Scraped")
        count += 1
    
    driver.quit()
    save_to_file(product_details_list, f"Bata/Bata_Men_{category}.json")

if __name__ == "__main__":
    main()
