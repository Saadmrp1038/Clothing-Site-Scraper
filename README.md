# Clothing-Site-Scraper

This project is a web scraper designed to extract data from multiple Bangladeshi fashion websites using **Selenium**, **BeautifulSoup**, and **multiprocessing**. It successfully scraped over 20,000 products from brands such as Aarong, Allen Solly, Apex, Bata, and Infinity. The scraper efficiently handles complex challenges such as dynamic content loading, rate limiting, and inconsistent product page structures across various sites.

## Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Challenges](#challenges)
- [Usage](#usage)
- [Categories Scraped](#categories-scraped)
- [Installation](#installation)
- [Parsed Dataset](#parsed-dataset)
- [License](#license)

## Features
- **Multi-Site Scraping**: Scrapes product information from Aarong, Allen Solly, Apex, Bata, and Infinity.
- **Dynamic Data Handling**: For pages that dynamically load products on scroll (e.g., Aarong), the scraper uses scroll up-down behavior to ensure all products are loaded.
- **Delayed Loading Management**: Some sites do not load all data instantly, requiring Selenium to simulate browsing and wait for data to load before fetching content.
- **Rotating Proxy IPs**: Implemented for sites like Bata to bypass rate limiting.
- **Parallel Processing**: Utilizes Python's multiprocessing to scrape multiple product pages simultaneously for faster data collection.
- **Data Storage**: Scraped data is stored in chunks and saved in JSON format, which can be reloaded and processed later.

## Technologies
- **Python**: Core programming language.
- **Selenium**: Used for simulating browser interactions (e.g., scrolling, clicking, waiting for content to load).
- **BeautifulSoup**: Parses HTML pages to extract product details.
- **Multiprocessing**: Improves performance by parallelizing the scraping tasks.
- **Rotating Proxies**: Bypasses rate limits on some websites.
- **Requests**: For direct HTTP requests to fetch static pages.
- **Hugging Face Datasets**: The parsed dataset is hosted and made available for reuse on Hugging Face.

## Challenges
- **Dynamic Content**: On sites like Aarong, content loads dynamically when the user scrolls. To handle this, the scraper mimics user behavior by scrolling up and down.
- **Delayed Data Loading**: Some websites use delayed loading, where fetching content immediately returns nothing because the data hasn’t fully loaded. For these sites, Selenium is used to open the page, wait for the content to load, and then scrape.
- **Rate Limiting**: Bata's site has strict rate limiting, so we employed a rotating proxy system to avoid getting blocked.
- **Inconsistent Product Data**: Infinity's product pages were not uniform, requiring special cases for data extraction.
- **Large Datasets**: Scraped over 20,000 product details, efficiently saving and managing the data in chunks.



## Categories Scraped
Sraped data of 4 categories with a total of 30 sub-categories. They are:

### Men
Coaty & Fatua, Footwear, Casual Pant, Formal Pant, New Arrivals, Panjabi, Shirts, Suit, T-Shirts, Wallets

### Women
Western, Daily Life, Casual, Footwear, New Arrivals, Panjabi & Kurta, Winter Wear, Bags, Saree

### Boys
Western, Daily Life, Winter Wear, Formal, Panjabi, T-Shirt, Pant

### Girls
Special, Casual, Daily Life, Winter Wear

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/Clothing-Site-Scraper.git
   cd Clothing-Site-Scraper
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download and set up the appropriate browser drivers (e.g., ChromeDriver for Selenium):
   - ChromeDriver: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)

## Parsed Dataset
The parsed dataset containing over 20,000 fashion products is hosted on Hugging Face. You can access and download the dataset from the following link:

[**Clothing-Site-Scraper Dataset on Hugging Face**](https://huggingface.co/datasets/Melikshah/products)

## Shop-Genie Integration
The dataset from this scraper played a crucial role in building a core module of our Shop-Genie project, integrated into insightAI. Here's a glimpse of how it's being used:

- Data Augmentation: Product descriptions were generated using the LLaVA (Language and Vision Assistant) model from product image, improving poorly formatted descriptions.
- Vector Database: Hosted in Qdrant, with vector representations for both images and text:
  - Image embeddings: Generated using `CLIP-ViT-B-32`.
  - Text embeddings: Created using `text-embedding-3-large`.
  - Products can be retrieved based on text, image, or a combination of both for a seamless search experience.
Product Recommendation: A recommendation engine based on a best-score strategy, retrieving vectors close to positive examples while avoiding negative ones.
- Sentiment Analysis: Integrated GPT-4o-mini to analyze product reviews and classify them as positive, neutral, or negative, providing insightful feedback for users.

Check out the video demo of Shop-Genie here: [**Watch Shop-Genie Module Demo**](https://youtu.be/LgaAnftgMvQ?si=neQWr30QoaN1-tge)

Check out the whole InsighAI project here: [**Watch Full Project Demo + System Architecture**](https://www.youtube.com/watch?v=Csjt2n3_XJ8&feature=youtu.be)