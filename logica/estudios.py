"""
Lógica de negocio para los Estudios Médicos.

Un Estudio Médico es un individuo de la clase :EstudioMedico que se asocia a una
Consulta mediante la propiedad :solicitaEstudio. La asociación con un paciente
se deriva de la consulta que solicita el estudio, porque la ontología no define
una relación directa entre EstudioMedico y Paciente.

La ontología no define una propiedad de texto específica para el estudio, por lo
que se usa 'nombre' (la propiedad de etiqueta disponible) y, si faltara, el
nombre interno del individuo. No se altera el esquema de clinica.owl.
"""

from owlready2 import destroy_entity

from logica.ontologia import generar_identificador, guardar_ontologia, onto
from logica.validaciones import texto_obligatorio

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


def nombre_de(estudio):
    """Devuelve la etiqueta visible de un estudio médico."""
    return _primer_valor(estudio, "nombre", estudio.name)


def _buscar_consulta(consulta_id):
    """Busca una consulta por su nombre interno, sin importar consultas."""
    if not consulta_id:
        return None

    for consulta in onto.Consulta.instances():

        if consulta.name == consulta_id:
            return consulta

    return None


def _consultas_por_estudio():
    """Construye un mapa nombre_estudio -> consultas que lo solicitan."""
    mapa = {}

    for consulta in onto.Consulta.instances():

        for estudio in (consulta.solicitaEstudio or []):

            mapa.setdefault(estudio.name, []).append(consulta)

    return mapa


def _datos_consulta(consulta):
    """Extrae los datos de una consulta relevantes para el estudio."""
    paciente = consulta.tienePaciente[0] if consulta.tienePaciente else None
    medico = consulta.tieneMedico[0] if consulta.tieneMedico else None

    return {
        "id": consulta.name,
        "fecha": _primer_valor(consulta, "fecha"),
        "paciente": _nombre_persona(paciente),
        "paciente_id": paciente.name if paciente else "",
        "medico": _nombre_persona(medico),
        "medico_id": medico.name if medico else "",
    }

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_estudios():
    """Devuelve los estudios con sus consultas y pacientes asociados."""
    consultas_por_estudio = _consultas_por_estudio()
    estudios = []

    for estudio in onto.EstudioMedico.instances():

        consultas = sorted(
            consultas_por_estudio.get(estudio.name, []),
            key=lambda consulta: _primer_valor(consulta, "fecha") or "",
            reverse=True
        )

        datos_consultas = [
            _datos_consulta(consulta)
            for consulta in consultas
        ]

        pacientes = []
        vistos = set()

        for consulta in datos_consultas:

            paciente_id = consulta["paciente_id"]

            if paciente_id and paciente_id not in vistos:

                vistos.add(paciente_id)
                pacientes.append({
                    "id": paciente_id,
                    "nombre": consulta["paciente"] or paciente_id,
                })

        estudios.append({
            "id": estudio.name,
            "nombre": nombre_de(estudio),
            "consultas": datos_consultas,
            "consulta_ids": [
                consulta["id"]
                for consulta in datos_consultas
            ],
            "pacientes": pacientes,
            "paciente_ids": [
                paciente["id"]
                for paciente in pacientes
            ],
            "asociado": bool(datos_consultas),
        })

    estudios.sort(key=lambda item: item["nombre"].casefold())

    return estudios


def obtener_estudio(estudio_id):
    """Busca un estudio por su nombre interno, o devuelve None."""
    if not estudio_id:
        return None

    for estudio in onto.EstudioMedico.instances():

        if estudio.name == estudio_id:
            return estudio

    return None


def crear_estudio(nombre, guardar=True):
    """Crea un Estudio Médico con id único. Si 'guardar' es False, no persiste."""
    nombre = texto_obligatorio(nombre, "estudio")

    estudio = onto.EstudioMedico(
        generar_identificador("Estudio", onto.EstudioMedico)
    )

    estudio.nombre = [nombre]

    if guardar:
        guardar_ontologia()

    return estudio


def actualizar_estudio(estudio_id, nombre):
    """Actualiza la etiqueta de un estudio existente. Devuelve el individuo o None."""
    estudio = obtener_estudio(estudio_id)

    if estudio is None:
        return None

    nombre = texto_obligatorio(nombre, "estudio")

    estudio.nombre = [nombre]

    guardar_ontologia()

    return estudio


def eliminar_estudio(estudio_id):
    """Desasocia el estudio de todas las consultas y lo elimina."""
    estudio = obtener_estudio(estudio_id)

    if estudio is None:
        return False

    for consulta in onto.Consulta.instances():

        actuales = list(consulta.solicitaEstudio or [])

        if estudio in actuales:

            consulta.solicitaEstudio = [
                item
                for item in actuales
                if item is not estudio
            ]

    destroy_entity(estudio)

    guardar_ontologia()

    return True


def asociar_estudio(estudio_id, consulta_id):
    """Asocia un estudio a una consulta (y, por tanto, a su paciente).

    Devuelve el estudio. Lanza ValueError si el estudio o la consulta no existen.
    """
    estudio = obtener_estudio(estudio_id)

    if estudio is None:
        raise ValueError("El estudio seleccionado no existe.")

    consulta = _buscar_consulta(consulta_id)

    if consulta is None:
        raise ValueError("La consulta seleccionada no existe.")

    actuales = list(consulta.solicitaEstudio or [])

    if estudio not in actuales:

        consulta.solicitaEstudio = actuales + [estudio]

        guardar_ontologia()

    return estudio


def desasociar_estudio(estudio_id, consulta_id):
    """Desasocia un estudio de una consulta concreta.

    Devuelve True si se eliminó la asociación y False si no existía.
    Lanza ValueError si el estudio o la consulta no existen.
    """
    estudio = obtener_estudio(estudio_id)

    if estudio is None:
        raise ValueError("El estudio seleccionado no existe.")

    consulta = _buscar_consulta(consulta_id)

    if consulta is None:
        raise ValueError("La consulta seleccionada no existe.")

    actuales = list(consulta.solicitaEstudio or [])

    if estudio not in actuales:
        return False

    consulta.solicitaEstudio = [
        item
        for item in actuales
        if item is not estudio
    ]

    guardar_ontologia()

    return True
