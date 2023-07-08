from flask import (
    Flask,
    render_template,
    request,
    session,
    url_for,
    redirect,
     jsonify,
    flash,
)
from models import Producto, ProductoAgregado, Usuario
from database import (
    add_usuario,
    create_product_table,
    add_producto,
    get_productos,
    obtener_nombre_usuario,
    obtener_tipo_usuario,
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
from flask_mysqldb import MySQL
from functools import wraps
# from transbank.webpay.webpay_plus.transaction import Transaction
# from transbank.error.transbank_error import TransbankError
from uuid import uuid4  # Importar la función uuid4 para generar un session_id único
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import make_response
import requests
import traceback, os, requests
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
app.secret_key = "123"
# Transaction.commerce_code = "tu_codigo_de_comercio"
# Transaction.api_key = "tu_llave_secreta"

# Configuración de la base de datos MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "password"
app.config["MYSQL_DB"] = "musicprodb"

CORS(app)
# SE HABILITA ACCESO PARA API DESDE EL ORIGEN *
cors = CORS(app, resource={
    #  RUTA O RUTAS HABILITADAS PARA SER CONSUMIDAS 
    r"/api/v1/transbank/*":{
        "origins":"*"
    }
})





# pagina 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404

# Función para establecer la conexión a la base de datos y seleccionar la base de datos
def conectar_db():
    mysql = MySQL(app)
    return mysql.connection


# Ruta principal - Catálogo de productos
@app.route("/")
def mostrar_productos():
    productos = get_productos()
    carrito = session.get("carrito", {})
    nombre_usuario = session.get("usuario", "")
    monto_total = session.get("monto_total", "")
    tipo_usuario = session.get("tipo_usuario", "")
    return render_template(
        "index.html",
        productos=productos,
        carrito=carrito,
        nombre_usuario=nombre_usuario,
        monto_total=monto_total,
        tipo_usuario=tipo_usuario,
    )


# Ruta para mostrar catalogo al mantenedor
def verificar_autorizacion(func):
    @wraps(func)
    def decorador(*args, **kwargs):
        tipo_usuario = session.get("tipo_usuario")

        if tipo_usuario not in [1, 2, 3]:
            # Redirigir a una página de acceso no autorizado
            return redirect(url_for("acceso_no_autorizado"))

        return func(*args, **kwargs)

    return decorador


@app.route("/mantenedor")
@verificar_autorizacion
def mostrar_mantenedor():
    nombre_usuario = session.get("usuario", "")
    # Código para obtener la lista de productos para el mantenedor
    productos = get_productos()
    return render_template(
        "mantenedor.html", productos=productos, nombre_usuario=nombre_usuario
    )


@app.route("/producto/<int:producto_id>")
def vista_producto(producto_id):
    nombre_usuario = session.get("usuario", "")
    producto = get_producto_by_id(producto_id)
    return render_template(
        "producto.html", producto=producto, nombre_usuario=nombre_usuario
    )


@app.route("/acceso-no-autorizado")
def acceso_no_autorizado():
    # Página de acceso no autorizado
    return render_template("acceso-no-autorizado.html")


# Ruta para insertar un producto
@app.route("/insertar", methods=["GET", "POST"])
def insertar():
    if request.method == "POST":
        nombre_producto = request.form["nombre_producto"]
        marca_producto = request.form["marca_producto"]
        color_producto = request.form["color_producto"]
        precio_producto = request.form["precio_producto"]
        imagen_producto = request.form["imagen_producto"]

        producto = ProductoAgregado(
            nombre_producto,
            marca_producto,
            color_producto,
            precio_producto,
            imagen_producto,
        )
        add_producto(producto)
        flash("Producto agregado exitosamente.")
        productos = get_productos()
        return render_template(
            "mantenedor.html",
            endpoint="insertar",
            action="Insertar",
            flash_message="Producto agregado exitosamente.",
            productos=productos,
        )
    return render_template(
        "mantenedor.html", endpoint="insertar", action="Insertar", productos=productos
    )


# Ruta para mostrar la página de búsqueda por ID
# @app.route("/buscar")
# def buscar():
#     return render_template("buscar.html")


# Ruta para obtener un producto por su ID
# @app.route("/producto", methods=["GET"])
# def obtener_producto():
#     id_producto = request.args.get("id_producto")
#     producto_data = get_producto_by_id(id_producto)
#     if producto_data:
#         producto = Producto(
#             *producto_data[1:]
#         )  # Crear objeto Producto con los valores de la tupla
#     else:
#         producto = None
#     return render_template("buscar.html", producto=producto)


# Ruta para eliminar un producto
@app.route("/eliminar/<int:id_producto>", methods=["POST"])
def eliminar(id_producto):
    if request.method == "POST":
        delete_producto(id_producto)
        flash("Producto eliminado exitosamente de la base de datos")
        productos = get_productos()
        return render_template(
            "mantenedor.html",
            flash_message="Producto eliminado exitosamente de la base de datos",
            productos=productos,
        )
    return render_template("mantenedor.html")


# Ruta para modificar un producto
@app.route("/modificar/<int:id_producto>", methods=["GET", "POST"])
def modificar(id_producto):
    nombre_usuario = session.get("usuario", "")
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
                nombre_usuario=nombre_usuario,
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
                nombre_usuario=nombre_usuario,
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
        nombre_usuario=nombre_usuario,
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

    monto_total = round(
        sum(
            producto.get("total", 0.00)
            for producto in carrito.values()
            if isinstance(producto, dict)
            and isinstance(producto.get("total"), (int, float))
        ),
        2,
    )
    session["monto_total"] = monto_total
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
    flash("Se agrego el producto al carrito")
    session["carrito"] = carrito
    productos = get_productos()
    return render_template(
        "index.html",
        flash_message="Se agrego el producto al carrito",
        carrito=carrito,
        productos=productos,
    )


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
            session["tipo_usuario"] = obtener_tipo_usuario(email)
            # Redirigir a la vista mostrar_productos con el nombre de usuario como parámetro
            return redirect(
                url_for(
                    "mostrar_productos",
                    nombre_usuario=session["usuario"],
                    tipo_usuario=session["tipo_usuario"],
                )
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


@app.route("/registrar_usuario", methods=["GET", "POST"])
def registrar_usuario():
    if request.method == "POST":
        nombre_completo = request.form["nombre_completo"]
        correo = request.form["correo"]
        password = request.form["password"]

        usuario = Usuario(
            nombre_completo, correo, password, 4
        )  # tipo_usuario siempre es 4
        add_usuario(usuario)
        flash("Registro exitoso, inicie sesión")
        return render_template(
            "login.html", flash_message="¡Registro exitoso!, puede iniciar sesión"
        )
    return render_template(
        "registro.html", flash_message="Hubo un error, intentelo denuevo"
    )


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


# Funcion para fenerar un pdf de la factura para cliente


def generar_boleta_pdf(factura):
    # Crear un nuevo archivo PDF en memoria
    pdf_buffer = BytesIO()

    # Configurar el estilo del documento
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Crear los elementos del contenido del PDF
    elementos = []

    # Título de la boleta
    titulo = Paragraph("<b>Boleta Cliente</b>", styles["Heading1"])
    elementos.append(titulo)
    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))

    # Datos de la factura
    datos_factura = [
        ["ID Factura:", factura["id_factura"]],
        ["Buy Order:", factura["buy_order"]],
        ["Session ID:", factura["session_id"]],
        ["Monto Total:", factura["monto_total"]],
        ["Fecha Emisión:", factura["fecha"]],
    ]
    tabla_factura = Table(datos_factura, colWidths=[100, 300])
    tabla_factura.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elementos.append(tabla_factura)
    elementos.append(Paragraph("<br/><br/>", styles["Normal"]))

    # Tabla de productos
    encabezados = ["Producto", "Cantidad", "Precio Unitario"]
    datos_productos = [encabezados] + [
        [producto["nombre"], producto["cantidad"], producto["precio"]]
        for producto in factura["productos_carrito"]
    ]
    tabla_productos = Table(datos_productos, colWidths=[200, 100, 100])
    tabla_productos.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    elementos.append(tabla_productos)

    # Agregar el texto "Music Master Pro" en la esquina
    elementos.append(Spacer(1, 60))
    elementos.append(
        Paragraph("<font size=8>Music Master Pro</font>", styles["Normal"])
    )

    # Generar el PDF
    doc.build(elementos)

    return pdf_buffer


