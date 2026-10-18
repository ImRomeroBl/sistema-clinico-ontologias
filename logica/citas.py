"""
Lógica de negocio para la gestión de Citas.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

Asegura las relaciones con Paciente (tienePaciente) y Médico (tieneMedico).
El identificador de una cita es el nombre interno del individuo (name), generado
con un UUID para evitar colisiones al crear o eliminar registros. Antes de
modificar la ontología se validan los datos y la existencia de las relaciones.
"""

from owlready2 import destroy_entity

from logica.medicos import obtener_medico
from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.pacientes import obtener_paciente
from logica.validaciones import validar_fecha, validar_hora

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


def _resolver_relaciones(paciente_ref, medico_ref):
    """Resuelve y valida paciente y médico (lanza ValueError si no existen)."""
    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        raise ValueError("El paciente seleccionado no existe.")

    medico = obtener_medico(medico_ref)

    if medico is None:
        raise ValueError("El médico seleccionado no existe.")

    return paciente, medico

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
    """Valida datos y relaciones, crea la cita con id único y persiste."""

    paciente, medico = _resolver_relaciones(paciente_nombre, medico_nombre)

    fecha = validar_fecha(fecha)
    hora = validar_hora(hora)

    nueva = onto.Cita(
        generar_identificador("Cita", onto.Cita)
    )

    nueva.fecha = [fecha]
    nueva.hora = [hora]

    nueva.tienePaciente = [paciente]
    nueva.tieneMedico = [medico]

    guardar_ontologia()

    return nueva

def actualizar_cita(cita_id, paciente_nombre, medico_nombre, fecha, hora):
    """Actualiza una cita existente (por nombre interno). Devuelve el individuo o None."""

    cita = _buscar_cita(cita_id)

    if cita is None:
        return None

    paciente, medico = _resolver_relaciones(paciente_nombre, medico_nombre)

    fecha = validar_fecha(fecha)
    hora = validar_hora(hora)

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
