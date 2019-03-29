from app.app import app
from app.database import db
from app.models import MHeroes, MItems, Matches, Players, Participants, Rosters, StatHeroes, StatSynergy, StatHeroes2, StatHeroesDuration
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from requests.exceptions import HTTPError

import gamelocker
from time import sleep
from datetime import datetime, date, timedelta


gamemode = '5v5_pvp_ranked'

def main(gamemode):
    offset = 100
    limit = 100
    while True:
        app.logger.info('offset = ' + str(offset))
        stat_list = StatHeroes.query.\
            order_by(StatHeroes.id).limit(limit).offset(offset).all()

        if stat_list is None or len(stat_list) == 0:
            break

        for stat in stat_list:
            app.logger.info('processing ' + str(stat.id))

            week_correct = None
            week_wrong = stat.week.strftime("%Y-%m-%d")
            app.logger.info(week_wrong)
            if week_wrong == '2018-09-03':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-05':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-07':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-09':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-11':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-13':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-15':
                week_correct = datetime.strptime('2018-09-03', "%Y-%m-%d")
            if week_wrong == '2018-09-10':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-12':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-14':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-16':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-18':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-20':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-22':
                week_correct = datetime.strptime('2018-09-10', "%Y-%m-%d")
            if week_wrong == '2018-09-17':
                week_correct = datetime.strptime('2018-09-17', "%Y-%m-%d")
            if week_wrong == '2018-09-19':
                week_correct = datetime.strptime('2018-09-17', "%Y-%m-%d")
            if week_wrong == '2018-09-21':
                week_correct = datetime.strptime('2018-09-17', "%Y-%m-%d")
            if week_wrong == '2018-09-23':
                week_correct = datetime.strptime('2018-09-17', "%Y-%m-%d")
            if week_wrong == '2018-09-25':
                week_correct = datetime.strptime('2018-09-17', "%Y-%m-%d")
            app.logger.info(week_correct)

            stat2 = StatHeroes2.query_one_or_init({
                'hero_id': stat.hero_id,
                'patchVersion': stat.patchVersion,
                'gameMode': stat.gameMode,
                'week': week_correct,
                'shardId': stat.shardId,
                'rank': stat.rank,
                'role': stat.role,
                'build_type': stat.build_type,
            })
            stat2.games += stat.games
            stat2.wins += stat.wins
            stat2.win_rate = stat2.wins / stat2.games
            db.session.add(stat2)

            stat_duration = StatHeroesDuration.query_one_or_init({
                'patchVersion' : stat.patchVersion,
                'gameMode' : stat.gameMode,
                'shardId' : stat.shardId,
                'hero_id' : stat.hero_id,
                'role' : stat.role,
                'build_type' : stat.build_type,
                'duration_type' : stat.duration_type,
            })
            stat_duration.games += stat.games
            stat_duration.wins += stat.wins
            stat_duration.win_rate = stat_duration.wins / stat_duration.games
            db.session.add(stat_duration)
            db.session.commit()

        offset += limit

# 2018-09-03
# 2018-09-03 -> 2018-09-03
# 2018-09-04 -> 2018-09-05
# 2018-09-05 -> 2018-09-07
# 2018-09-06 -> 2018-09-09
# 2018-09-07 -> 2018-09-11
# 2018-09-08 -> 2018-09-13
# 2018-09-09 -> 2018-09-15

# 2018-09-10
# 2018-09-10 -> 2018-09-10
# 2018-09-11 -> 2018-09-12
# 2018-09-12 -> 2018-09-14
# 2018-09-13 -> 2018-09-16
# 2018-09-14 -> 2018-09-18
# 2018-09-15 -> 2018-09-20
# 2018-09-16 -> 2018-09-22


# 実行！
main(gamemode)
