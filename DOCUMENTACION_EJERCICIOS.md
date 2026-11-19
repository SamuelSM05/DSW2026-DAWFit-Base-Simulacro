# DAW-Fit: ejercicios resueltos y código relacionado

Este documento explica la solución implementada para el examen práctico de
DAW-Fit. Los ejemplos corresponden al código actual del proyecto y muestran
las partes más importantes de cada ejercicio.

## Estructura general

- **Aplicación Flask:** `app/__init__.py`
- **Modelos y autenticación:** `app/models.py`
- **Formularios WTForms:** `app/forms.py`
- **Rutas públicas, cookies y reservas:** `app/blueprints/public.py`
- **Rutas de administración:** `app/blueprints/admin.py`
- **Rutas de usuarios:** `app/blueprints/auth.py`
- **Plantillas:** `app/templates/`

La aplicación utiliza *Blueprints*, SQLAlchemy, Flask-Login, Flask-WTF y
sesiones de Flask.

## Cómo se ejecuta una petición

1. Flask recibe la URL y busca una vista registrada en el Blueprint
   correspondiente.
2. Los decoradores se ejecutan antes de la función: por ejemplo,
   `@login_required` comprueba la sesión y `@admin_bp.before_request` comprueba
   el rol del usuario.
3. La vista obtiene datos de `request`, `session` o la base de datos.
4. En una petición GET normalmente se renderiza una plantilla.
5. En una petición POST se valida el formulario, se modifica la sesión o la
   base de datos y se redirige a otra vista.

Esta última redirección es el patrón **PRG** (*Post/Redirect/Get*). Evita que
el navegador vuelva a enviar los datos si el usuario actualiza la página.

## Elementos de Python, Flask y Jinja que aparecen en el código

- `request.args` contiene los parámetros de una URL GET, mientras que
  `request.form` contiene campos enviados por POST.
- `request.cookies.get(...)` lee una cookie enviada por el navegador.
- `session` es un diccionario asociado al navegador del usuario. En este
  proyecto guarda la lista de identificadores de reservas.
- `render_template` combina una plantilla HTML con variables proporcionadas
  desde la vista.
- `redirect` devuelve una respuesta HTTP que ordena al navegador visitar otra
  URL.
- `url_for("public.mostrar_actividades")` genera la URL usando el nombre de
  la vista, no una ruta escrita manualmente.
- En Jinja, `{{ ... }}` imprime un valor y `{% if ... %}` o
  `{% for ... %}` controla la lógica de la plantilla.
- SQLAlchemy permite construir una consulta sin escribir SQL directamente:
  `Actividad.query.filter(...).all()` devuelve una lista de objetos
  `Actividad`.

## Enunciado de cada ejercicio

### Bloque 1: catálogo público, GET, cookies y errores

#### Ejercicio 1.1: buscador combinado de actividades

Añadir al catálogo un formulario GET con un campo `busqueda` y una casilla
`solo_con_plazas`. El controlador debe leer ambos parámetros con
`request.args.get()`, buscar actividades cuyo nombre contenga el texto
recibido y, cuando se marque la casilla, limitar los resultados a actividades
con `plazas_libres > 0`. Los filtros deben funcionar juntos o por separado.

#### Ejercicio 1.2: cookie de deporte favorito

Guardar el deporte elegido en la cookie `deporte_fav` durante 15 días,
utilizando `make_response()`, `httponly=True` y `samesite="Lax"`. Leer la
cookie al cargar el catálogo y mostrar una insignia solo junto a las
actividades cuyo deporte coincida con ella. La ruta de limpiar preferencia
debe eliminar la cookie con `delete_cookie()`.

#### Ejercicio 1.3: ficha de detalle y error 404

Usar `db.get_or_404()` en la ruta de detalle de una actividad. Registrar un
gestor global `@app.errorhandler(404)` en la factoría y crear una plantilla
`404.html` heredada de `base.html`, con un enlace dinámico para volver al
catálogo.

### Bloque 2: panel de monitores, validadores e imágenes

