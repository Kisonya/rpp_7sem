# Flask — микрофреймворк для веб-приложений.
from flask import Flask, jsonify, request, render_template_string, redirect, url_for

# Requests — библиотека для отправки HTTP-запросов к инстансам.
import requests

# Threading — для фонового потока проверки состояния инстансов.
import threading

# Time — для паузы между проверками здоровья.
import time


# ==================== Создание приложения ====================

# Создаём объект приложения Flask.
app = Flask(__name__)

# Список всех инстансов (серверов).
# Каждый элемент — это словарь с адресом, портом и флагом активности.
instances = [
    {"ip": "127.0.0.1", "port": 5001, "active": True},
    {"ip": "127.0.0.1", "port": 5002, "active": True},
    {"ip": "127.0.0.1", "port": 5003, "active": True}
]

# Глобальный индекс для реализации стратегии Round Robin.
index = 0


# ==================== Проверка состояния (Health Check) ====================

def health_check():
    """
    Фоновая функция, которая каждые 5 секунд проверяет,
    доступны ли инстансы по маршруту /health.
    Если запрос проходит — активен, иначе помечается как недоступный.
    """
    while True:
        for instance in instances:
            # Формируем адрес проверки, например http://127.0.0.1:5001/health
            url = f"http://{instance['ip']}:{instance['port']}/health"

            try:
                # Пытаемся получить ответ за 1 секунду.
                requests.get(url, timeout=1)
                instance["active"] = True
            except requests.RequestException:
                # Если ответ не получен — сервер недоступен.
                instance["active"] = False

        # Пауза 5 секунд между циклами проверки.
        time.sleep(5)


# Запускаем поток, который будет постоянно проверять состояние инстансов.
# daemon=True означает, что поток завершится, когда закроется основная программа.
threading.Thread(target=health_check, daemon=True).start()


# ==================== Маршруты (Endpoints) ====================

@app.route('/health')
def get_health():
    """
    Возвращает список всех инстансов и их текущее состояние.
    """
    return jsonify(instances)


@app.route('/process')
def process():
    """
    Основной маршрут балансировщика.
    При получении запроса выбирает следующий активный инстанс
    по алгоритму Round Robin и перенаправляет запрос на него.
    """
    global index  # используем глобальный индекс

    # Выбираем только активные инстансы (которые отвечают на /health)
    active_instances = [i for i in instances if i["active"]]

    # Если нет ни одного активного сервера — возвращаем ошибку 503
    if not active_instances:
        return jsonify({"error": "Нет доступных инстансов"}), 503

    # Выбираем следующий инстанс по очереди
    instance = active_instances[index % len(active_instances)]
    index += 1  # увеличиваем индекс для следующего запроса

    # Формируем URL для выбранного инстанса, например: http://127.0.0.1:5001/process
    url = f"http://{instance['ip']}:{instance['port']}/process"

    try:
        # Перенаправляем запрос на выбранный сервер и возвращаем его ответ
        response = requests.get(url)
        return jsonify(response.json())
    except requests.RequestException:
        # Если сервер не ответил — помечаем его недоступным
        instance["active"] = False
        return jsonify({"error": "Инстанс недоступен"}), 503


@app.route('/add_instance', methods=['POST'])
def add_instance():
    """
    Добавление нового инстанса в пул.
    Поддерживает два варианта ввода данных:
    1) JSON-запрос (API)  2) HTML-форма из веб-интерфейса
    """
    # Проверяем тип входных данных
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # Извлекаем IP и порт
    ip = data.get("ip")
    port = int(data.get("port"))

    # Добавляем в список инстансов
    instances.append({
        "ip": ip,
        "port": port,
        "active": True
    })

    # Если запрос из API — возвращаем JSON-ответ
    if request.is_json:
        return jsonify({"message": "Инстанс добавлен"}), 201
    # Если из формы — перенаправляем обратно на главную страницу
    return redirect(url_for('index_page'))


@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    """
    Удаление инстанса из пула по индексу.
    Работает как через API, так и через веб-интерфейс.
    """
    # Определяем источник данных (JSON или HTML-форма)
    if request.is_json:
        data = request.get_json()
        idx = int(data.get("index", -1))
    else:
        idx = int(request.form.get("index", -1))

    # Проверяем, что индекс корректен
    if 0 <= idx < len(instances):
        removed = instances.pop(idx)

        if request.is_json:
            # Ответ для API
            return jsonify({
                "message": f"Инстанс {removed['ip']}:{removed['port']} удалён"
            })
        # Ответ для HTML-формы — возвращаемся на главную страницу
        return redirect(url_for('index_page'))

    # Если индекс неправильный
    if request.is_json:
        return jsonify({"error": "Неверный индекс"}), 400
    return redirect(url_for('index_page'))


# ==================== HTML-шаблон (Web UI) ====================

HTML_TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Балансировщик нагрузки</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    h1, h2 { color: #333; }
    ul { list-style-type: none; padding-left: 0; }
    li { margin: 6px 0; }
    form { display: inline; margin: 0; }
    input { margin-right: 5px; padding: 5px; }
    button, .link-btn {
      padding: 6px 12px;
      margin-right: 10px;
      cursor: pointer;
      border: none;
      border-radius: 4px;
      background-color: #007bff;
      color: white;
      text-decoration: none;
      font-size: 14px;
    }
    button:hover, .link-btn:hover {
      background-color: #0056b3;
    }
    .links {
      margin-top: 25px;
    }
  </style>
</head>
<body>
  <h1>Пул инстансов</h1>
  <ul>
    {% for inst in instances %}
      <li>
        {{ loop.index0 }} — {{ inst.ip }}:{{ inst.port }}
        — [{{ 'Доступен' if inst.active else 'Недоступен' }}]
        <form action="/remove_instance" method="post">
          <input type="hidden" name="index" value="{{ loop.index0 }}">
          <button type="submit">Удалить</button>
        </form>
      </li>
    {% endfor %}
  </ul>

  <h2>Добавить новый инстанс</h2>
  <form action="/add_instance" method="post">
    IP: <input name="ip" value="127.0.0.1" required>
    Порт: <input name="port" value="5004" required>
    <button type="submit">Добавить</button>
  </form>

  <div class="links">
    <a class="link-btn" href="/health" target="_blank">Проверить состояние</a>
    <a class="link-btn" href="/process" target="_blank">Отправить тестовый запрос</a>
  </div>
</body>
</html>
"""


@app.route('/')
def index_page():
    """
    Главная страница балансировщика (Web UI).
    Отображает список всех инстансов и предоставляет форму управления.
    """
    return render_template_string(HTML_TEMPLATE, instances=instances)


# ==================== Точка входа в программу ====================

if __name__ == '__main__':
    # Запускаем Flask-приложение на порту 8000.
    # В продакшене следовало бы использовать uWSGI или Gunicorn, но здесь — режим отладки.
    app.run(port=8000)
