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

men_categories = [
    "Casual Shirts",
    "Formal Shirts",
    "T-Shirts",
    "Jeans",
    "Suits",
    "Blazers",
    "Trousers",
    "Track Pants & Joggers",
    "Shorts",
    "Wallets",
    "Footwear"
]

men_urls = [
    "https://allensolly.abfrl.in/c/men-casual-shirts",
    "https://allensolly.abfrl.in/c/men-formal-shirts",
    "https://allensolly.abfrl.in/c/men-t-shirts",
    "https://allensolly.abfrl.in/c/men-jeans",
    "https://allensolly.abfrl.in/c/men-suits",
    "https://allensolly.abfrl.in/c/men-blazers",
    "https://allensolly.abfrl.in/c/men-trousers",
    "https://allensolly.abfrl.in/c/men-track-pants-and-joggers",
    "https://allensolly.abfrl.in/c/men-shorts",
    "https://allensolly.abfrl.in/c/men-wallets",
    "https://allensolly.abfrl.in/c/men-footwear"
]

women_categories = [
    "Tops",
    "Tunics",
    "Dresses",
    "Winterwear",
    "Jumpsuits",
    "Skirts",
    "Leggings & Jeggings",
    "Bags",
    "Footwear"
]

women_urls = [
    "https://allensolly.abfrl.in/c/women-tops",
    "https://allensolly.abfrl.in/c/women-tunics",
    "https://allensolly.abfrl.in/c/women-dresses",
    "https://allensolly.abfrl.in/c/women-winterwear",
    "https://allensolly.abfrl.in/c/women-jumpsuits",
    "https://allensolly.abfrl.in/c/women-skirts",
    "https://allensolly.abfrl.in/c/women-leggings-jeggings",
    "https://allensolly.abfrl.in/c/women-bags",
    "https://allensolly.abfrl.in/c/women-footwear"
]

boys_categories = [
    "Shirts",
    "Polo T-Shirts",
    "Round Neck & V Neck T-Shirts",
    "Sweatshirts",
    "Suits & Blazers",
    "Jackets",
    "Shorts",
    "Trousers",
    "Track Pants",
    "Jeans",
    "Gloves",
    "Masks"
]

boys_urls = [
    "https://allensolly.abfrl.in/c/boys-shirts",
    "https://allensolly.abfrl.in/c/boys-polo-t-shirts",
    "https://allensolly.abfrl.in/c/boys-round-neck-and-v-neck-t-shirts",
    "https://allensolly.abfrl.in/c/boys-sweatshirts",
    "https://allensolly.abfrl.in/c/boys-suits-and-blazers",
    "https://allensolly.abfrl.in/c/boys-jackets",
    "https://allensolly.abfrl.in/c/boys-shorts",
    "https://allensolly.abfrl.in/c/boys-trousers",
    "https://allensolly.abfrl.in/c/boys-track-pants",
    "https://allensolly.abfrl.in/c/boys-jeans",
    "https://allensolly.abfrl.in/c/boys-gloves",
    "https://allensolly.abfrl.in/c/boys-masks"
]

girls_categories = [
    "Tops & T-Shirts",
    "Frocks & Dresses",
    "Sweaters",
    "Dungarees",
    "Leggings & Jeggings",
    "Skirts"
]

girls_urls = [
    "https://allensolly.abfrl.in/c/girls-tops-and-t-shirts",
    "https://allensolly.abfrl.in/c/girls-frocks-dresses",
    "https://allensolly.abfrl.in/c/girls-sweaters",
    "https://allensolly.abfrl.in/c/girls-dungarees",
    "https://allensolly.abfrl.in/c/girls-leggings-and-jeggings",
    "https://allensolly.abfrl.in/c/girls-skirts"
]

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

