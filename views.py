from datetime import datetime
import time
import random

from flask import Flask, render_template, session, redirect, request
from sqlalchemy.sql import func
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, mail
from models import User, Dish, Category, Order, dishes_orders_association
from forms import phone_validator, check_password, check_admin_code
from forms import Cart, Registration, RegistrationConfirm, Restore, RestoreConfirm, RestoreComplete, Authentication
from config import ADMIN_ACCESS, SENDER
from months import months


@app.route('/')
def main():
    categories = db.session.query(Category).all()
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
    # one-time display message about deletion from the basket
    if session.get('is_delete_dish_confirm', False) is False:
        session['is_delete_dish'] = False
    if session.get('is_delete_dish_confirm', False):
        session['is_delete_dish_confirm'] = False
    
    # one-time error display
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
            day_of_month = datetime.strftime(datetime.now(), "%d")
            raw_month = datetime.strftime(datetime.now(), "%m")
            for i in months:
                if i == str(raw_month):
                    month = months[i]
                    break
            date = str(day_of_month) + ' ' + str(month)
            order = Order(
                name=name,
                address=address,
                email=mail,
                tel=tel,
                total=summ,
                status='a',
                date=date
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
                session['is_admin'] = user.is_admin
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
    if session.get('user_id', False):
        return redirect('/account/')
    if request.method == 'POST':
        if form.validate_on_submit():
            mail = form.mail.data
            password = form.password.data
            password_confirm = form.password_confirm.data
            admin_code = form.admin_code.data
            user = db.session.query(User).filter(User.mail==mail).first()
            if user:
                err = 'Такой пользователь уже существует'
                return render_template('register.html', form=form, err=err)
            else:
                if admin_code == str(ADMIN_ACCESS):
                    is_admin = True
                else:
                    is_admin = False
                session['user_confirm_registration'] = {
                    'mail': mail,
                    'password': password,
                    'is_admin': is_admin
                }
                return redirect('/register_confirm/')
    return render_template('register.html', form=form)


@app.route('/register_confirm/', methods=['GET', 'POST'])
def register_confirm():
    form = RegistrationConfirm()
    if request.method == 'POST':
        if form.validate_on_submit():
            code_confirm = form.code_confirm.data
            if code_confirm == session['request_confirm_pass']:
                password_hash = generate_password_hash(session['user_confirm_registration']['password'])
                user = User(
                    mail=session['user_confirm_registration']['mail'], 
                    password=password_hash,
                    is_admin=session['user_confirm_registration']['is_admin'])
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                session['user_confirm_registration'] = {}
                session['request_confirm_pass'] = False
                session['error'] = False
                return redirect('/account/')
            time.sleep(0.5)
            session['error'] = 'Не верный код подтверждения'
            session['register_error'] = True
            session['register_error_confirm'] = True
            return render_template('register_confirm.html', form=form)
    if not session.get('request_confirm_pass', False) or session.get('request_confirm_pass',False) == '':
        if session['user_confirm_registration'] and session['user_confirm_registration'] != {}:
            request_counte = ''
            for i in range(4):
                request_counte += str(random.randint(0, 9))
            request_confirm_pass = ''
            for i in range(4):
                request_confirm_pass += str(random.randint(0, 9))
            with app.app_context():
                subject = 'Подтверждение регистрации'
                sender = SENDER
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


@app.route('/restore/', methods=['GET', 'POST'])
def restore():
    form = Restore()
    if request.method == 'POST':
        if form.validate_on_submit():
            if db.session.query(User).filter(User.mail==form.mail.data).first():
                session['mail_restore'] = form.mail.data
                request_counte = ''
                for i in range(4):
                    request_counte += str(random.randint(0, 9))
                request_code_confirm = ''
                for i in range(4):
                    request_code_confirm += str(random.randint(0, 9))
                with app.app_context():
                    subject = 'Восстановление пароля'
                    sender = SENDER
                    recipients = [session['mail_restore']]
                    text_body = f'Для восстановления пароля введите код {request_code_confirm} (сессия №{request_counte})'
                    msg = Message(
                        subject,
                        sender=sender,
                        recipients=recipients
                    )
                    msg.body = text_body
                    mail.send(msg)
                session['request_counte'] = request_counte
                session['request_code_confirm'] = request_code_confirm
                return redirect('/restore_confirm/')
            else:
                time.sleep(0.5)
                session['error'] = 'В базе нет такого пользователя'
                session['find_error'] = True
                session['find_error_confirm'] = True
                return render_template('/restore.html/', form=form)
    if session.get('find_error_confirm', False) is False:
        session['find_error'] = False
    if session.get('find_error_confirm', False):
        session['find_error_confirm'] = False
    return render_template('restore.html', form=form)


@app.route('/restore_confirm/', methods=['GET', 'POST'])
def restore_confirm():
    form = RestoreConfirm()
    if session.get('request_code_confirm', False):
        if request.method == 'POST':
            if form.validate_on_submit():
                code_confirm = form.code_confirm.data
                if code_confirm == session['request_code_confirm']:
                    session['mail_complete_restore'] = session['mail_restore']
                    session['mail_restore'] = False
                    session['request_counte'] = False
                    session['request_code_confirm'] = False
                    return redirect('/restore_complete/')
                else:
                    time.sleep(0.5)
                    session['error'] = 'Не верный код подтверждения'
                    session['restore_error'] = True
                    session['restore_error_confirm'] = True
                    return render_template('restore_confirm.html', form=form)
        if session.get('restore_error_confirm', False) is False:
            session['restore_error'] = False
        if session.get('restore_error_confirm', False):
            session['restore_error_confirm'] = False
        return render_template('restore_confirm.html', form=form)
    else:
        return redirect('/restore/')


@app.route('/restore_complete/', methods=['GET', 'POST'])
def restore_complete():
    if session.get('mail_complete_restore', False):
        form = RestoreComplete()
        if request.method == 'POST':
            if form.validate_on_submit():
                password = form.password.data
                password_hash = generate_password_hash(password)
                user_mail = session['mail_complete_restore']
                user = db.session.query(User).filter(User.mail==user_mail).first()
                user.password = password_hash
                db.session.commit()
                session['user_id'] = user.id
                session['mail_complete_restore'] = False
                session['error'] = False
                return redirect('/account/')
        return render_template('restore_complete.html', form=form)
    else:
        return redirect('/restore/')

@app.route('/logout/', methods=['POST'])
def logout():
    if request.method == 'POST':
        session['user_id'] = False
        session['is_admin'] = False
    return redirect('/auth/')


@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')
