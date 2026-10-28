"""
Lógica de negocio para los Diagnósticos clínicos.

Un Diagnóstico es un individuo de la clase :Diagnostico que se asocia a una
Consulta mediante la propiedad :tieneDiagnostico.

La ontología no define una propiedad de texto específica para el diagnóstico,
por lo que se usa 'nombre' (la propiedad de etiqueta disponible) y, si faltara,
el nombre interno del individuo. No se altera el esquema de clinica.owl.
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


def nombre_de(diagnostico):
    """Devuelve la etiqueta visible de un diagnóstico."""
    return _primer_valor(diagnostico, "nombre", diagnostico.name)

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_diagnosticos():
    """Devuelve todos los diagnósticos como lista de diccionarios."""
    return [
        {
            "id": diagnostico.name,
            "nombre": nombre_de(diagnostico),
        }
        for diagnostico in onto.Diagnostico.instances()
    ]

def obtener_diagnostico(diagnostico_id):
    """Busca un diagnóstico por su nombre interno, o devuelve None."""
    if not diagnostico_id:
        return None

    for diagnostico in onto.Diagnostico.instances():
        if diagnostico.name == diagnostico_id:
            return diagnostico

    return None

def crear_diagnostico(texto, guardar=True):
    """Crea un Diagnóstico con id único. Si 'guardar' es False, no persiste."""
    texto = texto_obligatorio(texto, "diagnóstico")

    diagnostico = onto.Diagnostico(
        generar_identificador("Diagnostico", onto.Diagnostico)
    )

    diagnostico.nombre = [texto]

    if guardar:
        guardar_ontologia()

    return diagnostico

def actualizar_diagnostico(diagnostico_id, texto):
    """Actualiza la etiqueta de un diagnóstico existente. Devuelve el individuo o None."""
    diagnostico = obtener_diagnostico(diagnostico_id)

    if diagnostico is None:
        return None

    texto = texto_obligatorio(texto, "diagnóstico")

    diagnostico.nombre = [texto]

    guardar_ontologia()

    return diagnostico

def eliminar_diagnostico(diagnostico_id):
    """Elimina un diagnóstico existente. Devuelve True si existía, False si no."""
    diagnostico = obtener_diagnostico(diagnostico_id)

    if diagnostico is None:
        return False

    destroy_entity(diagnostico)

    guardar_ontologia()

    return True
