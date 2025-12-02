import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime
import re

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

# === 英文新聞（Google News RSS） ===
def fetch_news_en():
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("item")[:20]

        news_html = ""
        for item in items:
            title = item.title.text.strip()
            link = item.guid.text.strip() if item.guid else item.link.text.strip()
            news_html += f'<li><a href="{link}" target="_blank">{title}</a></li>'
        return news_html
    except Exception as e:
        return f"<li>英文新聞讀取失敗: {e}</li>"

# === 中文新聞（聯合新聞網 + 中央社） ===
def fetch_news_zh():
    sources = [
        ("聯合新聞網國際", "https://udn.com/rssfeed/news/1003/6638?ch=news"),
        ("中央社國際", "https://www.cna.com.tw/rss/firstnews_rss.xml")
    ]
    news_html = ""
    for source, url in sources:
        try:
            r = requests.get(url, timeout=10)
            soup = BeautifulSoup(r.text, "xml")
            items = soup.find_all("item")[:10]
            for item in items:
                title = item.title.text.strip()
                link = item.link.text.strip()
                news_html += f'<li><a href="{link}" target="_blank">{title}</a> <small>({source})</small></li>'
        except Exception as e:
            news_html += f"<li>{source} 讀取失敗: {e}</li>"
    return news_html

# === 政經局勢（Reuters World） ===
def fetch_geo():
    url = "https://www.reuters.com/world/"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("a[href*='/world/']")[:8]
        geo_html = ""
        for a in articles:
            title = a.get_text(strip=True)
            link = "https://www.reuters.com" + a.get("href")
            geo_html += f'<li><a href="{link}" target="_blank">{title}</a></li>'
        return geo_html
    except Exception as e:
        return f"<li>政經局勢讀取失敗: {e}</li>"

# === 更新 index.html ===
def update_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_path = "index.html"

    # 讀取現有 HTML
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        html = "<html><head><meta charset='utf-8'><title>Daily Report</title></head><body></body></html>"

    # 刪除舊資料區塊
    html = re.sub(r"<h2>📈 全球股市指數.*</body>", "</body>", html, flags=re.S)

    # 新資料區塊
    new_content = f"""
<h2>📈 全球股市指數（更新時間：{now}）</h2>
<ul>
{fetch_markets()}
</ul>

<h2>📰 國際重大新聞（英文）</h2>
<ul>
{fetch_news_en()}
</ul>

<h2>📰 國際重大新聞（中文）</h2>
<ul>
{fetch_news_zh()}
</ul>

<h2>🌐 政經局勢摘要</h2>
<ul>
{fetch_geo()}
</ul>
</body>
"""
    html = html.replace("</body>", new_content)

    # 寫回 HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update_html()
    print("首頁更新完成 ✅")
