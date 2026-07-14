from flask import Blueprint, render_template, request
from app.controllers.reportes import login_required
from app.services.ml_service import obtener_modelo_ml, predecir, CATEGORIAS_ML, ROTACIONES_ML, TIPOS_CAMION_ML

ml_bp = Blueprint("ml", __name__, url_prefix="/ml")

@ml_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard_ml():
    obj = obtener_modelo_ml()
    resultado = None
    datos_ingresados = None

    if request.method == "POST":
        datos_ingresados = {
            "categoria": request.form.get("categoria"),
            "camion": request.form.get("camion"),
            "cantidad_total": int(request.form.get("cantidad_total", 0)),
            "numero_productos": int(request.form.get("numero_productos", 1)),
            "stock_estimado": int(request.form.get("stock_estimado", 0)),
            "stock_minimo": int(request.form.get("stock_minimo", 0)),
            "demanda_semanal": int(request.form.get("demanda_semanal", 0)),
            "unidades_transito": int(request.form.get("unidades_transito", 0)),
            "tiempo_reposicion_dias": int(request.form.get("tiempo_reposicion_dias", 0)),
            "dias_sin_reposicion": int(request.form.get("dias_sin_reposicion", 0)),
            "tiene_incidencia": int(request.form.get("tiene_incidencia", 0)),
            "rotacion_producto": request.form.get("rotacion_producto"),
        }
        resultado = predecir(datos_ingresados)

    return render_template(
        "ml_dashboard.html",
        dataset=obj["dataset"],
        metricas=obj["metricas"],
        importancia=obj["importancia"],
        total_anomalias=obj.get("total_anomalias", 0),
        total_clusters=obj.get("total_clusters", 0),
        resultado=resultado,
        datos_ingresados=datos_ingresados,
        categorias=CATEGORIAS_ML,
        camiones=TIPOS_CAMION_ML,
        rotaciones=ROTACIONES_ML,
    )