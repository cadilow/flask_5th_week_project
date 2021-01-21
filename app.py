from flask import Flask

from config import Config
from models import db
# from views import *
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

migrate = Migrate(app, db)

db.init_app(app)



if __name__ == "__main__":
    app.run()