"""
Lógica de negocio para la gestión de Pacientes.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

El identificador de un paciente es el nombre interno del individuo (name),
generado con un UUID para evitar colisiones al crear o eliminar registros. Las
operaciones de búsqueda, modificación y borrado usan ese nombre interno y no el
texto mostrado en la interfaz. Los datos se validan antes de tocar la ontología.
"""

from owlready2 import destroy_entity

from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.validaciones import (
    formatear_telefono,
    texto_obligatorio,
    validar_edad,
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


def _nombre_de(paciente):
    """Devuelve el nombre mostrado (propiedad 'nombre') de un paciente."""
    return _primer_valor(paciente, "nombre")


def obtener_paciente(identificador):
    """Busca un paciente por su nombre interno (name) o, como respaldo, por 'nombre'."""
    if not identificador:
        return None

    for paciente in onto.Paciente.instances():
        if paciente.name == identificador:
            return paciente

    for paciente in onto.Paciente.instances():
        if _nombre_de(paciente) == identificador:
            return paciente

    return None


def _existe_nombre(nombre, excluir=None):
    """Indica si ya hay un paciente con ese nombre (excluyendo un individuo)."""
    for paciente in onto.Paciente.instances():

        if paciente is excluir:
            continue

        if _nombre_de(paciente) == nombre:
            return True

    return False

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_pacientes():
    """Devuelve una lista de diccionarios con los datos de cada paciente."""
    pacientes = []

    for paciente in onto.Paciente.instances():

        pacientes.append({
            "id": paciente.name,
            "nombre": _nombre_de(paciente),
            "edad": _primer_valor(paciente, "edad"),
            "telefono": formatear_telefono(
                _primer_valor(paciente, "telefono")
            ),
        })

    return pacientes

def crear_paciente(nombre, edad, telefono):
    """Valida los datos, crea un paciente con id único y persiste la ontología."""

    nombre = texto_obligatorio(nombre, "nombre")
    edad = validar_edad(edad)
    telefono = validar_telefono(telefono)

    if _existe_nombre(nombre):
        raise ValueError("Ya existe un paciente con ese nombre.")

    with onto:

        nuevo = onto.Paciente(generar_identificador("Paciente", onto.Paciente))

        nuevo.nombre = [nombre]
        nuevo.edad = [edad]
        nuevo.telefono = [telefono]

    guardar_ontologia()

    return nuevo

def actualizar_paciente(paciente_id, nuevo_nombre, nueva_edad, nuevo_telefono):
    """Actualiza un paciente (identificado por su nombre interno) o devuelve None."""

    paciente = obtener_paciente(paciente_id)

    if paciente is None:
        return None

    nuevo_nombre = texto_obligatorio(nuevo_nombre, "nombre")
    nueva_edad = validar_edad(nueva_edad)
    nuevo_telefono = validar_telefono(nuevo_telefono)

    if _existe_nombre(nuevo_nombre, excluir=paciente):
        raise ValueError("Ya existe otro paciente con ese nombre.")

    paciente.nombre = [nuevo_nombre]
    paciente.edad = [nueva_edad]
    paciente.telefono = [nuevo_telefono]

    guardar_ontologia()

    return paciente

PREFIJO_RECETA_CONSULTA = "Receta_"


def _receta_de_consulta(consulta):
    """Devuelve la receta determinista de una consulta, o None."""
    objetivo = PREFIJO_RECETA_CONSULTA + consulta.name

    for receta in onto.Receta.instances():

        if receta.name == objetivo:
            return receta

    return None


def _referenciada(entidad):
    """Indica si un diagnóstico o estudio sigue vinculado a alguna consulta."""
    for consulta in onto.Consulta.instances():

        if entidad in (consulta.tieneDiagnostico or []):
            return True

        if entidad in (consulta.solicitaEstudio or []):
            return True

    return False


def _eliminar_consulta(consulta, paciente):
    """Elimina una consulta y los componentes clínicos que queden huérfanos."""
    diagnosticos = list(consulta.tieneDiagnostico or [])
    estudios = list(consulta.solicitaEstudio or [])
    receta = _receta_de_consulta(consulta)

    paciente.tieneConsulta = [
        item
        for item in (getattr(paciente, "tieneConsulta", []) or [])
        if item is not consulta
    ]

    consulta.tienePaciente = []
    destroy_entity(consulta)

    if receta is not None:

        for medico in onto.Medico.instances():

            medico.generaReceta = [
                item
                for item in (getattr(medico, "generaReceta", []) or [])
                if item is not receta
            ]

        destroy_entity(receta)

    for diagnostico in diagnosticos:

        if not _referenciada(diagnostico):
            destroy_entity(diagnostico)

    for estudio in estudios:

        if not _referenciada(estudio):
            destroy_entity(estudio)


def eliminar_paciente(paciente_id):
    """Elimina un paciente y todo su expediente clínico (borrado en cascada).

    Incluye consultas, recetas, diagnósticos, estudios y citas asociadas.
    Devuelve True si el paciente existía y fue eliminado, False en caso contrario.
    """

    paciente = obtener_paciente(paciente_id)

    if paciente is None:
        return False

    # -----------------------------
    # CONSULTAS Y SUS COMPONENTES
    # -----------------------------

    consultas = [
        consulta
        for consulta in onto.Consulta.instances()
        if paciente in (consulta.tienePaciente or [])
    ]

    for consulta in consultas:
        _eliminar_consulta(consulta, paciente)

    # -----------------------------
    # RECETAS LEGADAS RESTANTES
    # -----------------------------

    for receta in list(onto.Receta.instances()):

        if paciente not in (receta.tienePaciente or []):
            continue

        for medico in onto.Medico.instances():

            medico.generaReceta = [
                item
                for item in (getattr(medico, "generaReceta", []) or [])
                if item is not receta
            ]

        destroy_entity(receta)

    # -----------------------------
    # CITAS
    # -----------------------------

    for cita in list(onto.Cita.instances()):

        if paciente in (cita.tienePaciente or []):
            destroy_entity(cita)

    # -----------------------------
    # PACIENTE
    # -----------------------------

    destroy_entity(paciente)

    guardar_ontologia()

    return True
