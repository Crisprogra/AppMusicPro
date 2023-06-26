from flask import Flask, render_template, request, session, url_for, redirect
from models import Producto
from database import create_product_table, add_producto, get_productos,update_producto,delete_producto,get_producto_by_id, create_table_tipo_usuario, create_table_usuario,create_table_factura_bodega,create_table_factura_contador
from Api_Transbank import header_request_transbank
from flask_mysqldb import MySQL
import requests
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.error.transbank_error import TransbankError

app = Flask(__name__)
app.secret_key = '123'
Transaction.commerce_code = "tu_codigo_de_comercio"
Transaction.api_key = "tu_llave_secreta"

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'musicprodb'

# Función para establecer la conexión a la base de datos y seleccionar la base de datos
def conectar_db():
    mysql = MySQL(app)
    return mysql.connection


# Ruta principal - Catálogo de productos
@app.route('/')
def mostrar_productos():
    productos = get_productos()
    carrito = session.get('carrito', {})
    return render_template('catalogo.html', productos=productos, carrito=carrito)
# Ruta para mostrar  catalogo al mantenedor
@app.route('/mantenedor')
def mostrar_mantenedor():
    # Código para obtener la lista de productos para el mantenedor
    productos = get_productos()
    return render_template('mantenedor.html', productos=productos)

# Ruta para insertar un producto
@app.route('/insertar', methods=['GET', 'POST'])
def insertar():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        nombre_producto = request.form['nombre_producto']
        marca_producto = request.form['marca_producto']
        color_producto = request.form['color_producto']
        precio_producto = request.form['precio_producto']
        imagen_producto = request.form['imagen_producto']

        producto = Producto(id_producto, nombre_producto, marca_producto, color_producto, precio_producto, imagen_producto)
        add_producto(producto)

        return "Producto insertado exitosamente en la base de datos."

    return render_template('mantenedor.html', endpoint='insertar', action='Insertar')

# Ruta para mostrar la página de búsqueda por ID
@app.route('/buscar')
def buscar():
    return render_template('buscar.html')

# Ruta para obtener un producto por su ID
@app.route('/producto', methods=['GET'])
def obtener_producto():
    id_producto = request.args.get('id_producto')
    producto_data = get_producto_by_id(id_producto)

    if producto_data:
        producto = Producto(*producto_data)  # Crear objeto Producto con los valores de la tupla
    else:
        producto = None

    return render_template('buscar.html', producto=producto)


# Ruta para eliminar un producto
@app.route('/eliminar/<int:id_producto>', methods=['POST'])
def eliminar(id_producto):
    if request.method == 'POST':
        delete_producto(id_producto)
        return "Producto eliminado exitosamente de la base de datos."
    return render_template('mantenedor.html')

# Ruta para modificar un producto
@app.route('/modificar/<int:id_producto>', methods=['GET', 'POST'])
def modificar(id_producto):
    # Obtener el producto por su ID
    producto = get_producto_by_id(id_producto)
    if producto is None:
        error_message = "No se encontró el producto con el ID especificado."
        return render_template('modificar.html', id_producto=id_producto, error_message=error_message,
                               endpoint='modificar', action='Modificar')

    
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_producto = request.form['nombre_producto']
        marca_producto = request.form['marca_producto']
        color_producto = request.form['color_producto']
        precio_producto = request.form['precio_producto']
        imagen_producto = request.form['imagen_producto']

        # Realizar la actualización del producto
        producto = Producto(id_producto, nombre_producto, marca_producto, color_producto, precio_producto, imagen_producto)

        # Validar si hay un mensaje de error
        error_message = update_producto(id_producto, producto)
        if error_message:
            producto = get_producto_by_id(id_producto)
            return render_template('modificar.html', id_producto=id_producto,
                                   nombre=nombre_producto, marca=marca_producto, color=color_producto,
                                   precio=precio_producto, imagen=imagen_producto, producto=producto,
                                   endpoint='modificar', action='Modificar', error_message=error_message)
        else:
            # Actualizar el nombre del producto en el carrito si está presente
            carrito = session.get('carrito', {})
            for producto_id, producto_carrito in carrito.items():
                if producto_id == str(id_producto):
                    producto_carrito['nombre'] = nombre_producto
                    # Actualizar los demás atributos del producto en el carrito si es necesario
            session['carrito'] = carrito

            return render_template('modificar.html', success_message="Producto modificado exitosamente en la base de datos.", producto=producto)
    
    return render_template('modificar.html', id_producto=id_producto,
                           nombre=producto.nombre_producto, marca=producto.marca_producto,
                           color=producto.color_producto, precio=producto.precio_producto,
                           imagen=producto.imagen_producto, producto=producto,
                           endpoint='modificar', action='Modificar')

