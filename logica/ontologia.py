"""
Carga y persistencia de la ontología 'clinica.owl'.

Centraliza la resolución de la ruta del archivo (respecto a la raíz del
proyecto), el guardado y la generación de identificadores únicos, para que toda
la capa de lógica persista de forma consistente y sin depender del directorio de
trabajo actual.
"""

import os
import uuid

from owlready2 import get_ontology

# -----------------------------
# RUTA CENTRALIZADA
# -----------------------------

# logica/ontologia.py -> raíz del proyecto (carpeta padre de 'logica')
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

RUTA_ONTOLOGIA = os.path.join(
    BASE_DIR,
    "clinica.owl"
)

# -----------------------------
# CARGA
# -----------------------------

onto = get_ontology(RUTA_ONTOLOGIA).load()

# -----------------------------
# IDENTIFICADORES
# -----------------------------

def generar_identificador(prefijo, clase):
    """Genera un nombre de individuo único para la clase indicada.

    Usa un UUID aleatorio en lugar de contadores secuenciales, de modo que crear
    o eliminar registros nunca provoca colisiones de identificadores.
    """

    while True:

        candidato = f"{prefijo}_{uuid.uuid4().hex}"

        if all(individuo.name != candidato for individuo in clase.instances()):
            return candidato

# -----------------------------
# GUARDADO
# -----------------------------

def guardar_ontologia():
    """Persiste la ontología en clinica.owl usando la ruta centralizada."""
    onto.save(file=RUTA_ONTOLOGIA)
