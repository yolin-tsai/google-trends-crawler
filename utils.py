from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from time import sleep
from rich.progress import Progress

def wait_for_element(driver: WebDriver, by: str, selector: str, timeout: int) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def fetch_titles(
    driver: WebDriver,
    total: int,
    sleep_sec: int,
    max_page: int
) -> list[dict[str, str]]:
    titles: list[dict[str, str]] = []
    seen: set[str] = set()
    page_count: int = 0
    from rich.progress import Progress

    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching titles...", total=total)
        while len(titles) < total and page_count < max_page:
            tr_elements = driver.find_elements(By.CSS_SELECTOR, "tr[jsname='oKdM2c']")
            for tr in tr_elements:
                try:
                    title = tr.find_element(By.CSS_SELECTOR, "div.mZ3RIc").text.strip()
                except Exception:
                    title = ""
                try:
                    volume = tr.find_element(By.CSS_SELECTOR, "div.lqv0Cb").text.strip()
                except Exception:
                    volume = ""
                try:
                    percent = tr.find_element(By.CSS_SELECTOR, "div.TXt85b").text.strip()
                except Exception:
                    percent = ""
                try:
                    time_info = tr.find_element(By.CSS_SELECTOR, "div.vdw3Ld").text.strip()
                except Exception:
                    time_info = ""
                if title and title not in seen:
                    titles.append({
                        "title": title,
                        "搜尋量": volume,
                        "上升幅度": percent,
                        "開始於": time_info
                    })
                    seen.add(title)
                    progress.update(task, advance=1)
                    if len(titles) >= total:
                        break
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='前往下一頁']")
                if not next_btn.is_enabled():
                    break
                next_btn.click()
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(tr_elements[0])
                )
                sleep(sleep_sec)
            except Exception:
                break
            page_count += 1
    return titles

def fetch_category_titles(
    driver: WebDriver,
    target_url: str,
    cat_id: int,
    sleep_sec: int
) -> set[str]:
    cat_url = f"{target_url}&category={cat_id}"
    driver.get(cat_url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mZ3RIc"))
        )
    except Exception:
        return set()
    cat_titles: set[str] = set()
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
            WebDriverWait(driver, 10).until(
                EC.staleness_of(cat_this_page[0])
            )
            sleep(sleep_sec)
        except Exception:
            break
    return cat_titles

def show_progress_for_filter(cat_name: str, cat_titles: set[str]) -> None:
    with Progress() as progress:
        task = progress.add_task(f"[red]Filtering {cat_name}...", total=len(cat_titles))
        for _ in cat_titles:
            progress.update(task, advance=1)