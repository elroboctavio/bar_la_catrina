import os
import psycopg2
from flask import Flask, redirect, render_template, request, url_for, flash, get_flashed_messages, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
import db
from werkzeug.utils import secure_filename
import math
from psycopg2.extras import RealDictCursor
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
