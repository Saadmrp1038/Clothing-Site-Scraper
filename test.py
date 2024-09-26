import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

def fetch_webpage(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return None

def main():
    url = "http://www.bdlex.com/pers/ViewDocMain.aspx?sort=&id=86055&p=OZsZiZ5PmnnlZHGPx/r0G/i79GEknZKwchar(43)ix0XFTqh7m6UVRTsL0gREQtSImZNxOW0HG6gb9qkkcHlDEMwqFrzRpYH1BabQ/612wkF4Lchar(43)uN/95NijQNXVgkWMQ1H6L9JAXOJS424ZsOchar(43)YhK0xi9uikpopL6ppklwWWJOTX9JeCiZ6q3oRL8DpCMoofvaNPZ4nWW0TsIx7c9cjS1pHichar(43)91vcJWxHtVg3LSPl5bGrfchar(43)char(43)PQ=#match0"
    
    # Define cookies
    cookies = [
        {"name": "ASP.NET_SessionId", "value": "3mdawtk54bfv5udbsy2dxjlt"},
        {"name": "ASPSESSIONIDCQATTSDR", "value": "EGALMOHDDLHFMGKIAIEGBDIB"},
        {"name": ".ASPXAUTH", "value": "B496227EDDD293F134B335DDB76D48FE2519A331E17AB20125C3F1D662AE31DEC8A958966AE496E1BEB7BEC940D8BADF36C6D85BCC64EB9005A403102ADBF4F4BBFEB2C7347A930F9BBD80E40E582434A0EEEC73B544A2B4B393D9779D560EC3EA8B82972F5596CFFED0E55DE0EDE9C028D4419A9E811A1548645A81F9CE4855601D4D97B90290F0AC5331C266D2EDD6"}
    ]
    
    print("Driver Start")
    driver = webdriver.Chrome(options=chrome_options)
    for cookie in cookies:
        driver.add_cookie(cookie)
        
    driver.get(url)
    time.sleep(5)
    html_content = driver.page_source
    driver.quit()
    
    print("Driver End")
    soup = BeautifulSoup(html_content, "lxml")
    
    # print("Fetching webpage using Selenium...")
    # html_content = fetch_webpage(url, cookies)
    # print("Webpage fetched successfully.")
    
    # print("Parsing HTML content with BeautifulSoup...")
    # soup = BeautifulSoup(html_content, "lxml")
    
    # print("Parsing complete. Displaying the parsed HTML content:")
    # print(soup.prettify())
    
    with open("testFile.html", "w", encoding='utf-8') as file:
        file.write(str(soup))
    print("HTML content saved to file")

if __name__ == "__main__":
    main()