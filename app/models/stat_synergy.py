from app.database import db
from sqlalchemy.types import VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class StatSynergy(db.Model):

    __tablename__ = 'stat_synergy'

    id = db.Column(INT, primary_key=True)
    patchVersion = db.Column(DECIMAL)
    gameMode = db.Column(VARCHAR)
    hero_id_1 = db.Column(INT)
    role_1 = db.Column(VARCHAR)
    build_type_1 = db.Column(VARCHAR)
    hero_id_2 = db.Column(INT)
    role_2 = db.Column(VARCHAR)
    build_type_2 = db.Column(VARCHAR)
    is_enemy = db.Column(BOOLEAN)
    games = db.Column(INT)
    wins = db.Column(INT)
    win_rate = db.Column(DECIMAL)
    synergy = db.Column(DECIMAL)

    def query_one_or_init(params):
        """
        find one result. create new one if there's no result.
        """
        model = StatSynergy.query.filter(
            StatSynergy.patchVersion == params['patchVersion'],
            StatSynergy.gameMode == params['gameMode'],
            StatSynergy.hero_id_1 == params['hero_id_1'],
            StatSynergy.role_1 == params['role_1'],
            StatSynergy.build_type_1 == params['build_type_1'],
            StatSynergy.hero_id_2 == params['hero_id_2'],
            StatSynergy.role_2 == params['role_2'],
            StatSynergy.build_type_2 == params['build_type_2'],
            StatSynergy.is_enemy == params['is_enemy']
        ).first()
        if (model is None):
            model = StatSynergy(
                patchVersion=params['patchVersion'],
                gameMode=params['gameMode'],
                hero_id_1=params['hero_id_1'],
                role_1=params['role_1'],
                build_type_1=params['build_type_1'],
                hero_id_2=params['hero_id_2'],
                role_2=params['role_2'],
                build_type_2=params['build_type_2'],
                is_enemy=params['is_enemy'],
                games=0, wins=0, win_rate=0
            )
        return model