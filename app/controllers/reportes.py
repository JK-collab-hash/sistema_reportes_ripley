from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models.usuario import Usuario
from app.models.camion import Camion
from app.models.categoria import Categoria
from app.models.reporte import Reporte, DetalleReporte
from app.services.ml_service import predecir_riesgo_desde_reporte


reportes_bp = Blueprint("reportes", __name__)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper


def generar_codigo_reporte():
    year = datetime.now().year
    total = Reporte.query.count() + 1
    return f"REP-{year}-{total:03d}"


@reportes_bp.route("/dashboard")
@login_required
def dashboard():
    busqueda = request.args.get("q", "").strip()
    query = Reporte.query.order_by(Reporte.id.desc())

    reportes = query.all()
    if busqueda:
        reportes = [
            r for r in reportes
            if busqueda.lower() in r.codigo.lower()
            or busqueda.lower() in r.camion.nombre.lower()
            or any(busqueda.lower() in d.nombre_producto.lower() for d in r.detalles)
        ]

    total_productos = sum(len(r.detalles) for r in Reporte.query.all())
    return render_template(
        "dashboard.html",
        reportes=reportes,
        total_reportes=Reporte.query.count(),
        total_productos=total_productos,
        busqueda=busqueda
    )


@reportes_bp.route("/reportes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_reporte():
    camiones = Camion.query.filter_by(activo=True).all()
    categorias = Categoria.query.all()

    if request.method == "POST":
        camion_id = request.form.get("camion_id")
        comentarios = request.form.get("comentarios", "").strip()
        incidencias = request.form.get("incidencias", "").strip()
        nombres = request.form.getlist("nombre_producto[]")
        cantidades = request.form.getlist("cantidad[]")
        categoria_ids = request.form.getlist("categoria_id[]")
        observaciones = request.form.getlist("observacion[]")

        errores = []
        if not camion_id:
            errores.append("Camión")

        detalles_validos = []
        for i, nombre in enumerate(nombres):
            nombre = nombre.strip()
            cantidad = cantidades[i] if i < len(cantidades) else ""
            categoria_id = categoria_ids[i] if i < len(categoria_ids) else ""
            observacion = observaciones[i] if i < len(observaciones) else ""

            if nombre or cantidad or categoria_id:
                if not nombre:
                    errores.append("Producto")
                if not cantidad:
                    errores.append("Cantidad del producto")
                if not categoria_id:
                    errores.append("Tipo de producto")
                try:
                    cantidad_int = int(cantidad)
                    if cantidad_int <= 0:
                        errores.append("Cantidad mayor a cero")
                except Exception:
                    cantidad_int = 0
                    errores.append("Cantidad válida")

                if nombre and cantidad_int > 0 and categoria_id:
                    detalles_validos.append((categoria_id, nombre, cantidad_int, observacion))

        if not detalles_validos:
            errores.append("Al menos un producto")

        if errores:
            flash("Faltan datos obligatorios: " + ", ".join(sorted(set(errores))), "error")
            return render_template(
                "nuevo_reporte.html",
                camiones=camiones,
                categorias=categorias,
                codigo=generar_codigo_reporte(),
                form=request.form,
                errores=sorted(set(errores))
            )

        reporte = Reporte(
            codigo=generar_codigo_reporte(),
            camion_id=int(camion_id),
            usuario_id=session["usuario_id"],
            comentarios=comentarios,
            incidencias=incidencias
        )
        db.session.add(reporte)
        db.session.commit()

        for categoria_id, nombre, cantidad, observacion in detalles_validos:
            detalle = DetalleReporte(
                reporte_id=reporte.id,
                categoria_id=int(categoria_id),
                nombre_producto=nombre,
                cantidad=cantidad,
                observacion=observacion
            )
            db.session.add(detalle)

        db.session.commit()
        flash("Reporte guardado correctamente. El registro queda disponible en modo lectura.", "success")
        return redirect(url_for("reportes.ver_reporte", reporte_id=reporte.id))

    return render_template(
        "nuevo_reporte.html",
        camiones=camiones,
        categorias=categorias,
        codigo=generar_codigo_reporte(),
        form=None,
        errores=[]
    )


@reportes_bp.route("/reportes/<int:reporte_id>")
@login_required
def ver_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    prediccion_ml = predecir_riesgo_desde_reporte(reporte)
    return render_template("ver_reporte.html", reporte=reporte, prediccion_ml=prediccion_ml)
