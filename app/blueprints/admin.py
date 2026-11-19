import os
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.models import db, login_manager, Actividad
from app.forms import ActividadForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def proteger_administracion():
    # Ejercicio 2.1: guardian exclusivo para usuarios con rol monitor.
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.es_monitor:
        abort(403)


@admin_bp.route("/actividad/nueva", methods=["GET", "POST"])
def crear_actividad():
    # Ejercicio 2.3: crea la actividad y prefija el nombre del cartel.
    form = ActividadForm()

    if form.validate_on_submit():
        act = Actividad()
        form.populate_obj(act)

        if form.archivo_imagen.data:
            archivo = form.archivo_imagen.data
            nombre_seguro = secure_filename(archivo.filename)
            nombre_imagen = f"{act.deporte.lower()}_{nombre_seguro}"
            carpeta = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(carpeta, exist_ok=True)
            archivo.save(os.path.join(carpeta, nombre_imagen))
            act.imagen = nombre_imagen
        
        db.session.add(act)
        db.session.commit()
        flash("Actividad creada correctamente.", "exito")
        return redirect(url_for("public.mostrar_actividades"))

    return render_template(
        "actividad_form.html", form=form, titulo="Nueva Actividad Deportiva"
    )
    



@admin_bp.route("/actividad/<int:act_id>/editar", methods=["GET", "POST"])
def editar_actividad(act_id):
    # Ejercicio 2.3: permite editar conservando el nombre propio y sustituir cartel.
    actividad = db.get_or_404(Actividad, act_id)
    form = ActividadForm(obj=actividad)
    form.actividad_actual = actividad

    if form.validate_on_submit():
        imagen_anterior = actividad.imagen
        form.populate_obj(actividad)

        if form.archivo_imagen.data:
            archivo = form.archivo_imagen.data
            nombre_seguro = secure_filename(archivo.filename)
            nombre_imagen = f"{actividad.deporte.lower()}_{nombre_seguro}"
            carpeta = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(carpeta, exist_ok=True)
            archivo.save(os.path.join(carpeta, nombre_imagen))
            actividad.imagen = nombre_imagen

            if imagen_anterior and imagen_anterior != nombre_imagen:
                ruta_anterior = os.path.join(carpeta, imagen_anterior)
                if os.path.exists(ruta_anterior):
                    os.remove(ruta_anterior)

        db.session.commit()
        flash("Actividad editada correctamente.", "exito")
        return redirect(url_for("public.mostrar_actividades"))

    return render_template(
        "actividad_form.html",
        form=form,
        titulo="Editar Actividad",
        actividad=actividad,
    )


@admin_bp.route("/actividad/<int:act_id>/eliminar", methods=["POST"])
def eliminar_actividad(act_id):
    # Ejercicio 2.4: solo elimina actividades con plazas disponibles y limpia su imagen.
    actividad = db.get_or_404(Actividad, act_id)
    if actividad.plazas_libres == 0:
        flash("No se puede eliminar una actividad con el cupo lleno.", "error")
        return redirect(url_for("public.mostrar_actividades"))

    if actividad.imagen:
        ruta_imagen = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            actividad.imagen,
        )
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    db.session.delete(actividad)
    db.session.commit()
    flash("Actividad eliminada correctamente.", "exito")
    return redirect(url_for("public.mostrar_actividades"))
