import os
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime
import re

# === 確保 index.htm 存在 ===
html_path = "index.html"
if not os.path.exists(html_path):
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>Daily Report</title>
</head>
<body>
<h1>每日國際經濟與新聞報告</h1>

<h2>📈 全球股市指數</h2>
<ul></ul>

<h2>📰 國際重大新聞（英文）</h2>
<ul></ul>

<h2>📰 國際重大新聞（中文）</h2>
<ul></ul>

<h2>🌐 政經局勢摘要</h2>
<ul></ul>

</body>
</html>""")

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
        try:
            ticker = yf.Ticker(symbol)
            price = round(ticker.fast_info["lastPrice"], 2)
            rows += f"<li>{name}: {price}</li>"
        except:
            rows += f"<li>{name}: 讀取失敗</li>"
    return rows

# === 英文新聞 (Google News RSS) ===
def fetch_news_en():
    url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.find_all("item")[:20]
        news_list = []
        for item in items:
            title = item.title.text.strip()
            link = item.link.text.strip()
            news_list.append(f'<li><a href="{link}" target="_blank">{title}</a></li>')
        return "\n".join(news_list)
    except:
        return "<li>英文新聞讀取失敗</li>"

# === 中文新聞 (聯合新聞網國際 RSS) ===
def fetch_news_zh():
    url = "https://udn.com/rssfeed/news/1/國際"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "xml")
        items = soup.find_all("item")[:20]
        news_list = []
        for item in items:
            title = item.title.text.strip()
            link = item.link.text.strip()
            news_list.append(f'<li><a href="{link}" target="_blank">{title}</a></li>')
        return "\n".join(news_list)
    except:
        return "<li>中文新聞讀取失敗</li>"

# === 政經局勢 (Reuters World) ===
def fetch_geo():
    url = "https://www.reuters.com/world/"
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("a[href*='/world/']")[:20]
        geo_html = ""
        for a in articles:
            title = a.get_text(strip=True)
            link = "https://www.reuters.com" + a.get("href")
            geo_html += f'<li><a href="{link}" target="_blank">{title}</a></li>'
        return geo_html
    except:
        return "<li>政經局勢讀取失敗</li>"

# === 更新 index.htm ===
def update_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 刪除舊資料區塊
    html = re.sub(r"<h2>📈 全球股市指數.*?<\/ul>", "", html, flags=re.S)
    html = re.sub(r"<h2>📰 國際重大新聞（英文）.*?<\/ul>", "", html, flags=re.S)
    html = re.sub(r"<h2>📰 國際重大新聞（中文）.*?<\/ul>", "", html, flags=re.S)
    html = re.sub(r"<h2>🌐 政經局勢摘要.*?<\/ul>", "", html, flags=re.S)

    # 新資料
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

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update_html()
    print("首頁更新完成 ✅")
