from utils.schema import *
from utils.utils import *

from flask import render_template, request, jsonify


def get_keywords(keyword_type):
    if keyword_type in tipo_clave:
        term = request.args.get('term')  # Obtiene el término de la consulta
        if term is not None:
            keywords = PalabraClave.query.filter(PalabraClave.palabra.ilike(f'%{term}%'), 
                                                 PalabraClave.tipo == keyword_type).limit(10).all()

            keyword_list = [keyword.palabra for keyword in keywords]
            return jsonify(keyword_list)
        else:
            return jsonify({'error': 'Missing term parameter'}), 400
    else:
        return jsonify({'error': 'Invalid keyword type'}), 400


def get_precio():
    origen = request.args.get('origen')  # Obtiene el valor del origen
    destino = request.args.get('destino')  # Obtiene el valor del destino

    if origen is not None and destino is not None:
        precio = ListaDePrecios.query.filter_by(origen=origen, destino=destino).first()

        if precio is not None:
            precio = precio.precio

        return jsonify(precio)
    else:
        return jsonify(None)
    

def get_chapa():
    chofer = request.args.get('chofer')  # Obtiene el valor del origen

    if chofer is not None:
        chapa = ListaDeChapas.query.filter_by(chofer=chofer).first()

        if chapa is not None:
            chapa = chapa.chapa

        return jsonify(chapa)
    else:
        return jsonify(None)


def palabras_clave():
    return render_template('palabras_clave.html')


def lista_claves(tipo):
    return render_template('lista_de_claves.html', tipo=tipo)


def borrar_clave(tipo):
    lista = request.form.get('lista')
    lista = lista.split(',')

    if tipo == 'chapa':
        for palabra in lista:
            palabra = palabra.split('.')
            entry = ListaDeChapas.query.filter_by(chofer=palabra[0], chapa=palabra[1]).first()
            try:
                db.session.delete(entry)
                db.session.commit()  # Confirmar los cambios en la base de datos

            except Exception as e:
                db.session.rollback()  # Revertir la transacción en caso de error
                return jsonify({'error': 'Chapa clave no eliminada'}), 404
    else:
        for palabra in lista:
            entry = PalabraClave.query.filter_by(tipo=tipo, palabra=palabra).first()

            try:
                db.session.delete(entry)
                db.session.commit()  # Confirmar los cambios en la base de datos

            except Exception as e:
                db.session.rollback()  # Revertir la transacción en caso de error
                return jsonify({'error': 'Palabra clave no eliminada'}), 404

    return jsonify({'message': 'Palabra clave eliminada exitosamente'}), 200


def get_claves(tipo):
    # Filtrar las planillas por año utilizando SQLAlchemy
    if tipo == 'chapa':
        chapas = ListaDeChapas.query.all()
        return jsonify([f'{chapa.chofer}.{chapa.chapa}' for chapa in chapas])

    else:
        palabras = PalabraClave.query.filter_by(tipo=tipo).all()
        
        # Ordenar las planillas por fecha
        palabras_ordenadas = sorted(palabras, key=lambda palabra: palabra.palabra)
        return jsonify([palabra.palabra for palabra in palabras_ordenadas])

