import requests
import traceback
from time import sleep

from app.app import app
from app.database import db
from app.models import VgproLeaderboard

"""
VGPROのリーダーボードから、各ゲームモードでRank7以上のプレイヤーのデータを引っ張ってくるバッチです。

実行
nohup python get_vgpro_leaderboard.py >> get_vgpro_leaderboard.py.log &
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
            app.logger.info(requesturl+'?limit=10&offset='+str(offset))

            is_under_threshold = False
            leaderboard = None
            try:
                params = {"limit": 10, "offset": offset}
                http = requests.get(requesturl, headers=headers, params=params)
                leaderboard = http.json()
            except:
                app.logger.error(traceback.print_exc())
                app.logger.info('retry in 5 seconds...')
                sleep(5) # 少し休んでからリトライさせる
                continue

            for player in leaderboard:
                try:
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
                except:
                    app.logger.error(player)
                    app.logger.error(traceback.print_exc())

            if is_under_threshold:
                break
            else:
                offset = offset + 10
                # 連続リクエストすると不味そうなので気休め程度にスリープする
                sleep(2)
