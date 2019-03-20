# coding:utf-8

import os, sys, traceback, time, requests, json, csv
import gamelocker

from requests.exceptions import HTTPError
from datetime import datetime, date, timedelta, timezone
from time import sleep

from app.app import app
from app.database import db
from app.models import MHeros, MItems, Matches, MatchesExtra, Players, Participants, Rosters, StatHeros, StatHerosDuration, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type, analyze_telemetry

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# export LC_CTYPE="ja_JP.UTF-8"

RETRIEVE_START_DATE = '2019-02-14T00:00:00Z'
CSV_OUTPUT_DIR = 'csv_out'
TARGET_IGN_LIST = {
    'GGNewType2nd': {
        'StarIy'    : {'ea': ['StarIy'],                            'na': ['一本満足']},
        'LyRiz'     : {'ea': ['LyRiz'],                             'na':['PaulSmithNA']},
        'minami0928': {'ea': ['minami0928','CelesteopXD','CcDuke'], 'na':['Guest_820402168']},
        'omg00X'    : {'ea': ['omg00X'],                            'na':['SatsukiNA']},
        'Supercell7': {'ea': ['Supercell7','FroNtLine'],            'na':['AirCRAFT']},
        'hiroki325' : {'ea': ['hiroki325']}
    },
    'Hunters': {
        'BaBalA'        : {'ea': ['BaBalA', 'MuaMyFaFa']},
        'Hunt_Godfather': {'ea': ['Hunt_Godfather', 'LvSSS', 'LImitless']},
        'XiGuaGua'      : {'ea': ['XiGuaGua']},
        'JeIIyfishEA'   : {'ea': ['JeIIyfishEA', 'JelltTvT']},
        'Ghostsoul'     : {'ea': ['Ghostsoul', 'BestSptCK', 'NuageuxCK']}
    },
    'ACE': {
        'sweetBox' : {'ea': ['sweetBox', 'NameSweet'],            'na': ['SweetBoxNA']},
        '-taSa-'   : {'ea': ['-taSa-', 'Time4SomeAction'],        'na': ['TwitchT4SA']},
        'SHaNa'    : {'ea': ['SHaNa', 'SHaNaEA'],                 'na': ['SHaNaNA']},
        'CreaTion' : {'ea': ['CreaTion', 'SouZou'],               'na': ['NAtioN']},
        'DarKLon'  : {'ea': ['DarKLon', 'theoneA3', 'DarkLonEA'], 'na': ['DarkLonNA'], 'sg': ['PinkLon']},
        '-SEULLEE-': {'ea': ['-SEULLEE-'],                        'na': ['seulleeNA']}
    },
    'Tribe': {
        'Hami'      : {'na': ['Hami', 'ZuIu']},
        'ttigers'   : {'na': ['ttigers', 'MewTwolnATutu']},
        'Chuck'     : {'na': ['Chuck', 'BlackCIover']},
        'Oldskool'  : {'na': ['Oldskool', 'HotSauceUT', 'Ceoscah', 'AshFromTheFiree', 'Magikarp', 'OmgItsPoohBear']},
        'gabevizzle': {'na': ['gabevizzle']},
    }
}

def main():
    if not os.path.exists(CSV_OUTPUT_DIR):
        os.mkdir(CSV_OUTPUT_DIR)

    csv_output_targets = {}
    for team in TARGET_IGN_LIST:
        app.logger.info('=== Retrieving match history : team {} ==='.format(team))  
        csv_output_targets[team] = []
        for player in TARGET_IGN_LIST[team]:
            app.logger.info('-- processing player {} --'.format(player))
            for region in TARGET_IGN_LIST[team][player]:
                for ign in TARGET_IGN_LIST[team][player][region]:
                    app.logger.info('processing ign {}'.format(ign))
                    match_id_list = request_api(team, region, ign)
                    csv_output_targets[team].extend(match_id_list)

    app.logger.info('=== generate csv ===')
    generate_csv(csv_output_targets)


