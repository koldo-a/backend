from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import mysql.connector

app = Flask(__name__)

# Configura la conexión a la base de datos MySQL utilizando las variables de entorno
db_host = os.environ.get('MYSQLHOST')
db_port = os.environ.get('MYSQLPORT')
db_user = os.environ.get('MYSQLUSER')
db_password = os.environ.get('MYSQLPASSWORD')
db_name = os.environ.get('MYSQLDATABASE')

# Configura CORS para permitir todas las solicitudes (ajusta según tus necesidades)
CORS(app)

# Función para conectar a la base de datos
def connect_to_database():
    return mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Ruta de inicio
@app.route('/')
def home():
    return jsonify({'message': '¡Bienvenido a la página de inicio!'})

# Ruta para el registro de usuarios
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    try:
        # Conectar a la base de datos
        db = connect_to_database()
        cursor = db.cursor()

        # Verifica si el usuario ya está registrado
        cursor.execute("SELECT * FROM users1 WHERE email_users=%s", (email,))
        result = cursor.fetchone()

        if result:
            return jsonify({'message': 'El usuario ya está registrado'}), 400

        # Inserta el nuevo usuario en la base de datos
        cursor.execute("INSERT INTO users1 (email_users) VALUES (%s)", (email,))
        db.commit()

        return jsonify({'message': 'Registro exitoso'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        db.close()

# ... (resto de las rutas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT", default=5000))
