from flask import Flask, render_template, request
from models import Producto
from database import create_product_table, add_producto, get_productos,update_producto,delete_producto,get_producto_by_id, create_table_tipo_usuario, create_table_usuario
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de la base de datos MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'musicprodb'

# Ruta principal - Catálogo de productos
@app.route('/')
def mostrar_productos():
   
    productos = get_productos()
    return render_template('catalogo.html', productos=productos)

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

# Ruta para modificar un producto
# Ruta para modificar un producto
@app.route('/modificar/<int:id_producto>', methods=['GET', 'POST'])
def modificar(id_producto):
    if request.method == 'POST':
        # Obtener los datos del formulario

        # Realizar la actualización del producto

        # Validar si hay un mensaje de error
        error_message = update_producto(id_producto, producto)
        if error_message:
            producto = get_producto_by_id(id_producto)
            return render_template('modificar.html', id_producto=id_producto, nombre=producto[1],
                                   precio=producto[2], marca=producto[3], color=producto[4], imagen=producto[5],
                                   endpoint='modificar', action='Modificar', error_message=error_message)
        else:
            return render_template('modificar.html', success_message="Producto modificado exitosamente en la base de datos.")

    # Obtener los datos del producto con el ID proporcionado
    producto = get_producto_by_id(id_producto)
    if not producto:
        return render_template('modificar.html', error_message="No existe un producto con el ID especificado.")

    # Renderizar la página de modificar con los datos del producto
    return render_template('modificar.html', id_producto=id_producto, nombre=producto[1],
                           precio=producto[2], marca=producto[3], color=producto[4], imagen=producto[5],
                           endpoint='modificar', action='Modificar')






if __name__ == '__main__':
    # Crear la tabla de productos si no existe
    create_product_table()
    create_table_tipo_usuario()
    create_table_usuario()
    app.run()


