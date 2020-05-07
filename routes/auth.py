from flask import Blueprint, render_template, redirect
from flask_login import login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

from data.db_session import create_session
from data.user import User

# Создание Blueprint
blueprint = Blueprint('auth_api', __name__)
# Сессия БД
session = create_session()


# Форма регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


# Форма входа
class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


# Путь для формы регистрации
@blueprint.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Проверка двух полей с паролями
        if form.password.data != form.password2.data:
            return render_template(
                'registration.html',
                title='Регистрация',
                form=form,
                error='Пароли не совпадают'
            )
        # Проверка занято ли имя пользователя
        if session.query(User).filter(User.username == form.username.data).first():
            return render_template(
                'registration.html',
                title='Регистрация',
                form=form,
                error='Имя пользователя уже занято'
            )
        # Создание пользователя
        user = User(
            username=form.username.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user)
        return redirect('/')
    return render_template(
        'registration.html',
        title='Регистрация',
        form=form,
    )


# Путь для входа
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Получение пользователя
        user = session.query(User).filter(User.username == form.username.data).first()
        # Проверка имени пользователя и пароля
        if not user or not user.check_password(form.password.data):
            return render_template(
                'login.html',
                title='Вход',
                form=form,
                error='Неверное имя пользователя или пароль'
            )
        # Создание сессии
        login_user(user)
        return redirect('/')
    return render_template(
        'login.html',
        title='Вход',
        form=form,
    )


# Путь для профиля пользователя
@blueprint.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль')


# Путь для выхода пользователя
@blueprint.route('/logout')
@login_required
def logout():
    # Удаление сессии
    logout_user()
    return redirect('/')
