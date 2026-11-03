"""
Lógica de negocio para Consultas clínicas (enfoque encounter-centric).

Una Consulta (:Consulta) representa un acto médico completo y vincula, de forma
atómica:

* Paciente            -> :tienePaciente y :tieneConsulta
* Médico              -> :tieneMedico
* Fecha               -> :fecha
* Notas clínicas      -> :notasClinicas
* Diagnóstico         -> :tieneDiagnostico
* Receta              -> dosis manual e indicaciones
* Estudios solicitados-> :solicitaEstudio

La ontología no define una relación directa Consulta-Receta. Para respetar el
esquema de 'clinica.owl' sin modificarlo, la receta de una consulta se
identifica de forma determinista mediante
``identificador_receta_de_consulta`` (``Receta_<id_consulta>``). La receta
conserva sus vínculos con Paciente, Médico y Medicamento.

Se reutiliza la propiedad de datos :fecha (cuyo dominio declarado en el esquema
es :Cita) sobre :Consulta para no alterar la ontología; la capa de lógica no
activa un razonador.

Atomicidad de la creación:

1. Todos los datos y referencias se validan antes de crear individuos.
2. Los individuos se construyen en memoria sin llamar a la persistencia.
3. Se llama una sola vez a ``guardar_ontologia()`` al final.
4. Si falla cualquier paso, se deshacen los vínculos y se destruyen los
   individuos nuevos, de modo que no queden datos parciales en memoria.

Los identificadores son UUID (ver ``logica.ontologia``) y las búsquedas usan el
nombre interno del individuo. La interfaz no accede directamente a Owlready2.
"""

from owlready2 import destroy_entity

from logica.diagnosticos import crear_diagnostico
from logica.diagnosticos import nombre_de as nombre_diagnostico
from logica.estudios import (
    crear_estudio,
    obtener_estudio_por_nombre,
)
from logica.estudios import (
    nombre_de as nombre_estudio,
)
from logica.medicamentos import obtener_medicamento
from logica.medicos import obtener_medico
from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.pacientes import obtener_paciente
from logica.recetas import (
    crear_receta,
    identificador_receta_de_consulta,
    listar_recetas,
    obtener_receta_de_consulta,
)
from logica.validaciones import texto_obligatorio, validar_dosis, validar_fecha

# -----------------------------
# CLASES QUE PARTICIPAN EN LA TRANSACCIÓN
# -----------------------------

