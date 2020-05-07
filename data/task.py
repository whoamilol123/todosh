from datetime import datetime

from sqlalchemy import orm
import sqlalchemy as s
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    """
    Модель задачи
    """
    __tablename__ = 'tasks'

    # ID задачи
    id = s.Column(s.Integer, primary_key=True, autoincrement=True)
    # ID владельца задачи
    owner_id = s.Column(s.Integer, s.ForeignKey('users.id'))
    # Название задачи
    title = s.Column(s.String)
    # Текст задачи
    content = s.Column(s.String, default='')
    # Приоритет задачи (см. priority_text)
    priority = s.Column(s.Integer, default=0)
    # Завершена ли задача
    finished = s.Column(s.Boolean, default=False)
    # Дедлайн задачи (может быть None)
    deadline = s.Column(s.DateTime, nullable=True)
    # Место проведения задачи в формате:
    # название|lat,lon|spn_lat,spn_lon
    # (может быть None)
    place = s.Column(s.String, nullable=True, default=None)

    # Объект владельца задачи
    owner = orm.relation('User')
    # Теги, присвоенные этой задаче
    tags = orm.relation('Tag', secondary='task_to_tag', backref='task')

    @property
    def deadline_in(self):
        """
        Вспомогательный метод, возвращающий разницу между
        текущей датой и датой дедлайна (если он есть)

        :return: timedelta или None
        """
        return (self.deadline - datetime.now()) if self.deadline else None

    @property
    def priority_text(self):
        """
        Вспомогательный метод, возвращающий приоритет задачи
        в читаемом (текстовом) виде

        :return: str
        """
        v = self.priority
        if v == 6:
            return 'ОЧЕНЬ ВЫСОКИЙ'
        if v == 5:
            return 'Высокий'
        if v == 4:
            return 'Повышенный'
        if v == 3:
            return 'Обычный'
        if v == 2:
            return 'Низкий'
        if v == 1:
            return 'Очень низкий'
        return f'Важность {v}'

