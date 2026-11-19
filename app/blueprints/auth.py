from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.models import db, Usuario
from app.forms import LoginForm, RegistroForm, CambiarPasswordForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Ruta de Login 100 % funcional para pruebas independientes."""
    if current_user.is_authenticated:
        return redirect(url_for("public.mostrar_actividades"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember.data)
            flash(f"¡Hola de nuevo, {usuario.username}!", "exito")

            siguiente_pagina = request.args.get("next")
            if siguiente_pagina and siguiente_pagina.startswith("/"):
                return redirect(siguiente_pagina)
            return redirect(url_for("public.mostrar_actividades"))
        else:
            flash("Correo electrónico o contraseña incorrectos.", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    # Ejercicio 4.1: registra al socio con edad y contraseña cifrada.
    if current_user.is_authenticated:
        return redirect(url_for("public.mostrar_actividades"))

    form = RegistroForm()
    if form.validate_on_submit():
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            edad=form.edad.data,
            rol="socio",
        )
        usuario.set_password(form.password.data)
        db.session.add(usuario)
        db.session.commit()
        flash("Registro completado. Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("auth.login"))

    return render_template("registro.html", form=form)


@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    # Ejercicio 4.2: valida y cambia la contraseña del usuario autenticado.
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password_actual.data):
            flash("La contraseña actual no es correcta.", "error")
        elif form.nueva_password.data == form.password_actual.data:
            flash("La nueva contraseña debe ser diferente a la actual.", "error")
        else:
            current_user.set_password(form.nueva_password.data)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "exito")
            return redirect(url_for("auth.perfil"))

    return render_template("perfil.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    # Ejercicio 4.3: evita que las reservas pasen al siguiente usuario.
    session.pop("reservas", None)
    logout_user()

    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("public.mostrar_actividades"))
