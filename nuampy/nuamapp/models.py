from mongoengine import Document, StringField, FloatField, IntField, ListField, EmbeddedDocument, EmailField, DateTimeField, DecimalField, BooleanField, ReferenceField,DateField
import datetime
from django.db import models  #Esta importancion es una herramienta para crear tablas por si preguntan, mantenemos cierto orden asi etc etc

# Modelo para usuarios
class usuarios(Document):
    nombre = StringField(max_length=200, required=True)
    correo = EmailField(required=True, unique=True) 
    contrasena = StringField(max_length=200, required=True) 
    rol = BooleanField(default=False)
    ruc = StringField(max_length=12, required=True)
    
    meta = {
        'collection': 'usuarios'
    }
    
    def __str__(self):
        return self.nombre
#Modelo para calificaciones
class CalificacionTributaria(Document):
    meta = {'collection': 'calificaciones_tributarias'} #Esto solo es para decir el nombre de la collecion , porque por defecto es el nombre de la clase mas una S al final
    mercado = StringField()
    instrumento = StringField()
    anio = IntField()
    fecha_pago = DateField()
    secuencia_evento = IntField()
    dividendo = FloatField()
    valor_historico = FloatField()
    descripcion = StringField()
    isfut = StringField()
    factor_actualizacion = FloatField()
    tipo_sociedad = StringField()
    corredor = StringField()

    factores = ListField(FloatField())