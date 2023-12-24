import os
import sys

from datetime import datetime

import shutil  # For copying files

from utils.schema import *
from utils.utils import *
from utils.cobranza import *
from utils.export import *
from utils.keywords import *
from utils.precio import *
from utils.liquidacion import *


from flask import Flask, render_template
from flask_caching import Cache


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# donde corre el script
script_directory = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

# poner base de datos en mismo directorio que el script
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(script_directory, "pagina_web.db")}'


db.init_app(app)


# Wrap db.create_all() in an app context
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


app.route('/add_cobranza/<string:fecha_creacion>', methods=['POST'])(add_cobranza)

app.route('/add_planilla/<int:year>', methods=['POST'])(add_planilla)

app.route('/cobranzas/<string:fecha>', methods=['GET'])(cobranzas)

app.route('/tabla_cobranzas', methods=['GET'])(tabla_cobranzas)

app.route('/planillas/<int:year>', methods=['GET'])(planillas)

app.route('/get_planillas', methods=['GET'])(get_planillas)

app.route('/borrar_cobranza', methods=['POST'])(borrar_cobranza)

app.route('/exportar_planilla', methods=['GET'])(exportar_planilla)

app.route('/exportar_informe', methods=['GET'])(exportar_informe)

app.route('/exportar_liquidacion/<chofer>/<fecha>', methods=['GET'])(exportar_liquidacion)

app.route('/exportar_precios', methods=['GET'])(exportar_precios)

app.route('/get_keywords/<keyword_type>', methods=['GET'])(get_keywords)

app.route('/get_precio', methods=['GET'])(get_precio)

app.route('/get_chapa', methods=['GET'])(get_chapa)

app.route('/palabras_clave', methods=['GET'])(palabras_clave)

app.route('/lista_claves/<string:tipo>', methods=['GET'])(lista_claves)

app.route('/borrar_clave/<string:tipo>', methods=['POST'])(borrar_clave)

app.route('/get_claves/<string:tipo>', methods=['GET'])(get_claves)

app.route('/lista_de_precios', methods=['GET'])(lista_de_precios)

app.route('/lista_precios', methods=['GET'])(lista_precios)

app.route('/borrar_precio', methods=['POST'])(borrar_precio)

app.route('/add_liquidacion/', methods=['POST'])(add_liquidacion)

app.route('/lista_de_liquidaciones', methods=['GET'])(lista_de_liquidaciones)

app.route('/get_liquidaciones', methods=['GET'])(get_liquidaciones)

app.route('/get_liquidaciones_fechas/<string:chofer>', methods=['GET'])(get_liquidaciones_fechas)

app.route('/liquidacion/<string:chofer>', methods=['GET'])(liquidacion)

app.route('/liquidacion_fecha/<string:lista>', methods=['GET'])(liquidacion_fecha)

app.route('/get_liquidaciones_pagado/<chofer>/<fecha>', methods=['GET'])(get_liquidaciones_pagado)

app.route('/liquidacion_pagado/<chofer>/<fecha>', methods=['POST'])(liquidacion_pagado)

app.route('/viajes/<chofer>/<fecha>', methods=['GET'])(viajes)

app.route('/add_viaje/<chofer>/<fecha_creacion>', methods=['POST'])(add_viaje)

app.route('/borrar_viaje/<int:id>', methods=['POST'])(borrar_viaje)

app.route('/tabla_viajes/<chofer>/<fecha>', methods=['GET'])(tabla_viajes)

app.route('/editar_viaje_precio/<int:id>/<float:precio>', methods=['POST'])(editar_viaje_precio)

app.route('/gastos/<chofer>/<fecha>', methods=['GET'])(gastos)

app.route('/add_gasto/<chofer>/<fecha_de_liquidacion>', methods=['POST'])(add_gasto)

app.route('/borrar_gasto/<int:id>', methods=['POST'])(borrar_gasto)

app.route('/tabla_gastos/<chofer>/<fecha>', methods=['GET'])(tabla_gastos)



def create_backup(script_directory_path):
    source_path = os.path.join(script_directory_path, "pagina_web.db")
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%d-%m-%Y_%H-%M-%S")
    backup_path = os.path.join(script_directory, f"backup/pagina_web_{formatted_datetime}.db")
    shutil.copy(source_path, backup_path)
    print("Database backup created.")

import signal
if __name__ == '__main__':
    print('*' * 50)
    print('\nLink de la página web: http://localhost:8080\n')
    print('*' * 50)
    app.run(host='127.0.0.1', port=8080)
    create_backup(script_directory)