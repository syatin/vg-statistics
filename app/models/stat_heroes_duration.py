from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class StatHeroesDuration(db.Model):

    __tablename__ = 'stat_heroes_duration'

    id = db.Column(INT, primary_key=True)
    patchVersion = db.Column(DECIMAL)
    gameMode = db.Column(VARCHAR)
    shardId = db.Column(VARCHAR)
    hero_id = db.Column(INT)
    rank = db.Column(INT)
    role = db.Column(VARCHAR)
    build_type = db.Column(VARCHAR)
    duration_type = db.Column(INT)
    games = db.Column(INT)
    wins = db.Column(INT)
    win_rate = db.Column(DECIMAL)

    def query_one_or_init(params):
        """
        find one result. create new one if there's no result.
        """
        model = StatHeroesDuration.query.filter(
            StatHeroesDuration.patchVersion == params['patchVersion'],
            StatHeroesDuration.gameMode == params['gameMode'],
            StatHeroesDuration.shardId == params['shardId'],
            StatHeroesDuration.hero_id == params['hero_id'],
            StatHeroesDuration.rank == params['rank'],
            StatHeroesDuration.role == params['role'],
            StatHeroesDuration.build_type == params['build_type'],
            StatHeroesDuration.duration_type == params['duration_type'],
        ).first()
        if model is None:
            model = StatHeroesDuration(
                patchVersion=params['patchVersion'],
                gameMode=params['gameMode'],
                shardId=params['shardId'],
                hero_id=params['hero_id'],
                rank=params['rank'],
                role=params['role'],
                build_type=params['build_type'],
                duration_type=params['duration_type'],
                games=0,
                wins=0
            )
        return model