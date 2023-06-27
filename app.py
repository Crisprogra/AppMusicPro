import json
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    session,
    url_for,
    redirect,
    flash,
)
from models import Producto
from database import (
    create_product_table,
    add_producto,
    get_productos,
    obtener_nombre_usuario,
    obtener_usuario_contraseña,
    update_producto,
    delete_producto,
    get_producto_by_id,
    create_table_tipo_usuario,
    create_table_usuario,
    guardar_factura_bodega,
    guardar_factura_contador,
    obtener_todas_facturas_bodega,
    obtener_todas_facturas_contador,
)
from Api_Transbank import header_request_transbank
from flask_mysqldb import MySQL
import requests
import random
import string
import re
from datetime import datetime

# from transbank.webpay.webpay_plus.transaction import Transaction
# from transbank.error.transbank_error import TransbankError
from uuid import uuid4  # Im

app = Flask(__name__)
app.secret_key = "123"
# Transaction.commerce_code = "tu_codigo_de_comercio"
# Transaction.api_key = "tu_llave_secreta"

# Configuración de la base de datos MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "musicprodb"


# Función para establecer la conexión a la base de datos y seleccionar la base de datos
def conectar_db():
    mysql = MySQL(app)
    return mysql.connection


# Ruta principal - Catálogo de productos
@app.route("/")
def mostrar_productos():
    productos = get_productos()
    carrito = session.get("carrito", {})
    nombre_usuario = session.get(
        "usuario", ""
    )  # Obtener el nombre de usuario de la sesión
    return render_template(
        "index.html",
        productos=productos,
        carrito=carrito,
        nombre_usuario=nombre_usuario,
    )


# Ruta para mostrar  catalogo al mantenedor
@app.route("/mantenedor")
def mostrar_mantenedor():
    # Código para obtener la lista de productos para el mantenedor
    productos = get_productos()
    return render_template("mantenedor.html", productos=productos)


# Ruta para insertar un producto
@app.route("/insertar", methods=["GET", "POST"])
def insertar():
    if request.method == "POST":
        id_producto = request.form["id_producto"]
        nombre_producto = request.form["nombre_producto"]
        marca_producto = request.form["marca_producto"]
        color_producto = request.form["color_producto"]
        precio_producto = request.form["precio_producto"]
        imagen_producto = request.form["imagen_producto"]

        producto = Producto(
            id_producto,
            nombre_producto,
            marca_producto,
            color_producto,
            precio_producto,
            imagen_producto,
        )
        add_producto(producto)
        return "Producto insertado exitosamente en la base de datos."
    return render_template("mantenedor.html", endpoint="insertar", action="Insertar")


# Ruta para mostrar la página de búsqueda por ID
@app.route("/buscar")
def buscar():
    return render_template("buscar.html")


# Ruta para obtener un producto por su ID
@app.route("/producto", methods=["GET"])
def obtener_producto():
    id_producto = request.args.get("id_producto")
    producto_data = get_producto_by_id(id_producto)
    if producto_data:
        producto = Producto(
            *producto_data[1:]
        )  # Crear objeto Producto con los valores de la tupla
    else:
        producto = None
    return render_template("buscar.html", producto=producto)


# Ruta para eliminar un producto
@app.route("/eliminar/<int:id_producto>", methods=["POST"])
def eliminar(id_producto):
    if request.method == "POST":
        delete_producto(id_producto)
        return "Producto eliminado exitosamente de la base de datos."
    return render_template("mantenedor.html")


# Ruta para modificar un producto
@app.route("/modificar/<int:id_producto>", methods=["GET", "POST"])
def modificar(id_producto):
    print(id_producto)
    # Obtener el producto por su ID
    producto = get_producto_by_id(id_producto)
    if producto is None:
        error_message = "No se encontró el producto con el ID especificado."
        return render_template(
            "modificar.html",
            id_producto=id_producto,
            error_message=error_message,
            endpoint="modificar",
            action="Modificar",
        )

    if request.method == "POST":
        # Obtener los datos del formulario
        nombre_producto = request.form["nombre_producto"]
        marca_producto = request.form["marca_producto"]
        color_producto = request.form["color_producto"]
        precio_producto = request.form["precio_producto"]
        imagen_producto = request.form["imagen_producto"]

        # Realizar la actualización del producto
        producto = Producto(
            id_producto,
            nombre_producto,
            marca_producto,
            color_producto,
            precio_producto,
            imagen_producto,
        )

        # Validar si hay un mensaje de error
        error_message = update_producto(id_producto, producto)
        if error_message:
            producto = get_producto_by_id(id_producto)
            return render_template(
                "modificar.html",
                id_producto=id_producto,
                nombre=nombre_producto,
                marca=marca_producto,
                color=color_producto,
                precio=precio_producto,
                imagen=imagen_producto,
                producto=producto,
                endpoint="modificar",
                action="Modificar",
                error_message=error_message,
            )
        else:
            # Actualizar el nombre del producto en el carrito si está presente
            carrito = session.get("carrito", {})
            for producto_id, producto_carrito in carrito.items():
                if producto_id == str(id_producto):
                    producto_carrito["nombre"] = nombre_producto
                    # Actualizar los demás atributos del producto en el carrito si es necesario
            session["carrito"] = carrito

            return render_template(
                "modificar.html",
                success_message="Producto modificado exitosamente en la base de datos.",
                producto=producto,
            )

    return render_template(
        "modificar.html",
        id_producto=id_producto,
        nombre=producto.nombre_producto,
        marca=producto.marca_producto,
        color=producto.color_producto,
        precio=producto.precio_producto,
        imagen=producto.imagen_producto,
        producto=producto,
        endpoint="modificar",
        action="Modificar",
    )


