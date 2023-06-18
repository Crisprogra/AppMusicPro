# Clase Producto
class Producto:
    def __init__(self, id_producto, nombre_producto, marca_producto, color_producto, precio_producto, imagen_producto):
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.marca_producto = marca_producto
        self.color_producto = color_producto
        self.precio_producto = precio_producto
        self.imagen_producto = imagen_producto


class Usuario:
    def __init__(self, id_usuario, nombre_completo, correo, password, tipo_usuario):
        self.id_usuario = id_usuario
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.password = password
        self.tipo_usuario = tipo_usuario

class TipoUsuario:
    def __init__(self, id_tipo_usuario, tipo_usuario):
        self.id_tipo_usuario = id_tipo_usuario
        self.tipo_usuario = tipo_usuario
