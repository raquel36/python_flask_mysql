
import mysql.connector
#Importamos los módulos necesarios
from flask import Flask, render_template, request, redirect, url_for
#El módulo os nos permite acceder a los directorios de una manera más facil
import os
# Librería necesaria para renderizar las imagenes
from PIL import Image
import io
import base64


try:
    db = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='',
        db='veterinary'
    )
    if db.is_connected():
        print("Conexión exitosa")
        info_server=db.get_server_info()
        cursor_c = db.cursor()
        print(info_server)
        cursor_c.execute('SELECT DATABASE()')
        row = cursor_c.fetchone()
        print("Conectado a la base de datos: {}".format(row))
except Exception as ex:
    print(ex)


# Variable que nos permite acceder a la ruta absoluta
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# Modificamos la variable para poder acceder a las carpetas del proyecto
template_dir = os.path.join(template_dir, 'src', 'templates')

# Inicializamos Flask para que encuentre la carpeta del proyecto
app = Flask(__name__, template_folder= template_dir)
# Configuración de la carpeta de archivos estáticos
app.static_folder = 'static'


# Rutas de la aplicación
@app.route('/')
def home():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM mascotas")
    myresult = cursor.fetchall()

    # Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        # Convertir los datos de la imagen a base64
        if record[6] is not None:
            img = Image.open(io.BytesIO(record[6]))
            max_size = (100,100)
            img.thumbnail(max_size)
            output_buffer = io.BytesIO()
            img.save(output_buffer, format='PNG')
            imagen_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
            imagen_url = f"data:image/PNG;base64,{imagen_base64}"
            record = list(record)
            record[6] = imagen_url
        else:
            record = list(record)
            record[6] = None

        # Agregar el diccionario al objeto de inserción
        insertObject.append(dict(zip(columnNames, record)))

    cursor.close()

    return render_template('index.html', data=insertObject)

import io
from PIL import Image

def convertToBinaryData(filename):
    file_binary = filename.read() # Obtener los datos binarios del archivo
    return file_binary

#Ruta para guardar mascotas en la bdd
@ app.route('/mascotas', methods=['POST'])
def addPet():
    nombre = request.form['nombre']
    especie = request.form['especie']
    genero = request.form['genero']
    fecha_nacimiento = request.form['fecha']
    peso = request.form['peso']
    foto = request.files['foto']  # Acceder al archivo cargado

    if nombre and especie and genero and fecha_nacimiento and peso and foto:
        cursor = db.cursor()

        # Leer el contenido del archivo cargado y convertirlo en un objeto de bytes
        img = convertToBinaryData(foto)
        

        # Insertar los datos en la base de datos, incluyendo el objeto de bytes
        sql = "INSERT INTO mascotas (nombre, especie, genero, fecha_nacimiento, peso, foto_mascota) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (nombre, especie, genero, fecha_nacimiento, peso, img)
        cursor.execute(sql, data)
        db.commit()
    return redirect(url_for('home'))


@ app.route('/delete/<string:id_mascota>')
def delete(id_mascota):
    cursor = db.cursor()
    sql = "DELETE FROM mascotas WHERE id_mascota =%s"
    data = (id_mascota,)
    cursor.execute(sql, data)
    db.commit()
    return redirect(url_for('home'))

@ app.route('/edit/<string:id_mascota>', methods=['POST'])
def edit(id_mascota):
    nombre = request.form['nombre']
    especie = request.form['especie']
    genero = request.form['genero']
    fecha_nacimiento = request.form['fecha']
    peso = request.form['peso']
    foto = request.files['foto'] if 'foto' in request.files else None  # Acceder al archivo cargado si está presente

    if nombre and especie and genero and fecha_nacimiento and peso:
        cursor = db.cursor()

       # Si se cargó una nueva imagen, leer el contenido del archivo y convertirlo en un objeto de bytes
        if foto:
            img = convertToBinaryData(foto)
            sql = "UPDATE mascotas SET nombre=%s, especie=%s, genero=%s, fecha_nacimiento=%s, peso=%s, foto_mascota=%s WHERE id_mascota=%s"
            data = (nombre, especie, genero, fecha_nacimiento, peso, img, id_mascota)
        else:
            sql = "UPDATE mascotas SET nombre=%s, especie=%s, genero=%s, fecha_nacimiento=%s, peso=%s WHERE id_mascota=%s"
            data = (nombre, especie, genero, fecha_nacimiento, peso, id_mascota)

        cursor.execute(sql, data)
        db.commit()


    return redirect(url_for('home'))


if __name__=='__main__':
    app.run(debug=True, port=4003)


