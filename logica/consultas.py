"""
Lógica de negocio para Consultas clínicas.

Una Consulta (:Consulta) relaciona un Paciente y un Médico, registra notas
clínicas y puede tener Diagnósticos (:tieneDiagnostico) y Estudios Médicos
solicitados (:solicitaEstudio).

Se usan las propiedades de datos disponibles en la ontología: 'fecha' y
'notasClinicas'. Los identificadores son UUID y todas las operaciones de
búsqueda, edición y borrado usan el nombre interno del individuo.
"""

from owlready2 import destroy_entity

from logica.diagnosticos import crear_diagnostico
from logica.diagnosticos import nombre_de as nombre_diagnostico
from logica.estudios import crear_estudio
from logica.estudios import nombre_de as nombre_estudio
from logica.medicos import obtener_medico
from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.pacientes import obtener_paciente
from logica.validaciones import validar_fecha

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)

    if valores:
        return valores[0]

    return defecto


def _nombre_persona(entidad):
    """Devuelve el nombre visible de una persona o cadena vacía."""
    if entidad is None:
        return ""

    return _primer_valor(entidad, "nombre", entidad.name)


def _buscar_consulta(consulta_id):
    """Devuelve la Consulta cuyo nombre interno coincide, o None."""
    if not consulta_id:
        return None

    for consulta in onto.Consulta.instances():
        if consulta.name == consulta_id:
            return consulta

    return None


def _vincular_paciente(consulta, paciente):
    """Vincula la consulta al paciente en ambas direcciones del modelo."""
    consulta.tienePaciente = [paciente]

    actuales = list(getattr(paciente, "tieneConsulta", []) or [])

    if consulta not in actuales:
        paciente.tieneConsulta = actuales + [consulta]


def _desvincular_paciente(consulta, paciente):
    """Quita la relación consulta-paciente si existe."""
    if paciente is None:
        return

    if consulta.tienePaciente and consulta.tienePaciente[0] == paciente:
        consulta.tienePaciente = []

    actuales = [
        otra
        for otra in (getattr(paciente, "tieneConsulta", []) or [])
        if otra is not consulta
    ]

    paciente.tieneConsulta = actuales


def _referenciada(entidad):
    """Indica si un diagnóstico/estudio sigue vinculado a alguna consulta."""
    for consulta in onto.Consulta.instances():

        if entidad in (consulta.tieneDiagnostico or []):
            return True

        if entidad in (consulta.solicitaEstudio or []):
            return True

    return False

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_consultas():
    """Devuelve las consultas ordenadas por fecha descendente."""
    consultas = []

    for consulta in onto.Consulta.instances():

        paciente = consulta.tienePaciente[0] if consulta.tienePaciente else None
        medico = consulta.tieneMedico[0] if consulta.tieneMedico else None

        consultas.append({
            "id": consulta.name,
            "paciente": _nombre_persona(paciente),
            "paciente_id": paciente.name if paciente else "",
            "medico": _nombre_persona(medico),
            "medico_id": medico.name if medico else "",
            "fecha": _primer_valor(consulta, "fecha"),
            "notas": _primer_valor(consulta, "notasClinicas"),
            "diagnosticos": [
                {"id": diagnostico.name, "nombre": nombre_diagnostico(diagnostico)}
                for diagnostico in (consulta.tieneDiagnostico or [])
            ],
            "estudios": [
                {"id": estudio.name, "nombre": nombre_estudio(estudio)}
                for estudio in (consulta.solicitaEstudio or [])
            ],
        })

    consultas.sort(key=lambda consulta: consulta["fecha"] or "", reverse=True)

    return consultas

def obtener_consulta(consulta_id):
    """Devuelve los datos de una consulta por su nombre interno, o None."""
    for consulta in listar_consultas():
        if consulta["id"] == consulta_id:
            return consulta

    return None

def listar_consultas_por_paciente(paciente_ref):
    """Devuelve las consultas de un paciente (por id o nombre mostrado)."""
    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        return []

    return [
        consulta
        for consulta in listar_consultas()
        if consulta["paciente_id"] == paciente.name
    ]

def listar_consultas_por_medico(medico_ref):
    """Devuelve las consultas atendidas por un médico (por id o nombre mostrado)."""
    medico = obtener_medico(medico_ref)

    if medico is None:
        return []

    return [
        consulta
        for consulta in listar_consultas()
        if consulta["medico_id"] == medico.name
    ]

def crear_consulta(
    paciente_ref,
    medico_ref,
    fecha,
    notas="",
    diagnostico="",
    estudios=None
):
    """Valida datos, crea la consulta con sus vínculos y persiste una sola vez."""

    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        raise ValueError("El paciente seleccionado no existe.")

    medico = obtener_medico(medico_ref)

    if medico is None:
        raise ValueError("El médico seleccionado no existe.")

    fecha = validar_fecha(fecha)
    notas = "" if notas is None else str(notas).strip()

    consulta = onto.Consulta(
        generar_identificador("Consulta", onto.Consulta)
    )

    _vincular_paciente(consulta, paciente)

    consulta.tieneMedico = [medico]
    consulta.fecha = [fecha]

    if notas:
        consulta.notasClinicas = [notas]

    if diagnostico is not None and str(diagnostico).strip():
        consulta.tieneDiagnostico = [
            crear_diagnostico(diagnostico, guardar=False)
        ]

    if isinstance(estudios, str):
        estudios = [estudios]

    estudios_vinculados = []

    for nombre in (estudios or []):

        if nombre is not None and str(nombre).strip():
            estudios_vinculados.append(crear_estudio(nombre, guardar=False))

    if estudios_vinculados:
        consulta.solicitaEstudio = estudios_vinculados

    guardar_ontologia()

    return consulta

def actualizar_consulta(consulta_id, paciente_ref, medico_ref, fecha, notas=""):
    """Actualiza los datos base de una consulta (los diagnósticos/estudios se conservan)."""

    consulta = _buscar_consulta(consulta_id)

    if consulta is None:
        return None

    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        raise ValueError("El paciente seleccionado no existe.")

    medico = obtener_medico(medico_ref)

    if medico is None:
        raise ValueError("El médico seleccionado no existe.")

    fecha = validar_fecha(fecha)
    notas = "" if notas is None else str(notas).strip()

    paciente_anterior = (
        consulta.tienePaciente[0] if consulta.tienePaciente else None
    )

    if paciente_anterior is not paciente:
        _desvincular_paciente(consulta, paciente_anterior)
        _vincular_paciente(consulta, paciente)

    consulta.tieneMedico = [medico]
    consulta.fecha = [fecha]
    consulta.notasClinicas = [notas] if notas else []

    guardar_ontologia()

    return consulta

def eliminar_consulta(consulta_id):
    """Elimina una consulta y sus diagnósticos/estudios si quedan huérfanos."""

    consulta = _buscar_consulta(consulta_id)

    if consulta is None:
        return False

    paciente = consulta.tienePaciente[0] if consulta.tienePaciente else None
    diagnosticos = list(consulta.tieneDiagnostico or [])
    estudios = list(consulta.solicitaEstudio or [])

    _desvincular_paciente(consulta, paciente)

    destroy_entity(consulta)

    for diagnostico in diagnosticos:
        if not _referenciada(diagnostico):
            destroy_entity(diagnostico)

    for estudio in estudios:
        if not _referenciada(estudio):
            destroy_entity(estudio)

    guardar_ontologia()

    return True
