from app import db

class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    creado_en = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
