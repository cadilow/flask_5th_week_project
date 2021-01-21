from flask import render_template, request

from app import app


@app.route('/')
def main():
    pass


@app.route('/cart/')
def cart():
    pass


@app.route('/account/')
def account():
    pass


@app.route('/auth/')
def auth():
    pass


@app.route('/register/')
def register():
    pass


@app.route('/logout/')
def logout():
    pass


@app.route('/ordered/')
def ordered():
    pass

