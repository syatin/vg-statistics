# vg-statistics

## How to get started

1. Python + MySQL の環境構築
2. MySQLにvaingloryデータベースを作成しておく
3. このプロジェクトを`git clone`
4. プロジェクトフォルダにて`pip install -r requirements.txt`
5. `app/config.py` を作成し設定情報を記載。内容は下記を参考にして下さい。  
```python
"""
git管理したくない情報です
"""
class DevelopmentConfig:
    # Vainglory API key
    # https://developer.vainglorygame.com/apps?locale=en
    API_KEY = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい'

    # Flask
    DEBUG = True

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/vainglory'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

Config = DevelopmentConfig
```

## リーダーボード取得バッチ

1. `sql/create_tables.sql` を実行してテーブル作成
2. `python get_vgpro_leaderboard.py`
3. 10時間程度でデータ取得が完了する筈です
