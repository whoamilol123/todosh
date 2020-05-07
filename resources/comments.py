from flask import jsonify, request
from flask_login import current_user
from flask_restful import Resource, abort, reqparse

from data.comment import Comment
from data.db_session import create_session

from data.task import Task

# Сессия БД
session = create_session()

# Парсер POST запросов
comment_parser = reqparse.RequestParser()
comment_parser.add_argument('content', required=True, type=str)
comment_parser.add_argument('task_id', required=True, type=int)


class CommentsResource(Resource):
    def get(self, comment_id):
        """
        Запрос одного комментария
        """

        # Получение комментария
        comment = session.query(Comment).get(comment_id)
        if not comment:
            # Комментарий не найден
            return abort(404, error=f'Comment {comment_id} not found')
        # Возврат комментария
        return jsonify(comment.to_dict(
            only=('id', 'sender.username', 'sender.id', 'content', 'time')
        ))


class CommentsListResource(Resource):
    def get(self):
        """
        Запрос списка комментариев к задаче
        """

        # Проверка авторизации пользователя
        if not current_user.is_authenticated:
            return abort(403, error='You must be logged in')
        # ID задачи, к которым надо получить комментарии
        task_id = request.args.get('task_id')
        if not task_id:
            # ID задачи не передан
            return abort(400, error='task_id not present')
        # Получение задачи
        task = session.query(Task).get(task_id)
        if not task or task.owner_id != current_user.id:
            # Задача не найдена или нет прав доступа
            return abort(404, error=f'Task {task_id} not found')
        # Запрос комментариев из БД
        comments = session \
            .query(Comment) \
            .filter(Comment.task_id == task_id) \
            .order_by(-Comment.time) \
            .all()
        # Возврат комментариев
        return jsonify({
            'comments': [
                i.to_dict(only=('id', 'sender.username', 'sender.id', 'content', 'time'))
                for i in comments
            ]
        })

    def post(self):
        """
        Добавление комментария к задаче
        """

        # Проверка авторизации пользователя
        if not current_user.is_authenticated:
            return abort(403, error='You must be logged in')
        args = comment_parser.parse_args()
        # Получение задачи
        task = session.query(Task).get(args["task_id"])
        if not task or task.owner_id != current_user.id:
            # Задача не найдена или нет прав доступа
            return abort(404, error=f'Task {args["task_id"]} not found')
        comment = Comment(**args, sender_id=current_user.id)
        session.add(comment)
        session.commit()
        return jsonify(comment.to_dict(
            only=('id', 'sender.username', 'sender.id', 'content', 'time')
        ))
