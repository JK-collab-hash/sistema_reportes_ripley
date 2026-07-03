from app import db

class Reporte(db.Model):
    __tablename__ = "reportes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    camion_id = db.Column(db.Integer, db.ForeignKey("camiones.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    comentarios = db.Column(db.Text)
    incidencias = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    camion = db.relationship("Camion", backref="reportes")
    usuario = db.relationship("Usuario", backref="reportes")
    detalles = db.relationship("DetalleReporte", backref="reporte", cascade="all, delete-orphan")

    def cantidad_total(self):
        return sum(detalle.cantidad for detalle in self.detalles)

class DetalleReporte(db.Model):
    __tablename__ = "detalle_reporte"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reporte_id = db.Column(db.Integer, db.ForeignKey("reportes.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    nombre_producto = db.Column(db.String(300), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    observacion = db.Column(db.Text)

    categoria = db.relationship("Categoria", backref="detalles")
