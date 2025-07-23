from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import hashlib, datetime
from pymongo import MongoClient

# ---------- 1. 连接 MongoDB ----------
client = MongoClient("mongodb://localhost:27017")
db = client["diecast"]
col = db["items"]
# 确保 item_no 唯一
col.create_index("item_no", unique=True)

def crawl():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.1stopdiecast.com/", timeout=60000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("tr")
    new_cnt = 0
    for tr in rows:
        text = tr.get_text(" ", strip=True)
        if "Item #:" not in text or "$" not in text:
            continue
        try:
            title = text.split("Item #:")[0].strip()
            item_no = text.split("Item #:")[1].split("$")[0].strip()
            price = "$" + text.split("$")[-1].split()[0]
            doc = {
                "title": title,
                "item_no": item_no,
                "price": price,
                "ts": datetime.datetime.utcnow()
            }
            # 用 upsert 保证增量
            res = col.update_one({"item_no": item_no}, {"$set": doc}, upsert=True)
            if res.upserted_id:
                new_cnt += 1
        except Exception:
            continue
    print(f"✅ MongoDB 新增 {new_cnt} 条记录")


if __name__ == "__main__":
    crawl()

