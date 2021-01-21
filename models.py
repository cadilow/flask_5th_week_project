from sqlalchemy import CheckConstraint
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///store.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "475fyv>ni!s517ryjv%2g7u4icb48sio2l"


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, CheckConstraint("email LIKE '%@%'"), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    orders = db.relationship('Order', back_populates='users')


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
    orders = db.relationship('Order', secondary=dishes_orders_association, back_populates='dishes')


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    meals = db.relationship('Dish', back_populates='category')
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    email = db.Column(db.String, CheckConstraint("email LIKE '%@%'"), nullable=False)
    tel = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    basket = db.Column(db.String, nullable=False)
    users = db.relationship('User', back_populates='orders')
    dishes = db.relationship('Dish', secondary=dishes_orders_association, back_populates='orders')


db.create_all()
