from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os 
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['MYSQL_URL']

CORS(app)
db = SQLAlchemy(app)

db_host = os.environ.get('DB_HOST') or '127.0.0.1'
db_port = os.environ.get('DB_PORT') or '3306'
db_user = os.environ.get('DB_USER') or 'root'
db_password = os.environ.get('DB_PASSWORD') or 'estibaliZ1.'
db_name = os.environ.get('DB_NAME') or 'fullstack_bottega'

# Configura la conexión a la base de datos MySQL utilizando las variables
db = mysql.connector.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)

# Ruta para el registro de usuarios
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    
    # Verifica si el usuario ya está registrado
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users1 WHERE email_users=%s", (email,))
    result = cursor.fetchone()
    
    if result is not None:
        return jsonify({'message': 'El usuario ya está registrado'}), 400
    
    # Inserta el nuevo usuario en la base de datos
    cursor.execute("INSERT INTO users1 (email_users) VALUES (%s)", (email,))
    db.commit()
    
    return jsonify({'message': 'Registro exitoso'}), 200

# Ruta para la autenticación de usuarios
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    
    # Verifica si el usuario existe en la base de datos
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users1 WHERE email_users=%s", (email,))
    result = cursor.fetchone()
    if result is None:
        unsuccess_message = f'Usuario con el email: {email} no se ha encontrado'
        return jsonify({'message': unsuccess_message}), 404
    else: 
        idusers = result[0]
        success_message = f'Inicio de sesión exitoso para el usuario con id: {idusers} y el email:{email}'
        # Retornar el mensaje de éxito junto con el idusers en la respuesta JSON
        return jsonify({'message': success_message, 'idusers': idusers }), 200

# Ruta para el cierre de sesión
@app.route('/logout', methods=['GET'])
def logout():
    # Realiza las acciones necesarias para cerrar sesión, como limpiar las cookies o el estado de autenticación
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200

# Ruta para verificar el estado de autenticación
@app.route('/check-authentication', methods=['GET'])
def check_authentication():
    # Aquí puedes realizar la lógica para verificar si el usuario está autenticado o no
    # Puedes usar cookies, tokens u otros métodos de autenticación según tu implementación
    # En este ejemplo, simplemente devolvemos un estado de autenticación aleatorio para demostración
    is_authenticated = True  # Aquí debes implementar tu propia lógica de autenticación
    
    return jsonify({'isLoggedIn': is_authenticated}), 200

# Rutas para las operaciones CRUD
@app.route('/items', methods=['GET', 'POST'])
def handle_items():
    if request.method == 'GET':
        # Consulta SQL para obtener todos los registros de la tabla
        query = 'SELECT * FROM items1'

        # Ejecutar la consulta
        cursor = db.cursor()
        cursor.execute(query)

        # Obtener los resultados y construir la lista de elementos
        items = []
        for item in cursor.fetchall():
            item_data = {
                'id': item[0],
                'name': item[1],
                'itemiduser': item[2]
            }
            items.append(item_data)

        return jsonify(items)

    elif request.method == 'POST':
        data = request.get_json()
        item = data.get('name')
        itemiduser = data.get('itemiduser')  # Obtener el id del usuario del cuerpo de la solicitud

        if item and itemiduser:
            try:
                # Consulta SQL para insertar un nuevo registro en la tabla
                query = 'INSERT INTO items1 (name, itemiduser) VALUES (%s, %s)'

                # Datos del nuevo elemento
                item_data = (item, itemiduser)

                # Ejecutar la consulta
                cursor = db.cursor()
                cursor.execute(query, item_data)
                db.commit()

                return jsonify({'message': 'Item added successfully'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Invalid item'}), 400
#----------------------------------------------------------------
# Rutas para las operaciones CRUD
@app.route('/users', methods=['GET'])
def handle_users():
    if request.method == 'GET':
        # Consulta SQL para obtener todos los registros de la tabla
        query = 'SELECT * FROM users1 ORDER BY idusers'

        # Ejecutar la consulta
        cursor = db.cursor()
        cursor.execute(query)

        # Obtener los resultados y construir la lista de elementos
        users = []
        for u in cursor.fetchall():
            u_data = {
                'idusers': u[0],
                'name': u[1]
            }
            users.append(u_data)

        return jsonify(users)


#----------------------------------------------------------------



@app.route('/items/<int:index>', methods=['DELETE', 'PUT'])
def handle_item_by_index(index):
    if request.method == 'DELETE':
        # Consulta SQL para eliminar un registro de la tabla
        query = 'DELETE FROM items1 WHERE id = %s'

        # Datos del índice del elemento a eliminar
        item_index = (index,)

        # Ejecutar la consulta
        cursor = db.cursor()
        cursor.execute(query, item_index)
        db.commit()

        return jsonify({'message': 'Item deleted successfully'})

    elif request.method == 'PUT':
        new_name = request.json.get('name')
        if new_name:
            # Consulta SQL para actualizar un registro de la tabla
            query = 'UPDATE items1 SET name = %s WHERE id = %s'

            # Datos del nuevo nombre y el índice del elemento a editar
            item_data = (new_name, index)

            # Ejecutar la consulta
            cursor = db.cursor()
            cursor.execute(query, item_data)
            db.commit()

            return jsonify({'message': 'Item edited successfully'})
        else:
            return jsonify({'error': 'Invalid item'})

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_email(user_id):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT email_users FROM users1 WHERE idusers=%s", (user_id,))
        result = cursor.fetchone()

        if result is not None:
            email = result[0]
            return jsonify({'email_users': email}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
