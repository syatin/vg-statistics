# coding:utf-8

import gamelocker
import sys, traceback, time, requests

from app.app import app
from app.database import db
from app.models import MHeros, MItems, Matches, MatchesExtra, Players, Participants, Rosters, StatHeros, StatHerosDuration, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type, analyze_telemetry

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from requests.exceptions import HTTPError
from datetime import datetime, date, timedelta, timezone
from time import sleep

"""
Usage

nohup python get_match_history.py ranked na >> log/get_match_history_3v3_na.log & echo $! > 3v3_na.pid
nohup python get_match_history.py ranked eu >> log/get_match_history_3v3_eu.log & echo $! > 3v3_eu.pid
nohup python get_match_history.py ranked ea >> log/get_match_history_3v3_ea.log & echo $! > 3v3_ea.pid
nohup python get_match_history.py ranked sg >> log/get_match_history_3v3_sg.log & echo $! > 3v3_sg.pid
nohup python get_match_history.py ranked sa >> log/get_match_history_3v3_sa.log & echo $! > 3v3_sa.pid
nohup python get_match_history.py ranked cn >> log/get_match_history_3v3_cn.log & echo $! > 3v3_cn.pid

nohup python get_match_history.py ranked5v5 na >> log/get_match_history_5v5_na.log & echo $! > 5v5_na.pid
nohup python get_match_history.py ranked5v5 eu >> log/get_match_history_5v5_eu.log & echo $! > 5v5_eu.pid
nohup python get_match_history.py ranked5v5 ea >> log/get_match_history_5v5_ea.log & echo $! > 5v5_ea.pid
nohup python get_match_history.py ranked5v5 sg >> log/get_match_history_5v5_sg.log & echo $! > 5v5_sg.pid
nohup python get_match_history.py ranked5v5 sa >> log/get_match_history_5v5_sa.log & echo $! > 5v5_sa.pid
nohup python get_match_history.py ranked5v5 cn >> log/get_match_history_5v5_cn.log & echo $! > 5v5_cn.pid

# Reference
https://developer.vainglorygame.com/docs#get-a-collection-of-players

## filter[gameMode]
- blitz_pvp_ranked
- casual_aral
- casual
- ranked
- 5v5_pvp_ranked
- 5v5_pvp_casual
- private_party_draft_match_5v5
- private_party_vg_5v5
"""

LIMIT = 5

args = sys.argv
if len(args) != 3:
    print('Specify gamemode and region. example : ranked5v5 ea')
    exit()

gamemode = args[1]
if gamemode not in  ['ranked', 'ranked5v5', 'casual', 'casual5v5', 'blitz', 'private5v5', 'private_draft5v5']:
    print('{} is not valid gamemode'.format(gamemode))
    exit()

region = args[2]
if region not in ['na', 'eu', 'ea', 'sg', 'sa', 'cn']:
    print('{} is not valid region'.format(region))
    exit()

def main(gamemode, region):
    if gamemode == 'ranked5v5':
        gamemode = '5v5_pvp_ranked'
    if gamemode == 'private5v5':
        gamemode = 'private_party_vg_5v5'
    if gamemode == 'private_draft5v5':
        gamemode = 'private_party_draft_match_5v5'
    if gamemode == 'casual5v5':
        gamemode = '5v5_pvp_casual'
    if gamemode == 'blitz':
        gamemode = 'blitz_pvp_ranked'

    batch_started_at = datetime.now(timezone.utc)
    retrieve_match_history(gamemode=gamemode, region=region, now=batch_started_at)

    return


