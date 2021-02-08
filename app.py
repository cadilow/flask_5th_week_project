from flask import Flask, render_template, session, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Email

#from config import Config
#from models import db
#from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///store.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "475fyv>ni!s517ryjv%2g7u4icb48sio2l"
#app.config.from_object(Config)

# migrate = Migrate(app, db)

#db.init_app(app)
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    orders = db.relationship('Order', back_populates='user')


dishes_orders_association = db.Table(
    'dishes_orders',
    db.Column('dish_id', db.Integer, db.ForeignKey('dishes.id')),
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'))
)


class Dish(db.Model):
    __tablename__ = 'dishes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    picture = db.Column(db.String, nullable=False)
    category = db.relationship('Category', back_populates='meals')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    orders = db.relationship('Order', secondary=dishes_orders_association, back_populates='dishes')


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, nullable=False)
    meals = db.relationship('Dish', back_populates='category')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    tel = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='orders')
    dishes = db.relationship('Dish', secondary=dishes_orders_association, back_populates='orders')


#db.create_all()


# Формы


def phone_validator(form, value):
    if len(str(value.data)) != 10:
        raise ValidationError('Формат ввода  номера телефона: "1234567890"')


class Cart(FlaskForm):
    name = StringField('Имя', [InputRequired(message='Нужно ввести имя')])
    address = StringField('Адрес', [InputRequired(message='Нужно ввести адрес')])
    mail = StringField('E-mail', [Email(message='Неправильная почта')])
    tel = IntegerField(
        'Телефон',
        [InputRequired(message='Нельзя оставить поле пустым'), phone_validator]
        )
    summ = HiddenField()
    cart = HiddenField([InputRequired(message='Нужно выбрать то, что вам понравилось')])
    submit = SubmitField('Оформить заказ')


#from views import *


@app.route('/')
def main():
    #session.clear()
    categories = db.session.query(Category).all()
    #dishes = db.session.query(Dish).order_by(db.func.random()).all()
    dishes = []
    for i in range(1, len(categories)+1):
        dishes.append(db.session.query(Dish).filter(Dish.category_id == i).order_by(db.func.random()).limit(3).all())
    return render_template(
        'main.html', 
        categories=categories, 
        dishes=dishes
    )

@app.route('/precart/<id>/')
def precart(id):
    if session.get('cart', False):
        cart = session['cart']
    else:
        cart = []
    cart.append(id)
    session['cart'] = cart 
    if session.get('total', False) == False:
        session['total'] = 0
    session['total'] += db.session.query(Dish).filter(Dish.id == id).first().price 
    return redirect('/cart/')


@app.route('/delcart/<id>/')
def delcart(id):
    cart = session['cart']
    cart.remove(id)
    session['cart'] = cart
    session['total'] -= db.session.query(Dish).filter(Dish.id == id).first().price 
    session['is_delete_dish'] = True
    session['redirect'] = True
    return redirect('/cart/')


@app.route('/cart/', methods=['GET', 'POST'])
def cart():
    if session.get('redirect', False) is False:
        session['is_delete_dish'] = False
    if session.get('redirect', False) and session.get('is_delete_dish', False):
        session['redirect'] = False
    if session.get('cart', False) == False:
        session['cart'] = []
    form = Cart()
    if request.method == 'POST':
        name = form.name.data
        address = form.address.data
        mail = form.mail.data
        tel = str(form.tel.data)
        summ = form.summ.data
        cart = form.cart.data
        result = ''
        for i in cart:
            if i =='[' or i ==']' or i =='\'' or i ==' ':
                result += ''
            else:
                result += i
        cart = result.split(',')
        if form.validate_on_submit():
            if session.get('is_auth', False) == True:
                order = Order(
                    name=name,
                    address=address,
                    email=mail,
                    tel=tel,
                    total=summ,
                    status='a',
                    # user_id=db.session.query(User).filter(User.mail==mail).first()
                )
                for i in cart:
                    dish = db.session.query(Dish).filter(Dish.id==i).first()
                    order.dishes.append(dish)
                db.session.commit()
            else:
                order = Order(
                    name=name,
                    address=address,
                    email=mail,
                    tel=tel,
                    total=summ,
                    status='a'
                )
                db.session.add(order)
                for i in cart:
                    dish = db.session.query(Dish).filter(Dish.id==i).first()
                    order.dishes.append(dish)
                db.session.commit()
            return redirect('/ordered/')
        else:
            return render_template('cart.html', Dish=Dish, form=form)
    return render_template('cart.html', Dish=Dish, form=form)


@app.route('/account/')
def account():
    return render_template('account.html')


@app.route('/auth/')
def auth():
    return render_template('auth.html')


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/logout/')
def logout():
    pass


@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')


if __name__ == "__main__":
    app.run(debug=True)
    