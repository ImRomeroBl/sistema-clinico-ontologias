"""
Lógica de negocio para la gestión de Médicos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

La especialidad se sigue tratando como propiedad de datos del médico
(propiedad 'especialidad'), conservando el mismo esquema que la vista original.
"""

from owlready2 import destroy_entity

from logica.ontologia import guardar_ontologia, onto

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _buscar_medico(nombre):
    """Devuelve el individuo Medico cuyo 'nombre' coincide, o None."""
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

def listar_medicos():
    """Devuelve una lista de diccionarios con los datos de cada médico."""
    medicos = []

    for medico in onto.Medico.instances():

        medicos.append({
            "nombre": _primer_valor(medico, "nombre"),
            "especialidad": _primer_valor(medico, "especialidad"),
            "telefono": _primer_valor(medico, "telefono"),
        })

    return medicos

def crear_medico(nombre, especialidad, telefono):
    """Crea un nuevo médico y persiste la ontología. Devuelve el individuo creado."""

    with onto:

        nuevo = onto.Medico(nombre.replace(" ", ""))

        nuevo.nombre = [nombre]
        nuevo.especialidad = [especialidad]
        nuevo.telefono = [telefono]

    guardar_ontologia()

    return nuevo

def actualizar_medico(nombre_antiguo, nuevo_nombre, nueva_especialidad, nuevo_telefono):
    """Actualiza un médico existente. Devuelve el individuo actualizado o None."""

    medico = _buscar_medico(nombre_antiguo)

    if medico is None:
        return None

    medico.nombre = [nuevo_nombre]
    medico.especialidad = [nueva_especialidad]
    medico.telefono = [nuevo_telefono]

    guardar_ontologia()

    return medico

def eliminar_medico(nombre):
    """Elimina un médico existente. Devuelve True si existía, False en caso contrario."""

    medico = _buscar_medico(nombre)

    if medico is None:
        return False

    destroy_entity(medico)

    guardar_ontologia()

    return True
