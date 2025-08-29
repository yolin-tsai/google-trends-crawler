import json
import logging
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options

from utils import *

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def load_config(path: str ) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_driver(headless: bool = True) -> WebDriver:
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

def main() -> None:
    config: dict[str, Any] = load_config("config.json")
    country_info: dict[str, Any] = config["TARGET_COUNTRY"]
    TARGET_COUNTRY: str = country_info.get("NAME", "台灣")
    GEO: str = country_info.get("GEO", "TW")
    HL: str = country_info.get("HL", "zh-TW")
    BASE_URL: str = config.get("TARGET_URL", "https://trends.google.com.tw/trending?")
    TOP_N: int = config.get("TOP_N", 100)
    HEADLESS: bool = config.get("HEADLESS", True)
    SLEEP_SEC: int = config.get("SLEEP_SEC", 1)
    CATEGORY: dict[str, Any] = config.get("CATEGORY", {})
    MAX_PAGE: int = config.get("MAX_PAGE", 10)
    WAIT_ELEMENT_SEC: int = config.get("WAIT_ELEMENT_SEC", 10)

    TARGET_URL: str = f"{BASE_URL}geo={GEO}&hl={HL}"

    logging.info("Launching browser...")
    driver: WebDriver = setup_driver(HEADLESS)

    try:
        logging.info("Navigating to Google Trends...")
        driver.get(TARGET_URL)
        wait_for_element(driver, By.CSS_SELECTOR, "div.mZ3RIc", WAIT_ELEMENT_SEC)
        titles: list[str] = fetch_titles(driver, TOP_N, SLEEP_SEC, MAX_PAGE)

        # Handle categories to be filtered out
        remove_cats: list[str] = [cat_name for cat_name, cat_info in CATEGORY.items() if not cat_info.get("enabled", True)]

        for cat_name in remove_cats:
            cat_id: int = CATEGORY[cat_name]["id"]
            logging.info(f"Fetching category '{cat_name}' for filtering...")
            cat_titles: set[str] = fetch_category_titles(driver, TARGET_URL, cat_id, SLEEP_SEC)
            show_progress_for_filter(cat_name, cat_titles)
            titles = [t for t in titles if t not in cat_titles]
            logging.info(f"Category '{cat_name}' filtered, total {len(cat_titles)} items removed.")

        logging.info(f"{TARGET_COUNTRY} Google Trends Top {TOP_N} Searches:")
        for i, title in enumerate(titles[:TOP_N], 1):
            print(f"{i}. {title}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()