from flask import jsonify
from flask_login import current_user
from flask_restful import Resource, abort, reqparse

from data.db_session import create_session
from data.user import User

# Сессия БД
session = create_session()

# Парсер для POST запросов
user_parser = reqparse.RequestParser()
user_parser.add_argument('password', type=str)
user_parser.add_argument('telegram_id', type=str)


class UserResource(Resource):
    def get(self, user_id):
        """
        Запрос одного пользователя
        """

        # Получение пользователя
        user = session.query(User).get(user_id)
        if not user:
            # Пользователь не найден
            abort(404, error=f'User {user_id} not found')
        # Возврат пользователя
        return jsonify(user.to_dict(only=('id', 'username')))

    def post(self, user_id):
        """
        Изменение пользователя
        """

        # Проверка авторизации и прав доступа
        if not current_user.is_authenticated or current_user.id != user_id:
            abort(403, error='Access denied')
        # Получение пользователя
        user = session.query(User).get(user_id)
        if not user:
            # Маловероятный случай, но (наверное?) возможный
            return abort(404, error='Invalid session')
        # Парсинг параметров
        args = user_parser.parse_args()

        # Смена пароля
        if args['password'] is not None:
            user.set_password(args['password'])
            session.commit()
            return jsonify({
                'ok': True
            })

        # Смена ID в Telegram
        if args['telegram_id'] is not None:
            telegram_id = args['telegram_id']
            try:
                # Преобразование пустой строки в None, строки с числами в int
                telegram_id = None if telegram_id == '' else int(telegram_id)
            except ValueError:
                # Неверное число
                return abort(400, error='Bad telegram_id')
            user.telegram_id = telegram_id
            session.commit()
            return jsonify({
                'ok': True
            })

        # Никакое поле не было передано.
        return abort(400, error='Bad request')
