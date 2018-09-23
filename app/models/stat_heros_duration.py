from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class StatHerosDuration(db.Model):

    __tablename__ = 'stat_heros_duration'

    id = db.Column(INT, primary_key=True)
    patchVersion = db.Column(DECIMAL)
    gameMode = db.Column(VARCHAR)
    shardId = db.Column(VARCHAR)
    hero_id = db.Column(INT)
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
        model = StatHerosDuration.query.filter(
            StatHerosDuration.patchVersion == params['patchVersion'],
            StatHerosDuration.gameMode == params['gameMode'],
            StatHerosDuration.shardId == params['shardId'],
            StatHerosDuration.hero_id == params['hero_id'],
            StatHerosDuration.role == params['role'],
            StatHerosDuration.build_type == params['build_type'],
            StatHerosDuration.duration_type == params['duration_type'],
        ).first()
        if model is None:
            model = StatHerosDuration(
                patchVersion=params['patchVersion'],
                gameMode=params['gameMode'],
                shardId=params['shardId'],
                hero_id=params['hero_id'],
                role=params['role'],
                build_type=params['build_type'],
                duration_type=params['duration_type'],
                games=0,
                wins=0
            )
        return model