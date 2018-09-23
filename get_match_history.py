import gamelocker
import sys, traceback, time

from app.app import app
from app.database import db
from app.models import MHeros, MItems, Matches, Players, Participants, Rosters, StatHeros, StatHerosDuration, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from requests.exceptions import HTTPError
from datetime import datetime, date, timedelta
from time import sleep

"""
Usage
nohup python get_match_history.py ranked na >> get_match_history_3v3_na.log &
nohup python get_match_history.py ranked eu >> get_match_history_3v3_eu.log &
nohup python get_match_history.py ranked ea >> get_match_history_3v3_ea.log &
nohup python get_match_history.py ranked sg >> get_match_history_3v3_sg.log &
nohup python get_match_history.py ranked sa >> get_match_history_3v3_sa.log &
nohup python get_match_history.py ranked cn >> get_match_history_3v3_cn.log &

nohup python get_match_history.py ranked5v5 na >> get_match_history_5v5_na.log &
nohup python get_match_history.py ranked5v5 eu >> get_match_history_5v5_eu.log &
nohup python get_match_history.py ranked5v5 ea >> get_match_history_5v5_ea.log &
nohup python get_match_history.py ranked5v5 sg >> get_match_history_5v5_sg.log &
nohup python get_match_history.py ranked5v5 sa >> get_match_history_5v5_sa.log &
nohup python get_match_history.py ranked5v5 cn >> get_match_history_5v5_cn.log &

# Reference
https://developer.vainglorygame.com/docs#get-a-collection-of-players

## filter[gameMode]
- blitz_pvp_ranked
- casual_aral
- casual
- ranked
- 5v5_pvp_ranked
- 5v5_pvp_casual
"""

PATCH_VERSION = '3.7'
LIMIT = 5

args = sys.argv
if len(args) != 3:
    print('Specify gamemode and region. example : ranked5v5 ea')
    exit()

gamemode = args[1]
if gamemode not in  ['ranked', 'ranked5v5', 'blitz']:
    print('{} is not valid gamemode'.format(gamemode))
    exit()

region = args[2]
if region not in ['na', 'eu', 'ea', 'sg', 'sa', 'cn']:
    print('{} is not valid region'.format(vgpro_region))
    exit()

def main(gamemode, region):
    if gamemode == 'ranked5v5':
        gamemode = '5v5_pvp_ranked'
    if gamemode == 'blitz':
        gamemode = 'blitz_pvp_ranked'

    while True:
        # 最後に処理した試合の後から取得する
        created_at = None
        last_match = Matches.query.filter(
            Matches.gameMode == gamemode,
            Matches.shardId == region
        ).order_by(Matches.createdAt.desc()).first()
        if last_match:
            created_at = last_match.createdAt.isoformat() + 'Z'
        else:
            # 未処理の場合は2週間前を起点とする
            two_weeks_ago = datetime.fromtimestamp(time.time()) - timedelta(weeks=2)
            created_at = two_weeks_ago.isoformat() + 'Z'

        # 処理本体の呼び出し
        retrieve_match_history(gamemode=gamemode, region=region, created_at=created_at)

        # 処理が一段落したら、Vain側に試合データが溜まるのを待つ
        sleep(30)


def retrieve_match_history(gamemode, region, created_at):
    """
    Gamelocker API から試合履歴を取得し諸々処理して保存する
    """
    offset = 0
    app.logger.info('gamemode = {}, createdAt = {}'.format(gamemode, str(created_at)))
    while True:
        try:
            app.logger.info('retrieving Gamelocker API data : offset = {}'.format(offset))
            api = gamelocker.Gamelocker(app.config['API_KEY']).Vainglory()
            matches = api.matches({
                'filter[patchVersion]' : PATCH_VERSION,
                'filter[gameMode]': gamemode,
                'filter[createdAt-start]': created_at,
                'page[limit]': LIMIT,
                'page[offset]': offset
            }, region=region)
            if matches is not None:
                processed_count = 0
                for match in matches:
                    processed_count += process_match(match)

                app.logger.info('{} matches were processed.'.format(processed_count))
                if processed_count >= LIMIT - 1:
                    if offset <= 1000:
                        offset += LIMIT
                        continue

                offset = 0
                break

        except HTTPError as e:
            if e.response.status_code == 404:
                app.logger.info('Couldn\'t find match history')
            else:
                app.logger.info(e)
            offset = 0
            break

    app.logger.info('retrieving data done')
    return