# Ruta para el carrito de compras


@app.route("/carrito", methods=["GET", "POST"])
def carrito():
    carrito = session.get("carrito", {})
    nombre_usuario = session.get("usuario", "")
    # Validar si los datos en la sesión tienen la estructura esperada
    if not isinstance(carrito, dict):
        # Redirigir a una página de error o realizar alguna otra acción adecuada
        return render_template("error.html")

    monto_total = sum(
        float(str(producto.get("total", "0.00")).replace(",", "").replace(".", ""))
        for producto in carrito.values()
        if isinstance(producto, dict)
        and isinstance(producto.get("total"), (int, float))
    )

    if request.method == "POST":
        producto_id = request.form.get("producto_id")
        accion = request.form.get("accion")

        if producto_id in carrito:
            if accion == "increment":
                carrito[producto_id]["cantidad"] += 1
            elif accion == "decrement":
                carrito[producto_id]["cantidad"] -= 1
                if carrito[producto_id]["cantidad"] < 1:
                    carrito[producto_id]["cantidad"] = 1

            carrito[producto_id]["total"] = (
                carrito[producto_id]["precio"] * carrito[producto_id]["cantidad"]
            )
            session["carrito"] = carrito

    return render_template(
        "carrito.html",
        carrito=carrito,
        monto_total=monto_total,
        nombre_usuario=nombre_usuario,
    )


# Ruta para agregar un producto al carrito
@app.route("/agregar_al_carrito", methods=["POST"])
def agregar_al_carrito():
    producto_id = request.form.get("producto_id")
    producto_nombre = request.form.get("nombre")
    producto_precio = float(request.form.get("precio"))
    buy_order = (
        generar_buy_order()
    )  # Generar el buy_order (puedes implementar tu propia lógica para esto)

    if (
        "session_id" not in session
    ):  # Verificar si el session_id no está presente en la sesión
        session["session_id"] = str(
            uuid4()
        )  # Generar un nuevo session_id único y asignarlo a la sesión

    session_id = session["session_id"]  # Obtener el session_id de la sesión actual
    session["buy_order"] = buy_order  # Almacenar el buy_order en la sesión

    print("Session ID:", session_id)
    print("Buy Order:", buy_order)

    carrito = session.get("carrito", {})
    if producto_id in carrito:
        carrito[producto_id]["cantidad"] += 1
        carrito[producto_id]["total"] = (
            carrito[producto_id]["precio"] * carrito[producto_id]["cantidad"]
        )
    else:
        carrito[producto_id] = {
            "nombre": producto_nombre,
            "precio": producto_precio,
            "cantidad": 1,
            "total": producto_precio,
            "buy_order": buy_order,
            "session_id": session_id,
        }

    session["carrito"] = carrito
    return redirect(url_for("mostrar_productos"))


# Ruta para actualizar cantidad del producto en el carrito
@app.route("/actualizar_cantidad_carrito", methods=["POST"])
def actualizar_cantidad_carrito():
    producto_id = request.form.get("producto_id")
    accion = request.form.get("accion")

    carrito = session.get("carrito", {})
    if producto_id in carrito:
        if accion == "decrement":
            carrito[producto_id]["cantidad"] -= 1
            if carrito[producto_id]["cantidad"] < 1:
                carrito[producto_id]["cantidad"] = 1
        elif accion == "increment":
            carrito[producto_id]["cantidad"] += 1
        carrito[producto_id]["total"] = (
            carrito[producto_id]["precio"] * carrito[producto_id]["cantidad"]
        )

    session["carrito"] = carrito
    return redirect(url_for("carrito"))