def retrieve_match_history(gamemode, region, now):
    """
    Gamelocker API から試合履歴を取得し諸々処理して保存する

    createdAt-startを、最新時刻より2時間前
    createdAt-endを、最新時刻より1時間前

    取りきるまで回す
    1時間毎に起動する（試合数が多いと多重起動になってサーバーが落ちるけど、まぁ...。）
    """
    offset = 0

    apikey_index = 'API_KEY_{}'.format(region.upper())
    apiKey = app.config[apikey_index]

    created_at_start = (now - timedelta(minutes=121)).strftime("%Y-%m-%dT%H:%M:%SZ")
    created_at_end = (now - timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")

    app.logger.info('process started : gamemode = {}, region = {}, createdAt-start = {}'.format(gamemode, region, created_at_start))

    while True:
        try:
            app.logger.info('retrieving Gamelocker API data : offset = {}'.format(offset))
            api = gamelocker.Gamelocker(apiKey).Vainglory()
            matches = api.matches({
                'filter[gameMode]': gamemode,
                'filter[createdAt-start]': created_at_start,
                'filter[createdAt-end]': created_at_end,
                'page[limit]': LIMIT,
                'page[offset]': offset
            }, region=region)
            if matches is not None:
                processed_count = 0
                for match in matches:
                    processed_count += process_match(match, now)

                app.logger.info('{} matches were processed.'.format(processed_count))
                offset += LIMIT
            else:
                # 試合履歴が無い時は 404 Exception になる模様
                pass
        except ConnectionResetError as e:
            # 通信エラー系はリトライ
            app.logger.info(e)
            app.logger.info('ConnectionResetError. sleep 10 seconds and continue')
            sleep(10)
            continue

        except HTTPError as e:
            if e.response.status_code == 404:
                app.logger.info('Couldn\'t find match history')
            else:
                app.logger.info(e)
            break

    app.logger.info('process finished : gamemode = {}, region = {}, createdAt-start = {}'.format(gamemode, region, created_at_start))
    return


def process_match(match, now):
    """
    1つの試合履歴を処理する
    """
    try:
        app.logger.info('processing a match : id = {}, createdAt = {}'.format(match.id, match.createdAt))

        gameMode = match.gameMode
        if gameMode is None:
            app.logger.error('gameMode is None!! match = {}'.format(vars(match)))
            return None

        match_model = Matches.query.filter_by(uuid=match.id).first()
        if match_model is not None:
            app.logger.info('skipped a match : id = {}'.format(match.id))
            # 処理済なので処理件数は0で返す
            return 0

        match_model = Matches(
            uuid=match.id,
            shardId=match.shardId,
            gameMode=gameMode,
            duration=match.duration,
            endGameReason=match.stats['endGameReason'],
            patchVersion=match.patchVersion,
            createdAt=datetime.strptime(match.createdAt, '%Y-%m-%dT%H:%M:%SZ')
        )
        db.session.add(match_model)
        db.session.flush()

        # テレメトリー解析情報
        telemetry_data = {}
        if gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual', 'private_party_vg_5v5', 'private_party_draft_match_5v5']:
            telemetry_url = match.assets[0].url
            telemetry = requests.get(telemetry_url).json()
            telemetry_data = analyze_telemetry(telemetry)

        if gameMode in ['5v5_pvp_ranked', 'private_party_draft_match_5v5']:
            #ドラフトピックの処理
            if len(match.assets) == 0:
                return match_model

            telemetry_url = match.assets[0].url
            telemetry = requests.get(telemetry_url).json()
            telemetry_data = analyze_telemetry(telemetry)
            banpick_order = telemetry_data['banpick_order']

            match_extra_model = MatchesExtra.query.filter_by(match_id=match_model.id).first()
            if match_extra_model is None:
                match_extra_model = MatchesExtra(
                    match_id=match_model.id,
                    banpick=banpick_order,
                )
                db.session.add(match_extra_model)
                db.session.commit()

        # シナジーデータ計算用に Participant モデルのリストを保持する
        participant_models_by_rosters = []
        is_rank7_or_more = True

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

                if player_model.updatedAt is None or player_model.updatedAt > datetime.now():
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
                if gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual', 'private_party_vg_5v5', 'private_party_draft_match_5v5']:
                    rank_point_key = 'ranked_5v5'
                if gameMode in ['casual', 'ranked']:
                    rank_point_key = 'ranked'
                if gameMode == 'blitz_pvp_ranked':
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
            patricipant_models_with_role = _assign_role_to_participants(match, participant_models, roster_model.side, telemetry_data)
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

            if roster_model.averageRank < 7:
                is_rank7_or_more = False

        # シナジーデータ蓄積
        if is_rank7_or_more:
            hero_synergy_models = _create_hero_synergy(match_model, participant_models_by_rosters)
            db.session.add_all(hero_synergy_models)

        db.session.commit()

        # 試合を処理したら処理件数(この場合は常に1)を返す
        return 1
    except:
        app.logger.error(traceback.print_exc())
        db.session.rollback()
        return 0

def _assign_role_to_participants(match, participant_models, side, telemetry_data):
    """
    各プレイヤーのCSやビルドからロールを割り振る
    """
    patricipant_models_with_role = []
    if match.gameMode in ['ranked', 'casual']:
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

    elif match.gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual', 'private_party_vg_5v5', 'private_party_draft_match_5v5']:
        # 5v5
        """
        5人の内、Mid のCS一番多い人がMid
        Mid を除いた4人の内、BotのCS一番多い人がBot
        Mid, Bot を除いた3人の内、TopのCS一番多い人がTop
        Mid, Bot, Top を除いた2人の内、ジャングルCSが多い方がJungle
        最後の1人がCaptain

        最初からAFKして居ないとかは統計的に誤差なので、そこを正しくするロジックは考えない
        """
        side = 'Left' if side == 'left/blue' else 'Right'
        minion_stat = telemetry_data['minion_stat'][side]
        mid_cs = sorted(minion_stat['Mid'].items(), key=lambda x:x[1], reverse=True)
        mid_actor = mid_cs[0][0]

        bot_cs = sorted(minion_stat['Bot'].items(), key=lambda x:x[1], reverse=True)
        bot_cs = [elem for elem in bot_cs if elem[0] != mid_actor]
        bot_actor = bot_cs[0][0]

        top_cs = sorted(minion_stat['Top'].items(), key=lambda x:x[1], reverse=True)
        top_cs = [elem for elem in top_cs if elem[0] != mid_actor]
        top_cs = [elem for elem in top_cs if elem[0] != bot_actor]
        top_actor = top_cs[0][0]

        jungle_or_captain = []
        for participant_model in participant_models:
            if participant_model.actor == mid_actor:
                participant_model.role = 'MID'
                patricipant_models_with_role.append(participant_model)
            elif participant_model.actor == bot_actor:
                participant_model.role = 'BOT'
                patricipant_models_with_role.append(participant_model)
            elif participant_model.actor == top_actor:
                participant_model.role = 'TOP'
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

    elif match.gameMode == 'blitz_pvp_ranked':
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
            'patchVersion': match_model.patchVersion,
            'gameMode': match_model.gameMode,
            'shardId': match_model.shardId,
            'hero_id': participant_model.hero_id,
            'role': participant_model.role,
            'build_type': participant_model.build_type,
            'week': get_week_start_date(match_model.createdAt),
            'rank': participant_model.rank
        })
        stat_hero_duration_model = StatHerosDuration.query_one_or_init({
            'patchVersion': match_model.patchVersion,
            'gameMode': match_model.gameMode,
            'shardId': match_model.shardId,
            'hero_id': participant_model.hero_id,
            'rank': participant_model.rank,
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
    # この処理で触ったヒーロー相性モデルのリスト
    hero_synergy_models = []

    # 相性計算で使うため、まずはヒーロー単体での勝率を取得する
    synergy_base_by_hero = {}
    for k in range(0, len(participant_models_by_rosters)):
        participant_models = participant_models_by_rosters[k]

        for i in range(0, len(participant_models)):
            p1 = participant_models[i]
            synergy_base = StatSynergy.query_one_or_init({
                'patchVersion': match_model.patchVersion,
                'gameMode': match_model.gameMode,
                'hero_id_1': p1.hero_id,
                'role_1': p1.role,
                'build_type_1': p1.build_type,
                'hero_id_2': None,
                'role_2': None,
                'build_type_2': None,
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
                    'build_type_1': p1.build_type,
                    'hero_id_2': p2.hero_id,
                    'role_2': p2.role,
                    'build_type_2': p2.build_type,
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
                    'build_type_1': p1.build_type,
                    'hero_id_2': p2.hero_id,
                    'role_2': p2.role,
                    'build_type_2': p2.build_type,
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

main(gamemode, region)