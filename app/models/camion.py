from app import db

class Camion(db.Model):
    __tablename__ = "camiones"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    conductor = db.Column(db.String(200))
    marca = db.Column(db.String(100))
    activo = db.Column(db.Boolean, nullable=False, default=True)