# Ruta para eliminar producto del carrito
@app.route("/eliminar_producto_carrito", methods=["POST"])
def eliminar_producto_carrito():
    producto_id = request.form.get("producto_id")

    carrito = session.get("carrito", {})
    if producto_id in carrito:
        del carrito[producto_id]
        session["carrito"] = carrito

    return redirect(url_for("carrito"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Obtener la contraseña asociada al correo electrónico
        stored_password = obtener_usuario_contraseña(email)
        print(password)
        print(stored_password)
        # Verificar las credenciales del usuario
        if password == stored_password:
            session["usuario"] = obtener_nombre_usuario(email)
            # Redirigir a la vista mostrar_productos con el nombre de usuario como parámetro
            return redirect(
                url_for("mostrar_productos", nombre_usuario=session["usuario"])
            )
        else:
            flash("Inicio de sesión fallido. Verifica tus credenciales.")
            # Renderizar nuevamente la plantilla de inicio de sesión con el mensaje de flash
            return render_template(
                "login.html",
                flash_message="Inicio de sesión fallido. Verifica tus credenciales.",
            )
    # Mostrar el formulario de inicio de sesión
    return render_template("login.html")


@app.route("/logout")
def logout():
    # Eliminar la información de sesión y redirigir al inicio de sesión
    session.clear()
    return redirect(url_for("mostrar_productos"))


# Funcion para crear una orden de compra random


def generar_buy_order():
    # Obtener el último correlativo de buy_order de la base de datos o de alguna fuente de datos
    # ...
    ultimo_correlativo = 1000  # Supongamos que el último correlativo es 1000

    # Generar el nuevo correlativo incrementando el último correlativo en 1
    nuevo_correlativo = ultimo_correlativo + 1

    # Formatear el correlativo con la sigla "BO" seguida de los dígitos
    buy_order = f"BO{nuevo_correlativo}"

    return buy_order


def generar_id_factura():
    # Obtener el último ID de factura de la base de datos o de alguna fuente de datos
    # ...
    ultimo_id_factura = 1000  # Supongamos que el último ID de factura es 1000

    # Generar el nuevo ID de factura incrementando el último ID en 1
    nuevo_id_factura = ultimo_id_factura + 1

    # Formatear el ID de factura con las iniciales "FA" seguidas de los dígitos
    id_factura = f"FA{nuevo_id_factura}"

    return id_factura


# Ruta para el retorno desde Transbank y generación de facturas
@app.route("/retorno-transbank", methods=["POST"])
def retorno_transbank():
    # Simulación de retorno desde Transbank y ejecución de la generación de facturas
    # Aquí se realizarían las operaciones necesarias para obtener los datos de la transacción

    # Verificar si la clave 'carrito' está presente en la sesión
    if "carrito" in session:
        carrito = session["carrito"]
        # Obtener el buy_order y el session_id de la sesión
        buy_order = session.get("buy_order")
        session_id = session.get("session_id")

        print("Session ID:", session_id)
        print("Buy Order:", buy_order)
        print("Productos del carrito:", carrito)

        # Obtener los productos del carrito
        productos_carrito = []
        monto_total = 0.0
        for producto_id, producto_info in carrito.items():
            producto = {
                "id": producto_id,
                "nombre": producto_info["nombre"],
                "precio": producto_info["precio"],
                "cantidad": producto_info["cantidad"],
                "total": producto_info["total"],
            }
            productos_carrito.append(producto)
            monto_total += producto_info["total"]

        print("Productos:", productos_carrito)
        print("Monto total:", monto_total)

        # Generar factura para el contador
        id_factura = generar_id_factura()
        fecha = datetime.now()  # Obtén la fecha actual

        # Crear los datos de la factura del contador
        factura_contador = {
            "id_factura": id_factura,
            "fecha": fecha,
            "buy_order": buy_order,
            "session_id": session_id,
            "productos_carrito": productos_carrito,
            "monto_total": monto_total,
        }

        # Llamar a la función para guardar la factura del contador en la base de datos
        guardar_factura_contador(factura_contador)

        # Generar factura para la bodega
        id_factura = generar_id_factura()
        fecha_emision = datetime.now()  # Obtén la fecha actual

        # Crear los datos de la factura de la bodega
        factura_bodega = {
            "id_factura": id_factura,
            "fecha": fecha,
            "buy_order": buy_order,
            "session_id": session_id,
            "productos_carrito": productos_carrito,
            "monto_total": monto_total,
        }

        # Llamar a la función para guardar la factura de la bodega en la base de datos
        guardar_factura_bodega(factura_bodega)

        # Redirigir a la página de éxito o mostrar un mensaje de confirmación
        return render_template("exito.html")

    # Si el carrito o los datos requeridos no están presentes, redirigir a una página de error
    return render_template("error.html")


# Función para renderizar las facturas de contador
@app.route("/facturas-contador")
def renderizar_facturas_contador():
    facturas_contador = obtener_todas_facturas_contador()
    return render_template("facturas_contador.html", facturas=facturas_contador)


# Función para renderizar las facturas de bodega
@app.route("/facturas-bodega")
def renderizar_facturas_bodega():
    facturas_bodega = obtener_todas_facturas_bodega()
    return render_template("facturas_bodega.html", facturas=facturas_bodega)


if __name__ == "__main__":
    # Establecer la conexión a la base de datos y seleccionar la base de datos
    connection = conectar_db()

    # Crear la tabla de productos si no existe
    create_product_table()
    create_table_tipo_usuario()
    create_table_usuario()

    app.run(debug=True)
