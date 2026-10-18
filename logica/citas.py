"""
Lógica de negocio para la gestión de Citas.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

Asegura las relaciones con Paciente (tienePaciente) y Médico (tieneMedico).
El identificador de una cita es el nombre del individuo (name).
"""

from owlready2 import destroy_entity

from logica.ontologia import onto, guardar_ontologia

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _buscar_cita(cita_id):
    """Devuelve la Cita cuyo nombre de individuo coincide, o None."""
    for cita in onto.Cita.instances():
        if cita.name == cita_id:
            return cita
    return None


def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)
    if valores:
        return valores[0]
    return defecto

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_citas():
    """Devuelve las citas que tienen paciente y médico asignados."""
    citas = []

    for cita in onto.Cita.instances():

        if (
            not cita.tienePaciente
            or not cita.tieneMedico
        ):
            continue

        citas.append({
            "id": cita.name,
            "paciente": _primer_valor(cita.tienePaciente[0], "nombre"),
            "medico": _primer_valor(cita.tieneMedico[0], "nombre"),
            "fecha": _primer_valor(cita, "fecha"),
            "hora": _primer_valor(cita, "hora"),
        })

    return citas

def crear_cita(paciente_nombre, medico_nombre, fecha, hora):
    """Crea una cita relacionando paciente y médico. Devuelve el individuo creado."""

    paciente = onto.search_one(nombre=paciente_nombre)
    medico = onto.search_one(nombre=medico_nombre)

    nueva = onto.Cita(
        f"Cita_{len(onto.Cita.instances()) + 1}"
    )

    nueva.fecha = [fecha]
    nueva.hora = [hora]

    nueva.tienePaciente = [paciente]
    nueva.tieneMedico = [medico]

    guardar_ontologia()

    return nueva

def actualizar_cita(cita_id, paciente_nombre, medico_nombre, fecha, hora):
    """Actualiza una cita existente. Devuelve el individuo o None."""

    cita = _buscar_cita(cita_id)

    if cita is None:
        return None

    paciente = onto.search_one(nombre=paciente_nombre)
    medico = onto.search_one(nombre=medico_nombre)

    cita.fecha = [fecha]
    cita.hora = [hora]

    cita.tienePaciente = [paciente]
    cita.tieneMedico = [medico]

    guardar_ontologia()

    return cita

def eliminar_cita(cita_id):
    """Elimina una cita existente. Devuelve True si existía, False si no."""

    cita = _buscar_cita(cita_id)

    if cita is None:
        return False

    destroy_entity(cita)

    guardar_ontologia()

    return True
