from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import re

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="root",
            password="password",
            database="todo_db",
            charset='utf8mb4',
            buffered=True
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def sanitize_input(text):
    if not text or len(text.strip()) == 0:
        return None
    text = text.strip()[:255]
    text = re.sub(r'[<>]', '', text)
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['POST'])
def create_task():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        data = request.json
        task = sanitize_input(data.get('task'))
        if not task:
            return jsonify({"error": "Task is required and must be valid"}), 400
        cursor.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
        conn.commit()
        task_id = cursor.lastrowid
        return jsonify({"message": "Task created", "id": task_id, "task": task}), 201
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/tasks', methods=['GET'])
def read_tasks():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, task FROM tasks ORDER BY id")
        tasks = cursor.fetchall()
        return jsonify(tasks), 200
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/tasks/<int:id>', methods=['GET'])
def read_task(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, task FROM tasks WHERE id = %s", (id,))
        task = cursor.fetchone()
        if task:
            return jsonify(task), 200
        return jsonify({"error": "Task not found"}), 404
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        data = request.json
        task = sanitize_input(data.get('task'))
        if not task:
            return jsonify({"error": "Task is required and must be valid"}), 400
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Task not found"}), 404
        cursor.execute("UPDATE tasks SET task = %s WHERE id = %s", (task, id))
        conn.commit()
        return jsonify({"message": "Task updated", "id": id, "task": task}), 200
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Task not found"}), 404
        cursor.execute("DELETE FROM tasks WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"message": "Task deleted", "id": id}), 200
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)