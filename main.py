from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)

db_host = os.environ.get('MYSQLHOST')
db_port = os.environ.get('MYSQLPORT')
db_user = os.environ.get('MYSQLUSER')
db_password = os.environ.get('MYSQLPASSWORD')
db_name = os.environ.get('MYSQLDATABASE')

db_config = {
    "pool_name": "my_pool",
    "pool_size": 5,
    "host": db_host,
    "port": db_port,
    "user": db_user,
    "password": db_password,
    "database": db_name
}

db_pool = pooling.MySQLConnectionPool(**db_config)

CORS(app)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to my API!'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    conn = db_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users1 WHERE email_users=%s", (email,))
    result = cursor.fetchone()
    if result is not None:
        conn.close()
        return jsonify({'message': 'El usuario ya está registrado'}), 400
    cursor.execute("INSERT INTO users1 (email_users) VALUES (%s)", (email,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Registro exitoso'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    conn = db_pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users1 WHERE email_users=%s", (email,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        unsuccess_message = f'Usuario con el email: {email} no se ha encontrado'
        return jsonify({'message': unsuccess_message}), 404
    else:
        idusers = result[0]
        success_message = f'Inicio de sesión exitoso para el usuario con id: {idusers} y el email:{email}'
        conn.close()
        return jsonify({'message': success_message, 'idusers': idusers}), 200

@app.route('/logout', methods=['GET'])
def logout():
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200

@app.route('/check-authentication', methods=['GET'])
def check_authentication():
    is_authenticated = True
    return jsonify({'isLoggedIn': is_authenticated}), 200

@app.route('/items', methods=['GET', 'POST'])
def handle_items():
    if request.method == 'GET':
        query = 'SELECT * FROM items1 ORDER BY id DESC'
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        items = []
        for item in cursor.fetchall():
            item_data = {
                'id': item[0],
                'name': item[1],
                'itemiduser': item[2],
                'fecha': item[3]
            }
            items.append(item_data)
        conn.close()
        return jsonify(items)
    elif request.method == 'POST':
        data = request.get_json()
        item = data.get('name')
        itemiduser = data.get('itemiduser')
        if item and itemiduser:
            try:
                query = 'INSERT INTO items1 (name, itemiduser) VALUES (%s, %s)'
                item_data = (item, itemiduser)
                conn = db_pool.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, item_data)
                conn.commit()
                conn.close()
                return jsonify({'message': 'Item added successfully'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid item'}), 400

@app.route('/users', methods=['GET'])
def handle_users():
    if request.method == 'GET':
        query = 'SELECT * FROM users1 ORDER BY idusers'
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        users = []
        for u in cursor.fetchall():
            u_data = {
                'idusers': u[0],
                'email_users': u[1]
            }
            users.append(u_data)
        conn.close()
        return jsonify(users)

@app.route('/items/<int:index>', methods=['DELETE', 'PUT'])
def handle_item_by_index(index):
    if request.method == 'DELETE':
        query = 'DELETE FROM items1 WHERE id = %s'
        item_index = (index,)
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, item_index)
        conn.commit()
        conn.close()
        return jsonify({'message': 'Item deleted successfully'})
    elif request.method == 'PUT':
        new_name = request.json.get('name')
        if new_name:
            query = 'UPDATE items1 SET name = %s WHERE id = %s'
            item_data = (new_name, index)
            conn = db_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, item_data)
            conn.commit()
            conn.close()
            return jsonify({'message': 'Item editado correctamente'})
        else:
            return jsonify({'error': 'Item invalido'})

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_email(user_id):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email_users FROM users1 WHERE idusers=%s", (user_id,))
        result = cursor.fetchone()
        if result is not None:
            email = result[0]
            conn.close()
            return jsonify({'email_users': email}), 200
        else:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
