from datetime import timedelta

from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from app.models import db, Actividad


public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return redirect(url_for("public.mostrar_actividades"))


@public_bp.route("/actividades")
def mostrar_actividades():
    # Ejercicio 1.1: buscador combinado por nombre y disponibilidad.
    busqueda = request.args.get("busqueda", "").strip()
    solo_con_plazas = request.args.get("solo_con_plazas")

    actividades = Actividad.query
    if busqueda:
        actividades = actividades.filter(Actividad.nombre.ilike(f"%{busqueda}%"))
    if solo_con_plazas:
        actividades = actividades.filter(Actividad.plazas_libres > 0)

    actividades = actividades.all()
    deporte_fav = request.cookies.get("deporte_fav")

    return render_template(
        "catalogo.html",
        lista_actividades=actividades,
        deporte_fav=deporte_fav,
        busqueda=busqueda,
        solo_con_plazas=bool(solo_con_plazas),
    )


@public_bp.route("/actividad/<int:act_id>")
def ver_actividad(act_id):
    # Ejercicio 1.3: db.get_or_404 devuelve la pagina 404 si no existe.
    actividad = db.get_or_404(Actividad, act_id)
    return render_template("actividad_detalle.html", actividad=actividad)


@public_bp.route("/preferencia/<string:deporte>")
def guardar_preferencia(deporte):
    # Ejercicio 1.2: guarda el deporte favorito durante 15 dias.
    respuesta = make_response(redirect(url_for("public.mostrar_actividades")))
    respuesta.set_cookie(
        "deporte_fav",
        deporte,
        max_age=timedelta(days=15),
        httponly=True,
        samesite="Lax",
    )
    return respuesta


@public_bp.route("/limpiar-preferencia")
def limpiar_preferencia():
    # Ejercicio 1.2: elimina la cookie de deporte favorito.
    respuesta = make_response(redirect(url_for("public.mostrar_actividades")))
    respuesta.delete_cookie("deporte_fav")
    return respuesta


@public_bp.route("/reservas/apuntar/<int:act_id>", methods=["POST"])
@login_required
def apuntar_actividad(act_id):
    # Ejercicio 3.1: controla cupo, duplicados y limite de tres reservas.
    actividad = db.get_or_404(Actividad, act_id)
    reservas = session.setdefault("reservas", [])
    session.permanent = True

    if actividad.plazas_libres <= 0:
        flash("Esta actividad no tiene plazas libres.", "error")
    elif act_id in reservas:
        flash("Ya tienes esta actividad entre tus reservas.", "error")
    elif len(reservas) >= 3:
        flash("No puedes reservar mas de 3 actividades.", "error")
    else:
        reservas.append(act_id)
        session["reservas"] = reservas
        session.modified = True
        flash("Actividad añadida a tus reservas.", "exito")
    return redirect(url_for("public.mostrar_actividades"))


@public_bp.route("/reservas")
@login_required
def ver_reservas():
    # Ejercicio 3.2: consulta las reservas y calcula el descuento multideporte.
    reservas = session.get("reservas", [])
    actividades = []
    if reservas:
        actividades = Actividad.query.filter(Actividad.id.in_(reservas)).all()

    total_sin_descuento = sum(actividad.cuota for actividad in actividades)
    descuento_aplicado = len(reservas) == 3
    total_final = (
        total_sin_descuento * 0.80
        if descuento_aplicado
        else total_sin_descuento
    )
    return render_template(
        "reservas.html",
        actividades=actividades,
        total_sin_descuento=total_sin_descuento,
        descuento_aplicado=descuento_aplicado,
        total_final=total_final,
    )


@public_bp.route("/reservas/cancelar/<int:act_id>", methods=["POST"])
@login_required
def cancelar_reserva(act_id):
    # Ejercicio 3.3A: cancela solamente la reserva indicada.
    reservas = session.get("reservas", [])
    if act_id in reservas:
        reservas.remove(act_id)
        session["reservas"] = reservas
        session.modified = True
        flash("Reserva cancelada.", "exito")
    else:
        flash("La actividad no estaba en tus reservas.", "error")
    return redirect(url_for("public.ver_reservas"))


@public_bp.route("/reservas/confirmar", methods=["POST"])
@login_required
def confirmar_reservas():
    # Ejercicio 3.3B: confirma las reservas y descuenta las plazas.
    reservas = session.get("reservas", [])
    if reservas:
        actividades = Actividad.query.filter(Actividad.id.in_(reservas)).all()
        for actividad in actividades:
            if actividad.plazas_libres > 0:
                actividad.plazas_libres -= 1
        db.session.commit()
    session.pop("reservas", None)
    session.modified = True
    flash("Reservas confirmadas correctamente.", "exito")
    return redirect(url_for("public.mostrar_actividades"))
