from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class StatBanHeroes(db.Model):

    __tablename__ = 'stat_ban_heroes'

    id = db.Column(INT, primary_key=True)
    patchVersion = db.Column(DECIMAL)
    shardId = db.Column(VARCHAR)
    gameMode = db.Column(VARCHAR)
    averageRank = db.Column(INT)
    side = db.Column(VARCHAR)
    ban_order = db.Column(INT)
    ban_hero_id = db.Column(INT)
    games = db.Column(INT)
    wins = db.Column(INT)
    win_rate = db.Column(DECIMAL)

    def query_one_or_init(params):
        """
        find one result. create new one if there's no result.
        """
        model = StatBanHeroes.query.filter(
            StatBanHeroes.patchVersion == params['patchVersion'],
            StatBanHeroes.shardId == params['shardId'],
            StatBanHeroes.gameMode == params['gameMode'],
            StatBanHeroes.averageRank == params['averageRank'],
            StatBanHeroes.side == params['side'],
            StatBanHeroes.ban_order == params['ban_order'],
            StatBanHeroes.ban_hero_id == params['ban_hero_id'],
        ).first()
        if model is None:
            model = StatBanHeroes(
                patchVersion=params['patchVersion'],
                shardId=params['shardId'],
                gameMode=params['gameMode'],
                averageRank=params['averageRank'],
                side=params['side'],
                ban_order=params['ban_order'],
                ban_hero_id=params['ban_hero_id'],
                games=0,
                wins=0
            )
        return model