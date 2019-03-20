from app.database import db
from sqlalchemy.types import VARCHAR, INT, DECIMAL, DATETIME, JSON

class MatchesExtra(db.Model):

    __tablename__ = 'matches_extra'

    id = db.Column(INT, primary_key=True)
    match_id = db.Column(INT)
    banpick = db.Column(JSON)