# Se usan para tomar una instantánea antes de crear la consulta y poder
# revertir la operación completa si algo falla.
_CLASES_TRANSACCION = (
    onto.Consulta,
    onto.Receta,
    onto.Diagnostico,
    onto.EstudioMedico,
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


def _vincular_receta_medico(medico, receta):
    """Añade la receta a la relación 'generaReceta' del médico."""
    if medico is None or receta is None:
        return

    actuales = list(getattr(medico, "generaReceta", []) or [])

    if receta not in actuales:
        medico.generaReceta = actuales + [receta]


def _desvincular_receta_medico(medico, receta):
    """Quita la receta de la relación 'generaReceta' del médico."""
    if medico is None or receta is None:
        return

    actuales = list(getattr(medico, "generaReceta", []) or [])

    if receta in actuales:
        medico.generaReceta = [
            item
            for item in actuales
            if item is not receta
        ]


def _restaurar_consulta_base(consulta, paciente, medico, fecha, notas):
    """Restaura los datos base de una consulta tras un fallo de actualización."""
    actual = consulta.tienePaciente[0] if consulta.tienePaciente else None

    if actual is not paciente:
        _desvincular_paciente(consulta, actual)

        if paciente is not None:
            _vincular_paciente(consulta, paciente)

    consulta.tieneMedico = [medico] if medico is not None else []
    consulta.fecha = [fecha] if fecha else []
    consulta.notasClinicas = [notas] if notas else []


def _restaurar_receta(receta, paciente, medico):
    """Restaura los vínculos de una receta a su estado anterior."""
    if receta is None:
        return

    receta.tienePaciente = [paciente] if paciente is not None else []
    receta.tieneMedico = [medico] if medico is not None else []

    for profesional in onto.Medico.instances():

        if profesional is medico:
            _vincular_receta_medico(profesional, receta)
        else:
            _desvincular_receta_medico(profesional, receta)


def _referenciada(entidad):
    """Indica si un diagnóstico/estudio sigue vinculado a alguna consulta."""
    for consulta in onto.Consulta.instances():

        if entidad in (consulta.tieneDiagnostico or []):
            return True

        if entidad in (consulta.solicitaEstudio or []):
            return True

    return False


def _normalizar_estudios(estudios):
    """Normaliza la lista de estudios solicitados, sin duplicados.

    Acepta una cadena, una lista de cadenas o una lista de individuos
    :EstudioMedico. Los estudios son opcionales: una consulta puede no
    solicitar ninguno.
    """
    if estudios is None:
        return []

    if isinstance(estudios, str):
        estudios = [estudios]

    nombres = []
    vistos = set()

    for estudio in estudios:

        if estudio is None:
            continue

        if isinstance(estudio, str):
            nombre = texto_obligatorio(estudio, "estudio")
        else:
            nombre = texto_obligatorio(nombre_estudio(estudio), "estudio")

        clave = nombre.casefold()

        if clave not in vistos:
            vistos.add(clave)
            nombres.append(nombre)

    return nombres


def _resolver_estudios(nombres):
    """Reutiliza estudios existentes o crea los que falten, sin persistir."""
    estudios = []

    for nombre in nombres:

        estudio = obtener_estudio_por_nombre(nombre)

        if estudio is None:
            estudio = crear_estudio(nombre, guardar=False)

        if estudio not in estudios:
            estudios.append(estudio)

    return estudios


def _instantanea_identificadores():
    """Guarda los nombres de los individuos existentes antes de crear."""
    return {
        clase: {
            individuo.name
            for individuo in clase.instances()
        }
        for clase in _CLASES_TRANSACCION
    }


def _eliminar_nuevos(ids_previos):
    """Destruye los individuos creados después de la instantánea.

    También deshace los vínculos manuales que no son inversos en la ontología
    (paciente -> consulta y médico -> receta) antes de eliminar los individuos.
    """
    # Desvincular consultas nuevas de sus pacientes.
    previas = ids_previos.get(onto.Consulta, set())

    for consulta in list(onto.Consulta.instances()):

        if consulta.name in previas:
            continue

        for paciente in list(consulta.tienePaciente or []):

            try:
                _desvincular_paciente(consulta, paciente)

            except Exception:  # noqa: BLE001, S110
                pass

    # Desvincular recetas nuevas de sus médicos.
    previas = ids_previos.get(onto.Receta, set())

    for receta in list(onto.Receta.instances()):

        if receta.name in previas:
            continue

        for medico in list(onto.Medico.instances()):

            try:
                _desvincular_receta_medico(medico, receta)

            except Exception:  # noqa: BLE001, S110
                pass

    # Destruir primero la consulta y después sus componentes.
    for clase in _CLASES_TRANSACCION:

        previas = ids_previos.get(clase, set())

        for individuo in list(clase.instances()):

            if individuo.name not in previas:

                try:
                    destroy_entity(individuo)

                except Exception:  # noqa: BLE001, S110
                    pass


def _revertir_creacion(ids_previos):
    """Deshace en memoria todos los individuos creados por una consulta fallida."""
    _eliminar_nuevos(ids_previos)


# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_consultas():
    """Devuelve las consultas ordenadas por fecha descendente."""
    # Índice único de recetas para no recorrer la ontología completa por cada
    # consulta. La receta de una consulta tiene un identificador determinista.
    recetas_por_id = {
        receta["id"]: receta
        for receta in listar_recetas()
    }

    consultas = []

    for consulta in onto.Consulta.instances():

        paciente = consulta.tienePaciente[0] if consulta.tienePaciente else None
        medico = consulta.tieneMedico[0] if consulta.tieneMedico else None
        receta = recetas_por_id.get(
            identificador_receta_de_consulta(consulta.name)
        )

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
            "receta": receta,
            "receta_id": receta["id"] if receta else "",
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
    estudios=None,
    medicamento_ref=None,
    dosis="",
    indicaciones=""
):
    """Registra de forma atómica un acto médico completo.

    Valida todas las entradas y referencias antes de crear individuos. Después
    construye la consulta, su diagnóstico, su receta y sus estudios solicitados
    en memoria, y persiste la ontología una sola vez.

    Args:
        paciente_ref: Nombre interno o nombre visible del paciente.
        medico_ref: Nombre interno o nombre visible del médico.
        fecha: Fecha en formato AAAA-MM-DD o DD/MM/AAAA.
        notas: Notas clínicas de la consulta (obligatorias).
        diagnostico: Texto del diagnóstico de la visita (obligatorio).
        estudios: Lista de estudios solicitados (opcional, sin duplicados).
        medicamento_ref: Nombre interno o nombre visible del medicamento.
        dosis: Dosis manual de la receta (debe incluir una cantidad numérica).
        indicaciones: Indicaciones de la receta (obligatorias).

    Returns:
        El individuo :Consulta creado y persistido.

    Raises:
        ValueError: Si un dato es inválido o una referencia no existe.
    """

    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        raise ValueError("El paciente seleccionado no existe.")

    medico = obtener_medico(medico_ref)

    if medico is None:
        raise ValueError("El médico seleccionado no existe.")

    medicamento = obtener_medicamento(medicamento_ref)

    if medicamento is None:
        raise ValueError(
            "El medicamento seleccionado no existe o no fue indicado."
        )

    fecha = validar_fecha(fecha)
    notas = texto_obligatorio(notas, "notas clínicas")
    diagnostico = texto_obligatorio(diagnostico, "diagnóstico")
    dosis = validar_dosis(dosis)
    indicaciones = texto_obligatorio(indicaciones, "indicaciones")
    nombres_estudios = _normalizar_estudios(estudios)

    # Instantánea previa: permite revertir también los individuos que pudieran
    # quedar creados si un servicio auxiliar falla a mitad de su construcción.
    ids_previos = _instantanea_identificadores()

    try:

        consulta = onto.Consulta(
            generar_identificador("Consulta", onto.Consulta)
        )

        _vincular_paciente(consulta, paciente)

        consulta.tieneMedico = [medico]
        consulta.fecha = [fecha]
        consulta.notasClinicas = [notas]

        diagnostico_obj = crear_diagnostico(
            diagnostico,
            guardar=False
        )

        consulta.tieneDiagnostico = [diagnostico_obj]

        # La receta se identifica de forma determinista a partir de la consulta
        # porque la ontología no define una relación directa Consulta-Receta.
        crear_receta(
            paciente.name,
            medico.name,
            medicamento.name,
            dosis,
            indicaciones,
            guardar=False,
            identificador=identificador_receta_de_consulta(consulta.name)
        )

        consulta.solicitaEstudio = _resolver_estudios(nombres_estudios)

        guardar_ontologia()

    except Exception:

        _revertir_creacion(ids_previos)

        raise

    return consulta


