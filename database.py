import json
import mysql.connector
from models import Producto, FacturaBodega, FacturaContador
import json


def create_table_tipo_usuario():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tipo_usuario (
                    id_tipo_usuario INT PRIMARY KEY,
                    tipo_usuario VARCHAR(255)
                )
            """
            )
            print("Tabla tipo_usuario creada exitosamente.")

        except mysql.connector.Error as error:
            print("Error al crear la tabla tipo_usuario:", error)

        connection.commit()

    except mysql.connector.Error as error:
        print("Error al crear la tabla tipo_usuario:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def create_table_usuario():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS usuario (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_completo VARCHAR(255),
                    correo VARCHAR(255),
                    password VARCHAR(255),
                    tipo_usuario INT,
                    FOREIGN KEY (tipo_usuario) REFERENCES tipo_usuario(id_tipo_usuario)
                )
                """
            )
            print("Tabla usuario creada exitosamente.")

        except mysql.connector.Error as error:
            print("Error al crear la tabla usuario:", error)

        connection.commit()

    except mysql.connector.Error as error:
        print("Error al crear la tabla usuario:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def create_product_table():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        query = """
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INT AUTO_INCREMENT PRIMARY KEY,
            nombre_producto VARCHAR(255),
            marca_producto VARCHAR(255),
            color_producto VARCHAR(255),
            precio_producto DECIMAL(10, 2),
            imagen_producto VARCHAR(255)
        )
        """
        cursor.execute(query)

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        print("Error al crear la tabla de productos:", error)


def add_producto(producto):
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        query = """
        INSERT INTO productos (nombre_producto, marca_producto, color_producto, precio_producto, imagen_producto)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            producto.nombre_producto,
            producto.marca_producto,
            producto.color_producto,
            producto.precio_producto,
            producto.imagen_producto,
        )
        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        print("Error al agregar un producto:", error)


def get_productos():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        query = "SELECT * FROM productos"
        cursor.execute(query)

        productos = []
        for (
            id_producto,
            nombre_producto,
            marca_producto,
            color_producto,
            precio_producto,
            imagen_producto,
        ) in cursor:
            producto = Producto(
                id_producto,
                nombre_producto,
                marca_producto,
                color_producto,
                precio_producto,
                imagen_producto,
            )
            productos.append(producto)

        cursor.close()
        connection.close()

        return productos

    except mysql.connector.Error as error:
        print("Error al obtener los productos:", error)
        return []


def get_producto_by_id(id_producto):
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        select_query = """
            SELECT * FROM productos WHERE id_producto = %s
        """

        cursor.execute(select_query, (id_producto,))
        producto_data = cursor.fetchone()

        cursor.close()
        connection.close()

        if producto_data:
            producto = Producto(
                *producto_data
            )  # Crear una instancia de Producto con los valores obtenidos
            return producto
        else:
            return None

    except mysql.connector.Error as error:
        print("Error al obtener el producto:", error)


# Función para actualizar un producto de la base de datos
def update_producto(id_producto, producto):
    try:
        # Verificar si el ID del producto existe en la base de datos
        producto_existente = get_producto_by_id(id_producto)
        if not producto_existente:
            return f"No existe un producto con el ID {id_producto}"

        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        update_query = """
            UPDATE productos SET nombre_producto = %s, marca_producto = %s, color_producto = %s, precio_producto = %s, imagen_producto = %s
            WHERE id_producto = %s
        """

        data = (
            producto.nombre_producto,
            producto.marca_producto,
            producto.color_producto,
            producto.precio_producto,
            producto.imagen_producto,
            id_producto,
        )
        cursor.execute(update_query, data)
        connection.commit()

        cursor.close()
        connection.close()

        return None  # No se produjo ningún error, devuelve None como indicador de éxito

    except mysql.connector.Error as error:
        return f"Error al actualizar el producto: {str(error)}"


# Función para eliminar un producto de la base de datos
def delete_producto(id_producto):
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        delete_query = """
            DELETE FROM productos WHERE id_producto = %s
        """

        cursor.execute(delete_query, (id_producto,))
        connection.commit()

        cursor.close()
        connection.close()
    except mysql.connector.Error as error:
        print("Error al eliminar el producto:", error)


