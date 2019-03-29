from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class StatHeroes(db.Model):

    __tablename__ = 'stat_heroes'

    id = db.Column(INT, primary_key=True)
    patchVersion = db.Column(DECIMAL)
    shardId = db.Column(VARCHAR)
    gameMode = db.Column(VARCHAR)
    week = db.Column(DATETIME)
    hero_id = db.Column(INT)
    rank = db.Column(INT)
    role = db.Column(VARCHAR)
    build_type = db.Column(VARCHAR)
    games = db.Column(INT)
    wins = db.Column(INT)
    win_rate = db.Column(DECIMAL)

    def query_one_or_init(params):
        """
        find one result. create new one if there's no result.
        """
        model = StatHeroes.query.filter(
            StatHeroes.hero_id == params['hero_id'],
            StatHeroes.patchVersion == params['patchVersion'],
            StatHeroes.gameMode == params['gameMode'],
            StatHeroes.week == params['week'],
            StatHeroes.shardId == params['shardId'],
            StatHeroes.rank == params['rank'],
            StatHeroes.role == params['role'],
            StatHeroes.build_type == params['build_type']
        ).first()
        if model is None:
            model = StatHeroes(
                hero_id=params['hero_id'],
                patchVersion=params['patchVersion'],
                gameMode=params['gameMode'],
                week=params['week'],
                shardId=params['shardId'],
                rank=params['rank'],
                role=params['role'],
                build_type=params['build_type'],
                games=0,
                wins=0
            )
        return model