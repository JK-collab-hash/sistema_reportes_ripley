from app import db

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(200), nullable=False)
    apellido_p = db.Column(db.String(200), nullable=False)
    apellido_m = db.Column(db.String(200), nullable=False, default="")
    contrasena = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="garita")
    creado_en = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_p} {self.apellido_m}".strip()
