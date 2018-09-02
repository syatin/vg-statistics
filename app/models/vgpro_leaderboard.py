from datetime import datetime
from app.database import db

class VgproLeaderboard(db.Model):

    __tablename__ = 'vgpro_leaderboard'

    id = db.Column(db.Integer, primary_key=True)
    gamemode = db.Column(db.String(16), nullable=False)
    playerId = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    region  = db.Column(db.String(2), nullable=False)
    tier  = db.Column(db.Integer, nullable=True)
    position  = db.Column(db.Integer, nullable=False)
    points  = db.Column(db.Integer, nullable=True)
    kda  = db.Column(db.Integer, nullable=True)
    winRate  = db.Column(db.Integer, nullable=True)
    kp  = db.Column(db.Integer, nullable=True)
    games  = db.Column(db.Integer, nullable=True)
    wins  = db.Column(db.Integer, nullable=True)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now)