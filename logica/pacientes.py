"""
Lógica de negocio para la gestión de Pacientes.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

No altera el esquema: reutiliza la ontología ya cargada y persiste mediante
la función centralizada guardar_ontologia() de logica.ontologia.
"""

from owlready2 import destroy_entity

from logica.ontologia import onto, guardar_ontologia

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _buscar_paciente(nombre):
    """Devuelve el individuo Paciente cuyo 'nombre' coincide, o None."""
    return onto.search_one(nombre=nombre)


def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)
    if valores:
        return valores[0]
    return defecto

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_pacientes():
    """Devuelve una lista de diccionarios con los datos de cada paciente."""
    pacientes = []

    for paciente in onto.Paciente.instances():

        pacientes.append({
            "nombre": _primer_valor(paciente, "nombre"),
            "edad": _primer_valor(paciente, "edad"),
            "telefono": _primer_valor(paciente, "telefono"),
        })

    return pacientes

def crear_paciente(nombre, edad, telefono):
    """Crea un nuevo paciente y persiste la ontología. Devuelve el individuo creado."""

    with onto:

        nuevo = onto.Paciente(nombre.replace(" ", ""))

        nuevo.nombre = [nombre]
        nuevo.edad = [int(edad)]
        nuevo.telefono = [telefono]

    guardar_ontologia()

    return nuevo

def actualizar_paciente(nombre_antiguo, nuevo_nombre, nueva_edad, nuevo_telefono):
    """Actualiza un paciente existente. Devuelve el individuo actualizado o None."""

    paciente = _buscar_paciente(nombre_antiguo)

    if paciente is None:
        return None

    paciente.nombre = [nuevo_nombre]
    paciente.edad = [int(nueva_edad)]
    paciente.telefono = [nuevo_telefono]

    guardar_ontologia()

    return paciente

def eliminar_paciente(nombre):
    """Elimina un paciente y sus recetas/citas asociadas (borrado en cascada).

    Devuelve True si el paciente existía y fue eliminado, False en caso contrario.
    """

    paciente = _buscar_paciente(nombre)

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
