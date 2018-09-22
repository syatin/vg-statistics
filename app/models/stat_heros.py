from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class StatHeros(db.Model):

    __tablename__ = 'stat_heros'

    id = db.Column(INT, primary_key=True)
    patchVersion = db.Column(DECIMAL)
    shardId = db.Column(VARCHAR)
    gameMode = db.Column(VARCHAR)
    week = db.Column(DATETIME)
    hero_id = db.Column(INT)
    rank = db.Column(INT)
    role = db.Column(VARCHAR)
    duration_type = db.Column(INT)
    build_type = db.Column(VARCHAR)
    games = db.Column(INT)
    wins = db.Column(INT)
    win_rate = db.Column(DECIMAL)

    def query_one_or_init(params):
        """
        find one result. create new one if there's no result.
        """
        model = StatHeros.query.filter(
            StatHeros.hero_id == params['hero_id'],
            StatHeros.patchVersion == params['patchVersion'],
            StatHeros.gameMode == params['gameMode'],
            StatHeros.week == params['week'],
            StatHeros.shardId == params['shardId'],
            StatHeros.rank == params['rank'],
            StatHeros.role == params['role'],
            StatHeros.duration_type == params['duration_type'],
            StatHeros.build_type == params['build_type']
        ).first()
        if model is None:
            model = StatHeros(
                hero_id=params['hero_id'],
                patchVersion=params['patchVersion'],
                gameMode=params['gameMode'],
                week=params['week'],
                shardId=params['shardId'],
                rank=params['rank'],
                role=params['role'],
                duration_type=params['duration_type'],
                build_type=params['build_type'],
                games=0,
                wins=0
            )
        return model