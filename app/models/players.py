from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DATETIME

class Players(db.Model):

    __tablename__ = 'players'

    id = db.Column(INT, primary_key=True)
    playerId = db.Column(VARCHAR)
    name = db.Column(VARCHAR)
    shardId = db.Column(VARCHAR)
    gamesPlayed = db.Column(JSON)
    guildTag  = db.Column(VARCHAR)
    karmaLevel  = db.Column(INT)
    level  = db.Column(INT)
    rankPoints  = db.Column(JSON)
    updatedAt  = db.Column(DATETIME)