# services.py
# Aquí moveremos la lógica que antes estaba en Streamlit
# Ej: carga de CSV, cálculo de factores, etc.

import csv
from mongoengine import Document, StringField, FloatField, DateTimeField, BooleanField

# Modelo temporal para factores (luego lo completamos según tu CSV original)
class CalificacionTributaria(Document):
    mercado = StringField()
    instrumento = StringField()
    ano = StringField()
    fecha_pago = StringField()
    descripcion = StringField()
    dividendo = FloatField()
    factor_8 = FloatField()
    factor_9 = FloatField()
    
    meta = {'collection': 'calificaciones'}

# Función para procesar CSV
def procesar_csv(file):
    decoded = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)

    registros = []
    for row in reader:
        registro = CalificacionTributaria(
            mercado=row.get("mercado"),
            instrumento=row.get("instrumento"),
            ano=row.get("año"),
            fecha_pago=row.get("fecha_pago"),
            descripcion=row.get("descripcion"),
            dividendo=float(row.get("dividendo", 0) or 0),
            factor_8=float(row.get("factor_8", 0) or 0),
            factor_9=float(row.get("factor_9", 0) or 0)
        )
        registro.save()
        registros.append(registro)

    return registros