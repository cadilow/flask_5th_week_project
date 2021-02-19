from flask import redirect, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import db, User, Dish, Category, Order


class AdminAccess(ModelView):
    def is_accessible(self):
        return session.get('is_admin', False)
    def inaccessible_callback(self, name, **kwargs):
        return redirect('/')


admin = Admin()
admin.add_view(AdminAccess(User, db.session))
admin.add_view(AdminAccess(Dish, db.session))
admin.add_view(AdminAccess(Category, db.session))
admin.add_view(AdminAccess(Order, db.session))
