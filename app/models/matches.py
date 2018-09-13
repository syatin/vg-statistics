from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME

class Matches(db.Model):

    __tablename__ = 'matches'

    id = db.Column(INT, primary_key=True)
    uuid = db.Column(VARCHAR)
    shardId = db.Column(VARCHAR)
    gameMode = db.Column(VARCHAR)
    duration  = db.Column(INT)
    endGameReason  = db.Column(VARCHAR)
    patchVersion  = db.Column(DECIMAL)
    createdAt  = db.Column(DATETIME)