#### Ejercicio 2.1: guardián de administración y vistas dinámicas

Crear un `@admin_bp.before_request` que envíe al login a los usuarios
anónimos mediante `login_manager.unauthorized()` y lance `abort(403)` para
los usuarios que no sean monitores. Ocultar en las plantillas los enlaces de
crear, editar y eliminar para los usuarios sin permisos.

#### Ejercicio 2.2: validación de `ActividadForm`

Validar que la cuota sea obligatoria y esté entre 5 y 150 euros, que las
plazas sean obligatorias y no negativas, y que la imagen tenga extensión JPG,
JPEG o PNG mediante `FileAllowed`. Crear `validate_nombre()` para impedir
nombres duplicados, permitiendo conservar el nombre de la propia actividad al
editarla.

#### Ejercicio 2.3: creación y edición con prefijo en el cartel

En las rutas de crear y editar, limpiar el nombre del archivo con
`secure_filename()`, anteponer el deporte en minúsculas y guardar el resultado
en `UPLOAD_FOLDER`. Al editar, conservar el nombre original si no se sube una
imagen y eliminar la imagen anterior si se sustituye por otra.

#### Ejercicio 2.4: borrado condicional y limpieza de imagen

La ruta de eliminación debe aceptar solo POST. Si la actividad tiene el cupo
lleno (`plazas_libres == 0`), debe impedir el borrado, mostrar un mensaje
`flash()` de categoría `error` y volver al catálogo. Si tiene plazas libres,
debe borrar primero su imagen del disco y después el registro de la base de
datos.

### Bloque 3: sesiones, inscripción y confirmación

#### Ejercicio 3.1: inscripción sin duplicados y con máximo de tres

Guardar los identificadores de las actividades en
`session["reservas"]`, usando una ruta POST protegida con `@login_required` y
una sesión permanente. Comprobar que haya plazas, que no exista un duplicado y
que la lista tenga menos de tres actividades. Informar con `flash()` si falla
alguna regla y marcar la sesión como modificada al añadir correctamente.

#### Ejercicio 3.2: resumen de reservas y descuento multideporte

Recuperar mediante `.in_()` las actividades cuyos identificadores estén en la
sesión, calcular `total_sin_descuento` y aplicar un descuento del 20 % cuando
el usuario tenga tres actividades. Enviar a `reservas.html` el total final y
el booleano `descuento_aplicado`.

#### Ejercicio 3.3: cancelación individual y confirmación en BD

Añadir una acción POST para eliminar individualmente una reserva con
`.remove()` y notificar el resultado. Crear otra acción POST que recorra las
reservas, reste una plaza a cada actividad, ejecute `db.session.commit()`,
elimine la clave de reservas con `session.pop("reservas", None)` y redirija al
catálogo.

### Bloque 4: registro, criptografía y perfil

#### Ejercicio 4.1: alta de socios mayores de 16 años

Añadir un campo entero `edad` obligatorio y con mínimo 16 en el formulario y
la plantilla de registro. Crear el usuario con rol `socio`, cifrar la
contraseña con `set_password()`, guardarlo en la base de datos y redirigir al
login.

#### Ejercicio 4.2: cambio de contraseña desde el perfil

Definir los campos `password_actual`, `nueva_password` de mínimo seis
caracteres y `confirmar_password` con `EqualTo`. Comprobar la contraseña
actual con `current_user.check_password()`, verificar que la nueva sea
distinta, generar el nuevo hash con `set_password()` y confirmar el cambio.

#### Ejercicio 4.3: limpieza de reservas al cerrar sesión

En la ruta de logout, además de ejecutar `logout_user()`, eliminar la clave
`"reservas"` de la sesión para evitar que otro usuario del mismo navegador
herede las inscripciones pendientes.

---

## Bloque 1: catálogo público, GET, cookies y errores

### Ejercicio 1.1: buscador combinado de actividades

