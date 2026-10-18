"""
Lógica de negocio para la gestión de Médicos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

La especialidad se sigue tratando como propiedad de datos del médico
(propiedad 'especialidad'), conservando el mismo esquema que la vista original.
El identificador de un médico es el nombre interno del individuo (name),
generado con un UUID para evitar colisiones; las operaciones usan ese nombre
interno y no el texto mostrado. Los datos se validan antes de tocar la ontología.
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


def _nombre_de(medico):
    """Devuelve el nombre mostrado (propiedad 'nombre') de un médico."""
    return _primer_valor(medico, "nombre")


def obtener_medico(identificador):
    """Busca un médico por su nombre interno (name) o, como respaldo, por 'nombre'."""
    if not identificador:
        return None

    for medico in onto.Medico.instances():
        if medico.name == identificador:
            return medico

    for medico in onto.Medico.instances():
        if _nombre_de(medico) == identificador:
            return medico

    return None


def _existe_nombre(nombre, excluir=None):
    """Indica si ya hay un médico con ese nombre (excluyendo un individuo)."""
    for medico in onto.Medico.instances():

        if medico is excluir:
            continue

        if _nombre_de(medico) == nombre:
            return True

    return False

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_medicos():
    """Devuelve una lista de diccionarios con los datos de cada médico."""
    medicos = []

    for medico in onto.Medico.instances():

        medicos.append({
            "id": medico.name,
            "nombre": _nombre_de(medico),
            "especialidad": _primer_valor(medico, "especialidad"),
            "telefono": _primer_valor(medico, "telefono"),
        })

    return medicos

def crear_medico(nombre, especialidad, telefono):
    """Valida los datos, crea un médico con id único y persiste la ontología."""

    nombre = texto_obligatorio(nombre, "nombre")
    especialidad = texto_obligatorio(especialidad, "especialidad")
    telefono = texto_obligatorio(telefono, "teléfono")

    if _existe_nombre(nombre):
        raise ValueError("Ya existe un médico con ese nombre.")

    with onto:

        nuevo = onto.Medico(generar_identificador("Medico", onto.Medico))

        nuevo.nombre = [nombre]
        nuevo.especialidad = [especialidad]
        nuevo.telefono = [telefono]

    guardar_ontologia()

    return nuevo

def actualizar_medico(medico_id, nuevo_nombre, nueva_especialidad, nuevo_telefono):
    """Actualiza un médico (identificado por su nombre interno) o devuelve None."""

    medico = obtener_medico(medico_id)

    if medico is None:
        return None

    nuevo_nombre = texto_obligatorio(nuevo_nombre, "nombre")
    nueva_especialidad = texto_obligatorio(nueva_especialidad, "especialidad")
    nuevo_telefono = texto_obligatorio(nuevo_telefono, "teléfono")

    if _existe_nombre(nuevo_nombre, excluir=medico):
        raise ValueError("Ya existe otro médico con ese nombre.")

    medico.nombre = [nuevo_nombre]
    medico.especialidad = [nueva_especialidad]
    medico.telefono = [nuevo_telefono]

    guardar_ontologia()

    return medico

def eliminar_medico(medico_id):
    """Elimina un médico existente. Devuelve True si existía, False en caso contrario."""

    medico = obtener_medico(medico_id)

    if medico is None:
        return False

    destroy_entity(medico)

    guardar_ontologia()

    return True
