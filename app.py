import re
import time
import random

from flask import Flask, render_template, session, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, HiddenField, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

#from config import Config
#from models import db
#from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///store.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "475fyv>ni!s517ryjv%2g7u4icb48sio2l"
app.config['MAIL_SERVER'] = 'smtp.mail.ru'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'stepik_test@list.ru'
app.config['MAIL_PASSWORD'] = 'test'
mail = Mail(app)
#app.config.from_object(Config)

# migrate = Migrate(app, db)

#db.init_app(app)
db = SQLAlchemy(app)

request_counte = 0


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


def check_password(form, value):
    msg = "Пароль должен содержать латинские сивмолы в верхнем и нижнем регистре и цифры"
    patern1 = re.compile('[a-z]+')
    patern2 = re.compile('[A-Z]+')
    patern3 = re.compile('\\d+')
    if (not patern1.search(value.data) or
        not patern2.search(value.data) or
        not patern3.search(value.data)):
        raise ValidationError(msg)


class Cart(FlaskForm):
    name = StringField('Имя', [InputRequired(message='Нужно ввести имя')])
    address = StringField('Адрес', [InputRequired(message='Нужно ввести адрес')])
    mail = StringField('E-mail', [Email(message='Неправильная почта')])
    tel = IntegerField(
        'Телефон',
        [InputRequired(message='Нельзя оставить поле пустым'), phone_validator]
        )
    # summ = HiddenField()
    # cart = HiddenField([Length(min=1, message='Нужно выбрать то, что вам понравилось')])
    submit = SubmitField('Оформить заказ')


class Registration(FlaskForm):
    mail = StringField('E-mail', [InputRequired(message='Нужно ввести почту'), Email(message='Неправильная почта')])
    password = PasswordField('Пароль', [
        InputRequired(message='Введите пароль'),
        Length(min=5, message='Пароль не может быть короче 5 символов'),
        check_password
        ])
    password_confirm = PasswordField('Подтверждение пароля', [EqualTo('password', message='Пароли не одинаковые')])
    submit = SubmitField('Зарегистрироваться')


class RegistrationConfirm(FlaskForm):
    code_confirm = StringField('Код подтверждения', [InputRequired(
        message='Введите код подтверждения, который был отправлен на вашу регистрационную почту'
        )])
    submit = SubmitField('Подтвердить')


class Authentication(FlaskForm):
    mail = StringField('E-mail', [InputRequired(message='Нужно ввести почту'), Email(message='Неправильная почта')])
    password = PasswordField('Пароль', [InputRequired(message='Введите пароль')])
    submit = SubmitField('Войти')


#from views import *


@app.route('/')
def main():
    #session.clear()
    categories = db.session.query(Category).all()
    #dishes = db.session.query(Dish).order_by(db.func.random()).all()
    dishes = []
    for i in range(1, len(categories)+1):
        dishes.append(db.session.query(Dish).filter(Dish.category_id==i).order_by(db.func.random()).limit(3).all())
    return render_template(
        'main.html', 
        categories=categories, 
        dishes=dishes
    )

@app.route('/precart/<id>/')
def precart(id):
    if id in session.get('cart', False):
        session['error'] = 'Можно заказать только одну порцию блюда за раз'
        session['cart_error'] = True
        session['cart_error_confirm'] = True
        return redirect('/cart/')
    if session.get('cart', False):
        cart = session['cart']
    else:
        cart = []
    cart.append(id)
    session['cart'] = cart 
    if session.get('total', False) == False:
        session['total'] = 0
    session['total'] += db.session.query(Dish).filter(Dish.id==id).first().price 
    return redirect('/cart/')


@app.route('/delcart/<id>/')
def delcart(id):
    cart = session['cart']
    cart.remove(id)
    session['cart'] = cart
    session['total'] -= db.session.query(Dish).filter(Dish.id==id).first().price 
    session['is_delete_dish'] = True
    session['is_delete_dish_confirm'] = True
    return redirect('/cart/')


