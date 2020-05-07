from datetime import datetime

import sqlalchemy as s
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    """
    Объект пользователя
    """
    __tablename__ = 'users'

    # ID пользователя
    id = s.Column(s.Integer, primary_key=True, autoincrement=True)
    # Имя пользователя
    username = s.Column(s.String, index=True, unique=True)
    # Хешированный пароль пользователя
    password = s.Column(s.String)
    # ID пользователя в Telegram (для уведомлений) (может быть None)
    telegram_id = s.Column(s.Integer, nullable=True, default=None)
    # Дата регистрации пользователя
    registration_date = s.Column(s.DateTime, default=datetime.now)

    def set_password(self, password):
        """
        Вспомогательный метод для установки пароля пользователя

        :param password: Plain-text пароль пользователя
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Вспомогательный метод для проверки пароля пользователя

        :param password: Plain-text ввод пароля
        :return: bool
        """
        return check_password_hash(self.password, password)

