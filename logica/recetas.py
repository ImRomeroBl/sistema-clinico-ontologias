"""
Lógica de negocio para la gestión de Recetas.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

Asegura las relaciones con Paciente (tienePaciente), Médico (tieneMedico) y
Medicamento (incluyeMedicamento), además de dosis e indicaciones.
El identificador de una receta es el nombre del individuo (name).
"""

import uuid

from owlready2 import destroy_entity

from logica.ontologia import onto, guardar_ontologia

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
    """Crea una receta relacionando paciente, médico y medicamento."""

    paciente = onto.search_one(nombre=paciente_nombre)
    medico = onto.search_one(nombre=medico_nombre)
    medicamento = onto.search_one(iri="*" + medicamento_nombre)

    id_receta = f"RECETA_{uuid.uuid4().hex[:8]}"

    nueva = onto.Receta(id_receta)

    nueva.tienePaciente = [paciente]
    nueva.tieneMedico = [medico]
    nueva.incluyeMedicamento = [medicamento]

    nueva.dosis = [dosis]
    nueva.indicaciones = [indicaciones]

    guardar_ontologia()

    return nueva

def actualizar_receta(receta_id, paciente_nombre, medico_nombre, medicamento_nombre, dosis, indicaciones):
    """Actualiza una receta existente. Devuelve el individuo o None."""

    receta = _buscar_receta(receta_id)

    if receta is None:
        return None

    paciente = onto.search_one(nombre=paciente_nombre)
    medico = onto.search_one(nombre=medico_nombre)
    medicamento = onto.search_one(iri="*" + medicamento_nombre)

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
