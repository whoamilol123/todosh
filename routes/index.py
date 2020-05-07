from flask import Blueprint, render_template
from flask_login import current_user

from data.db_session import create_session
from data.tag import Tag
from data.task import Task
from data.user import User

# Создание Blueprint
blueprint = Blueprint('index', __name__)
# Создание БД
session = create_session()


# Путь для главной страницы
@blueprint.route('/')
def index():
    # Проверка авторизации
    if current_user.is_authenticated:
        # Получение ближайших задач
        upcoming = session.query(Task) \
            .filter(
                Task.deadline.isnot(None),
                Task.finished == 0,
                Task.owner_id == current_user.id
            ).order_by(Task.deadline, -Task.priority) \
            .limit(5) \
            .all()

        return render_template(
            'overview.html',
            title='Обзор',
            upcoming=upcoming
        )
    else:
        # Рендер красивой страницы с фичами и все такое
        return render_template(
            'index.html',
            tasks=session.query(Task).count(),
            tags=session.query(Tag).count(),
            users=session.query(User).count(),
        )
