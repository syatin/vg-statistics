import requests

from app.util import get_tier3_items

from datetime import datetime, date, timedelta, timezone

def analyze_telemetry(telemetry):
    """
    Analyze telemetry data
    telemetryのデータを解析します
    """
    return _analyze_5v5(telemetry)

def _analyze_5v5(telemetry):
    minion_stat = {
        'Left': {'Top': {}, 'Mid': {}, 'Bot': {}},
        'Right': {'Top': {}, 'Mid': {}, 'Bot': {}}
    }
    banpick_order = []
    banned = {
        'Left': [], 'Right': []
    }
    first_buy_items = {
        'Left': {}, 'Right': {}
    }
    first_gold = {
        'Left': {}, 'Right': {}
    }
    item_build_order = {
        'Left': {}, 'Right': {}
    }
    use_item_ability = {
        'Left': {}, 'Right': {}
    }
    movement_summary = {
        'Left': {}, 'Right': {}
    }

    tier3_items = get_tier3_items()

    turret_break = {
        'first_turret': {'Left': None, 'Right': None},
        'first_mid_turret': {'Left': None, 'Right': None}
    }
    lane_minions = ['*5v5_Minion_Melee*', '*5v5_Minion_Range*', '*5v5_Minion_Siege*', '*5v5_Minion_Captain*']
    jungle_minions = [
        '*5v5_BuffCamp_CrystalOrb*', '*5v5_BuffCamp_WeaponOrb*', '*5v5_Goldshell*',
        '*5v5_CampA_Primary*', '*5v5_CampA_Secondary*',
        '*5v5_CampB_Primary*', '*5v5_CampB_Secondary*',
        '*5v5_CampC_Primary*', '*5v5_CampC_Secondary*'
    ]
    first_turret = '*OuterTurret5v5*'
    turrets = ['*OuterTurret5v5*', '*Turret5v5*', '*ArmoryTurret5v5*', '*VainNode*']
    vain_crystal = '*VainCrystal_Home_5v5*'

    match_start_time = None
    for evt in telemetry:
        try:
            evt_type = evt['type']
            evt_time = datetime.strptime(evt['time'], '%Y-%m-%dT%H:%M:%S%z')
            payload = evt['payload']
            seconds = 0 if match_start_time is None else (evt_time - match_start_time).total_seconds()

            # イベントの一覧
            known_events = [
                'HeroBan', 'HeroSelect', 'HeroSkinSelect', 'HeroSwap', 'PlayerFirstSpawn',
                'LevelUp', 'EarnXP', 'LearnAbility', 'UseAbility',
                'BuyItem', 'SellItem', 'UseItemAbility',
                'DealDamage', 'KillActor', 'Vampirism', 'HealTarget',
                'GoldFromTowerKill', # タレット壊した報酬
                'NPCkillNPC', # ミニオンがタレット壊した時（ミニオン同士では発生しない）
            ]
            if evt_type not in known_events:
                print(evt_type)

            # Draft Pick
            # -> matches に全体、rosters にもそのチームのBANを保存しておく？
            # -> 追加情報系なので、matches_append などでテーブルを分けるべきかもしれない。
            if evt_type == 'HeroBan':
                team = 'Left' if payload['Team'] == '1' else 'Right'
                banned[team].append(payload['Hero'])
                banpick_order.append(payload['Hero'])

            if evt_type == 'HeroSelect':
                banpick_order.append(payload['Hero'])

            # Initialize
            if evt_type == 'PlayerFirstSpawn':
                actor = _normalize_actor(payload['Actor'])
                team = payload['Team']
                first_buy_items[team][actor] = []
                first_gold[team][actor] = 600
                item_build_order[team][actor] = []
                use_item_ability[team][actor] = []
                movement_summary[team][actor] = []

            """
            {
                "time": "2018-09-08T14:18:58+0000",
                "type": "HealTarget",
                "payload": {
                    "Team": "Left", "Actor": "*Lance*", "TargetActor": "*Lance*", "TargetTeam": "Left",
                    "Source": "Buff_SpawnStage_Recharge", "Heal": 52, "Healed":  52, "IsHero": 1, "TargetIsHero": 1
                }
            }
            """
            # Recall
            if evt_type == 'HealTarget' and payload['Source'] == 'Buff_SpawnStage_Recharge':
                actor = _normalize_actor(payload['Actor'])
                team = payload['Team']
                position = [-90.00, 0.06, -0.00] if team == 'Left' else [90.00, 0.06, -0.00]
                movement_summary[team][actor].append({
                    'seconds': seconds,
                    'type': 'Recall',
                    'Position': position
                })

            # Buy item
            if evt_type == 'BuyItem':
                actor = _normalize_actor(payload['Actor'])
                team = payload['Team']
                item = payload['Item']
                movement_summary[team][actor].append({
                    'seconds': seconds,
                    'type': evt_type,
                    'Position': payload['Position']
                })

                # Match start time
                # This is not accurate but the nearest value
                if match_start_time is None:
                    match_start_time = evt_time

                """
                チームにおける各アイテムの購入個数別の勝率比較
                （契約、視界、飴ちゃん、ボーンソー、ストクラ、ウォートレ、シバスチ、アトラス等など、気になるし、今このデータは誰も持ってない）
                →stat item team purchase amount
                →ゲームモード、パッチ、地域、ランク、アイテムID（ゲームモードで使われるもの全て）、購入個数（0スタート）、試合数、勝利数のテーブル構造
                """
                # 契約、視界、tier3アイテム、build_type = support のアイテム、

                # 最後にビルド全売りして赤青インフ買う人も多いので割とブレそう
                # 視界、飴ちゃん、インフュージョンは、購入個数より使った回数の方が大事そうなので、そっちを見ようかな
                # UseItemAbility

                # first items
                cost = payload['Cost']
                first_gold[team][actor] -= cost
                if first_gold[team][actor] >= 0:
                    first_buy_items[team][actor].append(item)
                    first_buy_items[team][actor].sort() # A-Z順で並べておく

                # buy tier3 items
                if item in tier3_items:
                    item_build_order[team][actor].append(item)

            # Sell item
            if evt_type == 'SellItem':
                pass

            # Use item
            if evt_type == 'UseItemAbility':
                actor = _normalize_actor(payload['Actor'])
                team = payload['Team']
                item = payload['Ability']
                use_item_ability[team][actor].append({'seconds': seconds, 'item': item})
                movement_summary[team][actor].append({
                    'seconds': seconds,
                    'type': evt_type,
                    'Ability': payload['Ability'],
                    'Position': payload['Position'],
                    'TargetPosition': payload['TargetPosition']
                })

                """
                チームにおけるに特定アイテムの1〜20分の時刻別、「使用した場合」と「使用してない場合」の勝率
                （契約、インフュージョン、飴、視界、靴、泉、クルシ、アトラス）
                →stat item team usage
                →ゲームモード、パッチ、地域、ランク、アイテムID、試合時間、使用回数（0スタート）、試合数、勝利数
                """
                pass

            # Use Ability
            if evt_type == 'UseAbility':
                actor = _normalize_actor(payload['Actor'])
                team = payload['Team']
                movement_summary[team][actor].append({
                    'seconds': seconds,
                    'type': evt_type,
                    'Ability': payload['Ability'],
                    'Position': payload['Position'],
                    'TargetPosition': payload['TargetPosition'],
                    'TargetActor': payload['TargetActor']
                })

            # 回復など
            if evt_type == 'Vampirism':
                pass

            if evt_type == 'HealTarget':
                pass


            """
            # ダメージ、キル、オブジェクト破壊など
            # これを保存する訳だが...大きくなるからテーブル分けた方が良いな。やっぱり。
            # participants_append とかだな。
            {
                # seconds
                # time を Unixtime に変換して開始時刻 Unixtime を引き算する。
                'time': seconds,

                # 敵ヒーロー殴った/倒した、トレントタレットドラゴン倒した、倒された
                # DealDamage / Kill / Killed
                'type': 'DealDamage',

                # Top / Mid / Bot / River_Top / River_Bot
                # Jungle_Top Jungle_Top_Enemy / Jungle_Bot / Jungle_Bot_Enemy
                # Home / Home_Enemy
                'Position' : [-10.10, 0.06, 11.96], # DealDamageの時は場所が分からないっぽい
                'Area': 'Mid',

                # 敵ヒーロー、ミニオン、トレント、タレット、ドラゴン
                # hero / minion / jungle_camp / turret / dragon
                'Target':  'hero'
            }
            """

            # DealDamage 等いくつかの情報は位置情報が無い
            # だいたいどの辺りか見当を付ける為に、ヒーローの最後の位置を保存しておく。
            # 'Ardan' : {'time': 120, 'position': [ -28.81, 0.06, 17.97 ]} という様な感じ
            # 時間も保存するのは。まぁいちおう。
            # ただし、セレスのウルトとかで超遠距離からダメージ与えた場合、位置が全く違うので当てにならない。
            # というか、位置だけでも意味あるのか。これ。
            last_positions = {'Left' : {}, 'Right' : {}}

            hero_movements = {'Left' : {}, 'Right' : {}}
            """
            で、各ヒーローの下にこういうのが入る
            {
                'time': 123
                ああー、ここ普通にテレメトリデータで良さげ。
                ただし、Deathの場合はActorじゃなくてTargetActorになるので、その辺は気をつける。
                とりあえずやれば分かる。
            }
            """


            """
            アビリティ使った
            {
                "time": "2018-09-08T14:18:42+0000",
                "type": "UseAbility",
                "payload": {
                    "Team": "Left", "Actor": "*Malene*", "Ability": "HERO_ABILITY_MALENE_B2_NAME",
                    "Position": [ -28.81, 0.06, 17.97 ],
                    "TargetActor": "None",
                    "TargetPosition": [ -28.81, 0.06, 17.97 ]
                }
            }

            ヒーローにダメージ入れた時（IsHero と TargetIsHero を見れば良いか？）
            ダメージの時は場所が分からないっぽい...。前後のアビリティやキルから最寄りのポジションを出すしかない。
            {
                "time": "2018-09-08T14:16:18+0000",
                "type": "DealDamage",
                "payload": {
                    "Team": "Left", "Actor": "*Samuel*", "Target": "*Ardan*",
                    "Source": "Unknown",
                    "Damage": 100,
                    "Dealt":  83,
                    "IsHero": 1,
                    "TargetIsHero": 1
                }
            }
            ヒーロー倒した時（IsHero と TargetIsHero を見れば良いか？）
            {
                "time": "2018-09-08T14:16:38+0000",
                "type": "KillActor",
                "payload": {
                    "Team": "Right", "Actor": "*Grace*", "Killed": "*Yates*", "KilledTeam": "Left",
                    "Gold": "0", "IsHero": 1, "TargetIsHero": 1, "Position": [ -10.10, 0.06, 11.96 ]
                }
            }
            ミニオンキル
            {
                "time": "2018-09-08T14:16:46+0000",
                "type": "KillActor",
                "payload": {
                    "Team": "Right", "Actor": "*Lyra*", "Killed": "*5v5_Minion_Melee*",
                    "KilledTeam": "Left", "Gold": "30",
                    "IsHero": 1, "TargetIsHero": 0, "Position": [ -2.58, 0.06, 3.77 ]
                }
            }
            ゴーストウィング殴った
            {
                "time": "2018-09-08T14:30:30+0000",
                "type": "DealDamage",
                "payload": {
                    "Team": "Right", "Actor": "*Grumpjaw*", "Target": "*5v5_Ghostwing*",
                    "Source": "Buff_Grumpjaw_A_Damage", "Damage": 943, "Dealt":  290, "IsHero": 1, "TargetIsHero": 0
                }
            }
            ゴーストウィング獲った
            {
                "time": "2018-09-08T14:30:46+0000",
                "type": "KillActor",
                payload": {
                    "Team": "Right", "Actor": "*Grumpjaw*", "Killed": "*5v5_Ghostwing*",
                    "KilledTeam": "Neutral", "Gold": "0", "IsHero": 1, "TargetIsHero": 0,
                    "Position": [ -2.85, 0.06, 29.77 ]
                }
            }

            ブラッククロー（捕獲前）殴った
            {
                "time": "2018-09-08T14:31:07+0000",
                "type": "DealDamage",
                "payload": {
                    "Team": "Right", "Actor": "*Ardan*", "Target": "*5v5_Blackclaw_Uncaptured*",
                    "Source": "Ability__Ardan__B", "Damage": 144, "Dealt":  49, "IsHero": 1, "TargetIsHero": 0
                }
            }
            ブラッククローとったどー（KillActor で Killed が 5v5_Blackclaw_Uncaptured）
            {
                "time": "2018-09-08T14:31:27+0000",
                "type": "KillActor",
                "payload": {
                    "Team": "Right", "Actor": "*Lyra*", "Killed": "*5v5_Blackclaw_Uncaptured*",
                    "KilledTeam": "Neutral", "Gold": "0", "IsHero": 1, "TargetIsHero": 0,
                    "Position": [ 2.85, 0.06, -29.77 ]
                }
            }
            ブラッククロー（捕獲後）殴った
            {
                "time": "2018-09-08T14:32:08+0000",
                "type": "DealDamage",
                "payload": {
                    "Team": "Left", "Actor": "*Yates*", "Target": "*5v5_Blackclaw_Captured*",
                    "Source": "", "Damage": 364, "Dealt":  199, "IsHero": 1, "TargetIsHero": 0
                }
            }
            タレット壊した
            {
                "time": "2018-09-08T14:36:08+0000",
                "type": "KillActor",
                "payload": {
                    "Team": "Right", "Actor": "*Gwen*",
                    "Killed": "*ArmoryTurret5v5*", "KilledTeam": "Left", "Gold": "50",
                    "IsHero": 1, "TargetIsHero": 0, "Position": [ -63.00, 0.06, -22.41 ]
                }
            }
            NPCがタレット壊した
            {
                "time": "2018-09-08T14:37:56+0000",
                "type": "NPCkillNPC",
                "payload": {
                    "Team": "Right", "Actor": "*5v5_Blackclaw_Captured*",
                    "Killed": "*ArmoryTurret5v5*", "KilledTeam": "Left", "Gold": "50",
                    "IsHero": 0, "TargetIsHero": 0, "Position": [ -53.04, 0.06, 0.00 ]
                }
            }
            NPCがベインノード壊した
            {
                "time": "2018-09-08T14:38:20+0000",
                "type": "NPCkillNPC",
                "payload": {
                    "Team": "Right", "Actor": "*5v5_Blackclaw_Captured*",
                    "Killed": "*VainNode*", "KilledTeam": "Left", "Gold": "0",
                    "IsHero": 0, "TargetIsHero": 0, "Position": [ -63.00, 0.06, 0.00 ]
                }
            }
            """
            if evt_type == 'KillActor':
                team = payload['Team']
                actor = _normalize_actor(payload['Actor'])
                killed_target = payload['Killed']

                if payload['IsHero'] == 1:
                    movement_summary[team][actor].append({
                        'seconds': seconds,
                        'type': evt_type,
                        'Killed': killed_target,
                        'TargetIsHero': payload['TargetIsHero'],
                        'Position': payload['Position'],
                    })

                # Count CS around the middle of each lane
                if killed_target in lane_minions:
                    x_axis = payload['Position'][0]
                    y_axis = payload['Position'][2]
                    if abs(x_axis) < 50:
                        # 各レーン中央付近のミニオン処理をカウント
                        position = None
                        if abs(y_axis) < 10:
                            position = 'Mid'
                        elif y_axis <= -10:
                            position = 'Top' if team == 'Left' else 'Bot'
                        elif y_axis >= 10:
                            position = 'Bot' if team == 'Left' else 'Top'

                        if position is not None:
                            if actor not in minion_stat[team][position]:
                                minion_stat[team][position][actor] = 0
                            minion_stat[team][position][actor] += 1
        except Exception as e:
            print('Exception')
            print(evt)
            raise e

    return {
        'banned': banned,
        'banpick_order': banpick_order,
        'first_buy_items': first_buy_items,
        'item_build_order': item_build_order,
        'use_item_ability': use_item_ability,
        'minion_stat': minion_stat,
        'movement_summary': movement_summary,
    }

def _normalize_actor(actor):
    """
    Replace old actor names by correct ones.

    We still get these old actor names time to time, especially in private match telemetry.
    https://github.com/seripap/vainglory/pull/26/files/4d8602f9e52531747bce65dff8a43795e54abaad
    """
    hero_tokens_bad = {
        "*Hero009*" : "*Krul*",
        "*Hero010*" : "*Skaarf*",
        "*Sayoc*"   : "*Taka*",
        "*Hero016*" : "*Rona*",
    }

    if actor in hero_tokens_bad:
        actor = hero_tokens_bad[actor]

    return actor