# vg-statistics

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
    pip install git+https://github.com/yamadar/python-gamelocker.git
    ```
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
6. テーブル作成
    - `sql/create_tables.sql`
    - `sql/m_heros_2018-09-14.sql`
    - `sql/m_items_2018-09-14.sql`

## 試合履歴の取得

```sh
# 3v3 地域別
nohup python get_match_history.py ranked na >> get_match_history_3v3_na.log &
nohup python get_match_history.py ranked eu >> get_match_history_3v3_eu.log &
nohup python get_match_history.py ranked ea >> get_match_history_3v3_ea.log &
nohup python get_match_history.py ranked sg >> get_match_history_3v3_sg.log &
nohup python get_match_history.py ranked sa >> get_match_history_3v3_sa.log &
nohup python get_match_history.py ranked cn >> get_match_history_3v3_cn.log &

# 5v5 地域別
nohup python get_match_history.py ranked5v5 na >> get_match_history_5v5_na.log &
nohup python get_match_history.py ranked5v5 eu >> get_match_history_5v5_eu.log &
nohup python get_match_history.py ranked5v5 ea >> get_match_history_5v5_ea.log &
nohup python get_match_history.py ranked5v5 sg >> get_match_history_5v5_sg.log &
nohup python get_match_history.py ranked5v5 sa >> get_match_history_5v5_sa.log &
nohup python get_match_history.py ranked5v5 cn >> get_match_history_5v5_cn.log &
```

## リーダーボード取得バッチ

1. `sql/create_tables.sql` を実行してテーブル作成
2. `python get_vgpro_leaderboard.py`
3. 10時間程度でデータ取得が完了する筈です
