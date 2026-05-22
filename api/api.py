from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import time
import os

app = Flask(__name__)
CORS(app) # Permite peticiones desde el frontend

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "testdb")
DB_RETRIES = int(os.getenv("DB_RETRIES", "5"))
DB_RETRY_DELAY = int(os.getenv("DB_RETRY_DELAY", "3"))
API_PORT = int(os.getenv("API_PORT", "3000"))

def get_connection():
    retries = DB_RETRIES
    while retries > 0:
        try:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
        except Exception as e:
            retries -= 1
            print(f"Esperando a la base de datos... Reintentos restantes: {retries}")
            time.sleep(DB_RETRY_DELAY)
    raise Exception("No se pudo conectar a la base de datos")

# Inicializar la base de datos al arrancar
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Tabla 'users' verificada/creada exitosamente.")
except Exception as e:
    print("Error inicializando DB:", e)

@app.route("/")
def home():
    return "API corriendo"

@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users;")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{"id": row[0], "name": row[1]} for row in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        name = data.get("name")
        if not name:
            return jsonify({"error": "El nombre es requerido"}), 400

        conn = get_connection()
        cur = conn.cursor()
        # Insertar evitando duplicados exactos (opcional según el diseño)
        cur.execute("INSERT INTO users (name) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id;", (name,))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if result:
            return jsonify({"message": "Usuario creado", "id": result[0], "name": name}), 201
        else:
            return jsonify({"message": "El usuario ya existe o no se pudo crear"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"Iniciando servidor API en el puerto {API_PORT}...")
    app.run(host="0.0.0.0", port=API_PORT)