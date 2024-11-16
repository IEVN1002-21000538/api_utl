from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import config
from datetime import datetime

app = Flask(__name__)
CORS(app)
con = MySQL(app)

# Ruta para listar los pedidos
@app.route("/pedidos", methods=['GET'])
def lista_pedidos():
    try:
        cursor = con.connection.cursor()
        sql = 'SELECT * FROM pedidos ORDER BY pedido_id ASC'
        cursor.execute(sql)
        datos = cursor.fetchall()
        pedidos = []
        for fila in datos:
            pedido = {
                'pedido_id': fila[0],
                'nombre_completo': fila[1],
                'direccion': fila[2],
                'telefono': fila[3],
                'fecha_compra': fila[4].strftime("%Y-%m-%d %H:%M:%S") if isinstance(fila[4], datetime) else str(fila[4]),
                'tamanio': fila[5],
                'ingredientes': fila[6],
                'num_pizzas': fila[7],
                'subtotal': fila[8]
            }
            pedidos.append(pedido)
        return jsonify({'pedidos': pedidos, 'mensaje': 'Lista de Pedidos', 'exito': True})
    except Exception as ex:
        return jsonify({"message": f"Error al conectarse a la base de datos: {ex}"})

# Ruta para registrar un pedido
@app.route("/pedidos", methods=['POST'])
def registrar_pedido():
    try:
        data = request.json
        cursor = con.connection.cursor()

        # Insertar datos del pedido (incluyendo los datos del cliente)
        for pizza in data['pizzas']:
            sql_pedido = '''
                INSERT INTO pedidos (nombre_completo, direccion, telefono, fecha_compra, tamanio, ingredientes, num_pizzas, subtotal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql_pedido, (data['nombre_completo'], data['direccion'], data['telefono'], data['fecha_compra'],
                                        pizza['tamanio'], pizza['ingredientes'], pizza['num_pizzas'], pizza['subtotal']))

        con.connection.commit()
        return jsonify({"mensaje": "Pedido registrado con éxito", "exito": True}), 201

    except Exception as ex:
        return jsonify({"mensaje": f"Error al registrar el pedido: {ex}", "exito": False}), 400

# Ruta para obtener los pedidos de un cliente
@app.route("/pedidos/<string:nombre_completo>", methods=['GET'])
def obtener_pedidos(nombre_completo):
    try:
        cursor = con.connection.cursor()
        
        # Consultar todos los pedidos de un cliente específico
        sql_pedidos = 'SELECT pedido_id, nombre_completo, direccion, telefono, fecha_compra, tamanio, ingredientes, num_pizzas, subtotal FROM pedidos WHERE nombre_completo = %s'
        cursor.execute(sql_pedidos, (nombre_completo,))
        datos_pedidos = cursor.fetchall()
        
        if not datos_pedidos:
            return jsonify({"mensaje": "No se encontraron pedidos para este cliente", "exito": False}), 404

        pedidos = []
        for fila in datos_pedidos:
            pedido = {
                'pedido_id': fila[0],
                'nombre_completo': fila[1],
                'direccion': fila[2],
                'telefono': fila[3],
                'fecha_compra': fila[4].strftime("%Y-%m-%d %H:%M:%S") if isinstance(fila[4], datetime) else str(fila[4]),
                'tamanio': fila[5],
                'ingredientes': fila[6],
                'num_pizzas': fila[7],
                'subtotal': fila[8]
            }
            pedidos.append(pedido)
        
        return jsonify({'pedidos': pedidos, 'mensaje': 'Lista de pedidos del cliente', 'exito': True})

    except Exception as ex:
        return jsonify({"mensaje": f"Error al obtener pedidos: {ex}", "exito": False}), 500
    
@app.route("/pizzas/<int:pedido_id>", methods=['GET'])
def obtener_pizzas(pedido_id):
    try:
        cursor = con.connection.cursor()
        sql_pizzas = '''
            SELECT tamanio, ingredientes, num_pizzas, subtotal
            FROM pedidos
            WHERE pedido_id = %s
        '''
        cursor.execute(sql_pizzas, (pedido_id,))
        datos_pizzas = cursor.fetchall()

        if not datos_pizzas:
            return jsonify({"mensaje": "No se encontraron pizzas para este pedido", "exito": False}), 404

        pizzas = []
        for fila in datos_pizzas:
            pizza = {
                'tamanio': fila[0],
                'ingredientes': fila[1],
                'num_pizzas': fila[2],
                'subtotal': fila[3]
            }
            pizzas.append(pizza)
        
        return jsonify({'pizzas': pizzas, 'mensaje': 'Lista de pizzas del pedido', 'exito': True})

    except Exception as ex:
        return jsonify({"mensaje": f"Error al obtener las pizzas: {ex}", "exito": False}), 500

@app.route("/agregar_pizza/<int:pedido_id>", methods=['POST'])
def agregar_pizza(pedido_id):
    try:
        data = request.json
        cursor = con.connection.cursor()

        # Insertar una nueva pizza al pedido existente
        sql_pizza = '''
            INSERT INTO pedidos (pedido_id, tamanio, ingredientes, num_pizzas, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(sql_pizza, (pedido_id, data['tamanio'], data['ingredientes'], data['num_pizzas'], data['subtotal']))

        con.connection.commit()
        return jsonify({"mensaje": "Pizza agregada al pedido con éxito", "exito": True}), 201

    except Exception as ex:
        return jsonify({"mensaje": f"Error al agregar la pizza: {ex}", "exito": False}), 400

@app.route("/eliminar_pizza/<int:pedido_id>/<int:pizza_id>", methods=['DELETE'])
def eliminar_pizza(pedido_id, pizza_id):
    try:
        cursor = con.connection.cursor()
        sql = '''
            DELETE FROM pedidos
            WHERE pedido_id = %s AND pizza_id = %s
        '''
        cursor.execute(sql, (pedido_id, pizza_id))
        con.connection.commit()

        return jsonify({"mensaje": "Pizza eliminada con éxito", "exito": True}), 200

    except Exception as ex:
        return jsonify({"mensaje": f"Error al eliminar la pizza: {ex}", "exito": False}), 400

@app.route("/ventas/<fecha>", methods=['GET'])
def obtener_ventas(fecha):
    try:
        cursor = con.connection.cursor()
        # Asegúrate de que la consulta SQL esté correctamente diseñada para tus necesidades
        sql_ventas = '''
            SELECT SUM(total) AS total_ventas
            FROM pedidos
            WHERE fecha_compra LIKE %s
        '''
        cursor.execute(sql_ventas, (f"{fecha}%",))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({"mensaje": "No se encontraron ventas para esta fecha", "exito": False}), 404

        return jsonify({"ventas": resultado[0], "exito": True})

    except Exception as ex:
        return jsonify({"mensaje": f"Error al obtener las ventas: {ex}", "exito": False}), 500


# Ruta para calcular el total de un cliente
@app.route("/calcular_total/<string:nombre_completo>", methods=['GET'])
def calcular_total(nombre_completo):
    try:
        cursor = con.connection.cursor()
        
        # Sumar los subtotales de los pedidos de un cliente específico
        sql = 'SELECT SUM(subtotal) FROM pedidos WHERE nombre_completo = %s'
        cursor.execute(sql, (nombre_completo,))
        total = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        if total is None:
            total = 0

        return jsonify({'total': total, 'mensaje': 'Total calculado', 'exito': True})

    except Exception as ex:
        return jsonify({"mensaje": f"Error al calcular el total: {ex}", "exito": False}), 500

# Ruta de prueba para verificar conexión
@app.route("/test", methods=['GET'])
def test():
    return jsonify({"mensaje": "Conexión exitosa a pizzeria.py"}), 200

# Página 404 personalizada
def pagina_no_encontrada(error):
    return "<h1>La página que estas buscando no existe</h1>", 400

if __name__ == "__main__":
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000)
