from flask import Blueprint, render_template, redirect, abort, request
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired

from utils.color import is_dark
from utils.nullable_datefield import NullableDateField

from data.db_session import create_session
from data.tag import Tag
from data.task import Task
from utils.geocoder import get_ll_spn

# Создание Blueprint
blueprint = Blueprint('tasks', __name__)
# Сессия БД
session = create_session()


# Форма создания/изменения задачи
class TaskForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField('Описание')
    priority = SelectField('Приоритет', coerce=int, choices=[
        (6, 'ОЧЕНЬ ВЫСОКИЙ'),
        (5, 'Высокий'),
        (4, 'Повышенный'),
        (3, 'Обычный'),
        (2, 'Низкий'),
        (1, 'Очень низкий'),
    ], default=3)
    tags = SelectMultipleField('Теги', coerce=int)
    has_deadline = BooleanField('Есть дедлайн')
    deadline = NullableDateField(
        'Дедлайн',
        validators=[
            lambda form, field: field.data is not None if form.has_place.data else True
        ]
    )
    has_place = BooleanField('Есть место')
    place = StringField(
        'Место',
        validators=[
            lambda form, field: field.data is not None if form.has_place.data else True
        ]
    )
    submit = SubmitField('Сохранить')


# Путь списка задач
@blueprint.route('/tasks')
@login_required
def tasks_list():
    # Получение списка задач
    query = session.query(Task) \
        .order_by(Task.finished, Task.deadline, -Task.priority) \
        .filter(Task.owner_id == current_user.id)
    # Фильтрация по тегам
    tag_id = request.args.get('tag_id')
    if tag_id == '0':
        # Только задачи без тегов
        query = query.filter(~Task.tags.any())
    elif tag_id:
        # Только задачи, имеющие тег tag_id
        query = query.filter(Task.tags.any(id=tag_id))
    # Получение задач и всех тегов пользователя
    tasks = query.all()
    tags = session.query(Tag).filter(Tag.owner_id == current_user.id).all()
    return render_template(
        'tasks-list.html',
        title='Мои задачи',
        tasks=tasks,
        tags=tags,
        selected_tag=tag_id,
        is_dark=is_dark
    )


# Путь создания тега
@blueprint.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    # Доступные теги
    form.tags.choices = [(k.id, k.name) for k in session.query(Tag).filter(Tag.owner_id == current_user.id).all()]

    if form.validate_on_submit():
        # Создание задачи
        task = Task(
            title=form.title.data,
            content=form.content.data,
            priority=form.priority.data,
            deadline=form.deadline.data if form.has_deadline.data else None,
            place=get_ll_spn(form.place.data) if form.has_place.data else None,
            owner_id=current_user.id,
            tags=session.query(Tag).filter(Tag.id.in_(form.tags.data)).all()
        )
        session.add(task)
        session.commit()
        return redirect(f'/tasks/{task.id}')
    return render_template('task-form.html', form=form, title='Новая задача')


# Путь просмотра задачи
@blueprint.route('/tasks/<int:task_id>')
@login_required
def one_task(task_id):
    # Получение задачи
    task = session.query(Task).get(task_id)
    if not task or task.owner_id != current_user.id:
        # Задача не найдена
        return abort(404)
    return render_template(
        'task.html',
        task=task,
        title='Просмотр задачи',
        is_dark=is_dark
    )


# Путь отметки задачи как завершенной
@blueprint.route('/tasks/<int:task_id>/finish')
@login_required
def finish_task(task_id):
    # Получение задачи
    task = session.query(Task).get(task_id)
    if not task or task.owner_id != current_user.id:
        # Задача не найдена
        return abort(404)
    # Обновление задачи
    task.finished = True
    session.commit()
    return redirect(f'/tasks/{task_id}')


# Путь отметки задачи как незавершенной
@blueprint.route('/tasks/<int:task_id>/unfinish')
@login_required
def unfinish_task(task_id):
    # Получение задачи
    task = session.query(Task).get(task_id)
    if not task or task.owner_id != current_user.id:
        # Задача не найдена
        return abort(404)
    # Обновление задачи
    task.finished = False
    session.commit()
    return redirect(f'/tasks/{task_id}')


# Путь удаления задачи
@blueprint.route('/tasks/<int:task_id>/delete')
@login_required
def delete_task(task_id):
    # Получение задачи
    task = session.query(Task).get(task_id)
    if not task or task.owner_id != current_user.id:
        # Задача не найдена
        return abort(404)
    # Удаление задачи
    # Сначала надо удалить связанные теги, иначе будет ошибка
    task.tags = []
    session.commit()
    session.delete(task)
    session.commit()
    return redirect('/')


# Путь изменения задачи
@blueprint.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    # Получение задачи
    task = session.query(Task).get(task_id)
    if not task or task.owner_id != current_user.id:
        # Задача не найдена
        return abort(404)

    form = TaskForm()
    # Доступные теги
    form.tags.choices = [(k.id, k.name) for k in session.query(Tag).filter(Tag.owner_id == current_user.id).all()]

    if request.method == 'GET':
        # Заполнение полей формы задачей
        form.tags.data = [t.id for t in task.tags]
        form.content.data = task.content
        form.title.data = task.title
        form.has_deadline.data = task.deadline is not None
        form.deadline.data = task.deadline
        form.has_place.data = task.place is not None
        form.place.data = task.place.split('|')[0] if task.place is not None else None
        form.priority.data = task.priority
        return render_template('task-form.html', form=form, title='Изменить задачу')
    elif form.validate_on_submit():
        # Обновление задачи полями формы
        task.title = form.title.data
        task.content = form.content.data
        task.priority = form.priority.data
        task.deadline = form.deadline.data if form.has_deadline.data else None
        task.place = (get_ll_spn(form.place.data)) if form.has_place.data else None
        task.tags = session.query(Tag).filter(Tag.id.in_(form.tags.data)).all()
        session.commit()
        return redirect(f'/tasks/{task.id}')
