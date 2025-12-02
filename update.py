import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime

# === 1. 全球主要股市即時價格 ===
markets = {
    "道瓊指數 (DJI)": "^DJI",
    "NASDAQ": "^IXIC",
    "S&P 500": "^GSPC",
    "日經 225": "^N225",
    "台灣加權": "^TWII",
    "上證指數": "000001.SS",
    "德國 DAX": "^GDAXI"
}

def fetch_markets():
    rows = ""
    for name, symbol in markets.items():
        ticker = yf.Ticker(symbol)
        try:
            price = ticker.fast_info["lastPrice"]
            price = round(price, 2)
            rows += f"<li>{name}: {price}</li>"
        except:
            rows += f"<li>{name}: 讀取失敗</li>"
    return rows

# === 2. 國際重大新聞（Google News RSS） ===
def fetch_news():
    url = "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "text/xml,application/xml,application/xhtml+xml",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Referer": "https://news.google.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "keep-alive"
    }

    # ★ 禁止 redirect，把 example.com 擋掉
    r = requests.get(url, headers=headers, timeout=10, allow_redirects=False)

    # ★ 如果被偷偷轉址，直接錯誤提醒
    if r.status_code in (301, 302, 303, 307, 308):
        raise Exception("Google RSS 被 redirect → 可能被風控，需要換 IP 或 Proxy")

    text = r.text.strip()
    if "Example Domain" in text:
        raise Exception("⚠️ RSS 被反爬蟲導向 example.com！需要更強 headers 或 proxy")

    soup = BeautifulSoup(text, "xml")

    items = soup.find_all("item")[:10]
    news_html = ""

    for item in items:
        title = item.title.text
        link = item.link.text
        news_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"

    return news_html

# === 3. 政經局勢（Reuters World） ===
def fetch_geo():
    url = "https://www.reuters.com/world/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select("a[href*='/world/']")[:8]
    geo_html = ""
    for a in articles:
        title = a.get_text(strip=True)
        link = "https://www.reuters.com" + a.get("href")
        geo_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
    return geo_html

# === 4. 更新 index.html ===
def update_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 刪除舊資料區塊
    import re
    html = re.sub(r"<h2>📈 全球股市指數.*</body>", "</body>", html, flags=re.S)

    # 插入新資料
    new_content = f"""
<h2>📈 全球股市指數（更新時間：{now}）</h2>
<ul>
{fetch_markets()}
</ul>

<h2>📰 國際重大新聞</h2>
<ul>
{fetch_news()}
</ul>

<h2>🌐 政經局勢摘要</h2>
<ul>
{fetch_geo()}
</ul>
</body>
"""
    html = html.replace("</body>", new_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update_html()
    print("首頁更新完成 ✅")
