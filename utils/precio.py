from utils.schema import *
from utils.utils import *

from flask import render_template, jsonify, request

import locale


def lista_de_precios():
    return render_template('lista_de_precios.html')


def lista_precios():
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajusta esto según tus necesidades

    precios = ListaDePrecios.query.all()
    
    # Ordena las cobranzas por las columnas 'origen' y 'destino'
    precios_ordenados = sorted(precios, key=lambda precio: (precio.origen, precio.destino))

    # Editar el precio directamente en cobranzas_ordenadas y formatear con coma como separador decimal
    for precio in precios_ordenados:
        precio.precio = locale.format_string("%.2f", precio.precio, grouping=True, monetary=True)

    return render_template('lista_de_precios_content.html', precios=precios_ordenados)


def borrar_precio():
    lista = request.form.get('id')
    lista = lista.split(',')
    (origen, destino, precio) = lista[0], lista[1], lista[2]

    entrada = ListaDePrecios.query.filter_by(origen=origen, destino=destino, precio=precio).first()
    
    if entrada:
        try:
            db.session.delete(entrada)
            db.session.commit()
            return jsonify({'message': 'Precio eliminado exitosamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar precio'}), 500
    else:
        return jsonify({'error': 'Precio no encontrado'}), 404