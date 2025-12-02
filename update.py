import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime

# === 全球主要股市即時價格 ===
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

# === 國際重大新聞（Google News RSS） ===
def fetch_news():
    url = "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    items = soup.find_all("item")[:8]
    news_html = ""
    for item in items:
        title = item.title.text
        link = item.link.text
        news_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
    return news_html

# === 政經局勢（Reuters World） ===
def fetch_geo():
    url = "https://www.reuters.com/world/"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select("a[href*='/world/']")[:8]
    geo_html = ""
    for a in articles:
        title = a.get_text(strip=True)
        link = "https://www.reuters.com" + a.get("href")
        geo_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
    return geo_html

# === 更新 index.html ===
def update_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 刪除舊資料區塊
    import re
    html = re.sub(r"<h2>📈 全球股市指數.*</body>", "</body>", html, flags=re.S)

    # 新資料區塊
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
