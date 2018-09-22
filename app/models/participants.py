from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME, BOOLEAN

class Participants(db.Model):

    __tablename__ = 'participants'

    id = db.Column(INT, primary_key=True)
    match_id = db.Column(INT)
    roster_id = db.Column(INT)
    player_id = db.Column(INT)
    player_name = db.Column(VARCHAR)
    rankPoint = db.Column(INT)
    rank = db.Column(INT)
    hero_id = db.Column(INT)
    actor = db.Column(VARCHAR)
    skinKey = db.Column(VARCHAR)
    role = db.Column(VARCHAR)
    kills = db.Column(INT)
    assists = db.Column(INT)
    deaths = db.Column(INT)
    gold = db.Column(INT)
    minionKills = db.Column(INT)
    jungleKills = db.Column(INT)
    nonJungleMinionKills = db.Column(INT)
    items = db.Column(JSON)
    itemUses = db.Column(JSON)
    build_type = db.Column(VARCHAR)
    wentAfk = db.Column(BOOLEAN)
    winner = db.Column(BOOLEAN)