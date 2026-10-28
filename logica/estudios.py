"""
Lógica de negocio para los Estudios Médicos.

Un Estudio Médico es un individuo de la clase :EstudioMedico que se asocia a una
Consulta mediante la propiedad :solicitaEstudio.

La ontología no define una propiedad de texto específica para el estudio, por lo
que se usa 'nombre' (la propiedad de etiqueta disponible) y, si faltara, el
nombre interno del individuo. No se altera el esquema de clinica.owl.
"""

from owlready2 import destroy_entity

from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.validaciones import texto_obligatorio

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)

    if valores:
        return valores[0]

    return defecto


def nombre_de(estudio):
    """Devuelve la etiqueta visible de un estudio médico."""
    return _primer_valor(estudio, "nombre", estudio.name)

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_estudios():
    """Devuelve todos los estudios médicos como lista de diccionarios."""
    return [
        {
            "id": estudio.name,
            "nombre": nombre_de(estudio),
        }
        for estudio in onto.EstudioMedico.instances()
    ]

def obtener_estudio(estudio_id):
    """Busca un estudio por su nombre interno, o devuelve None."""
    if not estudio_id:
        return None

    for estudio in onto.EstudioMedico.instances():
        if estudio.name == estudio_id:
            return estudio

    return None

def crear_estudio(nombre, guardar=True):
    """Crea un Estudio Médico con id único. Si 'guardar' es False, no persiste."""
    nombre = texto_obligatorio(nombre, "estudio")

    estudio = onto.EstudioMedico(
        generar_identificador("Estudio", onto.EstudioMedico)
    )

    estudio.nombre = [nombre]

    if guardar:
        guardar_ontologia()

    return estudio

def actualizar_estudio(estudio_id, nombre):
    """Actualiza la etiqueta de un estudio existente. Devuelve el individuo o None."""
    estudio = obtener_estudio(estudio_id)

    if estudio is None:
        return None

    nombre = texto_obligatorio(nombre, "estudio")

    estudio.nombre = [nombre]

    guardar_ontologia()

    return estudio

def eliminar_estudio(estudio_id):
    """Elimina un estudio existente. Devuelve True si existía, False si no."""
    estudio = obtener_estudio(estudio_id)

    if estudio is None:
        return False

    destroy_entity(estudio)

    guardar_ontologia()

    return True