El catálogo debe poder filtrar por nombre, por disponibilidad o por ambos
criterios. El formulario utiliza GET para que los filtros queden representados
en la URL y puedan compartirse o repetirse.

#### Controlador: `app/blueprints/public.py`

```python
@public_bp.route("/actividades")
def mostrar_actividades():
    busqueda = request.args.get("busqueda", "").strip()
    solo_con_plazas = request.args.get("solo_con_plazas")

    actividades = Actividad.query
    if busqueda:
        actividades = actividades.filter(
            Actividad.nombre.ilike(f"%{busqueda}%")
        )
    if solo_con_plazas:
        actividades = actividades.filter(Actividad.plazas_libres > 0)

    return render_template(
        "catalogo.html",
        lista_actividades=actividades.all(),
        busqueda=busqueda,
        solo_con_plazas=bool(solo_con_plazas),
        deporte_fav=request.cookies.get("deporte_fav"),
    )
```

`ilike` permite una búsqueda sin distinguir mayúsculas y minúsculas. Cada
filtro se añade a la consulta solo si se ha solicitado, por lo que ambos
pueden combinarse.

`request.args.get("busqueda", "")` devuelve una cadena vacía si el usuario
todavía no ha enviado el campo. `strip()` elimina espacios sobrantes para que
una búsqueda formada solo por espacios no active el filtro. La casilla HTML
solo se envía cuando está marcada; por eso basta comprobar si
`solo_con_plazas` tiene algún valor.

La consulta se mantiene como objeto `Query` mientras se aplican los filtros.
La llamada final a `.all()` es la que ejecuta la consulta y obtiene los
registros que se entregan a `catalogo.html`.

#### Plantilla: `app/templates/catalogo.html`

```html
<form action="{{ url_for('public.mostrar_actividades') }}" method="get">
    <label for="busqueda">Buscar actividad:</label>
    <input id="busqueda" type="text" name="busqueda"
           value="{{ busqueda }}">

    <label>
        <input type="checkbox" name="solo_con_plazas" value="1"
               {% if solo_con_plazas %}checked{% endif %}>
        Solo con plazas
    </label>

    <button type="submit">Buscar</button>
    <a href="{{ url_for('public.mostrar_actividades') }}">Limpiar</a>
</form>
```

### Ejercicio 1.2: cookie de deporte favorito

La preferencia se guarda en una cookie con duración limitada. La respuesta
debe construirse con `make_response` porque hay que modificar sus cabeceras.

#### Guardar y borrar la cookie: `app/blueprints/public.py`

```python
@public_bp.route("/preferencia/<string:deporte>")
def guardar_preferencia(deporte):
    respuesta = make_response(
        redirect(url_for("public.mostrar_actividades"))
    )
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
    respuesta = make_response(
        redirect(url_for("public.mostrar_actividades"))
    )
    respuesta.delete_cookie("deporte_fav")
    return respuesta
```

La cookie se lee al cargar el catálogo y se pasa a la plantilla. Jinja solo
muestra la insignia cuando el deporte de la actividad coincide con ella:

```html
{% if deporte_fav and act.deporte == deporte_fav %}
    <span class="badge-fav">⭐ Tu deporte favorito</span>
{% endif %}
```

`max_age=timedelta(days=15)` hace que el navegador conserve la cookie durante
15 días. `httponly=True` impide que JavaScript del navegador la lea y
`samesite="Lax"` reduce el envío de la cookie en peticiones externas. La
cookie no se utiliza para autorizar al usuario; únicamente personaliza la
presentación del catálogo.

### Ejercicio 1.3: detalle y error 404 global

`db.get_or_404` busca la actividad por clave primaria y genera un 404 si no
existe:

```python
@public_bp.route("/actividad/<int:act_id>")
def ver_actividad(act_id):
    actividad = db.get_or_404(Actividad, act_id)
    return render_template(
        "actividad_detalle.html",
        actividad=actividad,
    )
```