@app.route('/cart/', methods=['GET', 'POST'])
def cart():
    # единоразовое выведение сообщения об удалении из корзины
    if session.get('is_delete_dish_confirm', False) is False:
        session['is_delete_dish'] = False
    if session.get('is_delete_dish_confirm', False):
        session['is_delete_dish_confirm'] = False
    
    # единоразовое выведение ошибки
    if session.get('cart_error_confirm', False) is False:
        session['cart_error'] = False
    if session.get('cart_error_confirm', False):
        session['cart_error_confirm'] = False

    if session.get('cart', False) == False:
        session['cart'] = []
    form = Cart()
    if request.method == 'POST':
        name = form.name.data
        address = form.address.data
        mail = form.mail.data
        tel = form.tel.data
        summ = session.get('total', False)
        cart = session.get('cart', False)
        if cart is False or cart == []:
            session['cart_error'] = True
            session['cart_error_confirm'] = True
            session['error'] = 'Нужно выбрать то, что вам понравилось'
            return redirect('/cart/')
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
                session['total'] = 0
                session['cart'] = []
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
                session['total'] = 0
                session['cart'] = []
            return redirect('/ordered/')
        else:
            return render_template('cart.html', Dish=Dish, form=form)
    return render_template('cart.html', Dish=Dish, form=form)


@app.route('/account/')
def account():
    if session.get('user_id', False):
        user = db.session.query(User).filter(User.id==session['user_id']).first()
        orders = db.session.query(Order).filter(Order.email==user.mail).order_by(Order.date)[::-1]
        return render_template('account.html', user=user, orders=orders)
    return redirect('/auth/')


@app.route('/auth/', methods=['GET', 'POST'])
def auth():
    form = Authentication()
    err = ''
    if session.get('user_id', False):
        return redirect('/')
    if request.method == 'POST':
        mail = form.mail.data
        password = form.password.data
        user = db.session.query(User).filter(User.mail==mail).first()
        if user:
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                return redirect('/account/')
            else:
                time.sleep(0.5)
                err = 'Не верная почта или пароль'
        else:
            time.sleep(0.5)
            err = 'Не верная почта или пароль'
    return render_template('auth.html', form=form, err=err)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = Registration()
    if request.method == 'POST':
        if form.validate_on_submit():
            mail = form.mail.data
            password = form.password.data
            password_confirm = form.password_confirm.data
            user = db.session.query(User).filter(User.mail==mail).first()
            if user:
                err = 'Такой пользователь уже существует'
                return render_template('register.html', form=form, err=err)
            else:
                session['user_confirm_registration'] = {
                    'mail': mail,
                    'password': password
                }
                return redirect('/register_confirm/')
                '''password_hash = generate_password_hash(password)
                user = User(mail=mail, password=password_hash)
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                return redirect('/account/')'''
    return render_template('register.html', form=form)


@app.route('/register_confirm/', methods=['GET', 'POST'])
def register_confirm():
    form = RegistrationConfirm()
    if request.method == 'POST':
        code_confirm = form.code_confirm.data
        if code_confirm == session['request_confirm_pass']:
            password_hash = generate_password_hash(session['user_confirm_registration']['password'])
            user = User(mail=session['user_confirm_registration']['mail'], password=password_hash)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            session['user_confirm_registration'] = {}
            session['request_confirm_pass'] = False
            session['error'] = False
            return redirect('/account/')
        session['error'] = 'Не верный код подтверждения'
        session['register_error'] = True
        session['register_error_confirm'] = True
        return render_template('register_confirm.html', form=form)
    if not session.get('request_confirm_pass', False) or session.get('request_confirm_pass',False) == '':
        if session['user_confirm_registration'] and session['user_confirm_registration'] != {}:
            request_counte += 1
            request_confirm_pass = ''
            for i in range(4):
                request_confirm_pass += str(random.randint(0, 9))
            with app.app_context():
                subject = 'Подтверждение регистрации'
                sender = app.config['MAIL_USERNAME']
                recipients = [session['user_confirm_registration']['mail']]
                text_body = f'Для подтверждения регистрации введите код {request_confirm_pass} (сессия №{request_counte})'
                msg = Message(
                    subject,
                    sender=sender,
                    recipients=recipients
                )
                msg.body = text_body
                mail.send(msg)
                session['request_counte'] = request_counte
                session['request_confirm_pass'] = request_confirm_pass
                return render_template('register_confirm.html', form=form)
        else:
            return redirect('/register/')
    if session.get('register_error_confirm', False) is False:
        session['register_error'] = False
    if session.get('register_error_confirm', False):
        session['register_error_confirm'] = False
    return render_template('register_confirm.html', form=form)


@app.route('/logout/', methods=['POST'])
def logout():
    if request.method == 'POST':
        if session.get('user_id', False):
            session['user_id'] = False
    return redirect('/auth/')


@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')


if __name__ == "__main__":
    app.run(debug=True)
    