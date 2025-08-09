import os
import re
import requests
from bs4 import BeautifulSoup
import time
import csv

# --- 設定 ---
KINDLE_FOLDER = r"~/Library/Application Support/Kindle/My Kindle Content/"  # パスを自分の環境に合わせて変更
CSV_OUTPUT_PATH = r"/Users/michika_maruyama/Desktop/kindle_coding/booklist/kindle_books.csv"
DELAY_SECONDS = 2

# 毎回の実行前に仮想環境を有効化する
# source .venv/bin/activate
# pip install -r requirements.txt

# --- 関数 ---
def extract_asin(filename):
    match = re.match(r"(B[A-Z0-9]{9})_EBOK", filename)
    return match.group(1) if match else None

def get_amazon_title(asin):
    url = f"https://www.amazon.co.jp/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        title_tag = soup.find(id="productTitle")
        if title_tag:
            return title_tag.get_text(strip=True)
    except Exception as e:
        print(f"[ERROR] {asin}: {e}")
    return None

# --- 実行 ---
if __name__ == "__main__":
    asin_title_list = []

    # サブフォルダを含めて再帰的にファイルを探索
    for root, dirs, files in os.walk(KINDLE_FOLDER):
        for fname in files:
            print(f"Checking file: {fname}")
            if fname.endswith(".azw"):
                asin = extract_asin(fname)
                if asin:
                    print(f"Fetching title for {asin}...")
                    title = get_amazon_title(asin)
                    title = title or "タイトル取得失敗"
                    asin_title_list.append((asin, title))
                    time.sleep(DELAY_SECONDS)

    # CSV 出力
    with open(CSV_OUTPUT_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ASIN", "Title"])
        writer.writerows(asin_title_list)

    print(f"\n📁 書籍一覧を {CSV_OUTPUT_PATH} に保存しました。")
