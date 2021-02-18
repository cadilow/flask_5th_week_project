from flask import Flask, redirect
from flask_mail import Mail
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from config import Config
from models import db, User, Dish, Category, Order


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

db.init_app(app)


class MicroBlogModelView(ModelView):
    def is_accessible(self):
        return session.get('is_admin', False)
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')
        

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Dish, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Order, db.session))


from views import *


if __name__ == "__main__":
    app.run()
    