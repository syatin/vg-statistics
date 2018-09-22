from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT

class Rosters(db.Model):

    __tablename__ = 'rosters'

    id = db.Column(INT, primary_key=True)
    match_id = db.Column(INT)
    acesEarned = db.Column(INT)
    gold = db.Column(INT)
    heroKills = db.Column(INT)
    krakenCaptures = db.Column(INT)
    side = db.Column(VARCHAR)
    turretKills = db.Column(INT)
    turretsRemaining = db.Column(INT)
    won = db.Column(INT)
    averageRankedPoint = db.Column(INT)
    averageRank = db.Column(INT)
