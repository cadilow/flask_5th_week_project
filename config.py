db_path = 'sqlite:///store.db'
SENDER = 'example@mail.com'


class Config:
    DEBUG = True
    SECRET_KEY= '475fyv>ni!s517ryjv%2g7u4icb48sio2l'
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.mail.ru'
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = SENDER
    MAIL_PASSWORD = 'example'


ADMIN_ACCESS = 1111