def actualizar_consulta(consulta_id, paciente_ref, medico_ref, fecha, notas=""):
    """Actualiza los datos base de una consulta.

    Los diagnósticos, la receta y los estudios se conservan intactos; cada uno
    se gestiona desde su servicio correspondiente. La operación valida todo
    antes de modificar la ontología y persiste una sola vez.

    Devuelve el individuo actualizado o None si la consulta no existe.
    """

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
    medico_anterior = (
        consulta.tieneMedico[0] if consulta.tieneMedico else None
    )
    fecha_anterior = _primer_valor(consulta, "fecha")
    notas_anteriores = _primer_valor(consulta, "notasClinicas")
    receta = obtener_receta_de_consulta(consulta.name)
    receta_paciente_anterior = (
        receta.tienePaciente[0]
        if receta is not None and receta.tienePaciente
        else None
    )
    receta_medico_anterior = (
        receta.tieneMedico[0]
        if receta is not None and receta.tieneMedico
        else None
    )

    try:

        if paciente_anterior is not paciente:
            _desvincular_paciente(consulta, paciente_anterior)
            _vincular_paciente(consulta, paciente)

        consulta.tieneMedico = [medico]
        consulta.fecha = [fecha]
        consulta.notasClinicas = [notas] if notas else []

        # La receta forma parte del mismo acto médico: si cambia el paciente o
        # el profesional, sus vínculos deben quedar sincronizados.
        if receta is not None:

            receta.tienePaciente = [paciente]
            receta.tieneMedico = [medico]

            if medico_anterior is not medico:
                _desvincular_receta_medico(medico_anterior, receta)
                _vincular_receta_medico(medico, receta)

        guardar_ontologia()

    except Exception:

        _restaurar_consulta_base(
            consulta,
            paciente_anterior,
            medico_anterior,
            fecha_anterior,
            notas_anteriores,
        )

        _restaurar_receta(
            receta,
            receta_paciente_anterior,
            receta_medico_anterior,
        )

        raise

    return consulta


def eliminar_consulta(consulta_id):
    """Elimina una consulta, su receta y sus diagnósticos/estudios huérfanos."""

    consulta = _buscar_consulta(consulta_id)

    if consulta is None:
        return False

    paciente = consulta.tienePaciente[0] if consulta.tienePaciente else None
    diagnosticos = list(consulta.tieneDiagnostico or [])
    estudios = list(consulta.solicitaEstudio or [])
    receta = obtener_receta_de_consulta(consulta.name)

    _desvincular_paciente(consulta, paciente)

    destroy_entity(consulta)

    if receta is not None:

        # La receta está vinculada al médico mediante 'generaReceta'.
        for medico in list(onto.Medico.instances()):
            _desvincular_receta_medico(medico, receta)

        destroy_entity(receta)

    for diagnostico in diagnosticos:

        if not _referenciada(diagnostico):
            destroy_entity(diagnostico)

    for estudio in estudios:

        if not _referenciada(estudio):
            destroy_entity(estudio)

    guardar_ontologia()

    return True
