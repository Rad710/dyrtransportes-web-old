from utils.schema import *
from utils.utils import *

from flask import render_template, request, redirect, url_for, jsonify, make_response
from sqlalchemy import extract

from datetime import datetime
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
import locale


def add_cobranza(fecha_creacion):
    fecha = request.form.get('fecha')
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date() 
    chofer = request.form.get('chofer')
    chapa = request.form.get('chapa')
    producto = request.form.get('producto')
    origen = request.form.get('origen')
    destino = request.form.get('destino')
    tiquet = int(request.form.get('tiquet').replace('.', ''))
    kilos_origen = int(request.form.get('kilos_origen').replace('.', ''))
    kilos_destino = int(request.form.get('kilos_destino').replace('.', ''))
    diferencia = kilos_destino - kilos_origen
    tolerancia = redondear(Decimal(kilos_origen) * Decimal(0.002))
    diferencia_de_tolerancia = diferencia + tolerancia
    precio = float(request.form.get('precio'))
    total = redondear(Decimal(precio) * Decimal(kilos_destino))
    
    fecha_creacion = datetime.strptime(fecha_creacion, '%Y-%m-%d').date() 
    
    # entrada existe en la tabla de lista de planillas
    existing_entry = ListaDePlanillas.query.filter_by(fecha=fecha).first()
    if existing_entry is None:
        #  agregar nueva entrada
        new_planilla = ListaDePlanillas(
            fecha=fecha_creacion,
        )

        try:
            db.session.add(new_planilla)
            db.session.commit()
            print("Nueva entrada en lista de planillas")
        except IntegrityError:
            db.session.rollback()
            print("Error: No se pudo agregar la entrada a la lista de planillas")
    else:
        print("Fecha ya existe en la lista de planillas")

    palabras_clave = {'chofer': chofer, 'producto': producto, 'origen': origen, 'destino': destino}

    for tipo in tipo_clave:
        # revisar si entrada en la table de palabras claves ya existe
        existing_entry = PalabraClave.query.filter_by(palabra=palabras_clave[tipo], tipo=tipo).first()
        if existing_entry is None:
            # nueva entrada
            new_clave = PalabraClave(palabra=palabras_clave[tipo], tipo=tipo)

            try:
                db.session.add(new_clave)
                db.session.commit()
                print(f'Nueva entrada en palabras clave de tipo: {tipo}')
            except IntegrityError:
                db.session.rollback()
                print('No se pudo cargar nueva palabras clave de tipo: {tipo}')


    existing_entry = ListaDePrecios.query.filter_by(origen=origen, destino=destino).first()
    if existing_entry is None:
        # nueva entrada
        new_precio = ListaDePrecios(origen=origen, destino=destino, precio=precio)

        try:
            db.session.add(new_precio)
            db.session.commit()
            print("Nuevo precio en lista de precios")
        except IntegrityError:
            db.session.rollback()
            print("No se pudo cargar nuevo precio el lista de precios")
    else:
        # Modificar la entrada existente y poner precio nuevo
        existing_entry.precio = precio

        try:
            db.session.commit()
            print("Se actualizó un precio en la lista de precios.")
        except:
            db.session.rollback()
            print("No se pudo actualizar precio de lista de precios")


    existing_entry = ListaDeChapas.query.filter_by(chofer=chofer).first()
    if existing_entry is None:
        # nueva entrada
        new_chapa = ListaDeChapas(chofer=chofer, chapa=chapa)

        try:
            db.session.add(new_chapa)
            db.session.commit()
            print("Nueva chapa en lista de chapas")
        except IntegrityError:
            db.session.rollback()
            print("No se pudo cargar nueva chapa en lista de chapas")
    else:
        # Modificar la entrada existente y poner precio nuevo
        existing_entry.chapa = chapa

        try:
            db.session.commit()
            print("Se actualizó una chapa en la lista de chapas.")
        except:
            db.session.rollback()
            print("No se pudo actualizar chapa de lista de chapas")

    new_cobranza = Cobranza(
        fecha=fecha,
        chofer=chofer,
        chapa=chapa,
        producto=producto,
        origen=origen,
        destino=destino,
        tiquet=tiquet,
        kilos_origen=kilos_origen,
        kilos_destino=kilos_destino,
        diferencia=diferencia,
        tolerancia=tolerancia,
        diferencia_de_tolerancia=diferencia_de_tolerancia,
        precio=precio,
        total=total,
        fecha_de_creacion=fecha_creacion
    )

    db.session.add(new_cobranza)
    db.session.commit()

    last_inserted_id = new_cobranza.id

    existing_entries = Liquidaciones.query.filter_by(chofer=chofer).all()
    if not existing_entries:
        # nueva entrada
        new_liquidacion = Liquidaciones(chofer=chofer, fecha_de_liquidacion=datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d').date() )
        try:
            db.session.add(new_liquidacion)
            db.session.commit()
            print("Nueva fecha de liquidacion agregada")

            ultima_liquidacion = new_liquidacion.fecha_de_liquidacion

        except IntegrityError:
            db.session.rollback()
            print("No se pudo cargar nueva fecha de liquidacion")
    else:
        liquidaciones_ordenadas = sorted(existing_entries, key=lambda liq: liq.fecha_de_liquidacion)
        ultima_liquidacion = liquidaciones_ordenadas[-1].fecha_de_liquidacion

    liq = LiquidacionesViajes(chofer=chofer, fecha_de_liquidacion=ultima_liquidacion, precio=precio, id=last_inserted_id, total=total)

    try:
        db.session.add(liq)
        db.session.commit()
        print("Nueva entrada en lista de liquidaciones agregada")
    except IntegrityError:
        db.session.rollback()
        print("No se pudo cargar nueva entrada en lista de liquidaciones")

    return redirect(url_for('cobranzas', fecha=fecha_creacion))


def add_planilla(year):
    fecha = request.form.get('fecha')
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date() 

    # entrada existe en la tabla de lista de planillas
    existing_entry = ListaDePlanillas.query.filter_by(fecha=fecha).first()
    if existing_entry is None:
        #  agregar nueva entrada
        new_planilla = ListaDePlanillas(
            fecha=fecha,
        )

        try:
            db.session.add(new_planilla)
            db.session.commit()
            print("Nueva entrada en lista de planillas")
        except IntegrityError:
            db.session.rollback()
            print("Error: No se pudo agregar la entrada a la lista de planillas")
    else:
        print("Fecha ya existe en la lista de planillas")

    return redirect(url_for('planillas', year=year))


def cobranzas(fecha):
    return render_template('cobranzas.html', fecha=fecha)


def tabla_cobranzas():
    fecha = request.args.get('fecha')
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajusta esto según tus necesidades

    cobranzas = Cobranza.query.filter_by(fecha_de_creacion=fecha).all()

    # Crea un diccionario para almacenar las sumas de subtotales por grupo
    subtotales_origen = defaultdict(int)
    subtotales_destino = defaultdict(int)
    subtotales_dif = defaultdict(int)
    subtotales = defaultdict(int)

    cambio_de_grupo = defaultdict(int)

    #calcula los subtotales
    for cobranza in cobranzas:
        grupo = (cobranza.origen, cobranza.destino)
        subtotales_origen[grupo] += cobranza.kilos_origen
        subtotales_destino[grupo] += cobranza.kilos_destino
        subtotales_dif[grupo] += cobranza.diferencia_de_tolerancia
        subtotales[grupo] += cobranza.total

        cambio_de_grupo[grupo] = cobranza.tiquet

    subtotales_origen = formatear_dict_numero(subtotales_origen)
    subtotales_destino = formatear_dict_numero(subtotales_destino)
    subtotales_dif = formatear_dict_numero(subtotales_dif)
    subtotales = formatear_dict_numero(subtotales)
    
    # Ordena las cobranzas por las columnas 'origen' y 'destino'
    cobranzas_ordenadas = sorted(cobranzas, key=lambda cobranza: (cobranza.origen, cobranza.destino))

    # Editar el precio directamente en cobranzas_ordenadas y formatear con coma como separador decimal
    for cobranza in cobranzas_ordenadas:
        cobranza.kilos_origen = locale.format_string("%d", cobranza.kilos_origen, grouping=True)
        cobranza.kilos_destino = locale.format_string("%d", cobranza.kilos_destino, grouping=True)
        cobranza.diferencia_de_tolerancia = locale.format_string("%d", cobranza.diferencia_de_tolerancia, grouping=True)
        cobranza.total = locale.format_string("%d", cobranza.total, grouping=True, monetary=True)

        cobranza.precio = locale.format_string("%.2f", cobranza.precio, grouping=True, monetary=True)

    return render_template('tabla_cobranzas_content.html', cobranzas=cobranzas_ordenadas, subtotales_origen=subtotales_origen, 
                        subtotales_destino=subtotales_destino, cambio_de_grupo=cambio_de_grupo, subtotales=subtotales,
                        subtotales_dif=subtotales_dif)


def planillas(year):
    return render_template('lista_de_planillas.html', year=year)


def get_planillas():
    year = request.args.get('year')
    # Filtrar las planillas por año utilizando SQLAlchemy
    planillas = ListaDePlanillas.query.filter(extract('year', ListaDePlanillas.fecha) == year).all()
    
    # Ordenar las planillas por fecha
    planillas_ordenadas = sorted(planillas, key=lambda planilla: planilla.fecha)

    # Crear una lista de fechas de planillas en formato 'YYYY-MM-DD'
    fechas_planillas = [planilla.fecha.strftime('%Y-%m-%d') for planilla in planillas_ordenadas]

    return jsonify(fechas_planillas)


def borrar_cobranza():
    id = request.form.get('id')
    cobranza = db.session.get(Cobranza, id)
    
    if cobranza:
        try:
            db.session.delete(cobranza)
            db.session.commit()
            return jsonify({'message': 'Cobranza eliminada exitosamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar la cobranza'}), 500
    else:
        return jsonify({'error': 'Cobranza no encontrada'}), 404