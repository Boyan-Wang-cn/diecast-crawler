from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import hashlib,json, datetime
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
    results = []
    for tr in rows:
        text = tr.get_text(" ", strip=True)
        if "Item #:" not in text or "$" not in text:
            continue
        try:
            title = text.split("Item #:")[0].strip()
            item_no = text.split("Item #:")[1].split("$")[0].strip()
            price = "$" + text.split("$")[-1].split()[0]
            # 取图片 URL（第一张 img 的 src）
            img_tag = tr.select_one("img.prodlistimg")
            img_url = img_tag["src"] if img_tag else None

            doc = {
                "title": title,
                "item_no": item_no,
                "price": price,
                "image": img_url,
                "ts": datetime.datetime.utcnow().isoformat() + "Z"
            }
            # upsert 入库
            col.update_one({"item_no": item_no}, {"$set": doc}, upsert=True)
            results.append(doc)
        except Exception:
            continue
    # 写 JSON 文件
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    crawl()

