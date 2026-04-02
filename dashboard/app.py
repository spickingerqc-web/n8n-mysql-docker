from flask import Flask, render_template, jsonify
import sqlite3
import random
import time
import threading
from datetime import datetime

app = Flask(__name__)
DB_PATH = "/data/sensor.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_sensor_data():
    while True:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO sensor_data (sensor_name, value, unit) VALUES (?, ?, ?)",
                  ("temperature", round(random.uniform(20.0, 35.0), 1), "celsius"))
        c.execute("INSERT INTO sensor_data (sensor_name, value, unit) VALUES (?, ?, ?)",
                  ("humidity", round(random.uniform(40.0, 80.0), 1), "percent"))
        c.execute("INSERT INTO sensor_data (sensor_name, value, unit) VALUES (?, ?, ?)",
                  ("pressure", round(random.uniform(1000.0, 1025.0), 1), "hPa"))
        conn.commit()
        conn.close()
        time.sleep(5)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    result = {}
    for sensor in ["temperature", "humidity", "pressure"]:
        c.execute("""
            SELECT value, recorded_at FROM sensor_data
            WHERE sensor_name = ?
            ORDER BY recorded_at DESC LIMIT 20
        """, (sensor,))
        rows = c.fetchall()
        rows.reverse()
        result[sensor] = {
            "values": [r[0] for r in rows],
            "times": [r[1][-8:] for r in rows]
        }
    conn.close()
    return jsonify(result)

@app.route("/api/latest")
def get_latest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    result = {}
    for sensor in ["temperature", "humidity", "pressure"]:
        c.execute("""
            SELECT value, unit FROM sensor_data
            WHERE sensor_name = ?
            ORDER BY recorded_at DESC LIMIT 1
        """, (sensor,))
        row = c.fetchone()
        if row:
            result[sensor] = {"value": row[0], "unit": row[1]}
    conn.close()
    return jsonify(result)

if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=insert_sensor_data, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
