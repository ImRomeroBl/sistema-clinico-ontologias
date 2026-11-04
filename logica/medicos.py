"""
Lógica de negocio para la gestión de Médicos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

La especialidad se modela como un individuo de :Especialidad vinculado al médico
mediante la Object Property :tieneEspecialidad. El texto introducido en la
interfaz se reutiliza si ya existe o se registra como una nueva especialidad.
El identificador de un médico es el nombre interno del individuo (name),
generado con un UUID para evitar colisiones; las operaciones usan ese nombre
interno y no el texto mostrado. Los datos se validan antes de tocar la ontología.
"""

import re

from owlready2 import destroy_entity

from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.validaciones import (
    formatear_telefono,
    texto_obligatorio,
    validar_telefono,
)

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


def _etiqueta_especialidad(especialidad):
    """Devuelve la etiqueta visible de un individuo :Especialidad."""
    etiquetas = list(getattr(especialidad, "label", []) or [])

    if etiquetas:
        return str(etiquetas[0])

    return str(especialidad.name).replace("_", " ").strip()


def _especialidad_de(medico):
    """Devuelve el texto de la primera especialidad semántica del médico."""
    especialidades = list(getattr(medico, "tieneEspecialidad", []) or [])

    if not especialidades:
        return ""

    return _etiqueta_especialidad(especialidades[0])


def _identificador_especialidad(texto):
    """Convierte una especialidad escrita por el usuario en un nombre interno."""
    base = re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", "_", str(texto).strip())
    base = re.sub(r"_+", "_", base).strip("_")

    if not base:
        return "Especialidad"

    return base[0].upper() + base[1:]


def _resolver_especialidad(texto):
    """Reutiliza una :Especialidad existente o crea una nueva."""
    objetivo = str(texto).strip().casefold()

    for especialidad in onto.Especialidad.instances():

        if _etiqueta_especialidad(especialidad).casefold() == objetivo:
            return especialidad

        if especialidad.name.casefold() == objetivo:
            return especialidad

    interno = _identificador_especialidad(texto)

    for especialidad in onto.Especialidad.instances():

        if especialidad.name == interno:
            return especialidad

    nueva = onto.Especialidad(interno)
    nueva.label = [str(texto).strip()]

    return nueva


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
            "especialidad": _especialidad_de(medico),
            "telefono": formatear_telefono(
                _primer_valor(medico, "telefono")
            ),
        })

    return medicos

def crear_medico(nombre, especialidad, telefono):
    """Valida los datos, crea un médico con id único y persiste la ontología."""

    nombre = texto_obligatorio(nombre, "nombre")
    especialidad = texto_obligatorio(especialidad, "especialidad")
    telefono = validar_telefono(telefono)

    if _existe_nombre(nombre):
        raise ValueError("Ya existe un médico con ese nombre.")

    with onto:

        nuevo = onto.Medico(generar_identificador("Medico", onto.Medico))

        nuevo.nombre = [nombre]
        nuevo.tieneEspecialidad = [_resolver_especialidad(especialidad)]
        nuevo.telefono = [telefono]

    guardar_ontologia()

    return nuevo

def actualizar_medico(medico_id, nuevo_nombre, nueva_especialidad, nuevo_telefono):
    """Actualiza un médico (identificado por su nombre interno) o devuelve None."""

    medico = obtener_medico(medico_id)

    if medico is None:
        return None

    nuevo_nombre = texto_obligatorio(nuevo_nombre, "nombre")
    nueva_especialidad = texto_obligatorio(
        nueva_especialidad,
        "especialidad"
    )
    nuevo_telefono = validar_telefono(nuevo_telefono)

    if _existe_nombre(nuevo_nombre, excluir=medico):
        raise ValueError("Ya existe otro médico con ese nombre.")

    with onto:

        medico.nombre = [nuevo_nombre]
        medico.tieneEspecialidad = [_resolver_especialidad(nueva_especialidad)]
        medico.telefono = [nuevo_telefono]

    guardar_ontologia()

    return medico


def _referencias_de(medico):
    """Cuenta las consultas, citas y recetas que dependen del médico."""
    total = 0

    for consulta in onto.Consulta.instances():

        if medico in (consulta.tieneMedico or []):
            total += 1

    for cita in onto.Cita.instances():

        if medico in (cita.tieneMedico or []):
            total += 1

    for receta in onto.Receta.instances():

        if medico in (receta.tieneMedico or []):
            total += 1

    return total


def eliminar_medico(medico_id):
    """Elimina un médico sin dejar registros clínicos huérfanos.

    Devuelve True si existía y fue eliminado, False en caso contrario. Lanza
    ValueError si todavía tiene consultas, citas o recetas asociadas.
    """

    medico = obtener_medico(medico_id)

    if medico is None:
        return False

    referencias = _referencias_de(medico)

    if referencias:
        raise ValueError(
            "No se puede eliminar el médico: tiene "
            f"{referencias} registro(s) clínico(s) asociado(s)."
        )

    destroy_entity(medico)

    guardar_ontologia()

    return True
