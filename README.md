# vg-statistics

## Preparation


Get **Development API key** via [Vainglory Developer Portal](https://developer.vainglorygame.com/).


## How to get started

1. Python + MySQL の環境構築
2. MySQLにvaingloryデータベースを作成しておく
3. このプロジェクトを`git clone`
    - pyenv と pyenv-virtualenv を使い、プロジェクトのディレクトリをPython3.6 にして下さい。
    - [【Python】pyenv pyenv-virtualenvの使い方](https://qiita.com/akidroid/items/9f983f875e98eae2fda8)
4. プロジェクトフォルダにて初期化
    ```
    pip install -r requirements.txt
    pip uninstall python-gamelocker
    pip install git+https://github.com/syatin/python-gamelocker.git
    ```
5. `app/config.py` を作成し設定情報を記載。内容は下記を参考にして下さい。  
```python
"""
git管理したくない情報です
"""
class DevelopmentConfig:
    # Vainglory API key
    # https://developer.vainglorygame.com/apps?locale=en
    API_KEY_CN = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい（CN用）'
    API_KEY_EA = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい（EA用）'
    API_KEY_EU = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい（EU用）'
    API_KEY_NA = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい（NA用）'
    API_KEY_SA = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい（SA用）'
    API_KEY_SG = 'あなたのVainglory DEVELOPMENT API KEY をここに貼り付けて下さい（SEA用）'

    # Flask
    DEBUG = True

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/vainglory'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

Config = DevelopmentConfig
```
6. テーブル作成
    - `sql/*` 直下のファイル群を上から順番に実行。
    - `sql/00-create_m_heroes_2018-09-14.sql`
    - `sql/01-create_m_items_2018-09-14.sql`
    - `sql/02-create_tables.sql`
    - （全ファイル終わるまでやる）

## 試合履歴の取得

```sh
# 3v3 地域別
nohup python get_match_history.py ranked na >> log/get_match_history_3v3_na.log & echo $! > 3v3_na.pid
nohup python get_match_history.py ranked eu >> log/get_match_history_3v3_eu.log & echo $! > 3v3_eu.pid
nohup python get_match_history.py ranked ea >> log/get_match_history_3v3_ea.log & echo $! > 3v3_ea.pid
nohup python get_match_history.py ranked sg >> log/get_match_history_3v3_sg.log & echo $! > 3v3_sg.pid
nohup python get_match_history.py ranked sa >> log/get_match_history_3v3_sa.log & echo $! > 3v3_sa.pid
nohup python get_match_history.py ranked cn >> log/get_match_history_3v3_cn.log & echo $! > 3v3_cn.pid

# 5v5 地域別
nohup python get_match_history.py ranked5v5 na >> log/get_match_history_5v5_na.log & echo $! > 5v5_na.pid
nohup python get_match_history.py ranked5v5 eu >> log/get_match_history_5v5_eu.log & echo $! > 5v5_eu.pid
nohup python get_match_history.py ranked5v5 ea >> log/get_match_history_5v5_ea.log & echo $! > 5v5_ea.pid
nohup python get_match_history.py ranked5v5 sg >> log/get_match_history_5v5_sg.log & echo $! > 5v5_sg.pid
nohup python get_match_history.py ranked5v5 sa >> log/get_match_history_5v5_sa.log & echo $! > 5v5_sa.pid
nohup python get_match_history.py ranked5v5 cn >> log/get_match_history_5v5_cn.log & echo $! > 5v5_cn.pid
```

## リーダーボード取得バッチ

1. `sql/create_tables.sql` を実行してテーブル作成
2. `python get_vgpro_leaderboard.py`
3. 10時間程度でデータ取得が完了する筈です
