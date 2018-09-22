from app.database import db
from sqlalchemy.types import VARCHAR, INT

class MHeros(db.Model):

    __tablename__ = 'm_heros'

    id = db.Column(INT, primary_key=True)
    actor = db.Column(VARCHAR)
    ja = db.Column(VARCHAR)
    en = db.Column(VARCHAR)
