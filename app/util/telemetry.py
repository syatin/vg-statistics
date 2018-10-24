import requests

def analyze_telemetry(match):
    """
    telemetryのデータを解析します
    """
    if match.gameMode in ['ranked', 'casual']:
        return {}

    elif match.gameMode in ['5v5_pvp_ranked', '5v5_pvp_casual']:
        return _analyze_5v5(match)

    elif match.gameMode == 'blitz_pvp_ranked':
        return {}

def _analyze_5v5(match):
    minion_stat = {
        'Left': {'Top': {}, 'Mid': {}, 'Bot': {}},
        'Right': {'Top': {}, 'Mid': {}, 'Bot': {}}
    }
    ban_pick = {
        'Left': [], 'Right': []
    }
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

    telemetry_url = match.assets[0].url
    response = requests.get(telemetry_url)
    telemetry = response.json()
    for evt in telemetry:
        # 中央付近のレーンミニオンの処理状況
        if evt['type'] == 'KillActor' and evt['payload']['Killed'] in lane_minions:
            team = evt['payload']['Team']
            actor = evt['payload']['Actor']
            x_axis = evt['payload']['Position'][0]
            y_axis = evt['payload']['Position'][2]
            if abs(x_axis) < 50:
                position = None
                if abs(y_axis) < 10:
                    # Mid
                    position = 'Mid'
                elif y_axis <= -10:
                    # Left から見てTop
                    position = 'Top' if team == 'Left' else 'Bot'
                elif y_axis >= 10:
                    # Left から見てBot
                    position = 'Bot' if team == 'Left' else 'Top'
                if position is not None:
                    if actor not in minion_stat[team][position]:
                        minion_stat[team][position][actor] = 0
                    minion_stat[team][position][actor] += 1

    return {'minion_stat': minion_stat}