Si la actividad existe, el objeto se pasa como `actividad` a la plantilla de
detalle. Si no existe, la vista no continúa y Flask ejecuta el manejador
global. El `, 404` del retorno es importante porque hace que la respuesta
tenga realmente el código HTTP 404, aunque se muestre una página HTML.

El manejador global se registra en la factoría de la aplicación:

```python
@app.errorhandler(404)
def recurso_no_encontrado(e):
    return render_template("404.html"), 404
```

La plantilla `app/templates/404.html` hereda de `base.html` y utiliza una
ruta con namespace:

```html
{% extends "base.html" %}

{% block content %}
<h1>404 - Actividad no encontrada</h1>
<p>El recurso solicitado no existe o ya no está disponible.</p>
<a href="{{ url_for('public.mostrar_actividades') }}">
    Volver al listado de actividades
</a>
{% endblock %}
```

---

## Bloque 2: administración, validación y archivos

### Ejercicio 2.1: guardián de administración y vistas dinámicas

El `before_request` del Blueprint se ejecuta antes de cualquier ruta
administrativa. Los usuarios anónimos son enviados al login y los usuarios
autenticados que no son monitores reciben un 403.

`current_user` lo proporciona Flask-Login. La propiedad `is_authenticated`
indica si hay una sesión iniciada y `es_monitor` consulta el rol almacenado en
el modelo `Usuario`. `abort(403)` detiene la vista inmediatamente; no basta
con ocultar botones porque un usuario podría escribir la URL de administración
manualmente.

#### `app/blueprints/admin.py`

```python
@admin_bp.before_request
def proteger_administracion():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.es_monitor:
        abort(403)
```

Los enlaces de administración se ocultan en las plantillas para usuarios que
no tienen el rol adecuado:

```html
{% if current_user.is_authenticated and current_user.es_monitor %}
    <a href="{{ url_for('admin.crear_actividad') }}">
        + Nueva Actividad
    </a>
{% endif %}
```

El mismo patrón se utiliza para los enlaces de editar y el formulario de
eliminar en `catalogo.html`. La ocultación visual no sustituye al guardián:
la protección real está en el servidor.

### Ejercicio 2.2: validación de `ActividadForm`

El formulario valida los datos antes de crear o modificar registros:

```python
class ActividadForm(FlaskForm):
    nombre = StringField(
        "Nombre de la Actividad",
        validators=[
            DataRequired(),
            Length(min=3, max=100),
        ],
    )
    cuota = FloatField(
        "Cuota Mensual (€)",
        validators=[
            DataRequired(),
            NumberRange(min=5.0, max=150.0),
        ],
    )
    plazas_libres = IntegerField(
        "Plazas Libres",
        validators=[
            DataRequired(),
            NumberRange(min=0),
        ],
    )
    archivo_imagen = FileField(
        "Cartel de la Actividad",
        validators=[FileAllowed(["jpg", "jpeg", "png"])],
    )
```

Cada campo combina un tipo de dato con validadores. `DataRequired` rechaza
valores vacíos, `Length` comprueba la longitud, `NumberRange` limita números y
`FileAllowed` revisa la extensión de la imagen. `validate_on_submit()` ejecuta
estas validaciones únicamente cuando la petición es POST y el token CSRF es
correcto.

El nombre debe ser único al crear, pero se permite conservarlo al editar la
misma actividad:

```python
def validate_nombre(self, field):
    actividad_existente = Actividad.query.filter_by(
        nombre=field.data
    ).first()
    actividad_actual = getattr(self, "actividad_actual", None)

    if actividad_existente and (
        actividad_actual is None
        or actividad_existente.id != actividad_actual.id
    ):
        raise ValidationError("Esa actividad ya está registrada.")
```

WTForms detecta automáticamente los métodos que empiezan por
`validate_` y los ejecuta como validadores del campo correspondiente. En la
vista de edición se asigna `form.actividad_actual = actividad`; por eso el
validador puede distinguir entre "el nombre pertenece a otra actividad" y
"el nombre pertenece al registro que estoy editando".

### Ejercicio 2.3: creación y edición con prefijo de imagen

