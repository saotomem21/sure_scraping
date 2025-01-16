import socket
import logging
from flask import Flask, render_template, request, redirect, url_for, session, make_response, send_file
import argparse
import os
import requests
import tempfile
import uuid
import atexit
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from io import StringIO

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')))
app.secret_key = os.urandom(24)
response_files = {}  # Dictionary to store temporary file paths

def scrape_responses(url):
    # Chromeオプション設定
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # WebDriver起動
    driver = webdriver.Chrome(
        service=ChromeService(executable_path='/Users/saotomem21/chromedriver/chromedriver-mac-arm64/chromedriver'),
        options=options
    )

    try:
        # ページにアクセス
        driver.get(url)
        
        # レスが表示されるまで待機
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.t_b"))
        )
        
        # HTMLを取得
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # 2ch風レスを取得
        responses = soup.select("div.t_b")
        if not responses:
            return None
        
        # レスをリストに格納
        res_list = []
        for res in responses:
            # 不要な要素を除去
            for bad in res.select("script, iframe, .ggl_ad_res1, .adslot_1, #bookmark, #bookmark2, .blogroll-channel"):
                bad.decompose()
            res_list.append(res.get_text("\n", strip=True))
        
        return res_list
    
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    urls = request.form.getlist('target_urls[]')
    if not urls:
        return render_template('responses.html', error=True, status_message='URLが入力されていません')
    
    all_responses = []
    for url in urls:
        logger.info(f"Processing URL: {url}")
        responses = scrape_responses(url)
        
        if responses is None:
            logger.warning(f"No responses found for URL: {url}")
            continue
            
        all_responses.append({
            'url': url,
            'responses': responses
        })
    
    if not all_responses:
        return render_template('responses.html', error=True, status_message="どのURLからもレスが見つかりませんでした")
    
    # Store responses in temporary file
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(tempfile.gettempdir(), f"responses_{file_id}.csv")
    logger.debug(f"Creating temporary CSV file at: {temp_path}")
    
    # Write responses to CSV file
    with open(temp_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "レス番号", "内容"])
        for url_data in all_responses:
            for i, res in enumerate(url_data['responses'], 1):
                writer.writerow([url_data['url'], i, res])
    
    logger.info(f"Successfully wrote {sum(len(url_data['responses']) for url_data in all_responses)} responses to CSV")
    response_files[file_id] = temp_path
    logger.debug(f"Stored file reference with ID: {file_id}")
    
    return render_template('responses.html', responses=all_responses, file_id=file_id)

@app.route('/download')
def download():
    file_id = request.args.get('file_id')
    filename = request.args.get('filename', 'responses.csv')
    logger.info(f"Download request received for file ID: {file_id}")
    
    if not file_id or file_id not in response_files:
        logger.warning(f"Invalid or missing file ID: {file_id}")
        return "解析が完了していません。まずURLを入力して解析を実行してください"
    
    temp_path = response_files[file_id]
    logger.debug(f"Looking for file at: {temp_path}")
    
    if not os.path.exists(temp_path):
        logger.error(f"File not found at specified path: {temp_path}")
        return "ファイルの有効期限が切れています。再度解析を実行してください"
    
    logger.info(f"Sending file: {temp_path}")
    try:
        return send_file(
            temp_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Failed to send file: {str(e)}")
        return "ファイルの送信中にエラーが発生しました"

def find_available_port(start_port):
    import socket
    port = start_port
    max_attempts = 10
    attempts = 0
    
    while attempts < max_attempts:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                s.listen(1)
                s.close()
                logger.info(f"Successfully bound to port {port}")
                return port
        except OSError as e:
            logger.warning(f"Port {port} unavailable: {e}")
            port += 1
            attempts += 1
    raise RuntimeError(f"Could not find available port after {max_attempts} attempts")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='ポート番号')
    args = parser.parse_args()
    
    try:
        port = find_available_port(args.port)
        logger.info(f" * Running on http://127.0.0.1:{port} (also accessible via your local network IP)")
        logger.info(f" * Accessible at http://{socket.gethostbyname(socket.gethostname())}:{port}")
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error("Please check:")
        logger.error("1. No other services are using the same port")
        logger.error("2. Your firewall allows connections to this port")
        logger.error("3. Your network configuration allows local connections")
