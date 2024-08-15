import os
import psycopg2
from flask import Flask, redirect, render_template, request, url_for, flash, get_flashed_messages, session, jsonify, make_response, send_file
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import forms
from forms import LoginForm
from wtforms.fields import PasswordField, StringField, SubmitField
import db 
from db import get_db, desconectar
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import math
from psycopg2.extras import RealDictCursor
import json
from functools import wraps
from datetime import datetime
import pdfkit
import platform

# from blueprints.auth import bp as auth_bp


app = Flask(__name__)
app.run(debug=1)
app.secret_key='5258654.crz'
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#------------------------- Error Handlers -------------------------
def pagina_no_encontrada(error):
    return render_template('error/404.html')

def acceso_no_autorizado(error):
    return redirect(url_for('login'))



# ----------------DECORADORES DE AUTORIZACION----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'Administrador':
            flash('No tienes acceso a esta pagina.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------Index----------------
@app.route('/')
@login_required
def index():
    return render_template('index.html')


# ----------------LOGIN----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = db.conectar()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM public.usuario WHERE usuario = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user['contraseña'], password):
            session['user_id'] = user['id_usuario']
            session['role'] = user['rol']
            session['username'] = user['usuario']
            flash('Inicio de Secion Correcto', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o Contraseña Invalido', 'danger')
    return render_template('auth/login.html', form=form)

# ----------------LOGOUT----------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Cierre de Sesion Exitoso', 'success')
    return redirect(url_for('login'))

# Ejemplo de verificación de contraseña
# stored_password_hash = "hash_almacenado_en_la_base_de_datos"
# input_password = "contraseña_introducida_por_el_usuario"

# if check_password_hash(stored_password_hash, input_password):
#     print("Contraseña correcta")
# else:
#     print("Contraseña incorrecta")

# ----------------CRUD DE USUARIOS----------------
# ----------------REGISTRAR DE USUARIOS----------------
@app.route("/usuarios/registrar_usuario", methods=["GET", "POST"])
@login_required
@admin_required
def registrar_usuario():
    if request.method == "POST":
        img = request.files.get("img")
        nombre = request.form["nombre"].title()
        ap_pat = request.form["ap_pat"].title()
        ap_mat = request.form["ap_mat"].title()
        usuario = request.form["usuario"].lower()
        contraseña = request.form["contraseña"]
        rol = request.form["rol"]
        f_nacimiento = request.form["f_nacimiento"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"].title()

        # Validaciones
        if len(telefono) != 10 or not telefono.isdigit():
            flash("El número de teléfono debe tener 10 dígitos.", "warning")
            return render_template("admin/usuarios/registrar_usuario.html", nombre=nombre, ap_pat=ap_pat, ap_mat=ap_mat, usuario=usuario, rol=rol, f_nacimiento=f_nacimiento, telefono=telefono, direccion=direccion)

        if len(contraseña) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "warning")
            return render_template("admin/usuarios/registrar_usuario.html", nombre=nombre, ap_pat=ap_pat, ap_mat=ap_mat, usuario=usuario, rol=rol, f_nacimiento=f_nacimiento, telefono=telefono, direccion=direccion)

        conn = db.conectar()
        cursor = conn.cursor()

        try:
            # Verificar si el número de teléfono ya está registrado
            cursor.execute("SELECT * FROM public.usuario WHERE telefono = %s", (telefono,))
            if cursor.fetchone():
                flash("El número de teléfono ya está registrado.", "warning")
                return render_template("admin/usuarios/registrar_usuario.html", nombre=nombre, ap_pat=ap_pat, ap_mat=ap_mat, usuario=usuario, rol=rol, f_nacimiento=f_nacimiento, telefono=telefono, direccion=direccion)

            # Verificar si el nombre de usuario ya está registrado
            cursor.execute("SELECT * FROM public.usuario WHERE usuario = %s", (usuario,))
            if cursor.fetchone():
                flash("El nombre de usuario ya está registrado.", "warning")
                return render_template("admin/usuarios/registrar_usuario.html", nombre=nombre, ap_pat=ap_pat, ap_mat=ap_mat, usuario=usuario, rol=rol, f_nacimiento=f_nacimiento, telefono=telefono, direccion=direccion)

            # Hashear la contraseña
            hashed_password = generate_password_hash(contraseña)

            if img:
                if allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                        os.makedirs(app.config["UPLOAD_FOLDER"])
                    img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    img_url = url_for("static", filename="uploads/" + filename)
                else:
                    flash("Los únicos formatos permitidos para la imagen son - png, jpg, jpeg, gif", "warning")
                    return render_template("admin/usuarios/registrar_usuario.html", nombre=nombre, ap_pat=ap_pat, ap_mat=ap_mat, usuario=usuario, rol=rol, f_nacimiento=f_nacimiento, telefono=telefono, direccion=direccion)
            else:
                # Usa una imagen por defecto si no se sube ninguna
                img_url = url_for("static", filename="uploads/default_usuario.png")

            cursor.execute(
                "INSERT INTO public.usuario (img, nombre, ap_pat, ap_mat, usuario, contraseña, rol, f_nacimiento, telefono, direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (img_url, nombre, ap_pat, ap_mat, usuario, hashed_password, rol, f_nacimiento, telefono, direccion),
            )
            conn.commit()
            flash("¡Usuario registrado exitosamente!", "success")
            return redirect(url_for("ver_usuarios"))

        finally:
            cursor.close()
            conn.close()

    return render_template("admin/usuarios/registrar_usuario.html")

# ----------------VER DE USUARIOS----------------
@app.route('/usuarios', methods=['GET'])
@login_required
@admin_required
def ver_usuarios():
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""SELECT id_usuario, img, nombre, ap_pat, ap_mat, usuario, rol, f_nacimiento, telefono, direccion, 
        CAST(DATE_PART('year', AGE(f_nacimiento)) AS INTEGER) AS edad
        FROM public.usuario 
        ORDER BY id_usuario ASC;""")
        usuarios = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('admin/usuarios/ver_usuarios.html', usuarios=usuarios)


# ----------------EDITAR DE USUARIOS----------------
@app.route('/usuarios/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(usuario_id):
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute('''SELECT * FROM public.usuario WHERE id_usuario = %s;''', (usuario_id,))
        usuario = cursor.fetchone()

        if request.method == 'POST':
            img = request.files["img"]
            nombre = request.form["nombre"].title()
            ap_pat = request.form["ap_pat"].title()
            ap_mat = request.form["ap_mat"].title()
            usuario_nombre = request.form["usuario"]
            contraseña = request.form["contraseña"]
            rol = request.form["rol"]
            f_nacimiento = request.form["f_nacimiento"]
            telefono = request.form["telefono"]
            direccion = request.form["direccion"]

            # Hashear la nueva contraseña si se proporciona
            hashed_password = generate_password_hash(contraseña) if contraseña else usuario['contraseña']

            if img and allowed_file(img.filename):
                filename = secure_filename(img.filename)
                if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                    os.makedirs(app.config["UPLOAD_FOLDER"])
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                img_url = url_for("static", filename="uploads/" + filename)
            else:
                img_url = usuario['img']

            cursor.execute(
                '''UPDATE public.usuario SET img=%s, nombre=%s, ap_pat=%s, ap_mat=%s, usuario=%s, contraseña=%s, rol=%s, f_nacimiento=%s, telefono=%s, direccion=%s WHERE id_usuario=%s''',
                (img_url, nombre, ap_pat, ap_mat, usuario_nombre, hashed_password, rol, f_nacimiento, telefono, direccion, usuario_id)
            )
            conn.commit()
            flash('Usuario actualizado exitosamente!', "success")
            return redirect(url_for('ver_usuarios'))
    finally:
        cursor.close()
        conn.close()

    return render_template('admin/usuarios/editar_usuario.html', usuario=usuario)


# ----------------ELIMINAR DE USUARIOS----------------
@app.route('/usuarios/eliminar_usuario/<int:usuario_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(usuario_id):
    conn = db.conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''DELETE FROM public.usuario WHERE id_usuario = %s;''', (usuario_id,))
        conn.commit()
        flash('Usuario eliminado exitosamente!', "success")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('ver_usuarios'))



# ----------------PAGINADOR----------------
def paginador(sql_count, sql_lim, in_page, per_pages, search_param):
    page = request.args.get('page', in_page, type=int)
    per_page = request.args.get('per_page', per_pages, type=int)

    offset = (page - 1) * per_page

    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(sql_count, (search_param, search_param))
        total_items = cursor.fetchone()['count']

        cursor.execute(sql_lim, (search_param, search_param, per_page, offset))
        items = cursor.fetchall()

        # Asegúrate de que 'Imagen' no sea None
        for item in items:
            if item['Imagen'] is None:
                item['Imagen'] = 'default.png'
    finally:
        cursor.close()
        db.desconectar(conn)

    total_pages = (total_items + per_page - 1) // per_page

    # Calcular el rango de páginas a mostrar
    start_page = max(page - 2, 1)
    end_page = min(page + 2, total_pages)
    page_range = range(start_page, end_page + 1)

    return items, page, per_page, total_items, total_pages, page_range

    return items, page, per_page, total_items, total_pages

# ----------------CRUD DE PRODUCTOS----------------
# ----------------REGISTRAR DE PRODUCTOS----------------
@app.route("/productos/registrar_producto", methods=["GET", "POST"])
@login_required
@admin_required
def registrar_producto():
    conn = db.conectar()
    cursor = conn.cursor()

    # Obtener categorías
    cursor.execute('SELECT id_cat, nombre_cat FROM categoria')
    categorias = cursor.fetchall()

    if request.method == "POST":
        img = request.files.get("img")
        nombre = request.form["nombre"].title()
        precio_u = request.form["precio_u"]
        fk_cat = int(request.form["fk_cat"])  # Convertir a entero
        contenido = request.form["contenido"] or None
        stock = request.form["stock"] or None
        marca = request.form["marca"].title() or None
        cod_barras = request.form["cod_barras"] or None

        print(f"fk_cat: {fk_cat}")  # Depuración

        try:
            # Verificar si el código de barras ya está registrado
            cursor.execute("SELECT * FROM public.productos WHERE cod_barras = %s", (cod_barras,))
            existing_product = cursor.fetchone()
            if existing_product:
                flash("El producto con este código de barras ya está registrado.", "warning")
                return render_template("admin/productos/registrar_producto.html", categorias=categorias, nombre=nombre, precio_u=precio_u, fk_cat=fk_cat, contenido=contenido, stock=stock, marca=marca, cod_barras=cod_barras)

            # Registro de imágenes
            if img:
                if allowed_file(img.filename):
                    filename = secure_filename(img.filename)
                    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                        os.makedirs(app.config["UPLOAD_FOLDER"])
                    img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    img_url = url_for("static", filename="uploads/" + filename)
                else:
                    flash("Los únicos formatos permitidos para la imagen son - png, jpg, jpeg, gif", "warning")
                    return render_template("admin/productos/registrar_producto.html", categorias=categorias, nombre=nombre, precio_u=precio_u, fk_cat=fk_cat, contenido=contenido, stock=stock, marca=marca, cod_barras=cod_barras)
            else:
                # Usa una imagen por defecto si no se sube ninguna
                img_url = url_for("static", filename="uploads/default_producto.png")

            # Inserción de datos
            cursor.execute(
                "INSERT INTO public.productos(img, nombre, precio_u, fk_cat, contenido, stock, marca, cod_barras) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    img_url,
                    nombre,
                    precio_u,
                    fk_cat,
                    contenido,
                    stock,
                    marca,
                    cod_barras,
                ),
            )
            conn.commit()
            flash("¡Producto añadido exitosamente!", "success")
            return redirect(url_for("registrar_producto"))

        except Exception as e:
            conn.rollback()
            flash(f"Error al registrar el producto: {e}", "danger")
        finally:
            cursor.close()
            db.desconectar(conn)

    return render_template("admin/productos/registrar_producto.html", categorias=categorias)
# ----------------VER DE PRODUCTOS----------------
@app.route('/productos', methods=['GET'])
@login_required
def ver_productos():
    search = request.args.get('search', '')
    sql_count = '''SELECT COUNT(*) FROM perfil_producto WHERE "Nombre" ILIKE %s OR "Categoria" ILIKE %s'''
    sql_lim = '''SELECT "Imagen", "Nombre", "Categoria", "Precio", "Contenido", "Stock", "ID" FROM perfil_producto WHERE "Nombre" ILIKE %s OR "Categoria" ILIKE %s ORDER BY "ID" ASC LIMIT %s OFFSET %s'''
    
    # Incluye los comodines % en los parámetros
    search_param = f'%{search}%'
    
    items, page, per_page, total_items, total_pages, page_range = paginador(
        sql_count=sql_count,
        sql_lim=sql_lim,
        in_page=1,
        per_pages=12,
        search_param=search_param
    )
    
    return render_template('admin/productos/ver_productos.html', prod=items, page=page, total_pages=total_pages, search=search, page_range=page_range)

# ----------------VER PERFIL DE PRODUCTOS----------------
@app.route('/productos/<int:producto_id>')
@login_required
def ver_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM perfil_producto WHERE "ID" = %s;''', (producto_id,))
    producto = cursor.fetchone()
    cursor.close()
    db.desconectar(conn)
    return render_template('admin/productos/perfil_producto.html', producto=producto)
# ----------------EDITAR DE PRODUCTOS----------------
@app.route('/productos/editar_producto/<int:producto_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM perfil_producto WHERE "ID" = %s;', (producto_id,))
    producto = cursor.fetchone()

    cursor.execute('SELECT id_cat, nombre_cat FROM categoria')
    categorias = cursor.fetchall()

    if request.method == 'POST':
        img = request.files.get("img")
        nombre = request.form['nombre'].title()
        precio_u = request.form['precio_u']
        fk_cat = int(request.form['fk_cat'])
        contenido = request.form['contenido'] or None
        stock = request.form['stock'] or None
        marca = request.form['marca'].title()
        cod_barras = request.form['cod_barras']or None

        print(f"producto[8]: {producto[8]}")  # Depuración


        cursor.execute('SELECT * FROM public.productos WHERE cod_barras = %s AND id_prod != %s', (cod_barras, producto_id))
        existing_product = cursor.fetchone()
        if existing_product:
            flash("El producto con este código de barras ya está registrado.", 'danger')
            cursor.close()
            db.desconectar(conn)
            return render_template('admin/productos/editar_producto.html', producto=producto, categorias=categorias)

        try:
            if img and allowed_file(img.filename):
                filename = secure_filename(img.filename)
                if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                    os.makedirs(app.config["UPLOAD_FOLDER"])
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                img_url = url_for("static", filename="uploads/" + filename)
                cursor.execute('UPDATE public.productos SET img=%s WHERE id_prod=%s', (img_url, producto_id))
            else:
                img_url = producto[1]

            cursor.execute('''UPDATE public.productos SET nombre=%s, precio_u=%s, fk_cat=%s, contenido=%s, stock=%s, marca=%s, cod_barras=%s WHERE id_prod=%s''',
                (nombre, precio_u, fk_cat, contenido, stock, marca, cod_barras, producto_id))
            conn.commit()
            flash('Producto actualizado exitosamente!', 'success')
        except (psycopg2.DatabaseError, IOError) as e:
            flash('Error al actualizar el producto: ' + str(e), 'danger')
        finally:
            cursor.close()
            db.desconectar(conn)
        return redirect(url_for('ver_productos'))

    cursor.close()
    db.desconectar(conn)
    return render_template('admin/productos/editar_producto.html', producto=producto, categorias=categorias)


# ----------------ELIMINARDE PRODUCTOS----------------
@app.route('/productos/eliminar_producto/<int:producto_id>', methods=['POST'])
@login_required
@admin_required
def eliminar_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM public.productos WHERE "id_prod" = %s;''', (producto_id,))
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    flash('Producto eliminado exitosamente!')
    return redirect(url_for('ver_productos'))
# ----------------CRUD DE CATEGORIAS----------------
# ----------------REGISTRAR DE CATEGORIA----------------
@app.route('/registrar_categoria', methods=['GET', 'POST'])
def registrar_categoria():
    if request.method == 'POST':
        nombre_cat = request.form['nombre_cat'].title()

        conn, cur = get_db()
        try:
            # Verificar si el nombre de la categoría ya existe
            cur.execute("SELECT * FROM categoria WHERE nombre_cat = %s", (nombre_cat,))
            existing_categoria = cur.fetchone()
            if existing_categoria:
                flash('El nombre de la categoría ya está registrado.', 'danger')
            else:
                cur.execute("""INSERT INTO categoria (nombre_cat)VALUES (%s)""", (nombre_cat,))
                conn.commit()
                flash('¡Categoría registrada exitosamente!', 'success')
                return redirect(url_for('ver_categorias'))  # Redirigir a "Ver Categorías" después del registro
        except psycopg2.DatabaseError as e:
            conn.rollback()
            flash(f'Error en la base de datos: {e}', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'Error inesperado: {e}', 'danger')
        finally:
            cur.close()
            desconectar(conn)

        return redirect(url_for('registrar_categoria'))

    return render_template('admin/categorias/registrar_categoria.html')


# ----------------VER DE CATEGORIA----------------
@app.route('/categorias')
def ver_categorias():
    conn, cur = get_db()
    try:
        cur.execute("SELECT * FROM public.categoria ORDER BY id_cat ASC")
        categorias = cur.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        categorias = []
    finally:
        cur.close()
        desconectar(conn)
    
    return render_template('admin/categorias/ver_categorias.html', categorias=categorias)
# ----------------EDITAR DE CATEGORIA----------------
@app.route('/editar_categoria/<int:id_cat>', methods=['GET', 'POST'])
def editar_categoria(id_cat):
    conn, cur = get_db()
    if request.method == 'POST':
        nombre_cat = request.form['nombre_cat'].title()
        try:
            # Verificar si el nombre de la categoría ya existe
            cur.execute("SELECT * FROM categoria WHERE nombre_cat = %s AND id_cat != %s", (nombre_cat, id_cat))
            existing_categoria = cur.fetchone()
            
            if existing_categoria:
                flash('El nombre de la categoría ya está registrado.', 'danger')
            else:
                cur.execute("""
                    UPDATE categoria
                    SET nombre_cat = %s
                    WHERE id_cat = %s
                """, (nombre_cat, id_cat))
                conn.commit()
                flash('Categoría actualizada exitosamente!', 'success')
                return redirect(url_for('ver_categorias'))  # Redirigir a "Ver Categorías" después de la actualización
        except psycopg2.DatabaseError as e:
            conn.rollback()
            flash(f'Error en la base de datos: {e}', 'danger')
        finally:
            cur.close()
            desconectar(conn)
        return redirect(url_for('editar_categoria', id_cat=id_cat))
    
    try:
        cur.execute("SELECT * FROM categoria WHERE id_cat = %s", (id_cat,))
        categoria = cur.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        categoria = None
    finally:
        cur.close()
        desconectar(conn)
    
    return render_template('admin/categorias/editar_categoria.html', categoria=categoria)



# ----------------ELIMINAR DE CATEGORIA----------------

@app.route('/eliminar_categoria/<int:id_cat>', methods=['POST'])
def eliminar_categoria(id_cat):
    conn, cur = get_db()
    try:
        cur.execute("DELETE FROM categoria WHERE id_cat = %s", (id_cat,))
        conn.commit()
        flash('Categoría eliminada exitosamente!', 'success')
    except psycopg2.DatabaseError as e:
        conn.rollback()
        flash(f'Error en la base de datos: {e}', 'danger')
    except Exception as e:
        conn.rollback()
        flash(f'Error inesperado: {e}', 'danger')
    finally:
        cur.close()
        desconectar(conn)
    
    return redirect(url_for('ver_categorias'))


# ----------------CRUD DE MESAS----------------
# ----------------REGISTRAR DE MESAS----------------
@app.route('/registrar_mesa', methods=['GET', 'POST'])
def registrar_mesa():
    if request.method == 'POST':
        num_mesa = request.form['num_mesa']
        ubicacion = request.form['ubicacion'].title()

        conn = db.conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO mesa (ubicacion, num_mesa)
                VALUES (%s, %s)
            """, (ubicacion, num_mesa))
            conn.commit()
            flash('Mesa registrada exitosamente!', 'success')
        except psycopg2.DatabaseError as e:
            conn.rollback()
            flash(f'Error en la base de datos: {e}', 'danger')
        finally:
            cursor.close()
            desconectar(conn)

        return redirect(url_for('ver_mesas'))

    return render_template('admin/mesas/registrar_mesa.html')
# ----------------VER DE MESAS----------------
@app.route('/mesas/ver_mesas')
def ver_mesas():
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM public.mesa ORDER BY num_mesa ASC")
    fila = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/mesas/ver_mesas.html', mesas=fila)
# ---------------ELIMINAR DE MESAS----------------
@app.route('/mesas/eliminar_mesa/<int:mesa_id>', methods=['POST'])
def eliminar_mesa(mesa_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM public.mesa WHERE id_mesa = %s;''', (mesa_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Mesa eliminada exitosamente!', 'success')
    return redirect(url_for('ver_mesas'))
# ----------------EDITAR DE MESAS----------------
@app.route('/mesas/editar_mesa/<int:mesa_id>', methods=['GET', 'POST'])
def editar_mesa(mesa_id):
    conn = db.conectar()
    cursor = conn.cursor()
    if request.method == 'POST':
        ubicacion = request.form['ubicacion'].title()
        num_mesa = request.form['num_mesa']
        try:
            cursor.execute('''UPDATE public.mesa SET ubicacion = %s, num_mesa = %s WHERE id_mesa = %s;''', (ubicacion, num_mesa, mesa_id))
            conn.commit()
            flash('Mesa actualizada exitosamente!', 'success')
        except psycopg2.DatabaseError as e:
            flash('Error al actualizar la mesa: ' + str(e), 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('ver_mesas'))
    else:
        cursor.execute('''SELECT * FROM public.mesa WHERE id_mesa = %s;''', (mesa_id,))
        mesa = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('admin/mesas/editar_mesa.html', mesa=mesa)


























# ----------------CRUD DE VENTAS----------------
# ----------------REGISTRAR DE VENTAS----------------
@app.route('/ventas/registrar_venta', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    conn = db.conectar()
    cursor = conn.cursor()
    
    # Obtener categorías
    cursor.execute('SELECT id_cat, nombre_cat FROM categoria')
    categorias = cursor.fetchall()
    
    # Obtener mesas
    cursor.execute('SELECT id_mesa, num_mesa FROM mesa')
    mesas = cursor.fetchall()
    
    # Obtener productos
    cursor.execute('SELECT id_prod, nombre, fk_cat, contenido, precio_u, cod_barras FROM productos')
    productos = cursor.fetchall()
    
    if request.method == 'POST':
        try:
            # Extraer los datos del formulario
            nombre_cliente = request.form['nombre_cliente'].title()
            forma_pago = request.form['forma_pago']
            fk_mesa = int(request.form['fk_mesa'])
            fk_usuario = session['user_id']  # Obtener el ID del usuario desde la sesión
            
            # Insertar en la tabla ventas
            cursor.execute("""
                INSERT INTO ventas (fecha_venta, cant_prod, total, forma_pago, fk_mesa, fk_usuario, nombre_cliente)
                VALUES (CURRENT_TIMESTAMP, 0, 0, %s, %s, %s, %s) RETURNING id_venta
            """, (forma_pago, fk_mesa, fk_usuario, nombre_cliente))
            
            id_venta = cursor.fetchone()[0]
            print(f"ID de la venta: {id_venta}")  # Línea de depuración
            
            # Insertar cada producto en la tabla detalles_venta
            total_venta = 0
            cant_prod = 0
            productos = request.form.to_dict(flat=False)
            print(f"Productos: {productos}")  # Línea de depuración

            num_productos = len([key for key in productos.keys() if key.startswith('productos[') and key.endswith('][id_prod]')])
            print(f"Número de productos: {num_productos}")  # Línea de depuración

            for i in range(num_productos):
                id_prod = int(request.form[f'productos[{i}][id_prod]'])
                cantidad = int(request.form[f'productos[{i}][cantidad]'])
                categoria_prod = request.form[f'productos[{i}][categoria]']
                nombre_prod = request.form[f'productos[{i}][nombre]']
                contenido_prod = request.form[f'productos[{i}][contenido]']
                precio_prod = float(request.form[f'productos[{i}][precio]'])
                cod_barras_prod = request.form[f'productos[{i}][cod_barras]']
                
                print(f"Producto {i}: ID={id_prod}, Cantidad={cantidad}, Categoría={categoria_prod}, Nombre={nombre_prod}, Contenido={contenido_prod}, Precio={precio_prod}, Código de Barras={cod_barras_prod}")  # Línea de depuración
                
                subtotal = precio_prod * cantidad
                total_venta += subtotal
                cant_prod += cantidad
                print(f"Subtotal para producto {id_prod}: {subtotal}")  # Línea de depuración
                
                cursor.execute("""
                    INSERT INTO detalles_venta (fk_venta, fk_producto, subtotal, cantidad, categoria_prod, nombre_prod, contenido_prod, precio_prod, cod_barras_prod)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_venta, id_prod, subtotal, cantidad, categoria_prod, nombre_prod, contenido_prod, precio_prod, cod_barras_prod))
            
            # Actualizar la tabla ventas con el total y la cantidad de productos
            cursor.execute("""
                UPDATE ventas
                SET cant_prod = %s, total = %s
                WHERE id_venta = %s
            """, (cant_prod, total_venta, id_venta))
            print(f"Total de la venta: {total_venta}, Cantidad de productos: {cant_prod}")  # Línea de depuración
            
            # Confirmar la transacción
            conn.commit()
            flash('Venta procesada exitosamente', 'success')
        
        except Exception as e:
            conn.rollback()
            flash(f'Ocurrió un error: {str(e)}', 'danger')
        
        finally:
            cursor.close()
            desconectar(conn)
        
        return redirect(url_for('registrar_venta'))
    
    return render_template('admin/ventas/registrar_venta.html', categorias=categorias, mesas=mesas, productos=productos)
# ----------------VER DE VENTAS----------------
@app.route('/ventas', methods=['GET'])
@login_required
def ver_ventas():
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Obtener los parámetros de fecha del formulario
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Construir la consulta SQL base
        query = """
            SELECT v.id_venta,  TO_CHAR(v.fecha_venta, 'YYYY-MM-DD HH24:MI:SS') AS fecha_venta, v.cant_prod, v.total, v.forma_pago, m.num_mesa, 
            CONCAT(u.nombre, ' ', u.ap_pat) AS nombre_completo, v.nombre_cliente
            FROM ventas v
            INNER JOIN mesa m ON v.fk_mesa = m.id_mesa
            INNER JOIN usuario u ON v.fk_usuario = u.id_usuario
        """
        
        # Añadir condiciones de fecha si están presentes
        conditions = []
        if start_date:
            conditions.append(f"v.fecha_venta >= '{start_date}'")
        if end_date:
            conditions.append(f"v.fecha_venta <= '{end_date}'")
        
        # Filtrar según el rol del usuario
        if session['role'] != 'Administrador':
            conditions.append(f"v.fk_usuario = {session['user_id']}")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY v.id_venta ASC"
        
        cursor.execute(query)
        ventas = cursor.fetchall()
    finally:
        cursor.close()
        db.desconectar(conn)
    
    return render_template('admin/ventas/ver_ventas.html', ventas=ventas)
# ----------------VER DETALLES DE VENTA----------------
@app.route('/ventas/detalles/<int:venta_id>', methods=['GET'])
@login_required
def ver_detalles_venta(venta_id):
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Obtener los detalles de la venta
        cursor.execute('''
            SELECT v.id_venta, TO_CHAR(v.fecha_venta, 'YYYY-MM-DD HH24:MI:SS') AS fecha_venta, v.cant_prod, v.total, v.forma_pago, m.num_mesa, 
            CONCAT(u.nombre, ' ', u.ap_pat) AS nombre_completo, v.nombre_cliente
            FROM ventas v
            INNER JOIN mesa m ON v.fk_mesa = m.id_mesa
            INNER JOIN usuario u ON v.fk_usuario = u.id_usuario
            WHERE v.id_venta = %s;
        ''', (venta_id,))
        venta = cursor.fetchone()
        
        # Obtener los productos de la venta
        cursor.execute('''
            SELECT dv.cantidad, c.nombre_cat AS categoria_prod, dv.nombre_prod, dv.contenido_prod, dv.precio_prod, dv.subtotal
            FROM detalles_venta dv
            INNER JOIN categoria c ON dv.categoria_prod = c.id_cat
            WHERE dv.fk_venta = %s;
        ''', (venta_id,))
        productos = cursor.fetchall()
        
    finally:
        cursor.close()
        db.desconectar(conn)
    
    return render_template('admin/ventas/ver_detalles_venta.html', venta=venta, productos=productos)
# ----------------IMPRIMIR TICKET DE VENTA----------------
@app.route('/ventas/imprimir_ticket/<int:venta_id>', methods=['GET'])
@login_required
def imprimir_ticket(venta_id):
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Consultar la información de la venta
        cursor.execute('''
            SELECT v.id_venta, TO_CHAR(v.fecha_venta, 'YYYY-MM-DD HH24:MI:SS') AS fecha_venta, v.cant_prod, v.total, 
            v.forma_pago, m.num_mesa, CONCAT(u.nombre, ' ', u.ap_pat) AS nombre_completo, v.nombre_cliente
            FROM ventas v
            INNER JOIN mesa m ON v.fk_mesa = m.id_mesa
            INNER JOIN usuario u ON v.fk_usuario = u.id_usuario
            WHERE v.id_venta = %s;
        ''', (venta_id,))
        venta = cursor.fetchone()

        # Consultar los productos de la venta
        cursor.execute('''
            SELECT dv.cantidad, c.nombre_cat AS categoria_prod, dv.nombre_prod, dv.contenido_prod, dv.precio_prod, dv.subtotal
            FROM detalles_venta dv
            INNER JOIN categoria c ON dv.categoria_prod = c.id_cat
            WHERE dv.fk_venta = %s;
        ''', (venta_id,))
        productos = cursor.fetchall()
    finally:
        cursor.close()
        desconectar(conn)
    
    # Renderizar la plantilla HTML
    rendered = render_template('admin/ventas/ticket.html', venta=venta, productos=productos)
    
    # Configuración de pdfkit según el sistema operativo
    if platform.system() == 'Windows':
        pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
    else:
        pdfkit_config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    
    # Opciones de configuración para wkhtmltopdf
    options = {
        'no-outline': None,
        'disable-smart-shrinking': None,
        'load-error-handling': 'ignore',
        'enable-local-file-access': '',  # Asegura que se pueda acceder a archivos locales
        'quiet': ''  # Reduce el output en consola
    }
    
    try:
        # Generar el PDF a partir del HTML renderizado
        pdf = pdfkit.from_string(rendered, False, configuration=pdfkit_config, options=options)
    except OSError as e:
        # Manejo de errores en caso de que wkhtmltopdf falle
        return f'Error al generar el PDF: {str(e)}', 500
    
    # Preparar la respuesta con el PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ticket_venta_{venta_id}.pdf'
    
    return response