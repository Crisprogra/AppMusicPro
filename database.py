import mysql.connector
from models import Producto,Usuario,TipoUsuario



def create_table_tipo_usuario():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
        )
        cursor = connection.cursor()

        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tipo_usuario (
                    id_tipo_usuario INT PRIMARY KEY,
                    tipo_usuario VARCHAR(255)
                )
            ''')
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
        )
        cursor = connection.cursor()

        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuario (
                    id_usuario INT PRIMARY KEY,
                    nombre_completo VARCHAR(255),
                    correo VARCHAR(255),
                    password VARCHAR(255),
                    tipo_usuario INT,
                    FOREIGN KEY (tipo_usuario) REFERENCES tipo_usuario(id_tipo_usuario)
                )
            ''')
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
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
            producto.imagen_producto
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
        )
        cursor = connection.cursor()

        query = "SELECT * FROM productos"
        cursor.execute(query)

        productos = []
        for (id_producto, nombre_producto, marca_producto, color_producto, precio_producto, imagen_producto) in cursor:
            producto = Producto(id_producto, nombre_producto, marca_producto, color_producto, precio_producto,
                                imagen_producto)
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
        )
        cursor = connection.cursor()

        select_query = '''
            SELECT * FROM productos WHERE id_producto = %s
        '''

        cursor.execute(select_query, (id_producto,))
        producto_data = cursor.fetchone()

        cursor.close()
        connection.close()

        if producto_data:
            producto = Producto(*producto_data)  # Crear una instancia de Producto con los valores obtenidos
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
        )
        cursor = connection.cursor()

        update_query = '''
            UPDATE productos SET nombre_producto = %s, marca_producto = %s, color_producto = %s, precio_producto = %s, imagen_producto = %s
            WHERE id_producto = %s
        '''

        data = (
            producto.nombre_producto,
            producto.marca_producto,
            producto.color_producto,
            producto.precio_producto,
            producto.imagen_producto,
            id_producto
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
            host="localhost",
            user="root",
            password="password",
            database="musicprodb"
        )
        cursor = connection.cursor()

        delete_query = '''
            DELETE FROM productos WHERE id_producto = %s
        '''

        cursor.execute(delete_query, (id_producto,))
        connection.commit()

        cursor.close()
        connection.close()
    except mysql.connector.Error as error:
        print("Error al eliminar el producto:", error)
