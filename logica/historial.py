"""
Lógica de negocio para el Historial Clínico.

Recopila y estructura, en una sola consulta, las consultas, recetas, citas,
diagnósticos y estudios asociados a un paciente. Es una capa de solo lectura:
no modifica ni persiste la ontología.

Los datos se obtienen de los módulos de servicio existentes para mantener la
interfaz libre de dependencias directas de Owlready2. Las consultas, citas y
registros clínicos se ordenan de forma cronológica descendente (lo más reciente
primero). Las recetas no tienen una propiedad de fecha en la ontología, por lo
que conservan el orden del expediente.
"""

from logica.citas import listar_citas
from logica.consultas import listar_consultas
from logica.pacientes import obtener_paciente
from logica.recetas import listar_recetas

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)

    if valores:
        return valores[0]

    return defecto


def _clave_fecha(registro):
    """Clave de orden cronológico para registros con fecha y, opcionalmente, hora."""
    return (
        registro.get("fecha") or "",
        registro.get("hora") or "",
    )


def _datos_paciente(paciente):
    """Extrae los datos generales del paciente para la pestaña de resumen."""
    return {
        "id": paciente.name,
        "nombre": _primer_valor(paciente, "nombre", paciente.name),
        "edad": _primer_valor(paciente, "edad", ""),
        "telefono": _primer_valor(paciente, "telefono", ""),
    }


def _registros_de_consulta(consultas):
    """Aplana diagnósticos y estudios de las consultas, conservando su contexto."""
    diagnosticos = []
    estudios = []
    registros = []

    for consulta in consultas:

        contexto = {
            "consulta_id": consulta.get("id", ""),
            "fecha": consulta.get("fecha", ""),
            "medico": consulta.get("medico", ""),
        }

        for diagnostico in consulta.get("diagnosticos", []):

            item = {
                "tipo": "Diagnóstico",
                "id": diagnostico.get("id", ""),
                "nombre": diagnostico.get("nombre", ""),
                **contexto,
            }

            diagnosticos.append(item)
            registros.append(item)

        for estudio in consulta.get("estudios", []):

            item = {
                "tipo": "Estudio",
                "id": estudio.get("id", ""),
                "nombre": estudio.get("nombre", ""),
                **contexto,
            }

            estudios.append(item)
            registros.append(item)

    return diagnosticos, estudios, registros

# -----------------------------
# HISTORIAL
# -----------------------------

def obtener_historial(paciente_ref):
    """Devuelve el historial estructurado de un paciente.

    Acepta el nombre interno del individuo o el nombre mostrado en la interfaz.
    Devuelve None si el paciente no existe. Para un paciente válido sin registros
    devuelve la estructura completa con listas vacías y conteos en cero.
    """

    paciente = obtener_paciente(paciente_ref)

    if paciente is None:
        return None

    consultas = [
        consulta
        for consulta in listar_consultas()
        if consulta.get("paciente_id") == paciente.name
    ]

    consultas.sort(key=_clave_fecha, reverse=True)

    recetas = [
        receta
        for receta in listar_recetas()
        if receta.get("paciente_id") == paciente.name
    ]

    citas = [
        cita
        for cita in listar_citas()
        if cita.get("paciente_id") == paciente.name
    ]

    citas.sort(key=_clave_fecha, reverse=True)

    diagnosticos, estudios, registros = _registros_de_consulta(consultas)
    registros.sort(key=_clave_fecha, reverse=True)

    conteos = {
        "consultas": len(consultas),
        "recetas": len(recetas),
        "citas": len(citas),
        "diagnosticos": len(diagnosticos),
        "estudios": len(estudios),
    }

    return {
        "paciente": _datos_paciente(paciente),
        "consultas": consultas,
        "recetas": recetas,
        "citas": citas,
        "diagnosticos": diagnosticos,
        "estudios": estudios,
        "registros_clinicos": registros,
        "conteos": conteos,
        "ultima_consulta": consultas[0] if consultas else None,
    }
