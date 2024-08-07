import functools
from ..db import get_db, desconectar
import psycopg2
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from ..utils import allowed_file  # Importar allowed_fi le desde utils.py

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        img = request.files['img'] if 'img' in request.files else None
        nombre = request.form['nombre']
        ap_pat = request.form['ap_pat']
        ap_mat = request.form['ap_mat']
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        rol = request.form['rol']
        f_nacimiento = request.form['f_nacimiento']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        
        conn, cursor = get_db()
        error = None
        img_url = None

        if not usuario:
            error = 'El usuario es requerido.'
        elif not contraseña:
            error = 'La contraseña es requerida.'

        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
                os.makedirs(current_app.config["UPLOAD_FOLDER"])
            img.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            img_url = url_for("static", filename="uploads/" + filename)
        else:
            error = 'Formato de imagen no permitido.'

        if error is None:
            try:
                cursor.execute(
                    """INSERT INTO user (img, nombre, ap_pat, ap_mat, usuario, contraseña, rol, f_nacimiento, telefono, direccion) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (img_url, nombre, ap_pat, ap_mat, usuario, generate_password_hash(contraseña), rol, f_nacimiento, telefono, direccion),
                )
                conn.commit()
            except psycopg2.IntegrityError:
                error = f"El usuario {usuario} ya está registrado."
                flash(error)
            else:
                return redirect(url_for("auth.login"))

        if error:
            flash(error)

        cursor.close()  # Cerrar el cursor
        desconectar(conn)  # Desconectar la conexión

    return render_template('auth/register.html')




@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        conn, cursor = get_db()
        error = None

        cursor.execute(
            'SELECT * FROM user WHERE usuario = %s', (usuario,)
        )
        user = cursor.fetchone()

        if user is None:
            error = 'Usuario incorrecto.'
        elif not check_password_hash(user[5], contraseña):  
            # Asumiendo que la contraseña está en la sexta columna
            error = 'Contraseña incorrecta.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]  
            # Asumiendo que el ID del usuario está en la primera columna
            return redirect(url_for('index'))

        flash(error)
        cursor.close()  # Cerrar el cursor
        desconectar(conn)  # Desconectar la conexión

    return render_template('auth/login.html')

