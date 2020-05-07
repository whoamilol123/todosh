from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_restful import Api

from config import PORT
from data.db_session import global_init, create_session
from data.user import User
from periodic import start_scheduler_thread

# Инициализация БД
global_init('db/todosh.db')
session = create_session()
# Инициализация Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'PADORU PADORU'
# Инициализация Flask-restful
api = Api(app)
# Инициализация Flask-login
login_manager = LoginManager()
login_manager.init_app(app)


# Метод загрузки пользователя сессии
@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


# Загрузка статичных ресурсов из папки static/
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    # Импорт Blueprint'ов
    from routes.index import blueprint as index_blueprint
    from routes.auth import blueprint as auth_blueprint
    from routes.tasks import blueprint as tasks_blueprint
    from routes.tags import blueprint as tags_blueprint

    # Импорт ресурсов
    from resources.users import UserResource
    from resources.comments import CommentsListResource, CommentsResource

    # Важно что импорты производятся после global_init() т.к.
    # они используют create_session()

    # Запуск планировщика в отдельном потоке
    start_scheduler_thread()

    # Регистрация Blueprint'ов
    app.register_blueprint(index_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(tasks_blueprint)
    app.register_blueprint(tags_blueprint)
    # Регистрация REST ресурсов
    api.add_resource(UserResource, '/api/users/<int:user_id>')
    api.add_resource(CommentsResource, '/api/comments/<int:user_id>')
    api.add_resource(CommentsListResource, '/api/comments')

    # Запуск веб сервера
    app.run(debug=True, port=PORT)
