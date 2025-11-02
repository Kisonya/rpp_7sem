# Импорт основных компонентов Flask:
# Flask — сам фреймворк
# render_template — для подключения HTML-шаблонов
# redirect и url_for — для переходов между страницами
# request — для получения данных из форм
# flash — для отображения сообщений (например, об ошибках)
from flask import Flask, render_template, redirect, url_for, request, flash

# Импорт библиотеки для работы с базой данных (ORM)
from flask_sqlalchemy import SQLAlchemy

# Импорт компонентов Flask-Login — отвечает за авторизацию и хранение данных пользователя в сессии
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)

# Импорт функций для шифрования и проверки паролей
from werkzeug.security import generate_password_hash, check_password_hash


# -----------------------------
# 1. ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# -----------------------------
app = Flask(__name__)  # создаём экземпляр Flask-приложения

# Настройки приложения
app.config['SECRET_KEY'] = 'secret-key-example'  # ключ для защиты сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # путь к БД
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # отключаем лишние уведомления

# Инициализация базы данных
db = SQLAlchemy(app)

# -----------------------------
# 2. НАСТРОЙКА Flask-Login
# -----------------------------
login_manager = LoginManager()  # создаём менеджер авторизации
login_manager.init_app(app)  # связываем его с нашим приложением
login_manager.login_view = 'login'  # если пользователь не вошёл — перенаправлять на /login


# -----------------------------
# 3. МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ
# -----------------------------
class User(UserMixin, db.Model):
    """
    Класс User описывает таблицу пользователей в базе данных.
    Наследуется от UserMixin (Flask-Login) и db.Model (SQLAlchemy).
    """
    id = db.Column(db.Integer, primary_key=True)  # уникальный ID пользователя
    name = db.Column(db.String(100), nullable=False)  # имя пользователя
    email = db.Column(db.String(100), unique=True, nullable=False)  # email (уникальный)
    password = db.Column(db.String(200), nullable=False)  # хэш пароля (не хранится в открытом виде)

    def __repr__(self):
        """Метод для удобного отображения пользователя в консоли"""
        return f'<User {self.email}>'


# -----------------------------
# 4. ФУНКЦИЯ ЗАГРУЗКИ ПОЛЬЗОВАТЕЛЯ
# -----------------------------
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login вызывает эту функцию для загрузки пользователя из БД
    по сохранённому в сессии идентификатору.
    """
    return db.session.get(User, int(user_id))


# -----------------------------
# 5. КОРНЕВАЯ СТРАНИЦА "/"
# -----------------------------
@app.route('/')
def index():
    """
    Главная страница.
    Если пользователь авторизован — показываем приветствие и кнопку "Выйти".
    Если нет — перенаправляем его на страницу входа.
    """
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return redirect(url_for('login'))


# -----------------------------
# 6. СТРАНИЦА ВХОДА (GET)
# -----------------------------
@app.route('/login', methods=['GET'])
def login():
    """
    Просто отображаем HTML-форму для входа (login.html).
    """
    return render_template('login.html')


# -----------------------------
# 7. АВТОРИЗАЦИЯ (POST)
# -----------------------------
@app.route('/login', methods=['POST'])
def login_post():
    """
    Обрабатывает данные, введённые пользователем в форме входа.
    Проверяет:
     - существует ли пользователь с таким email,
     - совпадает ли пароль.
    При успешном входе — перенаправляет на главную страницу.
    """
    email = request.form.get('email')      # получаем email из формы
    password = request.form.get('password')  # получаем пароль

    # ищем пользователя по email
    user = User.query.filter_by(email=email).first()

    # если пользователь не найден — выводим сообщение и возвращаем форму входа
    if not user:
        flash('Пользователь не найден.')
        return redirect(url_for('login'))

    # если пароль неверный — также сообщение и возврат
    if not check_password_hash(user.password, password):
        flash('Неверный пароль.')
        return redirect(url_for('login'))

    # если всё корректно — авторизуем пользователя
    login_user(user)
    return redirect(url_for('index'))


# -----------------------------
# 8. СТРАНИЦА РЕГИСТРАЦИИ (GET)
# -----------------------------
@app.route('/signup', methods=['GET'])
def signup():
    """
    Показываем форму регистрации (signup.html).
    """
    return render_template('signup.html')


# -----------------------------
# 9. РЕГИСТРАЦИЯ (POST)
# -----------------------------
@app.route('/signup', methods=['POST'])
def signup_post():
    """
    Обработка данных формы регистрации.
    Проверяет, есть ли уже пользователь с таким email.
    Если нет — добавляет нового в базу.
    """
    name = request.form.get('name')        # имя
    email = request.form.get('email')      # email
    password = request.form.get('password')  # пароль

    # Проверяем, есть ли пользователь с таким email
    user = User.query.filter_by(email=email).first()

    if user:
        flash('Пользователь с таким email уже существует.')
        return redirect(url_for('signup'))

    # Создаём нового пользователя. Пароль шифруем, чтобы не хранить открыто.
    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256')
    )

    # Добавляем в базу и сохраняем изменения
    db.session.add(new_user)
    db.session.commit()

    # Сообщение пользователю
    flash('Регистрация прошла успешно! Теперь войдите в систему.')
    return redirect(url_for('login'))


# -----------------------------
# 10. ВЫХОД ИЗ АККАУНТА
# -----------------------------
@app.route('/logout')
@login_required  # доступ только для авторизованных пользователей
def logout():
    """
    Завершает сессию текущего пользователя и возвращает на страницу входа.
    """
    logout_user()
    return redirect(url_for('login'))


# -----------------------------
# 11. ТОЧКА ВХОДА (СТАРТ ПРОГРАММЫ)
# -----------------------------
if __name__ == '__main__':
    # Создаём таблицы в базе данных, если они ещё не существуют
    with app.app_context():
        db.create_all()

    # Запускаем сервер Flask в режиме отладки
    app.run(debug=True)