El formulario de la actividad utiliza `multipart/form-data` y contiene el
token CSRF:

```html
<form action="" method="post" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    ...
</form>
```

Al crear una actividad, se limpia el nombre original del archivo, se añade el
deporte y se guarda en `UPLOAD_FOLDER`:

```python
if form.archivo_imagen.data:
    archivo = form.archivo_imagen.data
    nombre_seguro = secure_filename(archivo.filename)
    nombre_imagen = f"{act.deporte.lower()}_{nombre_seguro}"
    carpeta = current_app.config["UPLOAD_FOLDER"]

    os.makedirs(carpeta, exist_ok=True)
    archivo.save(os.path.join(carpeta, nombre_imagen))
    act.imagen = nombre_imagen
```

`secure_filename` elimina rutas y caracteres peligrosos del nombre enviado por
el cliente. `os.makedirs(..., exist_ok=True)` crea la carpeta si todavía no
existe. El archivo se guarda físicamente con `archivo.save(...)`, mientras
que en la base de datos solo se guarda el nombre (`act.imagen`), que después
se utiliza para construir la URL estática.

En la edición se conserva el nombre si no se sube una imagen nueva. Si cambia,
se borra el archivo anterior:

```python
imagen_anterior = actividad.imagen
form.populate_obj(actividad)

if form.archivo_imagen.data:
    archivo = form.archivo_imagen.data
    nombre_seguro = secure_filename(archivo.filename)
    nombre_imagen = f"{actividad.deporte.lower()}_{nombre_seguro}"
    carpeta = current_app.config["UPLOAD_FOLDER"]
    archivo.save(os.path.join(carpeta, nombre_imagen))
    actividad.imagen = nombre_imagen

    if imagen_anterior and imagen_anterior != nombre_imagen:
        ruta_anterior = os.path.join(carpeta, imagen_anterior)
        if os.path.exists(ruta_anterior):
            os.remove(ruta_anterior)
```

### Ejercicio 2.4: borrado condicional y limpieza

La ruta solo acepta POST. Una actividad sin plazas disponibles no se puede
eliminar:

```python
@admin_bp.route("/actividad/<int:act_id>/eliminar", methods=["POST"])
def eliminar_actividad(act_id):
    actividad = db.get_or_404(Actividad, act_id)

    if actividad.plazas_libres == 0:
        flash(
            "No se puede eliminar una actividad con el cupo lleno.",
            "error",
        )
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
```

El orden de las operaciones evita dejar archivos huérfanos: primero se
comprueba la regla de negocio, luego se elimina la imagen si existe y por
último se borra el registro. `db.session.commit()` hace permanentes los
cambios. Si el cupo es cero, se sale antes de tocar tanto el archivo como la
base de datos.

---

## Bloque 3: sesiones, reservas y confirmación

### Ejercicio 3.1: inscripción sin duplicados y con máximo de tres

La ruta exige autenticación y POST. La lista se inicializa dentro de la
sesión, se marca como permanente y se valida antes de modificarla:

```python
@public_bp.route(
    "/reservas/apuntar/<int:act_id>",
    methods=["POST"],
)
@login_required
def apuntar_actividad(act_id):
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
```

`setdefault` devuelve la lista existente o crea una lista vacía si es la
primera reserva. La comprobación de plazas se realiza consultando la
actividad, la de duplicados con `in` y el límite con `len`. El `else` solo se
alcanza cuando las tres reglas se cumplen. `session.modified = True` indica a
Flask que debe guardar la nueva versión de la sesión.

Si una regla falla, la lista no se modifica y se informa del motivo.

### Ejercicio 3.2: resumen y descuento multideporte

La lista de identificadores se convierte en actividades mediante `.in_()`.
Cuando contiene exactamente tres actividades se aplica un 20 % de descuento:

```python
@public_bp.route("/reservas")
@login_required
def ver_reservas():
    reservas = session.get("reservas", [])
    actividades = []

    if reservas:
        actividades = Actividad.query.filter(
            Actividad.id.in_(reservas)
        ).all()

    total_sin_descuento = sum(
        actividad.cuota for actividad in actividades
    )
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
```

