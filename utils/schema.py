from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


db = SQLAlchemy()

#tablas de la base de datos
class Cobranza(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    liquidaciones_viajes = relationship("LiquidacionesViajes", backref="liquidaciones_viajes", cascade="all, delete-orphan")
    fecha = db.Column(db.Date, nullable=False)
    chofer = db.Column(db.String(100), nullable=False)
    chapa = db.Column(db.String(100))
    producto = db.Column(db.String(100))
    origen = db.Column(db.String(100))
    destino = db.Column(db.String(100))
    tiquet = db.Column(db.BigInteger, nullable=False)
    kilos_origen = db.Column(db.Integer, nullable=False)
    kilos_destino = db.Column(db.Integer, nullable=False)
    diferencia = db.Column(db.Integer, nullable=False)
    tolerancia = db.Column(db.Integer, nullable=False)
    diferencia_de_tolerancia = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    total = db.Column(db.BigInteger, nullable=False)
    fecha_de_creacion = db.Column(db.Date, nullable=False)

class ListaDePlanillas(db.Model):
    fecha = db.Column(db.Date, nullable=False, primary_key=True)

tipo_clave = {'chofer', 'producto', 'origen', 'destino'} #tipos de palabras clave (a usar en tabla PalabraClave)
class PalabraClave(db.Model):
    palabra = db.Column(db.String(100), nullable=False, primary_key=True)
    tipo = db.Column(db.String(100), nullable=False, primary_key=True)


class ListaDePrecios(db.Model):
    origen = db.Column(db.String(100), nullable=False, primary_key=True)
    destino = db.Column(db.String(100), nullable=False, primary_key=True)
    precio = db.Column(db.Float, nullable=False)


class ListaDeChapas(db.Model):
    chofer = db.Column(db.String(100), nullable=False, primary_key=True)
    chapa = db.Column(db.String(100), nullable=False, primary_key=True)


class LiquidacionesViajes(db.Model):
    id = db.Column(db.Integer,ForeignKey('cobranza.id', ondelete='CASCADE'), primary_key=True)
    chofer = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    fecha_de_liquidacion = db.Column(db.Date, nullable=False)
    total = db.Column(db.BigInteger, nullable=False)


class LiquidacionesGastos(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    chofer = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    boleta = db.Column(db.Integer, nullable=True)
    importe = db.Column(db.BigInteger, nullable=False)
    fecha_de_liquidacion = db.Column(db.Date, nullable=False)


class Liquidaciones(db.Model):
    chofer = db.Column(db.String(100), nullable=False, primary_key=True)
    fecha_de_liquidacion = db.Column(db.Date, nullable=False, primary_key=True)
    pagado = db.Column(db.Boolean, default=False, nullable=False)