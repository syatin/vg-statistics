from flask_restplus import Resource, Api
from app.app import app

#if __name__ == '__main__':
#    app.run()

api = Api(app)

"""
Captain
Adagio Ardan Catherine Churnwalker Flicker
Fortress Grace Lance Lorelai Lyra Phinn Yates

Jungler
Alpha Graive Grumpjaw Inara Jule
Koshka Krul Ozo Petal Reim Rona Taka Tony Ylva

Laner
Sangfeng Anka Baptiste Baron BlackFeather
Celeste Gwen Idris Kensei Kestrel Kinetic Magnus
Malane Reza Ringo Samuel SAW Silvernail Skaarf Skye
Varya Vox
"""

@api.route('/master/heroes')
class HeroMaster(Resource):
    def get(self):
        return {
            'adagio': {
                'name' : 'Adagio',
                'name-ja' : 'アダージオ',
                'role': 'captain'
            },
            'alpha' : {
                'name' : 'Alpha',
                'name-ja' : 'アルファ',
                'role': 'jungler'
            }
        }

@api.route('/stat/hero')
class HeroStat(Resource):
    def get(self):
        return {
            'hero' : 'adagio',
            # バンピック率
            'ban' : 5.5,
            'pick' : {
                'bot': 15.0,
                'captain': 29.0,
                'mid': 5.0,
                'top': 10.0
            },
            # ポジションビルド別の勝率
            'stat' : {
                'bot' : {
                    'wp': {
                        'winrate' : 54.0,
                        'winrate-by-time' : {'10': 62.5, '15': 60.0, '20': 55.6, '25': 50.3, '30': 46.6}
                    }
                },
                'captain' : {
                    'utility': {
                        'winrate': 53.2,
                        'winrate-by-time' : {'10': 62.5, '15': 60.0, '20': 55.6, '25': 50.3, '30': 46.6}
                    }
                },
                'mid' : {
                    'cp': {
                        'winrate': 50.2,
                        'winrate-by-time' : {'10': 62.5, '15': 60.0, '20': 55.6, '25': 50.3, '30': 46.6}
                    },
                    'wp': {
                        'winrate': 43.2,
                        'winrate-by-time' : {'10': 62.5, '15': 60.0, '20': 55.6, '25': 50.3, '30': 46.6}
                    }
                },
                'top': {
                    'wp': {
                        'winrate': 54.0,
                        'winrate-by-time' : {'10': 62.5, '15': 60.0, '20': 55.6, '25': 50.3, '30': 46.6}
                    },
                    'utility': {
                        'winrate': 49.5,
                        'winrate-by-time' : {'10': 62.5, '15': 60.0, '20': 55.6, '25': 50.3, '30': 46.6}
                    },
                }
            }
        }


@api.route('/stat/ranking')
class Ranking(Resource):
    def get(self):
        return [
            {
                'hero' : 'adagio',
                'position' : 'captain',
                'build' : 'utility',
                'pick' : 32.5,
                'ban' : 3.7,
                'winrate' : 52.5,
                'winrate-by-time': {
                    '10': 62.5,
                    '15': 60.0,
                    '20': 55.6,
                    '25': 50.3,
                    '30': 46.6
                }
            },
            {
                'hero' : 'alpha',
                'role' : 'top',
                'build' : 'wp',
                'pick' : 32.5,
                'ban' : 3.7,
                'winrate' : 52.5,
                'winrate-time': {
                    '10': 62.5,
                    '15': 60.0,
                    '20': 55.6,
                    '25': 50.3,
                    '30': 46.6
                }
            }
        ]



@api.route('/items')
class Item(Resource):
    def get(self):
        return {'hello': 'world'}

if __name__ == '__main__':
    app.run(debug=True)