# Ruta para el carrito de compras

@app.route('/carrito', methods=['GET', 'POST'])
def carrito():
    carrito = session.get('carrito', {})
    monto_total = sum(float(str(producto.get('total', '0.00')).replace(',', '').replace('.', '')) for producto in carrito.values())


 
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        accion = request.form.get('accion')


        if producto_id in carrito:
            if accion == 'increment':
                carrito[producto_id]['cantidad'] += 1
            elif accion == 'decrement':
                carrito[producto_id]['cantidad'] -= 1
                if carrito[producto_id]['cantidad'] < 1:
                    carrito[producto_id]['cantidad'] = 1

            carrito[producto_id]['total'] = carrito[producto_id]['precio'] * carrito[producto_id]['cantidad']
            session['carrito'] = carrito

    return render_template('carrito.html', carrito=carrito, monto_total=monto_total)



# Ruta para agregar un producto al carrito
@app.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    producto_id = request.form.get('producto_id')
    producto_nombre = request.form.get('nombre')
    producto_precio = float(request.form.get('precio'))

    carrito = session.get('carrito', {})
    if producto_id in carrito:
        carrito[producto_id]['cantidad'] += 1
        carrito[producto_id]['total'] = carrito[producto_id]['precio'] * carrito[producto_id]['cantidad']
    else:
        carrito[producto_id] = {
            'nombre': producto_nombre,
            'precio': producto_precio,
            'cantidad': 1,
            'total': producto_precio
        }

    session['carrito'] = carrito
    return redirect(url_for('mostrar_productos'))


# Ruta para actualizar cantidad del producto en el carrito
@app.route('/actualizar_cantidad_carrito', methods=['POST'])
def actualizar_cantidad_carrito():
    producto_id = request.form.get('producto_id')
    accion = request.form.get('accion')

    carrito = session.get('carrito', {})
    if producto_id in carrito:
        if accion == 'decrement':
            carrito[producto_id]['cantidad'] -= 1
            if carrito[producto_id]['cantidad'] < 1:
                carrito[producto_id]['cantidad'] = 1
        elif accion == 'increment':
            carrito[producto_id]['cantidad'] += 1
        carrito[producto_id]['total'] = carrito[producto_id]['precio'] * carrito[producto_id]['cantidad']

    session['carrito'] = carrito
    return redirect(url_for('carrito'))


# Ruta para eliminar producto del carrito
@app.route('/eliminar_producto_carrito', methods=['POST'])
def eliminar_producto_carrito():
    producto_id = request.form.get('producto_id')

    carrito = session.get('carrito', {})
    if producto_id in carrito:
        del carrito[producto_id]
        session['carrito'] = carrito

    return redirect(url_for('carrito'))

if __name__ == '__main__':
    
    # Establecer la conexión a la base de datos y seleccionar la base de datos
    connection = conectar_db()

    # Crear la tabla de productos si no existe
    create_product_table()
    create_table_tipo_usuario()
    create_table_usuario()
    create_table_factura_contador()
    create_table_factura_bodega()
    
  
    app.run(debug=True)


