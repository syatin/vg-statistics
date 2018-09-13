from app.app import app
from app.database import db
from app.models import MItems, Matches, Players, Participants, Rosters, VgproLeaderboard

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from requests.exceptions import HTTPError

import gamelocker
import datetime, sys

"""
# Reference: https://developer.vainglorygame.com/docs#get-a-collection-of-players

## filter[gameMode]
blitz_pvp_ranked
casual_aral
casual
ranked
5v5_pvp_ranked
5v5_pvp_casual
"""

PATCH_VERSION = '3.7'
LIMIT = 5

args = sys.argv
if len(args) != 3:
    print('Specify gamemode and region. example : ranked5v5 ea')
    exit()

vgpro_gamemode = args[1]
if vgpro_gamemode not in  ['ranked', 'ranked5v5', 'blitz']:
    print(vgpro_gamemode + ' is not valid gamemode')
    exit()

vgpro_region = args[2]
if vgpro_region not in ['na', 'eu', 'ea', 'sg', 'sa', 'cn']:
    print(vgpro_region + 'is not valid region')
    exit()

def main(vgpro_gamemode, vgpro_region):
    gamemode = 'ranked'
    if vgpro_gamemode == 'ranked5v5':
        gamemode = '5v5_pvp_ranked'
    if vgpro_gamemode == 'blitz':
        gamemode = 'blitz_pvp_ranked'

    vgpro_players = VgproLeaderboard.query.filter(
        VgproLeaderboard.region == vgpro_region,
        VgproLeaderboard.gamemode == vgpro_gamemode
    ).order_by(VgproLeaderboard.position.asc())

    for player in vgpro_players:
        if player.games < 20:
            # 試合数が少ないプレイヤーは足切り
            continue

        app.logger.info('processing vgpro_player ign = ' + player.name + ', playerId = ' + player.playerId)
        retrieve_player_match_history(gamemode = gamemode, player_id = player.playerId)

    exit()


def retrieve_player_match_history(gamemode = None, player_id = None, ign = None):
    offset = 0
    while True:
        try:
            api = gamelocker.Gamelocker(app.config['API_KEY']).Vainglory()
            matches = api.matches({
                'filter[patchVersion]' : PATCH_VERSION,
                'filter[gameMode]': gamemode,
                #'filter[playerNames]': ign,
                'filter[playerIds]': player_id,
                'page[limit]': LIMIT,
                'page[offset]': offset
            }, region='ea')
            if matches is not None:
                process_count = 0
                for match in matches:
                    count = process_match(match)
                    process_count = process_count + count
                if process_count == 0:
                    # 全部処理済だったら、このプレイヤーは終了
                    break
                if LIMIT == len(matches):
                    # 続きがありそう
                    offset = offset + LIMIT
                    continue
            else:
                app.logger.info('no match found')
                break

        except HTTPError as e:
            if e.response.status_code == 404:
                # 最近試合してない、IGNが違う、など
                app.logger.info('Couldn\'t find match history')
            else:
                app.logger.info(e)
            # エラーが発生したら、とりあえずこのプレイヤーは終了
            break

def process_match(match):
    """
    試合履歴を処理する
    """
    match_model = Matches.query.filter_by(uuid = match.id).first()
    if match_model is not None:
        # 処理済なので処理件数は0で返す
        return 0

    app.logger.info('processing a match : id = ' + match.id)

    match_model = Matches(
        uuid = match.id,
        shardId = match.shardId,
        gameMode = match.gameMode,
        duration = match.duration,
        endGameReason = match.stats['endGameReason'],
        patchVersion = match.patchVersion,
        createdAt = datetime.datetime.strptime(match.createdAt, '%Y-%m-%dT%H:%M:%SZ')
    )
    db.session.add(match_model)
    db.session.commit()

    for roster in match.rosters:
        roster_model = Rosters(
            match_id = match_model.id,
            acesEarned = roster.stats['acesEarned'],
            gold = roster.stats['gold'],
            heroKills = roster.stats['heroKills'],
            krakenCaptures = roster.stats['krakenCaptures'],
            side = roster.stats['side'],
            turretKills = roster.stats['turretKills'],
            turretsRemaining = roster.stats['turretsRemaining'],
            won = 1 if roster.won == 'true' else 0,
            averageRankedPoint = 0,
            averageRank = 0
        )
        db.session.add(roster_model)
        db.session.commit()

        player_count = 0
        total_rank_points = 0
        for participant in roster.participants:
            player_count = player_count + 1
            player = participant.player
            player_model = Players.query.filter_by(playerId = player.key_id).first()
            if player_model is None:
                player_model = Players(
                    playerId = player.key_id,
                    shardId = player.shardId
                )
            player_model.name = player.name
            player_model.rankPoints = player.stats['rankPoints']
            player_model.gamesPlayed = player.stats['gamesPlayed']
            player_model.guildTag = player.stats['guildTag']
            player_model.karmaLevel = player.stats['karmaLevel']
            player_model.level = player.stats['level']
            player_model.updatedAt = datetime.datetime.now()
            db.session.add(player_model)
            db.session.commit()

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
            items = participant.stats['items']
            analyzed_build = analyze_build(items)
            participant_model = Participants(
                match_id = match_model.id,
                roster_id = roster_model.id,
                player_id = player_model.id,
                player_name = player_model.name,
                rankPoint = rank_point,
                rank = rank,
                actor = participant.actor,
                kills = participant.stats['kills'],
                assists = participant.stats['assists'],
                deaths = participant.stats['deaths'],
                gold = participant.stats['gold'],
                minionKills = participant.stats['minionKills'],
                jungleKills = participant.stats['jungleKills'],
                nonJungleMinionKills = participant.stats['nonJungleMinionKills'],
                items = items,
                itemUses = participant.stats['itemUses'],
                is_wp_build = analyzed_build['is_wp_build'],
                is_cp_build = analyzed_build['is_cp_build'],
                is_hybrid_build = analyzed_build['is_hybrid_build'],
                is_utility_build = analyzed_build['is_utility_build'],
                wentAfk = participant.stats['wentAfk'],
                skinKey = participant.stats['skinKey'],
                winner = participant.stats['winner'],
            )
            db.session.add(participant_model)
            db.session.commit()

        # 各サイドの平均ランクを保存
        roster_model.averageRankedPoint = total_rank_points / player_count
        roster_model.averageRank = get_rank(roster_model.averageRankedPoint)
        db.session.add(roster_model)
        db.session.commit()

    # 試合を処理したら処理件数(この場合は常に1)を返す
    return 1

