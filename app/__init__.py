from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.controllers.auth import auth_bp
    from app.controllers.reportes import reportes_bp
    from app.controllers.ml import ml_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(ml_bp)

    with app.app_context():
        from app.models.usuario import Usuario
        from app.models.camion import Camion
        from app.models.categoria import Categoria
        from app.models.reporte import Reporte, DetalleReporte

        db.create_all()
        seed_data()

    return app


def seed_data():
    from app.models.usuario import Usuario
    from app.models.camion import Camion
    from app.models.categoria import Categoria
    from app.models.reporte import Reporte, DetalleReporte

    if Usuario.query.count() == 0:
        admin = Usuario(
            nombre="Admin",
            apellido_p="Sistema",
            apellido_m="",
            contrasena="admin123",
            rol="admin"
        )
        jose = Usuario(
            nombre="Jose",
            apellido_p="Manuel",
            apellido_m="Alguay",
            contrasena="123456",
            rol="garita"
        )
        db.session.add_all([admin, jose])
        db.session.commit()

    if Categoria.query.count() == 0:
        admin = Usuario.query.first()
        categorias = [
            Categoria(nombre="Ropa", creado_por=admin.id),
            Categoria(nombre="Electrodoméstico", creado_por=admin.id),
            Categoria(nombre="Tecnología", creado_por=admin.id),
            Categoria(nombre="Alimentos", creado_por=admin.id),
            Categoria(nombre="Muebles", creado_por=admin.id),
        ]
        db.session.add_all(categorias)
        db.session.commit()

    if Camion.query.count() == 0:
        camiones = [
            Camion(placa="ABC-123", nombre="Camión 01", conductor="Juan Pérez", marca="Volvo"),
            Camion(placa="DEF-456", nombre="Camión 03", conductor="Luis Ramos", marca="Mercedes-Benz"),
            Camion(placa="GHI-789", nombre="Camión 05", conductor="Pedro Salas", marca="Scania"),
            Camion(placa="JKL-321", nombre="Camión 06", conductor="Carlos Vega", marca="Volvo"),
        ]
        db.session.add_all(camiones)
        db.session.commit()

    if Reporte.query.count() == 0:
        usuario = Usuario.query.filter_by(nombre="Jose").first() or Usuario.query.first()
        camion1 = Camion.query.filter_by(nombre="Camión 01").first()
        camion3 = Camion.query.filter_by(nombre="Camión 03").first()
        camion5 = Camion.query.filter_by(nombre="Camión 05").first()
        ropa = Categoria.query.filter_by(nombre="Ropa").first()
        electro = Categoria.query.filter_by(nombre="Electrodoméstico").first()
        muebles = Categoria.query.filter_by(nombre="Muebles").first()

        reportes_demo = [
            ("REP-2026-001", camion1, "Carga verificada sin incidencias.", [(ropa, "Polos de algodón", 30)]),
            ("REP-2026-002", camion3, "Ingreso validado por garita.", [(electro, "Licuadoras", 12)]),
            ("REP-2026-003", camion5, "Mercadería mixta registrada.", [(muebles, "Artículos mixtos", 18)]),
        ]

        for codigo, camion, comentario, detalles in reportes_demo:
            reporte = Reporte(codigo=codigo, camion_id=camion.id, usuario_id=usuario.id, comentarios=comentario, incidencias="")
            db.session.add(reporte)
            db.session.commit()
            for categoria, producto, cantidad in detalles:
                db.session.add(DetalleReporte(
                    reporte_id=reporte.id,
                    categoria_id=categoria.id,
                    nombre_producto=producto,
                    cantidad=cantidad,
                    observacion=""
                ))
            db.session.commit()
