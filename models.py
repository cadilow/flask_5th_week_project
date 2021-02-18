from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)


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
    date = db.Column(db.String, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    tel = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    dishes = db.relationship('Dish', secondary=dishes_orders_association, back_populates='orders')
