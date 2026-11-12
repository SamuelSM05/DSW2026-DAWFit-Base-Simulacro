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


@admin_bp.route("/actividad/nueva", methods=["GET", "POST"])
def crear_actividad():
    form = ActividadForm()

    if form.validate_on_submit():
        act = Actividad()
        form.populate_obj(act)
        
        if form.archivo_imagen.data:
            archivo = form.archivo_imagen.data
            nombre_seguro = secure_filename(archivo.filename)
            carpeta = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(carpeta, exist_ok=True)
            archivo.save(os.path.join(carpeta, nombre_seguro))
            act.imagen = nombre_seguro
        
        db.session.add(act)
        db.session.commit()
        flash("Actividad creada correctamente")
        return redirect(url_for("admin.crear_actividad"))

    return render_template(
        "actividad_form.html", form=form, titulo="Nueva Actividad Deportiva"
    )
    



@admin_bp.route("/actividad/<int:act_id>/editar", methods=["GET", "POST"])
def editar_actividad(act_id):
    actividad = db.get_or_404(Actividad, act_id)
    form = ActividadForm(obj=actividad)

    return render_template(
        "actividad_form.html",
        form=form,
        titulo="Editar Actividad",
        actividad=actividad,
    )


@admin_bp.route("/actividad/<int:act_id>/eliminar", methods=["POST"])
def eliminar_actividad(act_id):
    flash("Eliminación pendiente de implementar.", "info")
    return redirect(url_for("public.mostrar_actividades"))
