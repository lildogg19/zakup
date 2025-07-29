from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

DB_FILE = "zakupki.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

COLUMNS = [
    "Заказчик", "Назначение", "Страна", "Контакты", "Наименование",
    "Кол-во", "Дата оплат", "Комментарий", "Получен",
    "Итоговая стоимость", "Сумма доставки",
    "Растаможка", "Комиссия", "Документ(ы)"
]

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# ---- ВСТАВЬ ИНИЦИАЛИЗАЦИЮ ТАБЛИЦЫ СЮДА ----
def init_db():
    conn = get_db()
    cols = ", ".join([f'"{c}" TEXT' for c in COLUMNS])
    conn.execute(f"CREATE TABLE IF NOT EXISTS zakupki (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols})")
    conn.commit()
    conn.close()

init_db()  # <---- вызывется ОДИН раз при старте приложения

@app.route("/api/zakupki", methods=["GET"])
def get_zakupki():
    conn = get_db()
    rows = conn.execute("SELECT rowid, * FROM zakupki").fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return jsonify(result)

@app.route("/api/zakupki", methods=["POST"])
def add_zakupka():
    data = request.json
    conn = get_db()
    cols = ", ".join([f'"{c}"' for c in COLUMNS])
    placeholders = ",".join("?" for _ in COLUMNS)
    vals = [data.get(c, "") for c in COLUMNS]
    conn.execute(f'INSERT INTO zakupki ({cols}) VALUES ({placeholders})', vals)
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/api/zakupki/<int:rowid>", methods=["PUT"])
def update_zakupka(rowid):
    data = request.json
    setstr = ", ".join([f'"{c}"=?' for c in COLUMNS])
    vals = [data.get(c, "") for c in COLUMNS]
    conn = get_db()
    conn.execute(f'UPDATE zakupki SET {setstr} WHERE rowid=?', vals + [rowid])
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/api/zakupki/<int:rowid>", methods=["DELETE"])
def delete_zakupka(rowid):
    conn = get_db()
    conn.execute("DELETE FROM zakupki WHERE rowid=?", (rowid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    f = request.files["file"]
    save_path = os.path.join(UPLOAD_DIR, f.filename)
    f.save(save_path)
    return jsonify({"filename": f.filename})

@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