def process_match(match):
    """
    1つの試合履歴を処理する
    """
    try:
        match_model = Matches.query.filter_by(uuid=match.id).first()
        if match_model is not None:
            # 処理済なので処理件数は0で返す
            return 0

        app.logger.info('processing a match : id = {}'.format(match.id))

        match_model = Matches(
            uuid=match.id,
            shardId=match.shardId,
            gameMode=match.gameMode,
            duration=match.duration,
            endGameReason=match.stats['endGameReason'],
            patchVersion=match.patchVersion,
            createdAt=datetime.strptime(match.createdAt, '%Y-%m-%dT%H:%M:%SZ')
        )
        db.session.add(match_model)
        db.session.flush()

        # シナジーデータ計算用に Participant モデルのリストを保持する
        participant_models_by_rosters = []

        for roster in match.rosters:
            roster_model = Rosters(
                match_id=match_model.id,
                acesEarned=roster.stats['acesEarned'],
                gold=roster.stats['gold'],
                heroKills=roster.stats['heroKills'],
                krakenCaptures=roster.stats['krakenCaptures'],
                side=roster.stats['side'],
                turretKills=roster.stats['turretKills'],
                turretsRemaining=roster.stats['turretsRemaining'],
                won=1 if roster.won == 'true' else 0,
                averageRankedPoint=0,
                averageRank=0
            )
            db.session.add(roster_model)
            db.session.flush()

            player_count = 0
            total_rank_points = 0

            # ロール特定の為に Participant のモデル一覧を保持する
            participant_models = []

            for participant in roster.participants:
                # プレイヤーの情報を更新
                player_count += 1
                player = participant.player
                player_model = Players.query.filter_by(playerId = player.key_id).first()
                if player_model is None:
                    player_model = Players(playerId=player.key_id, shardId=player.shardId)
                player_model.name = player.name
                player_model.rankPoints = player.stats['rankPoints']
                player_model.gamesPlayed = player.stats['gamesPlayed']
                player_model.guildTag = player.stats['guildTag']
                player_model.karmaLevel = player.stats['karmaLevel']
                player_model.level = player.stats['level']
                player_model.updatedAt = datetime.now()
                db.session.add(player_model)
                db.session.flush()

                # ヒーローID取得
                actor = participant.actor
                hero = MHeros.query.filter(MHeros.actor == actor).first()
                if hero is None:
                    hero = MHeros(actor=actor, ja=actor, en=actor)
                    db.session.add(hero)
                    db.session.flush()

                rank_point_key = 'ranked'
                if match.gameMode == '5v5_pvp_ranked' or match.gameMode == '5v5_pvp_casual':
                    rank_point_key = 'ranked_5v5'
                if match.gameMode == 'casual' or match.gameMode == 'ranked':
                    rank_point_key = 'ranked'
                if match.gameMode == 'blitz_pvp_ranked':
                    rank_point_key == 'blitz'

                rank_point = player_model.rankPoints[rank_point_key]
                rank = get_rank(rank_point)
                total_rank_points = total_rank_points + rank_point
                participant_model = Participants(
                    match_id=match_model.id,
                    roster_id=roster_model.id,
                    player_id=player_model.id,
                    player_name=player_model.name,
                    rankPoint=rank_point,
                    rank=rank,
                    hero_id=hero.id,
                    actor=actor,
                    kills=participant.stats['kills'],
                    assists=participant.stats['assists'],
                    deaths=participant.stats['deaths'],
                    gold=participant.stats['gold'],
                    minionKills=participant.stats['minionKills'],
                    jungleKills=participant.stats['jungleKills'],
                    nonJungleMinionKills=participant.stats['nonJungleMinionKills'],
                    items=participant.stats['items'],
                    itemUses=participant.stats['itemUses'],
                    build_type=get_build_type(participant.stats['items']),
                    wentAfk=participant.stats['wentAfk'],
                    skinKey=participant.stats['skinKey'],
                    winner=participant.stats['winner'],
                )
                participant_models.append(participant_model)

            db.session.add_all(participant_models)
            db.session.flush()

            # ロール割り振り
            patricipant_models_with_role = _assign_role_to_participants(match.gameMode, participant_models)
            db.session.add_all(patricipant_models_with_role)

            participant_models_by_rosters.append(patricipant_models_with_role)

            # ヒーロー統計データ蓄積
            stat_hero_models = _create_stat_heros(match_model, patricipant_models_with_role)
            db.session.add_all(stat_hero_models)

            # 各サイドの平均ランクを保存
            roster_model.averageRankedPoint = total_rank_points / player_count
            roster_model.averageRank = get_rank(roster_model.averageRankedPoint)
            db.session.add(roster_model)
            db.session.flush()

        # シナジーデータ蓄積
        hero_synergy_models = _create_hero_synergy(match_model, participant_models_by_rosters)
        db.session.add_all(hero_synergy_models)

        db.session.commit()

        # 試合を処理したら処理件数(この場合は常に1)を返す
        return 1
    except:
        app.logger.error(traceback.print_exc())
        db.session.rollback()
        return 0


