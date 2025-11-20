import json
import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# --- Инициализация лимитера ---
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per day"]       # общее ограничение для всех маршрутов
)

DATA_FILE = "data.json"

# --- Загрузка данных при старте ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}

# --- Функция сохранения ---
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ------------------------- ROUTES ---------------------------- #

# POST /set
@app.route("/set", methods=["POST"])
@limiter.limit("10 per minute")   # отдельный лимит
def set_value():
    req = request.get_json()

    if not req or "key" not in req or "value" not in req:
        return jsonify({"error": "Нужно передать JSON с полями 'key' и 'value'"}), 400

    key = req["key"]
    value = req["value"]

    data[key] = value
    save_data()

    return jsonify({"status": "ok", "message": f"Ключ '{key}' сохранён"})


# GET /get/<key>
@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    if key in data:
        return jsonify({"key": key, "value": data[key]})
    return jsonify({"error": "Ключ не найден"}), 404


# DELETE /delete/<key>
@app.route("/delete/<key>", methods=["DELETE"])
@limiter.limit("10 per minute")   # отдельный лимит
def delete_value(key):
    if key in data:
        del data[key]
        save_data()
        return jsonify({"status": "ok", "message": f"Ключ '{key}' удалён"})
    return jsonify({"error": "Ключ не найден"}), 404


# GET /exists/<key>
@app.route("/exists/<key>", methods=["GET"])
def exists(key):
    return jsonify({"exists": key in data})


# ------------------------- RUN ---------------------------- #

if __name__ == "__main__":
    app.run(debug=True)
