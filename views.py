from flask import render_template, request

from app import app, db
from models import User, Dish, Category, Order, dishes_orders_association


@app.route('/')
def main():
    content = db.session.query(Dish).all()
    return render_template('main.html', content=content)


@app.route('/cart/')
def cart():
    return render_template('cart.html')


@app.route('/account/')
def account():
    return render_template('account.html')


@app.route('/auth/')
def auth():
    return render_template('auth.html')


@app.route('/register/')
def register():
    pass


@app.route('/logout/')
def logout():
    pass


@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')

