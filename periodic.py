import threading

import schedule
import requests

from config import TELEGRAM_PROXY, TELEGRAM_BOT_TOKEN
from data.db_session import create_session, global_init
from data.task import Task
from data.user import User

proxy = None if TELEGRAM_PROXY is None else {
    'http': TELEGRAM_PROXY,
    'https': TELEGRAM_PROXY,
}


# Отправка уведомлений в Telegram
def send_telegram_notifications():
    # Сессия БД
    session = create_session()
    # Получение пользователей, включивших уведомления
    users = session.query(User).filter(User.telegram_id.isnot(None)).all()
    for u in users:
        # Получение ближайших задач для каждого пользователя
        upcoming = session.query(Task) \
            .filter(Task.deadline.isnot(None), Task.finished == 0, Task.owner_id == u.id) \
            .order_by(Task.deadline, -Task.priority) \
            .limit(5) \
            .all()
        if not upcoming:
            continue

        # Создание текста сообщения
        text = 'Доброе утро! Несколько задач на ближайшее время:\n\n'
        for task in upcoming:
            text += f'<b>{task.title.replace("<", "&lt;").replace(">", "&gt;")}</b>\n' \
                    f'Приоритет: <b>{task.priority_text}</b>\n' \
                    f'Дедлайн: <code>{task.deadline.strftime("%m-%d-%Y")}</code> ' \
                    f'({f"через {task.deadline_in.days} дней" if task.deadline_in.days >= 0 else f"{-task.deadline_in.days} дней назад"})\n' \
                    f'{(task.content.replace("<", "&lt;").replace(">", "&gt;")[:50] + "...") if len(task.content) > 50 else (task.content.replace("<", "&lt;").replace(">", "&gt;") or "<i>нет описания</i>")}\n\n'
        text += '<i>Спасибо, что используете Todo.sh!</i>'

        # Отправка сообщения
        requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage', proxies=proxy, json=dict(
            chat_id=u.telegram_id,
            text=text,
            parse_mode='html'
        ))


# Создание расписания для отправки уведдомлений каждый день в 7:00
schedule.every().day.at('07:00').do(send_telegram_notifications)


# Функция, которая будет работать в отдельном потоке
def _scheduler():
    while True:
        schedule.run_pending()


# Запуск потока с планировщиком
def start_scheduler_thread():
    threading.Thread(target=_scheduler).start()


if __name__ == '__main__':
    # Отправка уведомлений без расписания (для отладки)
    global_init('db/todosh.db')
    send_telegram_notifications()
