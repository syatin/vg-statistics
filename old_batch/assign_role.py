from app.app import app
from app.database import db
from app.models import MItems, Matches, Players, Participants, Rosters, VgproLeaderboard

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from requests.exceptions import HTTPError

import gamelocker
import datetime, sys, traceback
from time import sleep

"""
かつての試合履歴にロールを割り振り
"""

gamemode = 'ranked'

def main(gamemode):
    match_list = Matches.query.\
        outerjoin(Participants, Matches.id == Participants.match_id).\
        filter(Participants.role == None).\
        filter(Matches.gameMode == gamemode).\
        order_by(Matches.createdAt.desc()).all()

    for match in match_list:
        assign_role_to_participants(match)


def assign_role_to_participants(match):
    app.logger.info('processing match_id=' + str(match.id))
    roster_list = Rosters.query.filter(
        Rosters.match_id == match.id
    ).all()

    for roster in roster_list:
        participant_models = Participants.query.filter(
            Participants.roster_id == roster.id
        ).all()

        try:
            # ロール計算
            if match.gameMode == 'ranked':
                # 3v3
                sorted_models = sorted(participant_models, key=lambda x:x.minionKills, reverse=True)
                carry_model = sorted_models[0]
                carry_model.role = 'laner'
                db.session.add(carry_model)
                jungler_model = sorted_models[1]
                jungler_model.role = 'jungler'
                db.session.add(jungler_model)
                captain_model = sorted_models[2]
                if captain_model.is_wp_build == 1 or captain_model.is_cp_build == 1:
                    # 低階層などのキャプテン無し構成
                    captain_model.role = 'jungler'
                else:
                    captain_model.role = 'captain'
                db.session.add(captain_model)
            elif match.gameMode == '5v5_pvp_ranked':
                # 5v5
                jungle_or_captain = []
                sorted_models = sorted(participant_models, key=lambda x:[x.nonJungleMinionKills, x.jungleKills], reverse=True)
                for idx in range(len(sorted_models)):
                    participant_model = sorted_models[idx]
                    if idx <= 2:
                        participant_model.role = 'laner'
                        db.session.add(participant_model)
                    else:
                        jungle_or_captain.append(participant_model)

                sorted_model = sorted(jungle_or_captain, key=lambda x:x.jungleKills, reverse=True)
                jungle_model = sorted_model[0]
                jungle_model.role = 'jungler'
                db.session.add(jungle_model)
                captain_model = sorted_model[1]
                captain_model.role = 'captain'
                db.session.add(captain_model)

            elif match.gameMode == 'blitz_pvp_ranked':
                for participant_model in participant_models:
                    participant_model.role = 'laner'
                    db.session.add(participant_model)

            db.session.commit()
        except:
            pass

# 実行！
main(gamemode)