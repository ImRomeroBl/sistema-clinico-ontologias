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
from logica.validaciones import texto_obligatorio, validar_edad

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
            "telefono": _primer_valor(paciente, "telefono"),
        })

    return pacientes

def crear_paciente(nombre, edad, telefono):
    """Valida los datos, crea un paciente con id único y persiste la ontología."""

    nombre = texto_obligatorio(nombre, "nombre")
    edad = validar_edad(edad)
    telefono = texto_obligatorio(telefono, "teléfono")

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
    nuevo_telefono = texto_obligatorio(nuevo_telefono, "teléfono")

    if _existe_nombre(nuevo_nombre, excluir=paciente):
        raise ValueError("Ya existe otro paciente con ese nombre.")

    paciente.nombre = [nuevo_nombre]
    paciente.edad = [nueva_edad]
    paciente.telefono = [nuevo_telefono]

    guardar_ontologia()

    return paciente

def eliminar_paciente(paciente_id):
    """Elimina un paciente y sus recetas/citas asociadas (borrado en cascada).

    Devuelve True si el paciente existía y fue eliminado, False en caso contrario.
    """

    paciente = obtener_paciente(paciente_id)

    if paciente is None:
        return False

    # -----------------------------
    # ELIMINAR RECETAS
    # -----------------------------

    for receta in list(onto.Receta.instances()):

        if receta.tienePaciente and receta.tienePaciente[0] == paciente:

            destroy_entity(receta)

    # -----------------------------
    # ELIMINAR CITAS
    # -----------------------------

    for cita in list(onto.Cita.instances()):

        if cita.tienePaciente and cita.tienePaciente[0] == paciente:

            destroy_entity(cita)

    # -----------------------------
    # ELIMINAR PACIENTE
    # -----------------------------

    destroy_entity(paciente)

    guardar_ontologia()

    return True
