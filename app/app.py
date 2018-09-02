from flask import Flask
from .database import init_db
import app.models

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    init_db(app)

    return app

app = create_app()
app.app_context().push()