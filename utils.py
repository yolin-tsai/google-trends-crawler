from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.progress import Progress
from typing import List, Set
from time import sleep
from selenium.webdriver.common.by import By
from rich.progress import Progress
from constants import TITLE_SELECTOR, NEXT_BTN_SELECTOR

def wait_for_element(driver: WebDriver, by: str, selector: str, timeout: int) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def fetch_titles(
    driver: WebDriver,
    total: int,
    sleep_sec: int,
    max_page: int
) -> List[str]:
    titles: List[str] = []
    seen: Set[str] = set()
    page_count: int = 0
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching titles...", total=total)
        while len(titles) < total and page_count < max_page:
            titles_this_page = driver.find_elements(By.CSS_SELECTOR, TITLE_SELECTOR)
            for t in titles_this_page:
                text = t.text.strip()
                if text and text not in seen:
                    titles.append(text)
                    seen.add(text)
                    progress.update(task, advance=1)
                    if len(titles) >= total:
                        break
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, NEXT_BTN_SELECTOR)
                if not next_btn.is_enabled():
                    break
                next_btn.click()
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(titles_this_page[0])
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
            EC.presence_of_element_located((By.CSS_SELECTOR, TITLE_SELECTOR))
        )
    except Exception:
        return set()
    cat_titles: Set[str] = set()
    while True:
        cat_this_page = driver.find_elements(By.CSS_SELECTOR, TITLE_SELECTOR)
        for t in cat_this_page:
            text = t.text.strip()
            if text:
                cat_titles.add(text)
        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, NEXT_BTN_SELECTOR)
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

def show_progress_for_filter(cat_name: str, cat_titles: Set[str]) -> None:
    with Progress() as progress:
        task = progress.add_task(f"[red]Filtering {cat_name}...", total=len(cat_titles))
        for _ in cat_titles:
            progress.update(task, advance=1)