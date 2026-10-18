"""
Carga y persistencia de la ontología 'clinica.owl'.

Centraliza la resolución de la ruta del archivo (respecto a la raíz del
proyecto) y el guardado, para que toda la capa de lógica persista de forma
consistente y sin depender del directorio de trabajo actual.
"""

import os

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
# GUARDADO
# -----------------------------

def guardar_ontologia():
    """Persiste la ontología en clinica.owl usando la ruta centralizada."""
    onto.save(file=RUTA_ONTOLOGIA)
