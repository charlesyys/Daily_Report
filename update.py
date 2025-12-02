import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime

# === 1. 抓取全球股市 ===
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
        data = yf.Ticker(symbol).history(period="1d")
        price = round(data["Close"].iloc[-1], 2)
        rows += f"<li>{name}: {price}</li>"
    return rows

# === 2. 抓國際新聞 ===
def fetch_news():
    url = "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "xml")

    items = soup.find_all("item")[:8]
    news_html = ""
    for item in items:
        title = item.title.text
        link = item.link.text
        news_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
    return news_html

# === 3. 政經局勢 ===
def fetch_geo():
    url = "https://www.reuters.com/world/"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # 找出文章清單
    articles = soup.select("a[href*='/world/']")[:8]

    geo_html = ""
    for a in articles:
        title = a.get_text(strip=True)
        link = "https://www.reuters.com" + a.get("href")
        geo_html += f"<li><a href='{link}' target='_blank'>{title}</a></li>"
    return geo_html


# === 4. 讀取 index.html 並替換內容 ===
def update_html():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace(
        "正在等待資料更新...",
        ""
    )

    html = html.replace(
        "</body>",
        f"""
<h2>📈 全球股市指數（更新時間：{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}）</h2>
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
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

update_html()
