import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.progress import Progress

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

def wait_for_element(driver, selector, timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )

def fetch_titles(driver, total, sleep_sec, max_page, selector="div.mZ3RIc"):
    titles = []
    page_count = 0
    with Progress() as progress:
        task = progress.add_task("[cyan]抓取資料中...", total=total)
        while len(titles) < total and page_count < max_page:
            titles_this_page = driver.find_elements(By.CSS_SELECTOR, selector)
            for t in titles_this_page:
                text = t.text.strip()
                if text and text not in titles:
                    titles.append(text)
                    progress.update(task, advance=1)
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='前往下一頁']")
                if not next_btn.is_enabled():
                    break
                next_btn.click()
                time.sleep(sleep_sec)
            except Exception:
                break
            page_count += 1
    return titles

def fetch_category_titles(driver, base_url, geo, hl, cat_id, sleep_sec):
    cat_url = f"{base_url}geo={geo}&hl={hl}&category={cat_id}"
    driver.get(cat_url)
    time.sleep(sleep_sec)
    cat_titles = set()
    while True:
        cat_this_page = driver.find_elements(By.CSS_SELECTOR, "div.mZ3RIc")
        for t in cat_this_page:
            text = t.text.strip()
            if text:
                cat_titles.add(text)
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='前往下一頁']")
            if not next_btn.is_enabled():
                break
            next_btn.click()
            time.sleep(sleep_sec)
        except Exception:
            break
    return cat_titles

def show_progress_for_filter(cat_name, cat_titles):
    with Progress() as progress:
        task = progress.add_task(f"[red]過濾{cat_name}分類...", total=len(cat_titles))
        for _ in cat_titles:
            progress.update(task, advance=1)
            time.sleep(0.01)  # 動畫效果，可調整或移除

def main():
    config = load_config()
    country_info = config["TARGET_COUNTRY"]
    TARGET_COUNTRY = country_info.get("NAME", "台灣")
    GEO = country_info.get("GEO", "TW")
    HL = country_info.get("HL", "zh-TW")
    BASE_URL = config.get("TARGET_URL", "https://trends.google.com.tw/trending?")
    TOP_N = config.get("TOP_N", 100)
    HEADLESS = config.get("HEADLESS", True)
    SLEEP_SEC = config.get("SLEEP_SEC", 1)
    CATEGORY = config.get("CATEGORY", {})
    MAX_PAGE = config.get("MAX_PAGE", 10)
    WAIT_ELEMENT_SEC = config.get("WAIT_ELEMENT_SEC", 10)

    TARGET_URL = f"{BASE_URL}geo={GEO}&hl={HL}"

    print("啟動瀏覽器中...")
    driver = setup_driver(HEADLESS)

    print("前往 Google Trends...")
    driver.get(TARGET_URL)
    wait_for_element(driver, "div.mZ3RIc", WAIT_ELEMENT_SEC)
    time.sleep(SLEEP_SEC)

    titles = fetch_titles(driver, TOP_N, SLEEP_SEC, MAX_PAGE)

    # 處理需去除的分類
    remove_cats = [cat_name for cat_name, cat_info in CATEGORY.items() if not cat_info.get("enabled", True)]

    for cat_name in remove_cats:
        cat_id = CATEGORY[cat_name]["id"]
        print(f"抓取「{cat_name}」分類以過濾...")
        cat_titles = fetch_category_titles(driver, BASE_URL, GEO, HL, cat_id, SLEEP_SEC)
        show_progress_for_filter(cat_name, cat_titles)
        titles = [t for t in titles if t not in cat_titles]
        print(f"「{cat_name}」分類，總共過濾 {len(cat_titles)} 筆資料\n")

    print(f"{TARGET_COUNTRY} Google Trends 每日熱門搜尋前{TOP_N}筆：")
    for i, title in enumerate(titles[:TOP_N], 1):
        print(f"{i}. {title}")

    driver.quit()

if __name__ == "__main__":
    main()