# Импортируем SQLAlchemy для работы с базой данных
from flask_sqlalchemy import SQLAlchemy
# Импортируем UserMixin — добавляет поддержку авторизации для модели
from flask_login import UserMixin

# Создаём объект базы данных
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    Класс User — это таблица в базе данных.
    Содержит информацию о зарегистрированных пользователях.
    """
    id = db.Column(db.Integer, primary_key=True)  # уникальный ID
    name = db.Column(db.String(100), nullable=False)  # имя
    email = db.Column(db.String(100), unique=True, nullable=False)  # email
    password = db.Column(db.String(200), nullable=False)  # хэш пароля

    def __repr__(self):
        """
        Возвращает понятное строковое представление пользователя,
        полезно при отладке (например, в консоли Python).
        """
        return f'<User {self.email}>'