`.in_(reservas)` equivale a buscar filas cuyo `id` esté dentro de la lista.
El total se calcula con la cuota almacenada en cada actividad, no con datos
enviados desde el navegador. El descuento se representa con un booleano para
que la plantilla decida si debe mostrar el mensaje explicativo.

La plantilla muestra el aviso solo cuando `descuento_aplicado` es verdadero:

```html
{% if descuento_aplicado %}
    <p>
        ¡Descuento Multideporte (3 actividades - 20 %) aplicado!
    </p>
{% endif %}
<h3>Cuota Total a Pagar: {{ "%.2f"|format(total_final) }} €/mes</h3>
```

### Ejercicio 3.3: cancelación y confirmación

#### Cancelación individual

Cada actividad tiene un formulario POST propio:

```html
<form action="{{ url_for('public.cancelar_reserva', act_id=act.id) }}"
      method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button type="submit">Cancelar</button>
</form>
```

La ruta elimina solo el identificador seleccionado:

```python
@public_bp.route("/reservas/cancelar/<int:act_id>", methods=["POST"])
@login_required
def cancelar_reserva(act_id):
    reservas = session.get("reservas", [])
    if act_id in reservas:
        reservas.remove(act_id)
        session["reservas"] = reservas
        session.modified = True
        flash("Reserva cancelada.", "exito")
    else:
        flash("La actividad no estaba en tus reservas.", "error")

    return redirect(url_for("public.ver_reservas"))
```

#### Confirmación en la base de datos

Al confirmar, se recuperan las actividades, se descuenta una plaza, se
confirma la transacción y se vacía la lista de sesión:

```python
@public_bp.route("/reservas/confirmar", methods=["POST"])
@login_required
def confirmar_reservas():
    reservas = session.get("reservas", [])
    if reservas:
        actividades = Actividad.query.filter(
            Actividad.id.in_(reservas)
        ).all()
        for actividad in actividades:
            if actividad.plazas_libres > 0:
                actividad.plazas_libres -= 1
        db.session.commit()

    session.pop("reservas", None)
    session.modified = True
    flash("Reservas confirmadas correctamente.", "exito")
    return redirect(url_for("public.mostrar_actividades"))
```

La condición `plazas_libres > 0` evita que el contador sea negativo si una
actividad se ha quedado sin plazas entre la reserva y la confirmación. La
sesión se limpia incluso cuando no hay reservas, por lo que la operación
siempre deja al usuario en un estado coherente.

---

## Bloque 4: socios, contraseñas y perfil

### Ejercicio 4.1: alta de socios mayores de 16 años

El campo `edad` se define como entero y se valida con `NumberRange`:

```python
edad = IntegerField(
    "Edad",
    validators=[
        DataRequired(),
        NumberRange(min=16),
    ],
)
```

La plantilla lo muestra y presenta sus errores:

```html
{{ form.edad.label }}<br>
{{ form.edad() }}<br>
{% for error in form.edad.errors %}
    <span style="color: red;">{{ error }}</span>
{% endfor %}
```

La ruta crea siempre un usuario con rol `socio` y nunca almacena la contraseña
en texto plano:

```python
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
```

`form.validate_on_submit()` también ejecuta los validadores personalizados de
usuario y correo, que evitan duplicados. `set_password` transforma la clave en
un hash antes de llamar a `commit`; posteriormente el usuario puede iniciar
sesión con la contraseña original, pero la base de datos no la almacena.

### Ejercicio 4.2: cambio de contraseña

El formulario contiene la contraseña actual, la nueva y su confirmación:

```python
class CambiarPasswordForm(FlaskForm):
    password_actual = PasswordField(
        "Contraseña actual",
        validators=[DataRequired()],
    )
    nueva_password = PasswordField(
        "Nueva contraseña",
        validators=[
            DataRequired(),
            Length(min=6),
        ],
    )
    confirmar_password = PasswordField(
        "Confirmar nueva contraseña",
        validators=[
            DataRequired(),
            EqualTo("nueva_password"),
        ],
    )
```