# Función para crear tabla factura_contador
# Función para crear tabla factura_contador
def create_table_factura_contador():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS factura_contador (
                    id_factura INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    fecha DATE,
                    buy_order VARCHAR(255),
                    session_id VARCHAR(255),
                    productos_carrito TEXT,
                    monto_total DECIMAL(10, 2)
                )
            """
            )
            print("Tabla factura_contador creada exitosamente.")

        except mysql.connector.Error as error:
            print("Error al crear la tabla factura_contador:", error)

        connection.commit()

    except mysql.connector.Error as error:
        print("Error al crear la tabla factura_contador:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Función para guardar factura de contador
def guardar_factura_contador(factura_contador):
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        productos_json = json.dumps(factura_contador["productos_carrito"])

        factura_query = """
        INSERT INTO factura_contador (fecha, buy_order, session_id, productos_carrito, monto_total)
        VALUES (%s, %s, %s, %s, %s)
        """
        factura_values = (
            factura_contador["fecha"],
            factura_contador["buy_order"],
            factura_contador["session_id"],
            productos_json,
            factura_contador["monto_total"],
        )
        cursor.execute(factura_query, factura_values)
        connection.commit()

        cursor.close()
        connection.close()

        print("FacturaContador guardada exitosamente.")

    except mysql.connector.Error as error:
        print("Error al guardar la FacturaContador:", error)


# Función para obtener todas las facturas de contador
def obtener_todas_facturas_contador():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        query = "SELECT * FROM factura_contador"
        cursor.execute(query)

        facturas_data = cursor.fetchall()
        facturas = []

        for factura_data in facturas_data:
            # Deserializar los productos del carrito desde el formato JSON
            productos_carrito = json.loads(factura_data[4])
            # Obtener el precio unitario de cada producto en el carrito
            for producto in productos_carrito:
                producto["precio_unitario"] = producto["precio"]

            factura = FacturaContador(
                id_factura=factura_data[0],
                fecha=factura_data[1],
                buy_order=factura_data[2],
                session_id=factura_data[3],
                productos_carrito=productos_carrito,
                monto_total=factura_data[5],
            )
            facturas.append(factura)

        cursor.close()
        connection.close()

        return facturas

    except mysql.connector.Error as error:
        print("Error al obtener las facturas del contador:", error)


# Función para crear tabla factura_bodega
def create_table_factura_bodega():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS factura_bodega (
                    id_factura INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    fecha DATE,
                    buy_order VARCHAR(255),
                    session_id VARCHAR(255),
                    productos_carrito TEXT,
                    monto_total DECIMAL(10, 2)
                )
            """
            )
            print("Tabla factura_bodega creada exitosamente.")

        except mysql.connector.Error as error:
            print("Error al crear la tabla factura_bodega:", error)

        connection.commit()

    except mysql.connector.Error as error:
        print("Error al crear la tabla factura_bodega:", error)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# Función para guardar factura de bodega
def guardar_factura_bodega(factura_bodega):
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        productos_json = json.dumps(factura_bodega["productos_carrito"])

        factura_query = """
        INSERT INTO factura_bodega (fecha, buy_order, session_id, productos_carrito, monto_total)
        VALUES (%s, %s, %s, %s, %s)
        """
        factura_values = (
            factura_bodega["fecha"],
            factura_bodega["buy_order"],
            factura_bodega["session_id"],
            productos_json,
            factura_bodega["monto_total"],
        )
        cursor.execute(factura_query, factura_values)
        connection.commit()

        cursor.close()
        connection.close()

        print("FacturaBodega guardada exitosamente.")

    except mysql.connector.Error as error:
        print("Error al guardar la FacturaBodega:", error)


# Función para obtener todas las facturas de bodega
def obtener_todas_facturas_bodega():
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        query = "SELECT * FROM factura_bodega"
        cursor.execute(query)

        facturas_data = cursor.fetchall()
        facturas = []

        for factura_data in facturas_data:
            # Deserializar los productos del carrito desde el formato JSON
            productos_carrito = json.loads(factura_data[4])

            # Obtener el precio unitario de cada producto en el carrito
            for producto in productos_carrito:
                producto["precio_unitario"] = producto["precio"]

            factura = FacturaBodega(
                id_factura=factura_data[0],
                fecha=factura_data[1],
                buy_order=factura_data[2],
                session_id=factura_data[3],
                productos_carrito=productos_carrito,
                monto_total=factura_data[5],
            )
            facturas.append(factura)

        cursor.close()
        connection.close()

        return facturas

    except mysql.connector.Error as error:
        print("Error al obtener las facturas de la bodega:", error)


def obtener_usuario_contraseña(email):
    connection = mysql.connector.connect(
        host="localhost", user="root", password="password", database="musicprodb"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM usuario WHERE correo = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        # Crear un diccionario con la contraseña y convertirlo a JSON
        return result[0]
    else:
        return None


def obtener_nombre_usuario(email):
    connection = mysql.connector.connect(
        host="localhost", user="root", password="password", database="musicprodb"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT nombre_completo FROM usuario WHERE correo = %s", (email,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        return result[0]
    else:
        return None


def obtener_tipo_usuario(email):
    connection = mysql.connector.connect(
        host="localhost", user="root", password="password", database="musicprodb"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT tipo_usuario FROM usuario WHERE correo = %s", (email,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        return result[0]
    else:
        return None


def add_usuario(usuario):
    try:
        connection = mysql.connector.connect(
            host="localhost", user="root", password="password", database="musicprodb"
        )
        cursor = connection.cursor()

        query = """
        INSERT INTO usuario (nombre_completo, correo, password, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            usuario.nombre_completo,
            usuario.correo,
            usuario.password,
            usuario.tipo_usuario,
        )
        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        print("Error al agregar un usuario:", error)