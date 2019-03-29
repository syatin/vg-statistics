from app.database import db
from sqlalchemy.types import VARCHAR, INT

class MHeroes(db.Model):

    __tablename__ = 'm_heroes'

    id = db.Column(INT, primary_key=True)
    actor = db.Column(VARCHAR)
    ja = db.Column(VARCHAR)
    en = db.Column(VARCHAR)
