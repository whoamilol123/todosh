import time
from sqlalchemy import orm
import sqlalchemy as s
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    """
    Модель комментария к задаче.
    """
    __tablename__ = 'comments'

    # ID комментария
    id = s.Column(s.Integer, primary_key=True, autoincrement=True)
    # ID отправителя комментария
    sender_id = s.Column(s.Integer, s.ForeignKey('users.id'))
    # ID задачи, к которой этот комментарий был отправлен
    task_id = s.Column(s.Integer, s.ForeignKey('tasks.id'))
    # Текст комментария
    content = s.Column(s.String)
    # Unix время написания комментария
    time = s.Column(s.Integer, default=time.time)

    # Объект отправителя комментария
    sender = orm.relation('User')
    # Объект задачи, к которой комметарий был отправлен
    task = orm.relation('Task')
