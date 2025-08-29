# google-trends-crawler

## 介紹

利用 Selenium 自動化瀏覽器，抓取 Google Trends 台灣每日熱門搜尋前 N 筆資料。  
可透過 config.json 設定自動過濾指定分類（如「政治」、「法律與政府」等）。

---

## 環境需求

- Python 3.9+
- Selenium
- Google Chrome + ChromeDriver
- rich（進度條顯示）

## 安裝方式

1. **建立虛擬環境（建議）**
    ```sh
    python3 -m venv venv
    # 或依系統設定
    python -m venv venv
    ```

2. **啟動虛擬環境**
    - macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - Windows:
        ```sh
        venv\Scripts\activate
        ```
    啟動成功後，命令列前方會出現 `(venv)` 提示字樣。

3. **安裝所需套件（推薦使用 pyproject.toml）**
    ```sh
    pip install .
    ```

4. **確認已安裝 Chrome 與 ChromeDriver**
    - 請確保 ChromeDriver 版本與 Chrome 瀏覽器相符。
    - 下載：[ChromeDriver 下載頁](https://chromedriver.chromium.org/downloads)

5. **執行主程式**
    ```sh
    python main.py
    ```

---

## 功能說明

- 自動抓取 Google Trends 熱門搜尋關鍵字
- 支援自動過濾指定分類（如政治、法律與政府等）

---

## 專案結構

```
google-trends-crawler/
├── main.py            # 主程式
├── scraper.py         # 負責資料抓取
├── filter.py          # 負責分類過濾
├── utils.py           # 共用工具
├── constants.py       # 常數與 selector 管理
├── config.json        # 設定檔
├── pyproject.toml     # Python 依賴管理
├── README.md          # 使用說明文件
├── venv/              # 虛擬環境資料夾（可選）
```

---

## 設定檔說明

編輯 `config.json` 以調整參數，例如：

```json
{
    "TARGET_COUNTRY": {
        "NAME": "台灣",
        "GEO": "TW",
        "HL": "zh-TW"
    },
    "TARGET_URL": "https://trends.google.com.tw/trending?",
    "TOP_N": 100,
    "HEADLESS": true,
    "SLEEP_SEC": 1,
    "CATEGORY": {
        "汽車與交通工具": { "id": 1, "enabled": true },
        "法律與政府": { "id": 10, "enabled": false },
        "政治": { "id": 14, "enabled": false }
        // ... 其他分類 ...
    }
}
```

- `TOP_N`：要抓取的熱門搜尋數量
- `HEADLESS`：是否啟用無頭模式（不顯示瀏覽器畫面）
- `SLEEP_SEC`：每次翻頁等待秒數
- `CATEGORY`：各分類的 id 及啟用狀態（`enabled: false` 會自動過濾該分類）

---

## 注意事項

- 請確認 ChromeDriver 已安裝且版本與 Chrome 瀏覽器相符
- 若需過濾分類，請將該分類的 `enabled` 設為 `false`
- 若 Google Trends 網頁結構有變動，請調整 CSS Selector（在 constants.py）

---

## 範例輸出

```
Launching browser...
Navigating to Google Trends...
Fetching titles... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
Filtering Law & Government category... ━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
Category 'Law & Government' filtered, total 5 items removed.
Taiwan Google Trends Top 100 Searches:
1. 熱門關鍵字1
2. 熱門關鍵字2
...
```