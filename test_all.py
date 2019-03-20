# coding:utf-8

import json

from PIL import Image, ImageDraw, ImageFilter
import numpy as np

import gamelocker
import sys, traceback, time, requests

from app.app import app
from app.database import db
from app.models import MHeros, MItems, Matches, Players, Participants, Rosters, StatHeros, StatHerosDuration, StatSynergy
from app.util import get_rank, get_build_type, get_week_start_date, get_duration_type, analyze_telemetry

from datetime import datetime, date, timedelta, timezone
from time import sleep

"""
test
"""

color_red = (255, 0, 0)
color_red_half = (128, 0, 0)
color_green = (0, 255, 0)
color_yellow = (255, 255, 0)
color_blue = (0, 0, 255)
color_water = (0, 255, 255)

turrets = ['*OuterTurret5v5*', '*Turret5v5*', '*ArmoryTurret5v5*', '*VainNode*']

def main():
    img = Image.open('sample_data/5v5map_base_2.png')

    # この秒数毎に別の画像にする
    slice_seconds = 60

    f = open("sample_data/telemetry-sample.json", 'r')
    telemetry = json.load(f)
    telemetry_data = analyze_telemetry(telemetry)
    movement_summary = telemetry_data['movement_summary']
    movement_slice = _create_movement_slice(movement_summary, slice_seconds)

    for timespan in movement_slice:

        # TODO 後で桁揃えの方法調べる
        second_start = slice_seconds * timespan
        second_end = second_start + slice_seconds
        title = f"Time {int(second_start/60)}:{second_start%60:02} - {int(second_end/60)}:{second_end%60:02}"

        img2, draw = _initalize_map(img, title)

        # 上に表示するために、後で描画する情報
        list_prot_later = []

        for team in movement_slice[timespan]:
            line_color = color_blue if team == 'Left' else color_red_half

            for actor in movement_slice[timespan][team]:
                sliced_timeline = movement_slice[timespan][team][actor]
                list_prot_later = _prot_timeline(img2, draw, actor, sliced_timeline, line_color, list_prot_later)

        for data in list_prot_later:
            prot_x, prot_y, prot_data = data
            text = prot_data['text']
            draw.text((prot_x - 10, prot_y - 14), text)

        img2.save(f"output/{timespan}.jpg", quality=100)

    return

def _create_movement_slice(movement_summary, slice_seconds):
    movement_slice = {}
    for team in movement_summary:
        for actor in movement_summary[team]:
            timeline = movement_summary[team][actor]
            timeline.reverse()
            last_evt = None
            while len(timeline) > 0:
                evt = timeline.pop()
                seconds = evt['seconds']
                timespan = int(seconds / slice_seconds)

                if timespan not in movement_slice:
                    movement_slice[timespan] = {}
                if team not in movement_slice[timespan]:
                    movement_slice[timespan][team] = {}
                if actor not in movement_slice[timespan][team]:
                    movement_slice[timespan][team][actor] = []
                    if last_evt is not None:
                        last_evt = {
                            'seconds': seconds,
                            'type': 'LastPosition',
                            'Position': last_evt['Position'],
                        }
                        movement_slice[timespan][team][actor].append(last_evt)
                        pass

                movement_slice[timespan][team][actor].append(evt)
                last_evt = evt

    return movement_slice


def _initalize_map(img, title):
    # オリジナル画像と同じサイズのImageオブジェクトを作成する
    img2 = img.copy()
    draw = ImageDraw.Draw(img2)
    draw.text((20, 20), title)

    return [img2, draw]

