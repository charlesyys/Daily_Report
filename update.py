import requests
from bs4 import BeautifulSoup
import yfinance as yf
import datetime
import re
import xml.etree.ElementTree as ET
import pytz # 🚨 新增：用於時區處理

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
    """獲取股市數據並格式化為 HTML 列表"""
    rows = ""
    for name, symbol in markets.items():
        ticker = yf.Ticker(symbol)
        try:
            # yfinance 的 fast_info 提供了快速獲取最新價格的方式
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
    """從 RSS 連結獲取新聞並格式化為 HTML 列表"""
    html = ""
    for name, url in rss_list:
        try:
            r = requests.get(url, timeout=10)
            r.encoding = r.apparent_encoding
            # 使用 ET.fromstring 處理 XML
            root = ET.fromstring(r.text)
            items = root.findall(".//item")[:20]
            # 尋找前 20 條新聞
            for item in items:
                title = item.find("title").text if item.find("title") is not None else "無標題"
                link = item.find("link").text if item.find("link") is not None else "#"
                html += f'<li><a href="{link}" target="_blank">{title}</a> <small>({name})</small></li>\n'
        except Exception as e:
            # 錯誤處理
            html += f"<li>{name} 讀取失敗: {e}</li>\n"
    return html

# === 中文新聞 RSS (中央社國際) ===
RSS_LIST_CN = [
    # 國際與綜合 (中央社 - 保持)
    ("中央社 國際", "https://feeds.feedburner.com/rsscna/intworld"),
    # 國際與綜合 (東森新聞)
    ("東森新聞 焦點", "https://news.ebc.net.tw/Rss/news"),
    # Google
    ("Google News 台灣焦點", "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
    # 財經專業 (ETtoday 財經)
    ("ETtoday 財經", "https://feeds.feedburner.com/ettoday/finance"),
    # 新增: 台灣證券交易所)
    #("台灣股市焦點", "https://www.taifex.com.tw/cht/11/RSS2")
]

def fetch_cn_news():
    """從中央社國際獲取中文新聞"""
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
    # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # 🚨 修正時區問題：使用 pytz 獲取 Asia/Taipei (CST/GMT+8) 時間
    taipei_tz = pytz.timezone('Asia/Taipei') 
    now_taipei = datetime.datetime.now(taipei_tz)
    
    # 格式化時間戳
    now_str = now_taipei.strftime("%Y-%m-%d %H:%M:%S (CST/GMT+8)")
    
    html_path = "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 找到 <body> 後第一個 <h2>📈 全球股市指數 的位置
    body_start, sep, _ = html.partition("<h2>📈 全球股市指數")
    head_part, sep_head, _ = body_start.partition("<body>")
    
    # 保留 <head> 區塊，只從 <body> 開始插入新資料
    html = head_part + sep_head  

    new_block = f"""
<h2>📈 全球股市指數（更新時間：{now_str}）</h2>
<ul>{fetch_markets()}</ul>

<h2>📰 國際重大新聞（英文）</h2>
<ul>{fetch_rss_news(RSS_LIST_EN)}</ul>

<h2>📰 國際重大新聞（中文）</h2>
<ul>{fetch_rss_news(RSS_LIST_CN)}</ul>

</body>
"""
    html += new_block

    # 寫回 HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    #print("首頁更新完成 ✅")
    print(f"首頁更新完成，時間：{now_str} ✅")

if __name__ == "__main__":
    update_html()

