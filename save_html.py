import requests
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = "https://www.calciomatome.net/article/508934697.html"
time.sleep(5)  # 5秒待機
r = requests.get(url, headers=headers)

with open("page.html", "w", encoding="utf-8") as f:
    f.write(r.text)