# Ruta para descargar el PDF
@app.route("/descargar-pdf", methods=["GET"])
def descargar_pdf():
    # Obtener factura_cliente de la sesión
    factura_cliente = session.get("factura_cliente")

    if factura_cliente:
        # Generar el archivo PDF de la boleta del cliente
        pdf_buffer = generar_boleta_pdf(factura_cliente)

        # Crear una respuesta HTTP con el archivo PDF como contenido adjunto
        response = make_response(pdf_buffer.getvalue())
        response.headers[
            "Content-Disposition"
        ] = "attachment; filename=boleta_cliente.pdf"
        response.headers["Content-Type"] = "application/pdf"

        # Eliminar el archivo PDF temporal
        pdf_buffer.close()

        return response

    # Si no se encuentra factura_cliente en la sesión, redirigir a una página de error
    return render_template("error.html")

def header_request_transbank():    
    headers = { # DEFINICIÓN TIPO DE AUTORIZACIÓN Y AUTENTICACIÓN
                "Authorization": "Token",
                # LLAVE QUE DEBE SER MODIFICADA PORQUE ES SOLO DEL AMBIENTE DE INTEGRACIÓN DE TRANSBANK (PRUEBAS)
                "Tbk-Api-Key-Id": "597055555532",
                # LLAVE QUE DEBE SER MODIFICADA PORQUE DEL AMBIENTE DE INTEGRACIÓN DE TRANSBANK (PRUEBAS)
                "Tbk-Api-Key-Secret": "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
                # DEFINICIÓN DEL TIPO DE INFORMACIÓN ENVIADA
                "Content-Type": "application/json",
                # DEFINICIÓN DE RECURSOS COMPARTIDOS ENTRE DISTINTOS SERVIDORES PARA CUALQUIER MÁQUINA
                "Access-Control-Allow-Origin": "*",
                'Referrer-Policy': 'origin-when-cross-origin',
                } 
    return headers