g.item_master = None
def analyze_build(items):
    """
    アイテムからビルドを分析して返す
    """
    if g.item_master is None:
        g.item_master = {}
        m_items = MItems.query.all()
        for m_item in m_items:
            g.item_master[m_item.name] = m_item

    wp_tier_count = 0
    cp_tier_count = 0
    utility_tier_count = 0
    for item in items:
        m_item = g.item_master[item]
        if m_item is not None:
            if m_item.build_type is None:
                continue
            elif m_item.build_type == 'wp':
                wp_tier_count = wp_tier_count + m_item.tier
            elif m_item.build_type == 'cp':
                cp_tier_count = cp_tier_count + m_item.tier
            elif m_item.build_type == 'support':
                utility_tier_count = utility_tier_count + m_item.tier

    is_wp_build = 0
    is_cp_build = 0
    is_hybrid_build = 0
    is_utility_build = 0
    max_tier = max(wp_tier_count, cp_tier_count, utility_tier_count)
    if max_tier != 0:
        if max_tier == wp_tier_count and max_tier == cp_tier_count:
            is_hybrid_build = 1
        elif max_tier == wp_tier_count:
            is_wp_build = 1
            if cp_tier_count >= 3:
                is_hybrid_build = 1
        elif max_tier == cp_tier_count:
            is_cp_build = 1
            if wp_tier_count >= 3:
                is_hybrid_build = 1
        elif max_tier == utility_tier_count:
            is_utility_build = 1

    return {
        'is_wp_build': is_wp_build,
        'is_cp_build': is_cp_build,
        'is_hybrid_build': is_hybrid_build,
        'is_utility_build': is_utility_build
    }  

def get_rank(point):
    """
    ランクポイントからランクを返す
    """
    if point >= 2800:
        return 10 # 10g
    elif point >= 2600:
        return 10 # 10s
    elif point >= 2400:
        return 10 # 10b
    elif point >= 2267:
        return 9 # 9g
    elif point >= 2134:
        return 9 # 9s
    elif point >= 2000:
        return 9 # 9b
    elif point >= 1933:
        return 8 # 8g
    elif point >= 1867:
        return 8 # 8s
    elif point >= 1800:
        return 8 # 8b
    elif point >= 1733:
        return 7 # 7g
    elif point >= 1667:
        return 7 # 7s
    elif point >= 1600:
        return 7 # 7b
    elif point >= 1533:
        return 6 # 6g
    elif point >= 1467:
        return 6 # 6s
    elif point >= 1400:
        return 6 # 6b
    elif point >= 1350:
        return 5 # 5g
    elif point >= 1300:
        return 5 # 5s
    elif point >= 1250:
        return 5 # 5b
    elif point >= 1200:
        return 4 # 4g
    elif point >= 1090:
        return 4 # 4s
    elif point >= 981:
        return 4 # 4b
    elif point >= 872:
        return 3 # 3g
    elif point >= 763:
        return 3 # 3s
    elif point >= 654:
        return 3 # 3b
    elif point >= 545:
        return 2 # 2g
    elif point >= 436:
        return 2 # 2s
    elif point >= 327:
        return 2 # 2b
    elif point >= 218:
        return 1 # 1g
    elif point >= 109:
        return 1 # 1s
    else:
        return 1 # 1b

# 実行！
main(vgpro_gamemode, vgpro_region)