from functools import wraps

from flask import Flask
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from config import Config
from models import db, User, Dish, Category, Order


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

db.init_app(app)


'''class AdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        if session.get('is_admin', False):
            return self.render('admin/master.html')
        return redirect('/')'''
        

admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Dish, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Order, db.session))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            abort(403, description="Forbidden")	
        return f(*args, **kwargs)
    return decorated_function


from views import *


'''@app.route('/admin/')
@admin_only
def adminka():
    return render_template('admin/master.html')'''


if __name__ == "__main__":
    app.run()
    