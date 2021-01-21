import os


current_path = os.path.dirname(os.path.realpath(__file__))

db_path = "sqlite:///" + current_path + "\\store.db"


class Config:
    DEBUG = True
    SECRET_KEY= "475fyv>ni!s517ryjv%2g7u4icb48sio2l"
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False

