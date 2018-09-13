from app.database import db
from sqlalchemy.types import JSON, VARCHAR, INT, DECIMAL, DATETIME

class MItems(db.Model):

    __tablename__ = 'm_items'

    id = db.Column(INT, primary_key=True)
    name = db.Column(VARCHAR)
    item_id = db.Column(VARCHAR)
    type = db.Column(VARCHAR)
    build_type = db.Column(VARCHAR)
    tier  = db.Column(INT)
