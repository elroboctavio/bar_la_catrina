import psycopg2
from flask import Flask, redirect, render_template, request, url_for, flash, get_flashed_messages
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
import db
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key='5258654.crz'
bootstrap = Bootstrap(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # print(request.form['usuario'])
        # print(request.form['contraseña'])

        return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


@app.route('/productos')
def productos():
    # Conectar con la base de datos
    conexion = psycopg2.connect (
        database="bar_la_catrina",
        user="postgres",
        password="tVE4QgrFP9rnEb",
        host="localhost",
        port="5432"
    )
    # crear un cursor (objeto para recorrer las tablas)
    cursor = conexion.cursor()
    # ejecutar una consulta en postgres
    cursor.execute('''SELECT * FROM public.producto''')
    #recuperar la informacion
    datos = cursor.fetchall()
    #cerrar cursos y conexion a la base de datos
    cursor.close()
    conexion.close()
    return render_template('productos.html', datos=datos)

@app.route('/categoria')
def categoria():
    # Conectar con la base de datos
    conexion = psycopg2.connect (
        database="bar_la_catrina",
        user="postgres",
        password="tVE4QgrFP9rnEb",
        host="localhost",
        port="5432"
    )
    # crear un cursor (objeto para recorrer las tablas)
    cursor = conexion.cursor()
    # ejecutar una consulta en postgres
    cursor.execute('''SELECT * FROM public.categoria''')
    # recuperar la informacion
    datos = cursor.fetchall()
    # cerrar cursos y conexion a la base de datos
    cursor.close()
    conexion.close()
    return render_template('categoria.html', datos=datos)


@app.route("/registrar_producto", methods=["GET", "POST"])
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
        cursor.execute(
            "SELECT * FROM public.productos WHERE cod_barras = %s", (cod_barras,)
        )
        existing_product = cursor.fetchone()

        if existing_product:
            flash("El producto con este código de barras ya está registrado.")
            cursor.close()
            conn.close()
            return redirect(url_for("registrar_producto"))

        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            img_url = url_for("static", filename="uploads/" + filename)

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

    return render_template("registrar_producto.html")


@app.route('/ver_productos')
def ver_productos():
    search_query = request.args.get('search', '')
    conn = db.conectar()
    cursor = conn.cursor()
    if search_query:
        cursor.execute('''SELECT * FROM perfil_producto WHERE "Nombre" ILIKE %s OR "Categoria" ILIKE %s''', ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute('''SELECT * FROM perfil_producto ORDER BY "ID" ASC ''')
    prod = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('ver_productos.html', prod=prod)


@app.route('/ver_productos/<int:producto_id>')
def ver_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM perfil_producto WHERE "ID" = %s;''', (producto_id,))
    producto = cursor.fetchone()
    cursor.close()
    db.desconectar(conn)
    return render_template('perfil_producto.html', producto=producto)





@app.route('/editar_producto/<int:producto_id>', methods=['GET', 'POST'])
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
        cursor.execute('''SELECT * FROM public.productos WHERE cod_barras = %s AND id_prod != %s''', (cod_barras, producto_id))
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
            flash('Producto actualizado exitosamente!', 'success')
        except (psycopg2.DatabaseError, IOError) as e:
            flash('Error al actualizar el producto: ' + str(e), 'danger')
        finally:
            cursor.close()
            db.desconectar(conn)
        
        return redirect(url_for('ver_productos'))
    
    cursor.close()
    db.desconectar(conn)
    return render_template('editar_producto.html', producto=producto)










@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM public.productos WHERE "id_prod" = %s;''', (producto_id,))
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    flash('Producto eliminado exitosamente!')
    return redirect(url_for('ver_productos'))
