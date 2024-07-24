import psycopg2
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField, StringField, SubmitField
import db
import os
from werkzeug.utils import secure_filename



app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
    #recuperar la informacion
    datos = cursor.fetchall()
    #cerrar cursos y conexion a la base de datos
    cursor.close()
    conexion.close()
    return render_template('categoria.html', datos=datos)


@app.route('/productos_card')
def productos_card():
    conn = db.conectar()
    cursor = conn.cursor()
    cursor.execute('''SELECT img, nombre, precio_u, fk_cat FROM productos''')
    datos = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('productos_card.html', datos=datos)

@app.route('/register_productos', methods=['GET', 'POST'])
def register_productos():
    if request.method == 'POST':
        img = request.files['img']
        nombre = request.form['nombre']
        precio_u = request.form['precio_u']
        fk_cat = request.form['fk_cat']
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = url_for('static', filename='uploads/' + filename)
            conn = db.conectar()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO public.productos(img, nombre, precio_u, fk_cat) VALUES (%s, %s, %s, %s)',
                        (img_url, nombre,precio_u,fk_cat))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Product added successfully!')
            return redirect(url_for('login'))
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return redirect(request.url)
    return render_template('add_product.html')
    # if request.method == 'POST':
    #     img = request.files['img']
    #     nombre = request.form['nombre']
    #     precio_u = request.form['precio_u']
    #     fk_cat = request.form['fk_cat']
    #     if img and allowed_file(img.filename):
    #         filename = secure_filename(img.filename)
    #         img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #         img = url_for('static', filename='img_ico/' + filename)
    #         conn = db.conectar()
    #         cursor = conn.cursor()
    #         cursor.execute('INSERT INTO public.productos(img, nombre, precio_u, fk_cat) VALUES (%s, %s, %s, %s,)',
    #                     (img, nombre,precio_u,fk_cat))
    #         conn.commit()
    #         cursor.close()
    #         conn.close()
    #         flash('Product added successfully!')
    #         return redirect(url_for('login'))
    #     else:
    #         flash('Allowed image types are - png, jpg, jpeg, gif')
    #         return redirect(request.url)
    # return render_template('add_product.html')
    # conn = db.conectar()
    # cursor = conn.cursor()
    # cursor.execute('''SELECT * FROM product_card_1''')
    # datos = cursor.fetchall()
    # cursor.close()
    # db.desconectar(conn)
    # return render_template('productos_card.html', datos=datos)
