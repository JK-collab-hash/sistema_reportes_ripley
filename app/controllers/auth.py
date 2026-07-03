from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.usuario import Usuario


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_texto = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "").strip()

        usuario = None

        # Acceso de demostración, alineado al mockup.
        if usuario_texto.lower() in ["jose.alguay@ripley.pe", "jose", "jose manuel alguay"]:
            usuario = Usuario.query.filter_by(nombre="Jose").first()
        elif usuario_texto.lower() in ["admin", "admin@sistema.pe"]:
            usuario = Usuario.query.filter_by(nombre="Admin").first()
        else:
            usuarios = Usuario.query.all()
            for u in usuarios:
                if usuario_texto.lower() == u.nombre_completo().lower():
                    usuario = u
                    break

        if usuario and usuario.contrasena == contrasena:
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre_completo()
            session["usuario_rol"] = usuario.rol
            return redirect(url_for("reportes.dashboard"))

        flash("Credenciales incorrectas. Usa jose.alguay@ripley.pe / 123456", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