def generate_csv(csv_output_targets):
    ign_player_table = {}
    for team in TARGET_IGN_LIST:
        ign_player_table[team] = {}
        for player in TARGET_IGN_LIST[team]:
            for region in TARGET_IGN_LIST[team][player]:
                for ign in TARGET_IGN_LIST[team][player][region]:
                    ign_player_table[team][ign] = player

    for team in csv_output_targets:
        app.logger.info(f'Generating {team} csv files')
        match_id_list = list(set(csv_output_targets[team]))

        # '5v5_pvp_ranked'
        match_models = Matches.query.\
            filter(Matches.id.in_(match_id_list)).\
            filter(Matches.gameMode == '5v5_pvp_ranked').\
            order_by(Matches.createdAt).all()

        app.logger.info('5v5_pvp_ranked : {} matches'.format(len(match_models)))

        used_heros_by_player = {}
        for match_model in match_models:
            participant_models = Participants.query.filter(Participants.match_id == match_model.id).all()
            for participant_model in participant_models:
                ign_name = participant_model.player_name
                if ign_name in ign_player_table[team]:
                    player_name = ign_player_table[team][ign_name]
                    if player_name not in used_heros_by_player:
                        used_heros_by_player[player_name] = []
                    used_heros_by_player[player_name].append(participant_model.actor)

        match_count_by_player = {}
        for player_name in used_heros_by_player:
            match_count_by_player[player_name] = len(used_heros_by_player[player_name])

        max_match_count = max(match_count_by_player.values())

        filename = f'{CSV_OUTPUT_DIR}/{team}_ranked.csv'
        with open(filename, 'w') as csv_file:
            fieldnames = used_heros_by_player.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(max_match_count):
                row = {}
                for player_name in fieldnames:
                    match_count = match_count_by_player[player_name]
                    if i < match_count_by_player[player_name]:
                        row[player_name] = used_heros_by_player[player_name][i]
                    else:
                        row[player_name] = ''
                writer.writerow(row)
        app.logger.info(f'Created {filename}')

        filename = f'{CSV_OUTPUT_DIR}/{team}_private.csv'
        with open(filename, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')

            # 'private_party_draft_match_5v5'
            match_models = Matches.query.\
                filter(Matches.id.in_(match_id_list)).\
                filter(Matches.gameMode == 'private_party_draft_match_5v5').\
                order_by(Matches.createdAt).all()

            app.logger.info('private_party_draft_match_5v5 : {} matches'.format(len(match_models)))
            write_private_match_csv(writer, match_models)

            match_models = Matches.query.\
                filter(Matches.id.in_(match_id_list)).\
                filter(Matches.gameMode == 'private_party_vg_5v5').\
                order_by(Matches.createdAt).all()

            app.logger.info('private_party_vg_5v5 : {} matches'.format(len(match_models)))
            write_private_match_csv(writer, match_models)

        app.logger.info(f'Created {filename}')

    return


def write_private_match_csv(writer, match_models):
    for match_model in match_models:
        creted_at = match_model.createdAt
        region = match_model.shardId
        game_length = f"{int(match_model.duration/60)}:{int(match_model.duration)%60:02}"
        win_side = ''
        hero_kills = []

        roster_models = Rosters.query.filter_by(match_id=match_model.id).all()
        for roster_model in roster_models:
            hero_kills.append(f'{str(roster_model.heroKills)}')
            if roster_model.won == 1:
                win_side = roster_model.side

        row1 = [creted_at, region, ' vs '.join(hero_kills), f'win: {win_side}', game_length]
        writer.writerow(row1)

        row2 = []
        row3 = []
        for roster_model in roster_models:
            if roster_model.won == 1:
                win_side = roster_model.side


            participant_models = Participants.query.filter_by(roster_id=roster_model.id).all()
            for participant_model in participant_models:
                row2.append(participant_model.player_name)
                row3.append(participant_model.actor)

        writer.writerow(row2)
        writer.writerow(row3)

        match_extra_model = MatchesExtra.query.filter_by(match_id=match_model.id).first()
        if match_extra_model is not None:
            banpick = match_extra_model.banpick
            if banpick is not None and banpick != '':
                row4 = ['ban/pick']
                row4.extend(banpick)
                writer.writerow(row4)

        writer.writerow(['----'])

def request_api(team, region, ign):
    offset = 0
    limit = 5
    created_at_start = RETRIEVE_START_DATE
    apiKey = app.config['API_KEY_RANKED']
    match_id_list = []
    while True:
        try:
            app.logger.info('retrieving Gamelocker API data : offset = {}'.format(offset))
            api = gamelocker.Gamelocker(apiKey).Vainglory()
            matches = api.matches({
                'filter[playerNames]': ign,
                'filter[createdAt-start]': created_at_start,
                'page[limit]': limit,
                'page[offset]': offset
            }, region=region)
            if matches is not None:
                for match in matches:
                    match_model = process_match(match)
                    if match_model is not None:
                        match_id_list.append(match_model.id)

                offset += limit
            else:
                # 404 Exception will be thrown when there's no data
                pass
        except ConnectionResetError as e:
            # retry
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

    return match_id_list


def process_match(match):
    gameMode = match.gameMode

    if gameMode is None:
        app.logger.error('gameMode is None!! match = {}'.format(vars(match)))
        return None

    if gameMode not in ['5v5_pvp_ranked', 'private_party_draft_match_5v5', 'private_party_vg_5v5']:
        # 対象外
        app.logger.info('skip analyzing banpick')
        return None

    match_model = process_match_normal(match)
    if match_model is None:
        return None

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

    return match_model


def process_match_normal(match):
    try:
        app.logger.info('processing a match : id = {}, createdAt = {}'.format(match.id, match.createdAt))

        match_model = Matches.query.filter_by(uuid=match.id).first()
        if match_model is not None:
            return match_model

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

        telemetry_data = {}
        if match.gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual']:
            if len(match.assets) > 0:
                telemetry_url = match.assets[0].url
                telemetry = requests.get(telemetry_url).json()
                telemetry_data = analyze_telemetry(telemetry)
            else:
                """
                Sometimes there's no telemetry data.
                Perhaps SEMC server's issue.
                """
                app.logger.error('There is no match.assets[0]')
                app.logger.error(vars(match))
                db.session.commit()
                return None

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
                if match.gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual']:
                    rank_point_key = 'ranked_5v5'
                if match.gameMode in ['casual', 'ranked']:
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
            try:
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
            except:
                # エラーは了解したので、取り敢えず進める
                # FIXME 後で直す
                app.logger.error(traceback.print_exc())
                db.session.commit()
                return match_model

            if roster_model.averageRank < 7:
                is_rank7_or_more = False

        # シナジーデータ蓄積
        if is_rank7_or_more:
            hero_synergy_models = _create_hero_synergy(match_model, participant_models_by_rosters)
            db.session.add_all(hero_synergy_models)

        db.session.commit()

        return match_model
    except:
        app.logger.error(traceback.print_exc())
        db.session.rollback()
        return None

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

    elif match.gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual']:
        #TODO 試合中にすぐ降伏した場合なのか何なのか、ここでエラーでて落ちる
        #FIXME
        """
        INFO:flask.app:processing a match : id = 08e86a78-5ace-4165-b7f8-6f280d845a2d, createdAt = 2019-03-07T14:45:54Z
        Traceback (most recent call last):
        File "collect_draft_data.py", line 264, in process_match_normal
            patricipant_models_with_role = _assign_role_to_participants(match, participant_models, roster_model.side, telemetry_data)
        File "collect_draft_data.py", line 342, in _assign_role_to_participants
            top_actor = top_cs[0][0]
        IndexError: list index out of range
        """

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


main()