def _prot_timeline(img, draw, actor, timeline, line_color, list_prot_later):
    width, height = img.size

    last_prot_x = None
    last_prot_y = None

    evt = None

    for evt in timeline:
        evt_type = evt['type']
        seconds = evt['seconds']
        minute = f"{int(seconds/60)}:{int(seconds)%60:02}"
        prot_x, prot_y = _calc_prot_position(width, height, evt['Position'])

        # first position in this timeline
        if last_prot_x is None:
            list_prot_later.append([prot_x, prot_y, {'text' : f'{minute} {actor}'}])
            _draw_rectangle(draw, prot_x, prot_y, 8, color_yellow)

        if evt_type == 'KillActor':
            killed = evt['Killed']
            if evt['TargetIsHero'] == 1:
                _draw_rectangle(draw, prot_x, prot_y, 8, color_red)
                # ヒーロー画像に差し替え
                list_prot_later.append([prot_x, prot_y, {'text' : f'{minute} Killed {killed}'}])
            elif killed in turrets:
                _draw_rectangle(draw, prot_x, prot_y, 4, color_red)
                list_prot_later.append([prot_x, prot_y, {'text' : f'{minute} Broke turret'}])
            elif killed == '*VainCrystal_Home_5v5*':
                _draw_ellipse(draw, prot_x, prot_y, 24, color_red)
                list_prot_later.append([prot_x, prot_y, {'text' : f'{minute} Good Game'}])
            else:
                _draw_rectangle(draw, prot_x, prot_y, 4, color_red)
        elif evt_type == 'UseAbility':
            #_draw_rectangle(draw, prot_x, prot_y, 4, color_green)
            pass
        elif evt_type == 'UseItemAbility':
            item = evt['Ability']

            # テレポ靴の時はターゲットの場所が大事
            if item == 'Teleport Boots':
                list_prot_later.append([prot_x, prot_y, {
                    'text' : 'Teleport', 'size' : 12, 'color': color_yellow
                }])
                prot_xx, prot_yy = _calc_prot_position(width, height, evt['TargetPosition'])
                _draw_rectangle(draw, prot_xx, prot_yy, 4, color_water)
                last_prot_x = prot_x
                last_prot_y = prot_y
                prot_x = prot_xx
                prot_y = prot_yy

            # 視界の場合は、視界っぽい何かを何とかする。
            # 視界アイテムの画像を、マップ上に植えるのはどうだろう
            if item == 'Vision Totem':
                _draw_rectangle(draw, prot_x, prot_y, 4, color_water)
                prot_xx, prot_yy = _calc_prot_position(width, height, evt['TargetPosition'])

                poly_size = (26,26)
                poly_offset = (int(prot_xx - 12),int(prot_yy - 12))
                poly = Image.new('RGBA', poly_size)
                pdraw = ImageDraw.Draw(poly)
                fill_color = line_color + (127,)
                #pdraw.ellipse([(2,2), (22,22)], fill=(255,255,100,127))
                pdraw.ellipse([(2,2), (22,22)], fill=fill_color)

                poly_blur = poly.filter(ImageFilter.GaussianBlur(3))
                img.paste(poly_blur, poly_offset, mask=poly_blur)

                _draw_rectangle(draw, prot_xx, prot_yy, 2, color_water)

            else:
                # アイテム画像に差し替え
                #draw.text((prot_x - 10, prot_y - 14), f'Used {item}')
                pass

        elif evt_type == 'Recall':
            _draw_rectangle(draw, prot_x, prot_y, 12, color_blue)
        else:
            #draw.rectangle((prot_x, prot_y, prot_x+3, prot_y+3), fill=(255, 255, 0), outline=(255, 255, 255))
            pass

        if last_prot_x and last_prot_y:
            draw.line((last_prot_x, last_prot_y, prot_x, prot_y), fill=line_color, width=1)

        last_prot_x = prot_x
        last_prot_y = prot_y

    # last position in this timeline
    #list_prot_later.append([prot_x, prot_y, {'text' : f'{minute} {actor}'}])
    _draw_rectangle(draw, prot_x, prot_y, 4, color_yellow)

    return list_prot_later



def _draw_rectangle(draw, prot_x, prot_y, width, color):
    draw.rectangle((prot_x-width/2, prot_y-width/2, prot_x+width/2, prot_y+width/2), fill=color)

def _draw_ellipse(draw, prot_x, prot_y, width, color):
    draw.ellipse([(prot_x-width/2, prot_y-width/2), (prot_x+width/2, prot_y+width/2)], fill=color)

def _calc_prot_position(width, height, position):
    x, z, y = position

    x_max = 124
    y_max = 123

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