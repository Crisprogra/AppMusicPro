# Clase Producto
class Producto:
    def __init__(
        self,
        id_producto,
        nombre_producto,
        marca_producto,
        color_producto,
        precio_producto,
        imagen_producto,
    ):
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.marca_producto = marca_producto
        self.color_producto = color_producto
        self.precio_producto = precio_producto
        self.imagen_producto = imagen_producto


class ProductoAgregado:
    def __init__(
        self,
        nombre_producto,
        marca_producto,
        color_producto,
        precio_producto,
        imagen_producto,
    ):
        self.nombre_producto = nombre_producto
        self.marca_producto = marca_producto
        self.color_producto = color_producto
        self.precio_producto = precio_producto
        self.imagen_producto = imagen_producto


class Usuario:
    def __init__(self, nombre_completo, correo, password, tipo_usuario):
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.password = password
        self.tipo_usuario = tipo_usuario


class TipoUsuario:
    def __init__(self, id_tipo_usuario, tipo_usuario):
        self.id_tipo_usuario = id_tipo_usuario
        self.tipo_usuario = tipo_usuario


class FacturaContador:
    def __init__(
        self, id_factura, buy_order, session_id, monto_total, fecha, productos_carrito
    ):
        self.id_factura = id_factura
        self.buy_order = buy_order
        self.session_id = session_id
        self.monto_total = monto_total
        self.fecha = fecha
        self.productos_carrito = productos_carrito


class FacturaBodega:
    def __init__(
        self, id_factura, buy_order, session_id, monto_total, fecha, productos_carrito
    ):
        self.id_factura = id_factura
        self.buy_order = buy_order
        self.session_id = session_id
        self.monto_total = monto_total
        self.fecha = fecha
        self.productos_carrito = productos_carrito
