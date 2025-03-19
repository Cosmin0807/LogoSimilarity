from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin

def get_rendered_html(url):
    """Fetch fully rendered HTML using Selenium (for JavaScript-heavy sites)."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

def extract_logo_from_img(soup, base_url):
    """Extracts logo from <img> tags."""
    img_tags = soup.find_all("img", src=True)
    for img_tag in img_tags:
        src = img_tag["src"]
        img_url = urljoin(base_url, src)
        if "logo" in src.lower() and "condensed" not in src.lower():
            return img_url
    return None

def extract_logo_from_css(soup, base_url):
    """Extracts logo from background-image in external CSS files."""
    css_links = [urljoin(base_url, link["href"]) for link in soup.find_all("link", rel="stylesheet", href=True)]
    
    for css_url in css_links:
        try:
            css_response = requests.get(css_url, timeout=5)
            if css_response.status_code != 200:
                continue
            
            # 🔥 More aggressive regex to capture background-image URLs
            background_images = re.findall(r'url\([\'"]?([^\'")]+)[\'"]?\)', css_response.text)
            
            for img in background_images:
                absolute_url = urljoin(css_url, img)
                if "logo" in absolute_url.lower():  # Prioritize 'logo'
                    return absolute_url
        except requests.exceptions.RequestException:
            continue

    return None  # No logo found in CSS

def get_logo_url(domain):
    """Extracts logo URL using both HTML and CSS methods."""
    base_url = f"https://{domain}"

    # Try BeautifulSoup First
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(base_url, headers=headers, timeout=5)
        response.raise_for_status()  # Raise error for bad status codes (4xx, 5xx)

        soup = BeautifulSoup(response.content, "html.parser")
        logo_url = extract_logo_from_img(soup, base_url) or extract_logo_from_css(soup, base_url)
        if logo_url:
            return logo_url

    except requests.exceptions.ConnectionError:
        return None  # Do not try Selenium if there's a connection error

    except requests.exceptions.RequestException:
        return None  # Do not try Selenium if there's a different request error

    # If No Logo Found, Try Selenium
    try:
        rendered_html = get_rendered_html(base_url)
        soup = BeautifulSoup(rendered_html, "html.parser")
        return extract_logo_from_img(soup, base_url) or extract_logo_from_css(soup, base_url)
    except Exception as e:
        return None