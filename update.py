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

# === 英文新聞 RSS ===
RSS_LIST_EN = [
    ("BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    ("CNN Top Stories", "http://rss.cnn.com/rss/edition.rss"),
    # Reuters 官方 HTTPS RSS，如果解析失敗會跳過
    ("Reuters World", "https://www.reuters.com/rssFeed/worldNews")
]

def fetch_rss_news(rss_list):
    html = ""
    for name, url in rss_list:
        try:
            r = requests.get(url, timeout=10)
            r.encoding = r.apparent_encoding
            root = ET.fromstring(r.text)
            items = root.findall(".//item")[:20]
            for item in items:
                title = item.find("title").text if item.find("title") is not None else "無標題"
                link = item.find("link").text if item.find("link") is not None else "#"
                html += f'<li><a href="{link}" target="_blank">{title}</a> <small>({name})</small></li>\n'
        except Exception as e:
            html += f"<li>{name} 讀取失敗: {e}</li>\n"
    return html

# === 中文新聞 RSS (中央社國際) ===
def fetch_cn_news():
    name = "中央社國際"
    url = "https://feeds.feedburner.com/rsscna/intworld"
    html = ""
    try:
        r = requests.get(url, timeout=10)
        r.encoding = r.apparent_encoding
        root = ET.fromstring(r.text)
        items = root.findall(".//item")[:20]
        for item in items:
            title = item.find("title").text if item.find("title") is not None else "無標題"
            link = item.find("link").text if item.find("link") is not None else "#"
            html += f'<li><a href="{link}" target="_blank">{title}</a> <small>({name})</small></li>\n'
    except Exception as e:
        html += f"<li>{name} 讀取失敗: {e}</li>\n"
    return html

# === 政經摘要 ===
def fetch_geo():
    try:
        r = requests.get("https://www.reuters.com/world/", timeout=10)
        r.encoding = r.apparent_encoding
        soup_text = r.text
        links = re.findall(r'href="(/world/[^"]+)"', soup_text)[:8]
        geo_html = ""
        for link in links:
            url = "https://www.reuters.com" + link
            title = link.split("/")[-1].replace("-", " ").title()
            geo_html += f'<li><a href="{url}" target="_blank">{title}</a></li>\n'
        return geo_html
    except:
        return "<li>Reuters 讀取失敗</li>"

# === 更新首頁 ===
def update_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_path = "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    import re
    html = re.sub(r"<h2>📈 全球股市指數.*</body>", "</body>", html, flags=re.S)

    new_block = f"""
<h2>📈 全球股市指數（更新時間：{now}）</h2>
<ul>{fetch_markets()}</ul>

<h2>📰 國際重大新聞（英文）</h2>
<ul>{fetch_rss_news(RSS_LIST_EN)}</ul>

<h2>📰 國際重大新聞（中文）</h2>
<ul>{fetch_cn_news()}</ul>

<h2>🌐 政經局勢摘要</h2>
<ul>{fetch_geo()}</ul>
</body>
"""
    html = html.replace("</body>", new_block)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("首頁更新完成 ✅")

if __name__ == "__main__":
    update_html()

