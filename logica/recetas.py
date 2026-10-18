"""
Lógica de negocio para la gestión de Recetas.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

Asegura las relaciones con Paciente (tienePaciente), Médico (tieneMedico) y
Medicamento (incluyeMedicamento), además de dosis e indicaciones.
El identificador de una receta es el nombre interno del individuo (name),
generado con un UUID para evitar colisiones al crear o eliminar registros. Antes
de modificar la ontología se validan los datos y la existencia de las relaciones.
"""

from owlready2 import destroy_entity

from logica.medicamentos import obtener_medicamento
from logica.medicos import obtener_medico
from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.pacientes import obtener_paciente
from logica.validaciones import texto_obligatorio, validar_dosis

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _buscar_receta(receta_id):
    """Devuelve la Receta cuyo nombre de individuo coincide, o None."""
    for receta in onto.Receta.instances():
        if receta.name == receta_id:
            return receta
    return None


def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)

    if valores:
        return valores[0]

    return defecto


def _resolver_relaciones(paciente_ref, medico_ref, medicamento_ref):
    """Resuelve y valida paciente, médico y medicamento (lanza ValueError)."""
    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        raise ValueError("El paciente seleccionado no existe.")

    medico = obtener_medico(medico_ref)

    if medico is None:
        raise ValueError("El médico seleccionado no existe.")

    medicamento = obtener_medicamento(medicamento_ref)

    if medicamento is None:
        raise ValueError("El medicamento seleccionado no existe.")

    return paciente, medico, medicamento

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_recetas():
    """Devuelve las recetas que tienen paciente, médico y medicamento."""
    recetas = []

    for receta in onto.Receta.instances():

        if (
            not receta.tienePaciente
            or not receta.tieneMedico
            or not receta.incluyeMedicamento
        ):
            continue

        recetas.append({
            "id": receta.name,
            "paciente": _primer_valor(receta.tienePaciente[0], "nombre"),
            "medico": _primer_valor(receta.tieneMedico[0], "nombre"),
            "medicamento": receta.incluyeMedicamento[0].name,
            "dosis": _primer_valor(receta, "dosis"),
            "indicaciones": _primer_valor(receta, "indicaciones"),
        })

    return recetas

def crear_receta(paciente_nombre, medico_nombre, medicamento_nombre, dosis, indicaciones):
    """Valida datos y relaciones, crea la receta con id único y persiste."""

    paciente, medico, medicamento = _resolver_relaciones(
        paciente_nombre,
        medico_nombre,
        medicamento_nombre
    )

    dosis = validar_dosis(dosis)
    indicaciones = texto_obligatorio(indicaciones, "indicaciones")

    nueva = onto.Receta(
        generar_identificador("Receta", onto.Receta)
    )

    nueva.tienePaciente = [paciente]
    nueva.tieneMedico = [medico]
    nueva.incluyeMedicamento = [medicamento]

    nueva.dosis = [dosis]
    nueva.indicaciones = [indicaciones]

    guardar_ontologia()

    return nueva

def actualizar_receta(
    receta_id,
    paciente_nombre,
    medico_nombre,
    medicamento_nombre,
    dosis,
    indicaciones
):
    """Actualiza una receta existente (por nombre interno). Devuelve el individuo o None."""

    receta = _buscar_receta(receta_id)

    if receta is None:
        return None

    paciente, medico, medicamento = _resolver_relaciones(
        paciente_nombre,
        medico_nombre,
        medicamento_nombre
    )

    dosis = validar_dosis(dosis)
    indicaciones = texto_obligatorio(indicaciones, "indicaciones")

    receta.tienePaciente = [paciente]
    receta.tieneMedico = [medico]
    receta.incluyeMedicamento = [medicamento]

    receta.dosis = [dosis]
    receta.indicaciones = [indicaciones]

    guardar_ontologia()

    return receta

def eliminar_receta(receta_id):
    """Elimina una receta existente. Devuelve True si existía, False si no."""

    receta = _buscar_receta(receta_id)

    if receta is None:
        return False

    destroy_entity(receta)

    guardar_ontologia()

    return True
