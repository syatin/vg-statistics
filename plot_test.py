# coding:utf-8

import json

from PIL import Image, ImageDraw
import numpy as np

import gamelocker
import sys, traceback, time, requests

from app.app import app
from app.database import db
from app.models import MHeroes, MItems, Matches, Players, Participants, Rosters, StatHeroes, StatHeroesDuration, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type, analyze_telemetry

from datetime import datetime, date, timedelta, timezone
from time import sleep

"""
test
"""

def main():
    img = Image.open('sample_data/5v5map_base.png')
    width, height = img.size

    color_red = (255, 0, 0)
    color_green = (0, 255, 0)
    color_blue = (0, 0, 255)
    color_water = (0, 255, 255)

    # この秒数毎に別の画像にする
    slice_seconds = 120

    f = open("sample_data/telemetry-sample.json", 'r')
    telemetry = json.load(f)
    telemetry_data = analyze_telemetry(telemetry)
    movement_summary = telemetry_data['movement_summary']
    for team in movement_summary:
        for actor in movement_summary[team]:
            print(f'creating {team} - {actor}')

            timeline = movement_summary[team][actor]
            img2, draw = _initalize_map(img, actor)

            last_prot_x = None
            last_prot_y = None
            last_timespan = None
            for evt in timeline:
                evt_type = evt['type']
                seconds = evt['seconds']
                timespan = int(seconds / slice_seconds)

                if timespan != last_timespan and last_timespan is not None:
                    img2.save(f"output/edited_img_{team}_{actor}_{last_timespan}.jpg", quality=95)
                    img2, draw = _initalize_map(img, actor)

                prot_x, prot_y = _calc_prot_position(width, height, evt['Position'])

                # first spawn
                if last_timespan is None:
                    _draw_rectangle(draw, prot_x, prot_y, 8, (255, 255, 0))

                if evt_type == 'KillActor':
                    if evt['TargetIsHero'] == 1:
                        killed = evt['Killed']
                        _draw_rectangle(draw, prot_x, prot_y, 8, color_red)
                        # ヒーロー画像に差し替え
                        draw.text((prot_x - 10, prot_y - 10), f'Killed {killed}')
                    else:
                        _draw_rectangle(draw, prot_x, prot_y, 4, color_red)
                elif evt_type == 'UseAbility':
                    _draw_rectangle(draw, prot_x, prot_y, 4, color_green)
                elif evt_type == 'UseItemAbility':
                    item = evt['Ability']
                    # アイテム画像に差し替え
                    draw.text((prot_x - 10, prot_y - 14), f'Used {item}')
                    _draw_rectangle(draw, prot_x, prot_y, 4, color_water)
                elif evt_type == 'Recall':
                    _draw_rectangle(draw, prot_x, prot_y, 12, color_blue)
                else:
                    #draw.rectangle((prot_x, prot_y, prot_x+3, prot_y+3), fill=(255, 255, 0), outline=(255, 255, 255))
                    pass


                if last_prot_x and last_prot_y:
                    draw.line((last_prot_x, last_prot_y, prot_x, prot_y), fill=(255, 255, 255), width=1)

                last_prot_x = prot_x
                last_prot_y = prot_y
                last_timespan = timespan

            img2.save(f"output/edited_img_{team}_{actor}_{last_timespan}.jpg", quality=95)

    return


def _initalize_map(img, actor):
    # オリジナル画像と同じサイズのImageオブジェクトを作成する
    img2 = img.copy()
    draw = ImageDraw.Draw(img2)
    draw.text((20, 20), actor)

    return [img2, draw]

def _draw_rectangle(draw, prot_x, prot_y, width, color):
    draw.rectangle((prot_x-width/2, prot_y-width/2, prot_x+width/2, prot_y+width/2), fill=color, outline=color)

def _calc_prot_position(width, height, position):
    x, z, y = position

    x_max = 124
    y_max = 124

    # 画像の真ん中を起点とする
    prot_x = width/2
    prot_y = height/2

    # x の計算
    prot_x = prot_x + (x / x_max) * width/2
    prot_y = prot_y - (x / x_max) * height/2

    # y の計算
    prot_x = prot_x + (y / y_max) * width/2
    prot_y = prot_y + (y / y_max) * height/2

    return [prot_x, prot_y]


main()