@app.route('/api/v1/transbank/transaction/create', methods= ['POST'])
def transbank_create():
    print('headers: ', request.headers)
    data = request.json
    #  LECTURA DE PAYLOAD (BODY) CON INFORMACIÓN DE TIPO JSON
    print('data: ', data)    
    # DEFINICIÓN DE RUTA API REST TRANSBANK CREAR TRANSACCIÓN
    url = 'https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2/transactions'
    headers = header_request_transbank()
    response = requests.post(url, json=data, headers=headers)
    print('response: ', response.json())
    return response.json()    












@app.route('/api/v1/transbank/transaction/commit/<string:tokenws>', methods= ['PUT'])
def transbank_commit(tokenws):
    print('tokenws: ', tokenws)
    # DEFINICIÓN DE RUTA API REST TRANSBANK CREAR TRANSACCIÓN
    url = 'https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2/transactions/{token}'.format(token=tokenws)
    headers = header_request_transbank()
    response = requests.put(url, headers=headers)
    print('response: ', response.json())
    return response.json() 



# #Ruta para pagar e ir a transbank
# API_REST_HOST = os.getenv('API_REST_HOST')
# API_REST_PORT = os.getenv('API_REST_PORT')

@app.route("/transbank-pay", methods=["GET", "POST"])
def pagar():
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

                    
        dolar = int(obtener_valor_dolar())
        if request.method == 'GET':     
            buy_order = buy_order
            amount = int(amount * dolar)
            print(amount)
            context = {
                'buy_order' : buy_order,
                'amount' : amount
            }
            return render_template('transbank-pay.html', context=context)
        elif request.method == 'POST':
            
            print('request.method:' , request.method)
            buy_order = session.get("buy_order")
            amount = int(monto_total * dolar)
            session_id = session_id
            return_url = 'http://127.0.0.1:5000/commit-pay'
            body = {
                'buy_order' : buy_order,
                'amount' : amount,
                'session_id': session_id,
                'return_url' : return_url
            }
            print('body:', body)
            url = 'http://127.0.0.1:5000/api/v1/transbank/transaction/create'
            response = requests.post(url, json=body)
            print('response:json: ', response.json())
            context = {
                'transbank': response.json(),
                'amount' : amount
            }
            
            return render_template('send-pay.html', context=context)

@app.route('/commit-pay', methods = ['GET'])
def tranbank_commit_view():  
    token_ws = request.args.get('token_ws')
    if token_ws is not None:
        url = 'http://127.0.0.1:5000/api/v1/transbank/transaction/commit/{token}'.format(token=token_ws)
        response = requests.put(url)  
        print('response: ',response.json())          
        context = {
            'response' : response.json()
        }
        return render_template('commit-pay.html', context=context)                
    else:
        context = {
            'message_error' : 'token inválido.'
        }
        return render_template('commit-pay.html', context=context)    
    

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

        # Generar boleta para el cliente
        factura_cliente = {
            "id_factura": id_factura,
            "fecha": fecha,
            "buy_order": buy_order,
            "session_id": session_id,
            "productos_carrito": productos_carrito,
            "monto_total": monto_total,
        }

        # Guardar factura_cliente en la sesión
        session["factura_cliente"] = factura_cliente

        # Generar el archivo PDF de la boleta del cliente
        pdf_buffer = generar_boleta_pdf(factura_cliente)

        # Crear una respuesta HTTP con el archivo PDF como contenido adjunto
        response = make_response(pdf_buffer.getvalue())
        response.headers[
            "Content-Disposition"
        ] = "attachment; filename=boleta_cliente.pdf"
        response.headers["Content-Type"] = "application/pdf"

        # Eliminar el archivo PDF temporal
        pdf_buffer.close()

        # Redirigir a la página de éxito o mostrar un mensaje de confirmación
        return render_template(
            "factura_cliente.html", facturas=[factura_cliente], pdf_response=response
        )

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


def obtener_valor_dolar():
    url = 'https://mindicador.cl/api/dolar'
    response = requests.get(url)
    data = response.json()
    valor_dolar = data['serie'][0]['valor']
    print(valor_dolar)
    return valor_dolar




if __name__ == "__main__":
    # Establecer la conexión a la base de datos y seleccionar la base de datos
    connection = conectar_db()

    # Crear la tabla de productos si no existe
    create_product_table()
    create_table_tipo_usuario()
    create_table_usuario()
    obtener_valor_dolar()
    app.run(debug=True)
