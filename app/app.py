import os
import psycopg2
from flask import Flask, redirect, render_template, request, url_for, flash, get_flashed_messages, session, jsonify, json
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
import db 
from db import get_db, desconectar
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import math
from psycopg2.extras import RealDictCursor
import json
# from blueprints.auth import bp as auth_bp


app = Flask(__name__)
app.run(debug=True)
app.secret_key='5258654.crz'
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# app.register_blueprint(auth_bp)

#------------------------- Error Handlers -------------------------
def pagina_no_encontrada(error):
    return render_template('error/404.html')

def acceso_no_autorizado(error):
    return redirect(url_for('login'))



if __name__ == '__main__':
    # csrf.init_app(app)
    # app.register_blueprint(custom_tags)
    app.register_error_handler(404, pagina_no_encontrada)
    app.register_error_handler(401, acceso_no_autorizado)
    app.run(debug=True, port=5000)


@app.route('/')
def index():
    # if 'usuario' in session:
    #     return render_template('home.html')
    return render_template('auth/login.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         print(request.form['usuario'])
#         print(request.form['contraseña'])
#         session['usuario'] = request.form['usuario']
#         return redirect(url_for('index'))
#     else:
#         return render_template('auth/login.html')

# @app.route('/logout')
# def logout():
#     # remove the username from the session if it's there
#     session.pop('usuario', None)







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
def registrar_usuario():
    if request.method == "POST":
        img = request.files["img"]
        nombre = request.form["nombre"].title()
        ap_pat = request.form["ap_pat"].title()
        ap_mat = request.form["ap_mat"].title()
        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        rol = request.form["rol"]
        f_nacimiento = request.form["f_nacimiento"]
        telefono = request.form["telefono"]
        direccion = request.form["direccion"]

        # Hashear la contraseña
        hashed_password = generate_password_hash(contraseña)

        conn = db.conectar()
        cursor = conn.cursor()

        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            img_url = url_for("static", filename="uploads/" + filename)

            cursor.execute(
                "INSERT INTO public.usuario (img, nombre, ap_pat, ap_mat, usuario, contraseña, rol, f_nacimiento, telefono, direccion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (img_url, nombre, ap_pat, ap_mat, usuario, hashed_password, rol, f_nacimiento, telefono, direccion),
            )
            conn.commit()
            flash("Usuario registrado exitosamente!")
        else:
            flash("Los únicos formatos permitidos para la imagen son - png, jpg, jpeg, gif")

        cursor.close()
        conn.close()
        return redirect(url_for("registrar_usuario"))

    return render_template("admin/usuarios/registrar_usuario.html")


# ----------------VER DE USUARIOS----------------
@app.route('/usuarios', methods=['GET'])
def ver_usuarios():
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM public.usuario ORDER BY id_usuario ASC")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/usuarios/ver_usuarios.html', usuarios=usuarios)

# ----------------EDITAR DE USUARIOS----------------
@app.route('/usuarios/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
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
        flash('Usuario actualizado exitosamente!')
        return redirect(url_for('ver_usuarios'))

    cursor.close()
    conn.close()
    return render_template('admin/usuarios/editar_usuario.html', usuario=usuario)

# ----------------ELIMINAR DE USUARIOS----------------
@app.route('/usuarios/eliminar_usuario/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM public.usuario WHERE id_usuario = %s;''', (usuario_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Usuario eliminado exitosamente!')
    return redirect(url_for('ver_usuarios'))



# ----------------PAGINADOR----------------
def paginador(sql_count, sql_lim, in_page, per_pages, search_param):
    page = request.args.get('page', in_page, type=int)
    per_page = request.args.get('per_page', per_pages, type=int)

    offset = (page - 1) * per_page

    conn = db.conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(sql_count, (search_param, search_param))
    total_items = cursor.fetchone()['count']

    cursor.execute(sql_lim, (search_param, search_param, per_page, offset))
    items = cursor.fetchall()

    # Asegúrate de que 'Imagen' no sea None
    for item in items:
        if item['Imagen'] is None:
            item['Imagen'] = 'default.png'

    cursor.close()
    conn.close()

    total_pages = (total_items + per_page - 1) // per_page

    return items, page, per_page, total_items, total_pages





# ----------------CRUD DE PRODUCTOS----------------
# ----------------REGISTRAR DE PRODUCTOS----------------
@app.route("/productos/registrar_producto", methods=["GET", "POST"])
def registrar_producto():
    if request.method == "POST":
        img = request.files["img"]
        nombre = request.form["nombre"].title()
        precio_u = request.form["precio_u"]
        fk_cat = request.form["fk_cat"]
        contenido = request.form["contenido"] or None
        stock = request.form["stock"] or None
        marca = request.form["marca"].title()or None
        cod_barras = request.form["cod_barras"]or None
        conn = db.conectar()
        cursor = conn.cursor()
        # Verificar si el código de barras ya está registrado
        cursor.execute("SELECT * FROM public.productos WHERE cod_barras = %s", (cod_barras,))
        existing_product = cursor.fetchone()
        if existing_product:
            flash("El producto con este código de barras ya está registrado.")
            cursor.close()
            conn.close()
            return redirect(url_for("registrar_producto"))
        #Registro de imagenes
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            img_url = url_for("static", filename="uploads/" + filename)
            #Inserccion de datos
            cursor.execute(
                "INSERT INTO public.productos(img, nombre, precio_u, fk_cat, contenido, stock, marca, cod_barras ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
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
            flash("Producto añadido exitosamente!")
        else:
            flash(
                "Los únicos formatos permitidos para la imagen son - png, jpg, jpeg, gif"
            )
        cursor.close()
        conn.close()
        return redirect(url_for("registrar_producto"))
    return render_template("admin/productos/registrar_producto.html")
# ----------------VER DE PRODUCTOS----------------
@app.route('/productos', methods=['GET'])
def ver_productos():
    search = request.args.get('search', '')
    sql_count = '''SELECT COUNT(*) FROM perfil_producto WHERE "Nombre" ILIKE %s OR "Categoria" ILIKE %s'''
    sql_lim = '''SELECT "Imagen", "Nombre", "Categoria", "Precio", "Contenido", "Stock", "ID" FROM perfil_producto WHERE "Nombre" ILIKE %s OR "Categoria" ILIKE %s ORDER BY "ID" ASC LIMIT %s OFFSET %s'''
    
    # Incluye los comodines % en los parámetros
    search_param = f'%{search}%'
    
    items, page, per_page, total_items, total_pages = paginador(
        sql_count=sql_count,
        sql_lim=sql_lim,
        in_page=1,
        per_pages=12,
        search_param=search_param
    )
    
    return render_template('admin/productos/ver_productos.html', prod=items, page=page, total_pages=total_pages, search=search)



# ----------------VER PERFIL DE PRODUCTOS----------------
@app.route('/productos/<int:producto_id>')
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
def editar_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM perfil_producto WHERE "ID" = %s;''', (producto_id,))
    producto = cursor.fetchone()
    if request.method == 'POST':
        img = request.files["img"]
        nombre = request.form['nombre'].title()
        precio_u = request.form['precio_u']
        fk_cat = request.form['fk_cat']
        contenido = request.form['contenido'] or None
        stock = request.form['stock'] or None
        marca = request.form['marca'].title()
        cod_barras = request.form['cod_barras']
        # Verificar si el código de barras ya existe en otro producto
        cursor.execute('''SELECT * FROM public.productos WHERE cod_barras = %s AND id_prod != %s''',
                        (cod_barras, producto_id))
        existing_product = cursor.fetchone()
        if existing_product:
            flash("El producto con este código de barras ya está registrado.", 'danger')
            cursor.close()
            db.desconectar(conn)
            return redirect(url_for('editar_producto', producto_id=producto_id))
        try:
            # Manejo de la imagen
            if img and allowed_file(img.filename):
                filename = secure_filename(img.filename)
                if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                    os.makedirs(app.config["UPLOAD_FOLDER"])
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                img_url = url_for("static", filename="uploads/" + filename)
                cursor.execute('''UPDATE public.productos SET img=%s WHERE id_prod=%s''', (img_url, producto_id))
            cursor.execute('''UPDATE public.productos SET nombre=%s, precio_u=%s, fk_cat=%s, contenido=%s, stock=%s, marca=%s, cod_barras=%s WHERE id_prod=%s''',
                (nombre, precio_u, fk_cat, contenido, stock, marca, cod_barras, producto_id))
            conn.commit()
            flash('Producto actualizado exitosamente!')
        except (psycopg2.DatabaseError, IOError) as e:
            flash('Error al actualizar el producto: ' + str(e), 'danger')
        finally:
            cursor.close()
            db.desconectar(conn)
        return redirect(url_for('ver_productos'))
    cursor.close()
    db.desconectar(conn)
    return render_template('admin/productos/editar_producto.html', producto=producto)
# ----------------ELIMINARDE PRODUCTOS----------------
@app.route('/productos/eliminar_producto/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM public.productos WHERE "id_prod" = %s;''', (producto_id,))
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    flash('Producto eliminado exitosamente!')
    return redirect(url_for('admin/productos/ver_productos'))
# ----------------CRUD DE CATEGORIAS----------------
# ----------------REGISTRAR DE CATEGORIA----------------
@app.route('/registrar_categoria', methods=['GET', 'POST'])
def registrar_categoria():
    if request.method == 'POST':
        nombre_cat = request.form['nombre_cat']

        conn, cur = get_db()
        try:
            cur.execute("""
                INSERT INTO categoria (nombre_cat)
                VALUES (%s)
            """, (nombre_cat,))
            conn.commit()
            flash('Categoría registrada exitosamente!', 'success')
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
        nombre_cat = request.form['nombre_cat']
        try:
            cur.execute("""
                UPDATE categoria
                SET nombre_cat = %s
                WHERE id_cat = %s
            """, (nombre_cat, id_cat))
            conn.commit()
            flash('Categoría actualizada exitosamente!', 'success')
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

        return redirect(url_for('registrar_mesa'))

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
    flash('Mesa eliminada exitosamente!')
    return redirect(url_for('mesas'))
# ----------------EDITAR DE MESAS----------------
@app.route('/mesas/editar_mesa/<int:mesa_id>', methods=['GET', 'POST'])
def editar_mesa(mesa_id):
    conn = db.conectar()
    cursor = conn.cursor()
    if request.method == 'POST':
        ubicacion = request.form['ubicacion']
        num_mesa = request.form['num_mesa']
        try:
            cursor.execute('''UPDATE public.mesa SET ubicacion = %s, num_mesa = %s WHERE id_mesa = %s;''', (ubicacion, num_mesa, mesa_id))
            conn.commit()
            flash('Mesa actualizada exitosamente!')
        except psycopg2.DatabaseError as e:
            flash('Error al actualizar la mesa: ' + str(e), 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('mesas'))
    else:
        cursor.execute('''SELECT * FROM public.mesa WHERE id_mesa = %s;''', (mesa_id,))
        mesa = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('admin/mesas/editar_mesa.html', mesa=mesa)


























# ----------------CRUD DE VENTAS----------------
# ----------------REGISTRAR DE VENTAS----------------
@app.route('/registrar_venta')
def registrar_venta():
    return render_template('admin/ventas/registrar_venta.html')

@app.route('/finalizar', methods=['POST'])
def finalizar():
    productos = json.loads(request.form['productos'])
    forma_pago = request.form['forma_pago']
    fk_mesa = request.form['fk_mesa']
    nombre_cliente = request.form['nombre_cliente']
    fk_usuario = 7  # Asumiendo un usuario fijo por simplicidad

    total = sum([p['subtotal'] for p in productos])
    cant_prod = sum([p['cantidad'] for p in productos])

    conn, cur = get_db()
    try:
        # Insertar en la tabla ventas
        cur.execute("""
            INSERT INTO ventas (fecha_venta, cant_prod, total, forma_pago, fk_mesa, fk_usuario, nombre_cliente)
            VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s)
            RETURNING id_venta
        """, (cant_prod, total, forma_pago, fk_mesa, fk_usuario, nombre_cliente))
        id_venta = cur.fetchone()[0]

        # Insertar en la tabla detalles_venta y actualizar stock
        for producto in productos:
            cur.execute("""
                INSERT INTO detalles_venta (id_venta, id_producto, cantidad, subtotal)
                VALUES (%s, %s, %s, %s)
            """, (id_venta, producto['idProducto'], producto['cantidad'], producto['subtotal']))

            # Actualizar el stock del producto
            cur.execute("""
                UPDATE productos
                SET stock = stock - %s
                WHERE id_producto = %s
            """, (producto['cantidad'], producto['idProducto']))

        conn.commit()
    except psycopg2.DatabaseError as e:
        conn.rollback()
        print(f"Database error: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error: {e}")
    finally:
        cur.close()
        desconectar(conn)

    return redirect(url_for('admin/ventas/registrar_venta.html'))

@app.route('/buscar_productos', methods=['GET'])
def buscar_productos():
    termino = request.args.get('termino', '')
    conn, cur = get_db()
    try:
        cur.execute("""
            SELECT id_prod AS "ID", img AS "Imagen", nombre AS "Nombre", precio_u AS "Precio", contenido AS "Contenido", stock AS "Stock", marca AS "Marca", cod_barras AS "Codigo de Barras", nombre_cat AS "Categoria"
            FROM perfil_producto
            WHERE nombre ILIKE %s OR nombre_cat ILIKE %s
        """, (f'%{termino}%', f'%{termino}%'))
        productos = cur.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        productos = []
    finally:
        cur.close()
        desconectar(conn)
    
    return jsonify(productos)
