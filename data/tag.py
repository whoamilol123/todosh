from sqlalchemy import orm
import sqlalchemy as s
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

# Вспомогательная таблица для связи тегов и задач
tags_association = s.Table(
    'task_to_tag',
    SqlAlchemyBase.metadata,
    s.Column('task', s.Integer, s.ForeignKey('tasks.id'), primary_key=True),
    s.Column('tag', s.Integer, s.ForeignKey('tags.id'), primary_key=True)
)


class Tag(SqlAlchemyBase, SerializerMixin):
    """
    Модель тега задачи. Имеет связь may-to-many с задачами.
    """
    __tablename__ = 'tags'

    # ID тега
    id = s.Column(s.Integer, primary_key=True, autoincrement=True)
    # ID владельца тега
    owner_id = s.Column(s.Integer, s.ForeignKey('users.id'))
    # Название тега
    name = s.Column(s.String)
    # Цвет тега (#rrggbb)
    color = s.Column(s.String, default='#d4d4d4')

    # Объект владельца тега
    owner = orm.relation('User')
    # Список задач, у которых есть этот тег
    tasks = orm.relation('Task', secondary='task_to_tag', backref='tag')


