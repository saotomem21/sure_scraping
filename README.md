# Webスクレイピングアプリケーション

PythonとNode.jsで構築されたWebスクレイピングアプリケーションです。

## 機能

- Webスクレイピング機能
- HTML解析と保存機能
- Flaskを使用したWebインターフェース
- Tailwind CSSによるスタイリング
- Webpackによるバンドル

## 必要環境

- Python 3.x
- Node.js

## インストール方法

1. リポジトリをクローン
2. Pythonの依存関係をインストール:
   ```bash
   pip install -r requirements.txt
   ```
3. Node.jsの依存関係をインストール:
   ```bash
   npm install
   ```

## 使用方法

1. Flask開発サーバーを起動:
   ```bash
   python app.py
   ```
2. Webインターフェースにアクセス: `http://localhost:5000`

## プロジェクト構成

- `app.py` - メインのFlaskアプリケーション
- `analyze_html.py` - HTML解析スクリプト
- `save_html.py` - HTML保存機能
- `webpack.config.js` - Webpack設定
- `tailwind.config.js` - Tailwind CSS設定
- `templates/` - HTMLテンプレート（親ディレクトリに配置）

## ライセンス

MIT