def scrape_product(link, category, gender, count, lock):
    product_page = fetch_webpage(link)
    
    if not product_page:
        print(f"Not Found: {link}")
        return
    
    product_soup = BeautifulSoup(product_page , "lxml")
    
    # Extracting product details
    product_name_div = product_soup.find('h1', class_='MuiTypography-root MuiTypography-h1 PDPDetails_productTitle_name__CZYmj css-jff0b8')
    
    if product_name_div:
        product_name = product_name_div.text.strip()
    else:
        print(f"Product name not found for {link}")
        return
        
    product_price_div = product_soup.find(class_='actual-price')
    
    if product_price_div:
        product_price = product_price_div.get_text().replace("\u20b9", "Tk")
    else:
        
        product_price_div = product_soup.find(class_='price')
        if product_price_div:
            product_price = product_price_div.get_text().replace("\u20b9", "Tk")
        else:
            print(f"Product price not found for {link}")
            return
    
    img_divs = product_soup.find_all('div', class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-6 PDPMedia_imageGrid__22jkn css-1s50f5r")
    
    if len(img_divs) == 0:
        print(f"Product images not found for {link}")
        return
    
    image_links = []
    
    for div in img_divs:
        image_link = div.find('img')['src'].split('?')[0]
        if  "https://" in image_link:
            image_links.append(image_link)
    
    if len(img_divs) == 0:
        print(f"Product images not valid for {link}")
        return
    
    description_div = product_soup.find('div', class_='ProductDetails_container__0vRlj ProductDetails_AS__WcrW_')
    
    if description_div:
        description = description_div.text.strip().split("product description")[1].split("product details")[0]
    else:
        print(f"Product description not found for {link}")
        return
    
    features = product_soup.find_all(class_='ProductDetails_accordioncontainer__zctDK')
    # print(len(features))
    specifications = {}
    
    if len(features) == 0:
        print(f"Product features not found for {link}")
        return
    
    for feature in features:
        key = feature.find(class_='ProductDetails_detailsList__GuauJ').span.text.strip().replace(':', '')
        value = feature.find(class_='ProductDetails_detailsItem__qb2Mv').div.text.strip()
        
        if key != "StyleCode":
            specifications[key] = value
              
    product_details = {
        "Name": product_name,
        "Price": product_price,
        "Image_links": image_links,
        "Link": link,
        "Description": description,
        "Specifications": specifications,
        "Company": "Allen Solly",
        "Category": category,
        "Gender": gender
    }
    
    # Increment count
    lock.acquire()
    count.value += 1
    lock.release()
    
    print(f"Product {count.value} scraped.")
    
    return product_details

def scrape_products(product_links, category, gender):
    # Multiprocessing Pool with Manager for shared count
    with Pool() as pool, Manager() as manager:
        count = manager.Value('i', 0) 
        lock = manager.Lock()
        chunk_results = [pool.apply_async(scrape_product, (link, category, gender, count, lock)) for link in product_links]
        product_details_list = [result.get() for result in chunk_results]
            
    return product_details_list

'''
Men(11) - 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
Women(9) - 0, 1, 2, 3, 4, 5, 6, 7, 8
Boys(12) - 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
Girls(6) - 0, 1, 2, 3, 4, 5
'''

def main():
    
    index = 5
    url = girls_urls[index]
    category = girls_categories[index]
    gender = "Girls"

    print(f"Category: {category}")
    
    print("Driver Start")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    scroll_down(driver)
    html_content = driver.page_source
    driver.quit()
    
    print("Driver End")
    
    product_links = []
    
    soup = BeautifulSoup(html_content, "lxml")
    

    all_links = soup.find_all('img')
    product_codes = [link['srcset'].split('?')[0].split("/")[-1].split("-")[0] for link in all_links if link.get('srcset') and 'https://imagescdn.allensolly.com/img/app/product/' in link.get('srcset')]
    
    div_elements = soup.find_all('div', class_='ProductCard_description__BQzle')
    product_titles = [div['title'] for div in div_elements]
    
    for code,title in zip(product_codes,product_titles):
        lowercase_title = title.lower()
        hyphenated_title = lowercase_title.replace(" ", "-")
        product_link = f"https://allensolly.abfrl.in/p/{hyphenated_title}-{code}.html?source=plp"
        
        product_links.append(product_link)
    
    print(len(product_links))
    
    product_details_list = scrape_products(product_links, category, gender)
    
    save_to_file(product_details_list, f"Allen Solly/Allen_Solly_{gender}_{category}.json")

if __name__ == "__main__":
    main()