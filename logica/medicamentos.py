"""
Lógica de negocio para la gestión de Medicamentos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

El identificador de un medicamento es el nombre interno del individuo (name),
que se mantiene legible (sin espacios) porque es el texto que se muestra en la
tabla. Las operaciones usan ese nombre interno y no la propiedad 'nombre'. Los
datos se validan antes de tocar la ontología.
"""

from owlready2 import destroy_entity

from logica.ontologia import guardar_ontologia, onto
from logica.validaciones import texto_obligatorio, validar_dosis

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)

    if valores:
        return valores[0]

    return defecto


def _slug(nombre):
    """Convierte un nombre a un identificador interno legible (sin espacios)."""
    return nombre.strip().replace(" ", "_")


def obtener_medicamento(identificador):
    """Busca un medicamento por su nombre interno (name) o, como respaldo, por 'nombre'."""
    if not identificador:
        return None

    for medicamento in onto.Medicamento.instances():
        if medicamento.name == identificador:
            return medicamento

    for medicamento in onto.Medicamento.instances():
        if _primer_valor(medicamento, "nombre") == identificador:
            return medicamento

    return None

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_medicamentos():
    """Devuelve una lista de diccionarios con los datos de cada medicamento."""
    medicamentos = []

    for medicamento in onto.Medicamento.instances():

        medicamentos.append({
            "id": medicamento.name,
            "nombre": medicamento.name,
            "dosis": _primer_valor(medicamento, "dosis"),
            "descripcion": _primer_valor(medicamento, "descripcion"),
        })

    return medicamentos

def obtener_dosis_base(nombre):
    """Devuelve la dosis base de un medicamento (por nombre interno), o ''."""
    medicamento = obtener_medicamento(nombre)

    if medicamento is None:
        return ""

    return _primer_valor(medicamento, "dosis")

def crear_medicamento(nombre, dosis, descripcion):
    """Valida los datos y crea un medicamento con id interno único.

    Lanza ValueError si el nombre ya está en uso.
    """

    nombre = texto_obligatorio(nombre, "nombre")
    dosis = validar_dosis(dosis, "dosis base")

    identificador = _slug(nombre)

    if obtener_medicamento(identificador) is not None:
        raise ValueError("Ya existe un medicamento con ese nombre.")

    nuevo = onto.Medicamento(identificador)

    nuevo.nombre = [nombre]
    nuevo.dosis = [dosis]

    if descripcion != "":

        nuevo.descripcion = [descripcion]

    guardar_ontologia()

    return nuevo

def actualizar_medicamento(medicamento_id, nuevo_nombre, nueva_dosis, nueva_descripcion):
    """Actualiza un medicamento (identificado por su nombre interno) o devuelve None."""

    medicamento = obtener_medicamento(medicamento_id)

    if medicamento is None:
        return None

    nuevo_nombre = texto_obligatorio(nuevo_nombre, "nombre")
    nueva_dosis = validar_dosis(nueva_dosis, "dosis base")

    nuevo_identificador = _slug(nuevo_nombre)

    if (
        nuevo_identificador != medicamento.name
        and obtener_medicamento(nuevo_identificador) is not None
    ):
        raise ValueError("Ya existe otro medicamento con ese nombre.")

    medicamento.nombre = [nuevo_nombre]
    medicamento.dosis = [nueva_dosis]

    if nueva_descripcion != "":

        medicamento.descripcion = [nueva_descripcion]

    else:

        medicamento.descripcion = []

    guardar_ontologia()

    return medicamento

def eliminar_medicamento(medicamento_id):
    """Elimina un medicamento existente. Devuelve True si existía, False si no."""

    medicamento = obtener_medicamento(medicamento_id)

    if medicamento is None:
        return False

    destroy_entity(medicamento)

    guardar_ontologia()

    return True
