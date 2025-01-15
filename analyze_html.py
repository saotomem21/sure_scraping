import requests
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

url = "https://www.calciomatome.net/article/508934697.html"

# リクエスト間隔を空ける
time.sleep(5)

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.text, "html.parser")

# HTML全体を表示
print(soup.prettify())
