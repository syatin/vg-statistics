from app.app import app
from app.database import db
from app.models import MHeros, MItems, Matches, Players, Participants, Rosters, StatHeros, StatSynergy

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
    match_model_list = Matches.query.filter(Matches.gameMode == gamemode).\
        order_by(Matches.createdAt.desc()).all()

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
    ヒーロー統計
    """
    stat_hero_models = []
    for participant_model in participant_models:
        createdAt = match_model.createdAt
        monday = createdAt - timedelta(days=-createdAt.weekday())
        week = monday.replace(hour=0, minute=0, second=0, microsecond=0)

        stat_hero_model = StatHeros.query.filter(
            StatHeros.hero_id == participant_model.hero_id,
            StatHeros.patchVersion == match_model.patchVersion,
            StatHeros.gameMode == match_model.gameMode,
            StatHeros.week == week,
            StatHeros.shardId == match_model.shardId,
            StatHeros.rank == participant_model.rank,
            StatHeros.role == participant_model.role,
            StatHeros.duration_type == _get_duration_type(match_model.duration),
            StatHeros.build_type == participant_model.build_type
        ).first()
        if stat_hero_model is None:
            stat_hero_model = StatHeros(
                hero_id=participant_model.hero_id,
                patchVersion=match_model.patchVersion,
                gameMode=match_model.gameMode,
                week=week,
                shardId=match_model.shardId,
                rank=participant_model.rank,
                role=participant_model.role,
                duration_type=_get_duration_type(match_model.duration),
                build_type=participant_model.build_type,
                games=0,
                wins=0
            )
        stat_hero_model.games += 1
        if participant_model.winner == True:
            stat_hero_model.wins += 1
        stat_hero_models.append(stat_hero_model)
    return stat_hero_models

def _get_duration_type(duration):
    if duration < 15 * 60:
        return 10
    elif duration < 20 * 60:
        return 15
    elif duration < 25 * 60:
        return 20
    elif duration < 30 * 60:
        return 25
    else:
        return 30

def _create_hero_synergy(match_model, participant_models_by_rosters):
    """
    ヒーロー相性統計
    """
    hero_synergy_models = []
    for k in range(0, len(participant_models_by_rosters) -1):
        participant_models = participant_models_by_rosters[k]
        participant_models_enemy = participant_models_by_rosters[1 - k]

        # チーム別の participant リスト
        for i in range(0, len(participant_models) - 1):
            p1 = participant_models[i]
            synergy_base = StatSynergy.query.filter(
                StatSynergy.patchVersion == match_model.patchVersion,
                StatSynergy.gameMode == match_model.gameMode,
                StatSynergy.hero_id_1 == p1.hero_id,
                StatSynergy.role_1 == p1.role,
                StatSynergy.hero_id_2 == None,
                StatSynergy.role_2 == None,
                StatSynergy.is_enemy == False
            ).first()
            if (synergy_base is None):
                synergy_base = StatSynergy(
                    patchVersion=match_model.patchVersion,
                    gameMode=match_model.gameMode,
                    hero_id_1=p1.hero_id,
                    role_1=p1.role,
                    hero_id_2=None,
                    role_2=None,
                    is_enemy=False, games=0, wins=0, win_rate=0
                )
            synergy_base.games += 1
            if p1.winner == True:
                synergy_base.wins += 1
            synergy_base.win_rate = synergy_base.wins / synergy_base.games
            hero_synergy_models.append(synergy_base)

            # 味方との相性
            for j in range(0, len(participant_models) - 1):
                p2 = participant_models[j]
                if p1 == p2:
                    continue
                synergy_ally = StatSynergy.query.filter(
                    StatSynergy.patchVersion == match_model.patchVersion,
                    StatSynergy.gameMode == match_model.gameMode,
                    StatSynergy.hero_id_1 == p1.hero_id,
                    StatSynergy.role_1 == p1.role,
                    StatSynergy.hero_id_2 == p2.hero_id,
                    StatSynergy.role_2 == p2.role,
                    StatSynergy.is_enemy == False
                ).first()
                if synergy_ally is None:
                    synergy_ally = StatSynergy(
                        patchVersion=match_model.patchVersion,
                        gameMode=match_model.gameMode,
                        hero_id_1=p1.hero_id,
                        role_1=p1.role,
                        hero_id_2=p2.hero_id,
                        role_2=p2.role,
                        is_enemy=False, games=0, wins=0, win_rate=0
                    )
                synergy_ally.games += 1
                if p1.winner == True:
                    synergy_ally.wins += 1
                synergy_ally.win_rate = synergy_ally.wins / synergy_ally.games
                hero_synergy_models.append(synergy_ally)

            # 敵との相性
            for j in range(0, len(participant_models_enemy) -1):
                p2 = participant_models_enemy[j]
                synergy_enemy = StatSynergy.query.filter(
                    StatSynergy.patchVersion == match_model.patchVersion,
                    StatSynergy.gameMode == match_model.gameMode,
                    StatSynergy.hero_id_1 == p1.hero_id,
                    StatSynergy.role_1 == p1.role,
                    StatSynergy.hero_id_2 == p2.hero_id,
                    StatSynergy.role_2 == p2.role,
                    StatSynergy.is_enemy == True
                ).first()
                if synergy_enemy is None:
                    synergy_enemy = StatSynergy(
                        patchVersion=match_model.patchVersion,
                        gameMode=match_model.gameMode,
                        hero_id_1=p1.hero_id,
                        role_1=p1.role,
                        hero_id_2=p2.hero_id,
                        role_2=p2.role,
                        is_enemy=True, games=0, wins=0, win_rate=0
                    )
                synergy_enemy.games += 1
                if p1.winner == True:
                    synergy_enemy.wins += 1
                synergy_enemy.win_rate = synergy_enemy.wins / synergy_enemy.games
                hero_synergy_models.append(synergy_enemy)

    return hero_synergy_models






# 実行！
main(gamemode)