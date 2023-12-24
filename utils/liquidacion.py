from utils.schema import *
from utils.utils import *

from flask import render_template, request, redirect, url_for, jsonify

from datetime import datetime
from sqlalchemy.exc import IntegrityError
import locale



def add_liquidacion():
    chofer = request.form.get('chofer')
    chapa = request.form.get('chapa')

    # entrada existe en la tabla de lista de planillas
    existing_entry = ListaDeChapas.query.filter_by(chofer=chofer, chapa=chapa).first()
    if existing_entry is None:
        #  agregar nueva entrada
        new_liquidacion = ListaDeChapas(chofer=chofer, chapa=chapa)

        try:
            db.session.add(new_liquidacion)
            db.session.commit()
            print("Nueva entrada en lista de choferes")

            new_entry = Liquidaciones(chofer=chofer, fecha_de_liquidacion=datetime.now())

            db.session.add(new_entry)
            db.session.commit()
            print("Nueva entrada en lista de liquidaciones")

        except IntegrityError:
            db.session.rollback()
            print("Error: No se pudo agregar la entrada a la lista de choferes")
    else:
        print("Chofer ya existe en la lista de choferes")

    return redirect(url_for('lista_de_liquidaciones'))


def lista_de_liquidaciones():
    return render_template('lista_de_liquidaciones.html')


def get_liquidaciones():
    # Filtrar las planillas por año utilizando SQLAlchemy
    liquidaciones = ListaDeChapas.query.all()
    liquidaciones_ordenadas = sorted(liquidaciones, key=lambda liquidacion: liquidacion.chofer)

    return jsonify([liquidacion.chofer for liquidacion in liquidaciones_ordenadas])


def get_liquidaciones_fechas(chofer):
    # Filtrar las planillas por año utilizando SQLAlchemy
    liquidaciones = Liquidaciones.query.filter_by(chofer=chofer).all()
    liquidaciones_ordenadas = sorted(liquidaciones, key=lambda liquidacion: liquidacion.fecha_de_liquidacion)

    return jsonify([f'{liquidacion.chofer},{liquidacion.fecha_de_liquidacion.strftime("%Y-%m-%d")}' for liquidacion in liquidaciones_ordenadas])


def liquidacion(chofer):
    return render_template('liquidacion.html', chofer=chofer)



def liquidacion_fecha(lista):
    lista = lista.split(',')
    return render_template('liquidacion_botones.html', chofer=lista[0], fecha=lista[1])


def get_liquidaciones_pagado(chofer, fecha):
    liquidacion = Liquidaciones.query.filter_by(chofer=chofer, fecha_de_liquidacion=fecha).first()
    return jsonify(liquidacion.pagado)


