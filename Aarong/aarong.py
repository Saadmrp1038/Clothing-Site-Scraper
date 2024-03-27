import time
import json
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Pool, Manager

import sys
# Set recursion limit to a higher value
sys.setrecursionlimit(10**6)

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

def chunk_and_write_to_file(page_source):
    soup = BeautifulSoup(page_source, "lxml")
    product_elements = soup.find_all(class_='product-item-info')

    chunk_size = 100

    script_dir = os.path.dirname(__file__)

    file_count = 0
    for i in range(0, len(product_elements), chunk_size):
        chunk = product_elements[i:i+chunk_size]
        file_count += 1
        file_path = os.path.join(script_dir, f"output_{file_count}.html")
        with open(file_path, "w") as file:
            for item in chunk:
                file.write(str(item) + '\n')
        
    return file_count

def fetch_webpage(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return None

def scrape_product_details(product_url):
    response = requests.get(product_url)
    if response.status_code == 200:
        product_soup = BeautifulSoup(response.content, "lxml")
        
        product_details = {}
        product_details["Description"] = product_soup.find("div", class_="product attribute description").find("div", class_="value").text.strip()

        specifications_table = product_soup.find("table", id="product-attribute-specs-table")
        specifications = {}
        if specifications_table:
            rows = specifications_table.find_all("tr")
            for row in rows:
                label = row.find("th").text.strip()
                value = row.find("td").text.strip()
                specifications[label] = value

        product_details["Specifications"] = specifications
        return product_details
    else:
        print("Failed to fetch product details from:", product_url)
        return None

def scrape_product(product, count, lock):
    product_details = {}
    product_details["Name"] = product.find('strong', class_='product name product-item-name').text.strip()
    product_details["Price"] = product.find('span', class_='price').text.strip()
    product_details["Image_link"] = product.find('img', class_='product-image-photo')['src']
    product_details["Link"] =  product.find('a', class_='product-item-link')['href']
    
    product_details.update(scrape_product_details(product_details["Link"]))
    
    # Increment count
    lock.acquire()
    count.value += 1
    lock.release()
    
    print(f"Product {count.value} scraped.")
    
    return product_details

def scrape_products(page_source):
    soup = BeautifulSoup(page_source, "lxml")
    product_elements = soup.find_all(class_='product-item-info')
    product_details_list = []

    # Multiprocessing Pool with Manager for shared count
    with Pool() as pool, Manager() as manager:
        count = manager.Value('i', 0) 
        lock = manager.Lock()
        chunk_results = [pool.apply_async(scrape_product, (product, count, lock)) for product in product_elements]
        product_details_list = [result.get() for result in chunk_results]
            
    return product_details_list

def save_to_file(product_details_list, filename):
    with open(filename, "w") as file:
        json.dump(product_details_list, file, indent=4)

def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    count = 0
    max_attempt = 10
    attempt = 0
    
    while attempt < max_attempt:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollBy(0, -100);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempt += 1
            print(f"Attempt Count: {attempt}")
            continue
        
        attempt = 0
        last_height = new_height
        
        count += 1
        print(f"Scoll Count: {count}")

def get_catagory_details(category_elements):
    for index, category in enumerate(category_elements[0:], start=1):
        category_href = category.find('a')['href']
        category_name = category.find('a').text
        print(f"{index}. {category_name} - {category_href}")   
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(category_href)
        html_content = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(html_content, "lxml")
        amount = soup.find("span", class_="toolbar-number").text.strip()
        print(f"Amount: {amount}")

def load_page_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def main():
    url = "https://www.aarong.com/men"
    page_source = fetch_webpage(url)
    
    if page_source:
        category_soup = BeautifulSoup(page_source, "lxml")
        category_elements = category_soup.find_all(class_='shopby-info')
        
        # get_catagory_details(category_elements)
        
        # for index, category in enumerate(category_elements[0:], start=1):
        
        category = category_elements[8]
        
        category_href = category.find('a')['href']
        category_name = category.find('a').text
        
        print("Driver Start")
        
        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Chrome()
        driver.get(category_href)
        scroll_down(driver)
        html_content = driver.page_source
        driver.quit()
        
        print("Driver End")
        
        # html_file_path = f"./men-shirt.html"
        # html_content = load_page_from_file(html_file_path)
        file_count = chunk_and_write_to_file(html_content)
        
        product_details_list = []
        for i in range(file_count):
            file_path = f"./output_{i+1}.html"
            content = load_page_from_file(file_path)
            product_details_list.extend(scrape_products(content))
            os.remove(f"./output_{i+1}.html")
        
        save_to_file(product_details_list, f"Men_{category_name}.json")

if __name__ == "__main__":
    main()
