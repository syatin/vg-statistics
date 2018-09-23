from app.app import app
from app.database import db
from app.models import MHeros, MItems, Matches, Players, Participants, Rosters, StatHeros, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from requests.exceptions import HTTPError

import gamelocker
from time import sleep
from datetime import datetime, date, timedelta

"""
かつての試合履歴からヒーロー統計を作成
"""

gamemode = '5v5_pvp_ranked'

def main(gamemode):
    match_model_list = Matches.query.filter(Matches.gameMode == gamemode, Matches.id >= 742).\
        order_by(Matches.id).all()

    for match_model in match_model_list:
        app.logger.info('processing match id:'+str(match_model.id))

        participant_models_all = Participants.query.\
            filter(Participants.match_id == match_model.id).all()
        
        roster_id_1 = participant_models_all[0].roster_id
        participant_models_1 = []
        participant_models_2 = []
        for participant_model in participant_models_all:
            if participant_model.roster_id == roster_id_1:
                participant_models_1.append(participant_model)
            else:
                participant_models_2.append(participant_model)

        hero_stat_models_1 = _create_stat_heros(match_model, participant_models_1)
        hero_stat_models_2 = _create_stat_heros(match_model, participant_models_2)
        db.session.add_all(hero_stat_models_1)
        db.session.add_all(hero_stat_models_2)

        participant_models_by_rosters = [participant_models_1, participant_models_2]
        hero_synergy_models = _create_hero_synergy(match_model, participant_models_by_rosters)
        db.session.add_all(hero_synergy_models)

        db.session.commit()


def _create_stat_heros(match_model, participant_models):
    """
    ヒーロー統計を計算し、更新があった行を返す
    """
    stat_hero_models = []
    for participant_model in participant_models:
        stat_hero_model = StatHeros.query_one_or_init({
            'hero_id': participant_model.hero_id,
            'patchVersion': match_model.patchVersion,
            'gameMode': match_model.gameMode,
            'week': get_week_start_date(match_model.createdAt),
            'shardId': match_model.shardId,
            'rank': participant_model.rank,
            'role': participant_model.role,
            'duration_type': get_duration_type(match_model.duration),
            'build_type': participant_model.build_type
        })
        stat_hero_model.games += 1
        if participant_model.winner == True:
            stat_hero_model.wins += 1
        stat_hero_model.win_rate = stat_hero_model.wins / stat_hero_model.games

        stat_hero_models.append(stat_hero_model)

    return stat_hero_models


def _create_hero_synergy(match_model, participant_models_by_rosters):
    """
    ヒーロー相性統計を計算し、更新があった行を返す
    """
    # 更新があったモデルリスト
    hero_synergy_models = []

    # 相性計算で使う
    synergy_base_by_hero = {}

    # まずはヒーロー単体での勝率を取得する
    for k in range(0, len(participant_models_by_rosters)):
        participant_models = participant_models_by_rosters[k]

        for i in range(0, len(participant_models)):
            p1 = participant_models[i]
            synergy_base = StatSynergy.query_one_or_init({
                'patchVersion': match_model.patchVersion,
                'gameMode': match_model.gameMode,
                'hero_id_1': p1.hero_id,
                'role_1': p1.role,
                'hero_id_2': None,
                'role_2': None,
                'is_enemy': False
            })
            synergy_base.games += 1
            if p1.winner == True:
                synergy_base.wins += 1
            synergy_base.win_rate = synergy_base.wins / synergy_base.games

            synergy_base_by_hero[p1.actor] = synergy_base
            hero_synergy_models.append(synergy_base)

    # 敵／味方との相性
    for k in range(0, len(participant_models_by_rosters)):
        participant_models = participant_models_by_rosters[k]
        participant_models_enemy = participant_models_by_rosters[1 - k]
        for i in range(0, len(participant_models)):
            p1 = participant_models[i]

            # 味方との相性
            for j in range(0, len(participant_models)):
                p2 = participant_models[j]

                if p1 == p2:
                    continue

                synergy_ally = StatSynergy.query_one_or_init({
                    'patchVersion': match_model.patchVersion,
                    'gameMode': match_model.gameMode,
                    'hero_id_1': p1.hero_id,
                    'role_1': p1.role,
                    'hero_id_2': p2.hero_id,
                    'role_2': p2.role,
                    'is_enemy': False
                })
                synergy_ally.games += 1
                if p1.winner == True:
                    synergy_ally.wins += 1
                synergy_ally.win_rate = synergy_ally.wins / synergy_ally.games

                # シナジー計算(味方)
                if synergy_ally.games >= 50:
                    me = synergy_base_by_hero[p1.actor]
                    ally = synergy_base_by_hero[p2.actor]
                    if me.win_rate != 0 and ally.win_rate != 0:
                        synergy_ally.synergy = (synergy_ally.win_rate * 2) / ((me.win_rate * 2) * (ally.win_rate * 2))

                hero_synergy_models.append(synergy_ally)

            # 敵との相性
            for j in range(0, len(participant_models_enemy)):
                p2 = participant_models_enemy[j]
                synergy_enemy = StatSynergy.query_one_or_init({
                    'patchVersion': match_model.patchVersion,
                    'gameMode': match_model.gameMode,
                    'hero_id_1': p1.hero_id,
                    'role_1': p1.role,
                    'hero_id_2': p2.hero_id,
                    'role_2': p2.role,
                    'is_enemy': True
                })
                synergy_enemy.games += 1
                if p1.winner == True:
                    synergy_enemy.wins += 1
                synergy_enemy.win_rate = synergy_enemy.wins / synergy_enemy.games

                # シナジー計算(敵)
                if synergy_enemy.games >= 50:
                    me = synergy_base_by_hero[p1.actor]
                    enemy = synergy_base_by_hero[p2.actor]
                    if me.win_rate != 0 and enemy.win_rate != 1:
                        synergy_enemy.synergy = (synergy_enemy.win_rate * 2) / ((me.win_rate * 2) * ((1 - enemy.win_rate) * 2))

                hero_synergy_models.append(synergy_enemy)

    return hero_synergy_models


# 実行！
main(gamemode)