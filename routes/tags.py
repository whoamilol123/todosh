import re

from flask import Blueprint, render_template, redirect, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from data.db_session import create_session
from data.tag import Tag, tags_association
from utils.color import is_dark

# Создание Blueprint
blueprint = Blueprint('tags', __name__)
# Сессия БД
session = create_session()


# Форма создания/изменения тега
class TagForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    color = StringField(
        'Цвет',
        validators=[
            DataRequired(),
            # Проверка правильности ввода цвета (#rrggbb)
            lambda form, field: field.data and re.fullmatch(r'^#[0-f]{6}$', field.data)
        ],
        default='#ffa5a5'
    )
    submit = SubmitField('Сохранить')


# Путь создания тега
@blueprint.route('/tags/new', methods=['GET', 'POST'])
@login_required
def new_tag():
    form = TagForm()
    if form.validate_on_submit():
        # Создание тега
        tag = Tag(
            name=form.name.data,
            color=form.color.data,
            owner_id=current_user.id
        )
        session.add(tag)
        session.commit()
        back = request.args.get('back')
        return redirect(back if back else '/')
    return render_template('tag.html', form=form, title='Новый тег')


# Путь списка тегов
@blueprint.route('/tags')
@login_required
def my_tags():
    # Получение списка тегов
    tags = session.query(Tag).filter(Tag.owner_id == current_user.id).all()
    return render_template(
        'tags-list.html',
        tags=tags,
        title='Мои теги',
        is_dark=is_dark
    )


# Путь изменения тега
@blueprint.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    form = TagForm()
    # Получение тега
    tag = session.query(Tag).get(tag_id)
    if not tag or tag.owner_id != current_user.id:
        # Тег не найден
        abort(404)
    if request.method == 'GET':
        # Заполнение полей формы
        form.name.data = tag.name
        form.color.data = tag.color
    elif form.validate_on_submit():
        # Обновление тега полями из формы
        tag.name = form.name.data
        tag.color = form.color.data
        session.commit()
        return redirect('/tags')
    return render_template('tag.html', form=form, title='Изменить тег')


# Путь удаления тега
@blueprint.route('/tags/<int:tag_id>/delete')
@login_required
def delete_tag(tag_id):
    # Получение тега
    tag = session.query(Tag).get(tag_id)
    if not tag or tag.owner_id != current_user.id:
        # Тег не найден
        abort(404)

    # Удаление тега и связей с ним
    session.execute(tags_association.delete().where(tags_association.columns.tag == tag_id))
    session.delete(tag)
    session.commit()
    return redirect('/tags')