La vista comprueba la contraseña anterior y evita guardar la misma contraseña:

```python
@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password_actual.data):
            flash("La contraseña actual no es correcta.", "error")
        elif form.nueva_password.data == form.password_actual.data:
            flash(
                "La nueva contraseña debe ser diferente a la actual.",
                "error",
            )
        else:
            current_user.set_password(form.nueva_password.data)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "exito")
            return redirect(url_for("auth.perfil"))

    return render_template("perfil.html", form=form)
```

`current_user` representa al usuario autenticado, de modo que no se recibe
ningún identificador desde el formulario. La comparación de la contraseña se
hace con `check_password`, que compara el hash de forma segura. Solo después
de superar todas las comprobaciones se genera el nuevo hash y se confirma el
cambio.

El modelo genera y comprueba el hash con Werkzeug:

```python
def set_password(self, password: str) -> None:
    self.password_hash = generate_password_hash(password)

def check_password(self, password: str) -> bool:
    return check_password_hash(self.password_hash, password)
```

### Ejercicio 4.3: limpieza de reservas al cerrar sesión

La sesión se limpia antes de cerrar la sesión de Flask-Login, evitando que el
siguiente usuario del mismo navegador herede reservas:

```python
@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("reservas", None)
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("public.mostrar_actividades"))
```

`session.pop("reservas", None)` elimina la clave si existe y no produce error
si no había reservas. `logout_user()` elimina la identidad autenticada; ambas
acciones son necesarias porque la identidad y las reservas son datos
independientes dentro de la sesión.

---

## Rúbrica transversal

### Namespaces de Blueprint

Las rutas se generan con el nombre del Blueprint y de la vista:

```python
url_for("public.mostrar_actividades")
url_for("auth.login")
url_for("admin.crear_actividad")
```

Esto evita rutas escritas a mano y mantiene las URL coherentes aunque cambien
los prefijos de los módulos.

### Patrón PRG y mensajes flash

Las operaciones POST modifican la sesión o la base de datos, muestran un
mensaje y terminan con una redirección. Así se evita reenviar el formulario al
actualizar la página:

```python
flash("Actividad añadida a tus reservas.", "exito")
return redirect(url_for("public.mostrar_actividades"))
```

Las categorías usadas por la aplicación son `exito`, `error` e `info`, y
`base.html` las presenta mediante los mensajes flash de Flask.

### CSRF y métodos HTTP

Los formularios Flask incluyen:

```html
{{ form.hidden_tag() }}
```

Los formularios manuales que modifican datos incluyen el token explícito:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

La protección global se activa en `app/__init__.py`:

```python
csrf = CSRFProtect()
csrf.init_app(app)
```

Las operaciones que modifican sesión, base de datos o archivos usan POST:

- apuntarse a una actividad;
- cancelar o confirmar reservas;
- crear, editar o eliminar actividades;
- enviar formularios de registro y contraseña.

La subida de imágenes utiliza además:

```html
enctype="multipart/form-data"
```

## Comprobaciones manuales recomendadas

1. Abrir `/actividades` y probar búsqueda por nombre y la casilla de plazas.
2. Elegir un deporte favorito y comprobar la insignia; después quitar la cookie.
3. Abrir un identificador de actividad inexistente y verificar el 404.
4. Entrar como socio y comprobar que no aparecen las acciones de monitor.
5. Entrar como monitor y probar crear, editar y eliminar actividades.
6. Intentar eliminar una actividad con `plazas_libres == 0`.
7. Reservar actividades repetidas, llenas y más de tres.
8. Cancelar una reserva y confirmar el descuento al tener tres.
9. Registrar un usuario menor de 16 años y otro válido.
10. Cambiar la contraseña con datos incorrectos y correctos.
11. Cerrar sesión y comprobar que las reservas desaparecen.