def liquidacion_pagado(chofer, fecha):
    liquidacion = Liquidaciones.query.filter_by(chofer=chofer, fecha_de_liquidacion=fecha).first()
    db.session.commit()

    try:
        liquidacion.pagado = True
        new_entry = Liquidaciones(chofer=chofer, fecha_de_liquidacion=datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d').date())

        db.session.add(new_entry)
        db.session.commit()
        print("Nueva entrada en lista de liquidaciones")

    except IntegrityError:
        db.session.rollback()
        print("Error: No se pudo agregar la entrada a la lista de choferes")
    return jsonify(None)


def viajes(chofer, fecha):
    return render_template('viajes.html', chofer=chofer, fecha=fecha)


def add_viaje(chofer, fecha_creacion):
    fecha = request.form.get('fecha')
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date() 
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

    # Modificar la entrada existente y poner precio nuevo

    liq = LiquidacionesViajes(chofer=chofer, fecha_de_liquidacion=fecha_creacion, precio=precio, id=last_inserted_id, total=total)

    try:
        db.session.add(liq)
        db.session.commit()
        print("Nueva entrada en lista de liquidaciones agregada")
    except IntegrityError:
        db.session.rollback()
        print("No se pudo cargar nueva entrada en lista de liquidaciones")

    return redirect(url_for('viajes', chofer=chofer, fecha=fecha_creacion))


def borrar_viaje(id):
    viaje = db.session.get(LiquidacionesViajes, id)
    
    if viaje:
        try:
            db.session.delete(viaje)
            db.session.commit()
            return jsonify({'message': 'Viaje eliminada exitosamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar la Viaje'}), 500
    else:
        return jsonify({'error': 'Viaje no encontrada'}), 404


def tabla_viajes(chofer, fecha):
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajusta esto según tus necesidades
    
    # Perform an inner join between Cobranza and Liquidaciones based on 'chofer' and 'fecha_de_liquidacion'
    results = db.session.query(Cobranza, LiquidacionesViajes).join(
        LiquidacionesViajes,
        Cobranza.id == LiquidacionesViajes.id
    ).filter(
        Cobranza.chofer == chofer,
        LiquidacionesViajes.fecha_de_liquidacion == fecha
    ).all()
    
    # Ordena las cobranzas por las columnas 'origen' y 'destino'
    results_sorted = sorted(results, key=lambda result: (result[0].origen, result[0].destino))

    # Editar el precio directamente en cobranzas_ordenadas y formatear con coma como separador decimal
    for cobranza, liquidacion in results_sorted:
        cobranza.kilos_origen = locale.format_string("%d", cobranza.kilos_origen, grouping=True)
        cobranza.kilos_destino = locale.format_string("%d", cobranza.kilos_destino, grouping=True)
        cobranza.diferencia_de_tolerancia = locale.format_string("%d", cobranza.diferencia_de_tolerancia, grouping=True)
        liquidacion.total = locale.format_string("%d", redondear(Decimal(liquidacion.precio) * Decimal(cobranza.kilos_destino)), grouping=True, monetary=True)

        liquidacion.precio = locale.format_string("%.2f", liquidacion.precio, grouping=True, monetary=True)
    
    return render_template('tabla_viaje_content.html', results=results_sorted)


def editar_viaje_precio(id, precio):
    viaje = db.session.get(LiquidacionesViajes, {"id": id})
    
    if viaje:
        try:
            viaje.precio = precio

            cobranza = db.session.get(Cobranza, {"id": id})
            viaje.total = redondear(Decimal(viaje.precio) * Decimal(cobranza.kilos_destino))
            db.session.commit()

            return jsonify({'message': 'Precio editado exitosamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error al editar la precio'}), 500
    else:
        return jsonify({'error': 'Precio no encontrado'}), 404



def gastos(chofer, fecha):
    return render_template('gastos.html', chofer=chofer, fecha=fecha)


def add_gasto(chofer, fecha_de_liquidacion):
    fecha = request.form.get('fecha')
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date() 
    fecha_de_liquidacion = datetime.strptime(fecha_de_liquidacion, '%Y-%m-%d').date() 

    boleta = request.form.get('boleta').replace('.', '')

    if boleta:
        boleta = int(boleta)
    else:
        boleta = None

    importe = int(request.form.get('importe').replace('.', ''))

    new_gasto = LiquidacionesGastos(
        chofer=chofer, 
        fecha=fecha, 
        boleta=boleta, 
        importe=importe, 
        fecha_de_liquidacion=fecha_de_liquidacion
        )

    db.session.add(new_gasto)
    db.session.commit()

    return redirect(url_for('gastos', chofer=chofer, fecha=fecha_de_liquidacion))


def borrar_gasto(id):
    gasto = db.session.get(LiquidacionesGastos, id)
    
    if gasto:
        try:
            db.session.delete(gasto)
            db.session.commit()
            return jsonify({'message': 'Gasto eliminado exitosamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar el gasto'}), 500
    else:
        return jsonify({'error': 'Gasto no encontrado'}), 404



def tabla_gastos(chofer, fecha):
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Ajusta esto según tus necesidades
    
    # Perform an inner join between Cobranza and Liquidaciones based on 'chofer' and 'fecha_de_liquidacion'
    gastos_sin_boleta = LiquidacionesGastos.query.filter_by(chofer=chofer, fecha_de_liquidacion=fecha, boleta=None).all()
    gastos_con_boleta = LiquidacionesGastos.query.filter_by(chofer=chofer, fecha_de_liquidacion=fecha).filter(LiquidacionesGastos.boleta.isnot(None)).all()

    for gasto in gastos_sin_boleta:
        gasto.importe = locale.format_string("%d", gasto.importe, grouping=True)

    for gasto in gastos_con_boleta:
        gasto.importe = locale.format_string("%d", gasto.importe, grouping=True)
        

    # Ordenar los resultados por importe en orden ascendente
    gastos_sin_boleta_ordenado = sorted(gastos_sin_boleta, key=lambda x: x.id)
    gastos_con_boleta_ordenado = sorted(gastos_con_boleta, key=lambda x: x.id)

    # Rellenar las listas para que tengan la misma longitud con None si es necesario
    max_len = max(len(gastos_sin_boleta_ordenado), len(gastos_con_boleta_ordenado))
    gastos_sin_boleta_ordenado += [None] * (max_len - len(gastos_sin_boleta_ordenado))
    gastos_con_boleta_ordenado += [None] * (max_len - len(gastos_con_boleta_ordenado))

    # Combinar las listas en una lista de tuplas
    results = zip(gastos_sin_boleta_ordenado, gastos_con_boleta_ordenado)

    return render_template('tabla_gasto_content.html', results=results)

