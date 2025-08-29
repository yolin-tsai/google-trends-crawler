import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from rich.progress import Progress

# 從 config.json 讀取參數
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

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

# 設定無頭模式
chrome_options = Options()
if HEADLESS:
    chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# 啟動瀏覽器
print("啟動瀏覽器中...")
driver = webdriver.Chrome(options=chrome_options)

# 前往 Google Trends 指定國家每日熱門搜尋頁面
print("前往 Google Trends...")
driver.get(TARGET_URL)

# 等待主要元素載入
WebDriverWait(driver, WAIT_ELEMENT_SEC).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.mZ3RIc"))
)

time.sleep(SLEEP_SEC)  # 額外等待

titles = []

with Progress() as progress:
    task = progress.add_task("[cyan]抓取資料中...", total=TOP_N)

    # 持續點擊「下一頁」直到至少有 TOP_N 筆資料或達到最大頁數
    page_count = 0
    while len(titles) < TOP_N and page_count < MAX_PAGE:
        titles_this_page = driver.find_elements(By.CSS_SELECTOR, "div.mZ3RIc")
        for t in titles_this_page:
            text = t.text.strip()
            titles.append(text)
            # 顯示進度條
            progress.update(task, advance=1)
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='前往下一頁']")
            if not next_btn.is_enabled():
                break
            next_btn.click()
            time.sleep(SLEEP_SEC)
        except Exception:
            break
        page_count += 1

# 處理需去除的分類
remove_cats = []

# 根據 enabled = false 自動過濾
for cat_name, cat_info in CATEGORY.items():
    if not cat_info.get("enabled", True):  # 預設 True，確保沒寫 enabled 的也能跑
        remove_cats.append(cat_name)

for cat_name in remove_cats:
    cat_id = CATEGORY[cat_name]["id"]
    cat_url = f"{BASE_URL}geo={GEO}&hl={HL}&category={cat_id}"
    print(f"抓取「{cat_name}」分類以過濾...")
    driver.get(cat_url)
    time.sleep(SLEEP_SEC)
    cat_titles = set()
    with Progress() as progress:
        task = progress.add_task(f"[red]過濾{cat_name}分類...", total=TOP_N)
        while True:
            cat_this_page = driver.find_elements(By.CSS_SELECTOR, "div.mZ3RIc")
            added = 0
            for t in cat_this_page:
                text = t.text.strip()
                if text:
                    cat_titles.add(text)
                    added += 1
            progress.update(task, advance=added)
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='前往下一頁']")
                if not next_btn.is_enabled():
                    break
                next_btn.click()
                time.sleep(SLEEP_SEC)
            except Exception:
                break
    # 過濾該分類標題
    titles = [t for t in titles if t not in cat_titles]
    print(f"完成 {cat_name} 分類，總共過濾 {len(cat_titles)} 筆資料")

print(f"{TARGET_COUNTRY} Google Trends 每日熱門搜尋前{TOP_N}筆：")
for i, title in enumerate(titles[:TOP_N], 1):
    print(f"{i}. {title}")

driver.quit()