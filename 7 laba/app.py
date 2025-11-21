# Подключаем стандартную библиотеку json — она нужна для чтения и записи данных в формате JSON.
import json

# Подключаем библиотеку os — она позволяет работать с файлами и проверять, существуют ли они.
import os

# Импортируем классы Flask, request, jsonify:
# Flask — основной класс для создания веб-приложения.
# request — позволяет получать данные, которые отправил клиент (POST, JSON и т.п.)
# jsonify — превращает Python-объекты в правильный JSON-ответ для клиента.
from flask import Flask, request, jsonify

# Импортируем Limiter — модуль, который ограничивает количество запросов (rate limiting).
from flask_limiter import Limiter

# Функция get_remote_address — определяет IP-адрес пользователя, чтобы лимитер мог считать запросы по IP.
from flask_limiter.util import get_remote_address

# Создаём объект приложения Flask.
# __name__ — имя текущего файла, Flask использует его для правильной работы.
app = Flask(__name__)


# === Инициализация лимитера (ограничителя запросов) ===
# Создаём объект Limiter и передаём:
# key_func — функция, по которой определяется "ключ" лимита (например IP-адрес клиента).
# app — приложение, к которому подключается ограничитель.
# default_limits — общее ограничение для всех маршрутов (например, 100 запросов в сутки).
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per day"]  # ограничение по умолчанию
)


# Имя файла, в котором будут храниться данные словаря.
DATA_FILE = "data.json"


# === Загрузка данных из файла при старте приложения ===
# Проверяем, существует ли файл data.json.
if os.path.exists(DATA_FILE):
    # Если да — открываем файл на чтение ("r") с кодировкой UTF-8.
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        # Загружаем JSON-данные из файла в словарь data.
        data = json.load(f)
else:
    # Если файла нет — создаём пустой словарь.
    data = {}


# === Функция сохранения данных в файл ===
def save_data():
    # Открываем файл на запись ("w") с перезаписью содержимого.
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # json.dump — записывает Python-объект в JSON-файл.
        # indent=4 — форматирует JSON красиво и с отступами.
        # ensure_ascii=False — сохраняет русские буквы нормально, не \uXXXX.
        json.dump(data, f, indent=4, ensure_ascii=False)


# ======================= ROUTES (маршруты API) ======================= #

# === Маршрут POST /set — сохраняет ключ и значение ===
@app.route("/set", methods=["POST"])
@limiter.limit("10 per minute")  # отдельное ограничение: не более 10 запросов в минуту
def set_value():
    # Получаем JSON, который прислал клиент.
    # request.get_json() превращает JSON-тело запроса в Python-словарь.
    req = request.get_json()

    # Проверяем, что пользователь отправил JSON и что там есть ключи "key" и "value".
    if not req or "key" not in req or "value" not in req:
        # Возвращаем ошибку 400 (неправильный запрос).
        return jsonify({"error": "Nuzhno peredat JSON s polyami 'key' i 'value'"}), 400

    # Извлекаем ключ и значение из JSON.
    key = req["key"]
    value = req["value"]

    # Сохраняем значение в словарь data.
    data[key] = value

    # Сохраняем обновлённый словарь в файл.
    save_data()

    # Возвращаем успешный ответ.
    return jsonify({"status": "ok", "message": f"Kluch '{key}' sohranen"})


# === Маршрут GET /get/<key> — возвращает значение по ключу ===
@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    # Если ключ есть в словаре — возвращаем его значение.
    if key in data:
        return jsonify({"key": key, "value": data[key]})
    # Если ключа нет — возвращаем ошибку.
    return jsonify({"error": "Kluch ne nayden"}), 404


# === Маршрут DELETE /delete/<key> — удаляет ключ из хранилища ===
@app.route("/delete/<key>", methods=["DELETE"])
@limiter.limit("10 per minute")  # отдельный лимит на удаление
def delete_value(key):
    # Проверяем, есть ли такой ключ.
    if key in data:
        # Удаляем ключ.
        del data[key]
        # Сохраняем обновлённый словарь.
        save_data()
        # Возвращаем успешный ответ.
        return jsonify({"status": "ok", "message": f"Kluch '{key}' udalen"})
    # Если ключа нет — отправляем ошибку.
    return jsonify({"error": "Kluch ne nayden"}), 404


# === Маршрут GET /exists/<key> — проверяет существование ключа ===
@app.route("/exists/<key>", methods=["GET"])
def exists(key):
    # Возвращаем True или False в зависимости от того, есть ли ключ в словаре.
    return jsonify({"exists": key in data})


# ======================= Запуск приложения ======================= #

# Эта конструкция означает:
# Если файл запущен напрямую (а не импортирован как модуль),
# то запускаем веб-сервер Flask.
if __name__ == "__main__":
    # debug=True — включает автоматический перезапуск при изменениях и отображение ошибок.
    app.run(debug=True)