def _assign_role_to_participants(gamemode, participant_models):
    """
    各プレイヤーのCSやビルドからロールを割り振る
    """
    patricipant_models_with_role = []
    if gamemode == 'ranked':
        # 3v3
        sorted_models = sorted(participant_models, key=lambda x:x.minionKills, reverse=True)
        carry_model = sorted_models[0]
        carry_model.role = 'LANE'
        patricipant_models_with_role.append(carry_model)

        jungler_model = sorted_models[1]
        jungler_model.role = 'JUNGLE'
        patricipant_models_with_role.append(jungler_model)

        captain_model = sorted_models[2]
        if captain_model.build_type == 'WP' or captain_model.build_type == 'CP':
            # 低階層などのキャプテン無し構成
            captain_model.role = 'JUNGLE'
        else:
            captain_model.role = 'CAPTAIN'
        patricipant_models_with_role.append(captain_model)

    elif gamemode == '5v5_pvp_ranked':
        # 5v5
        jungle_or_captain = []
        sorted_models = sorted(participant_models, key=lambda x:[x.nonJungleMinionKills, x.jungleKills], reverse=True)
        for idx in range(len(sorted_models)):
            participant_model = sorted_models[idx]
            if idx <= 2:
                participant_model.role = 'LANE'
                patricipant_models_with_role.append(participant_model)
            else:
                jungle_or_captain.append(participant_model)

        sorted_model = sorted(jungle_or_captain, key=lambda x:x.jungleKills, reverse=True)
        jungle_model = sorted_model[0]
        jungle_model.role = 'JUNGLE'
        patricipant_models_with_role.append(jungle_model)
        captain_model = sorted_model[1]
        captain_model.role = 'CAPTAIN'
        patricipant_models_with_role.append(captain_model)

    elif gamemode == 'blitz_pvp_ranked':
        # 電撃モード
        for participant_model in participant_models:
            participant_model.role = 'LANE'
            patricipant_models_with_role.append(participant_model)
    
    return patricipant_models_with_role


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
            'build_type': participant_model.build_type
        })
        stat_hero_duration_model = StatHerosDuration.query_one_or_init({
            'patchVersion': match_model.patchVersion,
            'gameMode': match_model.gameMode,
            'shardId': match_model.shardId,
            'hero_id': participant_model.hero_id,
            'role': participant_model.role,
            'build_type': participant_model.build_type,
            'duration_type': get_duration_type(match_model.duration)
        })
        stat_hero_model.games += 1
        stat_hero_duration_model.games += 1
        if participant_model.winner == True:
            stat_hero_model.wins += 1
            stat_hero_duration_model.wins += 1
        stat_hero_model.win_rate = stat_hero_model.wins / stat_hero_model.games
        stat_hero_duration_model.win_rate = stat_hero_duration_model.wins / stat_hero_duration_model.games

        stat_hero_models.append(stat_hero_model)
        stat_hero_models.append(stat_hero_duration_model)

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
main(gamemode, region)