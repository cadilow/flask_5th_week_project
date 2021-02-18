import re

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, HiddenField, PasswordField
from wtforms.validators import InputRequired, Email, ValidationError, Length, EqualTo

from config import ADMIN_ACCESS



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


def check_admin_code(form, value):
    msg = 'В доступе к админ панеле отказано'
    if value.data:
        if value.data != str(ADMIN_ACCESS):
            raise ValidationError(msg)


class Cart(FlaskForm):
    name = StringField('Имя', [InputRequired(message='Нужно ввести имя')])
    address = StringField('Адрес', [InputRequired(message='Нужно ввести адрес')])
    mail = StringField('E-mail', [Email(message='Неправильная почта')])
    tel = IntegerField(
        'Телефон',
        [InputRequired(message='Нельзя оставить поле пустым'), phone_validator]
        )
    submit = SubmitField('Оформить заказ')


class Registration(FlaskForm):
    mail = StringField('E-mail', [InputRequired(message='Нужно ввести почту'), Email(message='Неправильная почта')])
    password = PasswordField('Пароль', [
        InputRequired(message='Введите пароль'),
        Length(min=5, message='Пароль не может быть короче 5 символов'),
        check_password
        ])
    password_confirm = PasswordField('Подтверждение пароля', [EqualTo('password', message='Пароли не одинаковые')])
    admin_code = StringField('Код доступа администратора', [check_admin_code])
    submit = SubmitField('Зарегистрироваться')


class RegistrationConfirm(FlaskForm):
    code_confirm = StringField('Код подтверждения', [InputRequired(
        message='Введите код подтверждения, который был отправлен на вашу регистрационную почту'
        )])
    submit = SubmitField('Подтвердить')


class Restore(FlaskForm):
    mail = StringField('E-mail', [InputRequired(message='Нужно ввести почту'), Email(message='Неправильная почта')])
    submit = SubmitField('Восстановить')


class RestoreConfirm(FlaskForm):
    code_confirm = StringField('Код подтверждения', [InputRequired(
        message='Введите код подтверждения, который был отправлен на вашу регистрационную почту'
        )])
    submit = SubmitField('Подтвердить')


class RestoreComplete(FlaskForm):
    password = PasswordField('Пароль', [
        InputRequired(message='Введите пароль'),
        Length(min=5, message='Пароль не может быть короче 5 символов'),
        check_password
        ])
    password_confirm = PasswordField('Подтверждение пароля', [EqualTo('password', message='Пароли не одинаковые')])
    submit = SubmitField('Сменить пароль')


class Authentication(FlaskForm):
    mail = StringField('E-mail', [InputRequired(message='Нужно ввести почту'), Email(message='Неправильная почта')])
    password = PasswordField('Пароль', [InputRequired(message='Введите пароль')])
    submit = SubmitField('Войти')
    