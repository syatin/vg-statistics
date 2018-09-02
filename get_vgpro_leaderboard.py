import requests
from time import sleep

from app.app import app
from app.database import db
from app.models import VgproLeaderboard

"""
VGPROのリーダーボードから、各ゲームモードでRank7以上のプレイヤーのデータを引っ張ってくるバッチです。

実行
python get_vgpro_leaderboard.py
"""

apiurl = 'https://api.vgpro.gg/leaderboard'
headers = {
    "Accept": "application/vnd.api+json",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Host": "api.vgpro.gg"
}

# Skill Tier ポイントの足切り設定
# ポイントとランクの対応表
# https://brokenmyth.net/skill-tier-point-far-next-tier/
threshold_points = 1600 # 7b

for gamemode in ['ranked', 'ranked5v5', 'blitz']:
    # region = na, eu, ea, sg(sea), sa, cn
    for region in ['na', 'eu', 'ea', 'sg', 'sa', 'cn']:
        requesturl = '{apiurl}/{gamemode}/{region}'.format(**{
            'apiurl': apiurl,
            'gamemode': gamemode,
            'region': region
        })
        offset = 0

        while True:
            is_under_threshold = False
            params = {"limit": 10, "offset": offset}
            http = requests.get(requesturl, headers=headers, params=params)
            print(requesturl+'?limit=10&offset='+str(offset))
            leaderboard = http.json()
            for player in leaderboard:
                if float(player['points']) < threshold_points:
                    is_under_threshold = True
                    break
                else:
                    winRate = int(player['winRate'].replace('%','')) if type(player['winRate']) is str else player['winRate']
                    kp = int(player['kp'].replace('%','')) if type(player['kp']) is str else player['kp']
                    playerModel = VgproLeaderboard(
                        gamemode = gamemode,
                        region = region,
                        playerId = player['playerId'],
                        name = player['name'],
                        tier = int(player['tier']),
                        position = player['position'],
                        points = float(player['points']),
                        kda = player['kda'],
                        winRate = winRate,
                        kp = kp,
                        games = player['games'],
                        wins = player['wins']
                    )
                    db.session.add(playerModel)
                    db.session.commit()

            if is_under_threshold:
                break
            else:
                offset = offset + 10
                # 連続リクエストすると不味そうなので気休め程度にスリープする
                sleep(2)
