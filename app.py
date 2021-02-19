from flask import Flask
from flask_mail import Mail

from config import Config
from models import db
from admin import admin


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

db.init_app(app)

admin.init_app(app)


from views import *


if __name__ == "__main__":
    app.run()
    