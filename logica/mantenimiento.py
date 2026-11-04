"""
Auditoría y depuración de la persistencia de la ontología 'clinica.owl'.

Este módulo concentra las operaciones de mantenimiento que no forman parte del
flujo clínico normal:

* ``auditar_ontologia()`` es de solo lectura y devuelve un informe de registros
  huérfanos, incompletos o que todavía usan las propiedades de texto antiguas.
* ``depurar_ontologia()`` aplica una limpieza idempotente y persiste una sola
  vez. Antes de escribir crea un respaldo de ``clinica.owl``.

Reglas aplicadas (arquitectura Encounter-Centric):

* Toda receta debe corresponder a una consulta existente mediante el
  identificador determinista ``Receta_Consulta_<id_consulta>``.
* Toda cita debe tener paciente y médico.
* Diagnósticos y estudios deben estar referenciados por alguna consulta.
* Las contraindicaciones, efectos secundarios y especialidades se expresan con
  Object Properties y individuos de catálogo, no con texto legado.
"""

import os
import re
import shutil
from datetime import datetime

from owlready2 import destroy_entity

from logica.ontologia import BASE_DIR, RUTA_ONTOLOGIA, guardar_ontologia, onto

# -----------------------------
# CONSTANTES
# -----------------------------

# Igual que logica.recetas.identificador_receta_de_consulta: el sufijo es el
# nombre completo de la consulta (por ejemplo, "Consulta_<uuid>").
PREFIJO_RECETA_CONSULTA = "Receta_"

# Propiedades de datos que ya no forman parte del modelo semántico.
PROPIEDADES_LEGADAS = (
    "contraindicaciones",
    "efectosSecundarios",
    "especialidad",
)

# Correspondencias conocidas entre los textos antiguos y los individuos de
# catálogo existentes. Evita duplicar conceptos clínicos al migrar.
ALIAS_CONTRAINDICACIONES = {
    "alergia a la penicilina": "Alergia_Penicilina",
    "alergia penicilina": "Alergia_Penicilina",
    "reacciones alergicas": "Alergia_Penicilina",
    "reaccion alergica": "Alergia_Penicilina",
    "insuficiencia renal": "Insuficiencia_Renal",
    "insuficiencia renal grave": "Insuficiencia_Renal",
    "embarazo": "Embarazo",
    "embarazada": "Embarazo",
    "embarazadas": "Embarazo",
    "hipertension no controlada": "Hipertension_No_Controlada",
}

ALIAS_EFECTOS_SECUNDARIOS = {
    "mareo": "Mareo",
    "nauseas": "Nauseas",
    "cefalea": "Cefalea",
    "somnolencia": "Somnolencia",
    "reaccion cutanea": "Reacciones_Cutaneas",
    "reacciones cutaneas": "Reacciones_Cutaneas",
    "reacciones en la piel": "Reacciones_Cutaneas",
}

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _consulta_por_id(consulta_id):
    """Devuelve la consulta con ese nombre interno, o None."""
    if not consulta_id:
        return None

    for consulta in onto.Consulta.instances():

        if consulta.name == consulta_id:
            return consulta

    return None


def _consulta_de_receta(receta):
    """Devuelve la consulta asociada a una receta Encounter-Centric o None."""
    nombre = str(getattr(receta, "name", "") or "")

    if not nombre.startswith(PREFIJO_RECETA_CONSULTA):
        return None

    return _consulta_por_id(nombre[len(PREFIJO_RECETA_CONSULTA):])


def _referenciada(entidad):
    """Indica si un diagnóstico o estudio sigue vinculado a alguna consulta."""
    for consulta in onto.Consulta.instances():

        if entidad in (consulta.tieneDiagnostico or []):
            return True

        if entidad in (consulta.solicitaEstudio or []):
            return True

    return False


def _texto(valor):
    """Normaliza un valor de texto para comparaciones y etiquetas."""
    return " ".join(str(valor or "").replace("_", " ").split())


def _clave(valor):
    """Clave de comparación sin mayúsculas ni diferencias de separadores."""
    return _texto(valor).casefold()


def _etiqueta(entidad):
    """Devuelve la etiqueta visible de un individuo de catálogo."""
    etiquetas = list(getattr(entidad, "label", []) or [])

    if etiquetas:
        return str(etiquetas[0])

    return _texto(entidad.name)


def _identificador_legible(texto):
    """Convierte un texto libre en un nombre interno estable y legible."""
    base = re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", "_", _texto(texto))
    base = re.sub(r"_+", "_", base).strip("_")

    if not base:
        return "Valor"

    return base[0].upper() + base[1:]


def _partir_texto_legado(texto):
    """Divide un texto histórico en entradas limpias y sin duplicados."""
    partes = []
    vistos = set()

    for linea in str(texto or "").replace(";", "\n").replace(",", "\n").splitlines():

        parte = _texto(linea)

        if not parte:
            continue

        clave = parte.casefold()

        if clave in vistos:
            continue

        vistos.add(clave)
        partes.append(parte)

    return partes


def _resolver_catalogo(clase, texto, alias):
    """Busca o crea un individuo de catálogo para un texto legado."""
    clave = _clave(texto)
    nombre_alias = alias.get(clave)

    if nombre_alias:

        for individuo in clase.instances():

            if individuo.name == nombre_alias:
                return individuo

    for individuo in clase.instances():

        if _clave(individuo.name) == clave:
            return individuo

        if _clave(_etiqueta(individuo)) == clave:
            return individuo

    interno = _identificador_legible(texto)

    for individuo in clase.instances():

        if individuo.name == interno:
            return individuo

    with onto:

        nuevo = clase(interno)
        nuevo.label = [_texto(texto)]

    return nuevo


def _migrar_texto_a_relacion(
    medicamento,
    propiedad_texto,
    propiedad_relacion,
    clase,
    alias,
):
    """Migra un texto legado a relaciones semánticas y limpia el texto."""
    textos = list(getattr(medicamento, propiedad_texto, []) or [])

    if not textos:
        return 0

    actuales = list(getattr(medicamento, propiedad_relacion, []) or [])
    agregados = 0

    for texto in textos:

        for parte in _partir_texto_legado(texto):

            individuo = _resolver_catalogo(clase, parte, alias)

            if individuo not in actuales:

                actuales.append(individuo)
                agregados += 1

    setattr(medicamento, propiedad_relacion, actuales)
    setattr(medicamento, propiedad_texto, [])

    return agregados


def _migrar_alertas_legadas():
    """Convierte contraindicaciones/efectos de texto en relaciones semánticas."""
    migrados = 0

    for medicamento in onto.Medicamento.instances():

        migrados += _migrar_texto_a_relacion(
            medicamento,
            "contraindicaciones",
            "tieneContraindicacion",
            onto.Contraindicacion,
            ALIAS_CONTRAINDICACIONES,
        )

        migrados += _migrar_texto_a_relacion(
            medicamento,
            "efectosSecundarios",
            "tieneEfectoSecundario",
            onto.EfectoSecundario,
            ALIAS_EFECTOS_SECUNDARIOS,
        )

    return migrados


def _limpiar_dosis_legada():
    """Elimina los valores de 'dosis' guardados en medicamentos.

    ``dosis`` pertenece a Receta; los medicamentos solo la conservaban por el
    esquema antiguo.
    """
    limpiados = []

    for medicamento in onto.Medicamento.instances():

        if getattr(medicamento, "dosis", None):

            medicamento.dosis = []
            limpiados.append(medicamento.name)

    return limpiados


def _migrar_especialidades_legadas():
    """Convierte la especialidad de texto en individuos :Especialidad."""
    migradas = 0

    for medico in onto.Medico.instances():

        textos = list(getattr(medico, "especialidad", []) or [])

        if not textos:
            continue

        actuales = list(getattr(medico, "tieneEspecialidad", []) or [])

        for texto in textos:

            especialidad = _resolver_catalogo(
                onto.Especialidad,
                texto,
                {},
            )

            if especialidad not in actuales:

                actuales.append(especialidad)
                migradas += 1

        medico.tieneEspecialidad = actuales
        medico.especialidad = []

    return migradas


def _eliminar_recetas_sin_consulta():
    """Elimina las recetas que no dependen de una consulta existente."""
    eliminadas = []

    for receta in list(onto.Receta.instances()):

        if _consulta_de_receta(receta) is not None:
            continue

        for medico in onto.Medico.instances():

            actuales = [
                item
                for item in (getattr(medico, "generaReceta", []) or [])
                if item is not receta
            ]

            medico.generaReceta = actuales

        eliminadas.append(receta.name)
        destroy_entity(receta)

    return eliminadas


def _eliminar_citas_incompletas():
    """Elimina las citas sin paciente o sin médico."""
    eliminadas = []

    for cita in list(onto.Cita.instances()):

        if cita.tienePaciente and cita.tieneMedico:
            continue

        eliminadas.append(cita.name)
        destroy_entity(cita)

    return eliminadas


def _eliminar_huerfanos():
    """Elimina diagnósticos y estudios que ninguna consulta referencia."""
    diagnosticos = []
    estudios = []

    for diagnostico in list(onto.Diagnostico.instances()):

        if not _referenciada(diagnostico):

            diagnosticos.append(diagnostico.name)
            destroy_entity(diagnostico)

    for estudio in list(onto.EstudioMedico.instances()):

        if not _referenciada(estudio):

            estudios.append(estudio.name)
            destroy_entity(estudio)

    return diagnosticos, estudios


def _eliminar_propiedades_legadas():
    """Elimina del esquema las propiedades de datos que ya no se usan."""
    eliminadas = []

    for nombre in PROPIEDADES_LEGADAS:

        propiedad = getattr(onto, nombre, None)

        if propiedad is not None:

            eliminadas.append(nombre)

            with onto:
                destroy_entity(propiedad)

    return eliminadas


def _corregir_inverso_paciente():
    """Elimina la inversa inválida entre tienePaciente y esPacienteDe.

    ``tienePaciente`` se usa desde Cita, Consulta y Receta, por lo que no puede
    tener como inversa una propiedad cuyo dominio es Paciente y rango Medico.
    Esa combinación generaba relaciones ``esPacienteDe`` espurias en memoria.
    """
    corregida = False

    tiene_paciente = getattr(onto, "tienePaciente", None)
    es_paciente_de = getattr(onto, "esPacienteDe", None)

    if tiene_paciente is None:
        return False

    with onto:

        if tiene_paciente.inverse_property is not None:

            tiene_paciente.inverse_property = None
            corregida = True

        if es_paciente_de is not None:

            destroy_entity(es_paciente_de)
            corregida = True

    return corregida

# -----------------------------
# RESPALDO
# -----------------------------

def crear_respaldo():
    """Copia clinica.owl a 'backups' y devuelve la ruta del respaldo."""
    carpeta = os.path.join(BASE_DIR, "backups")
    os.makedirs(carpeta, exist_ok=True)

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(carpeta, f"clinica_{marca}.owl")

    shutil.copy2(RUTA_ONTOLOGIA, destino)

    return destino

# -----------------------------
# AUDITORÍA (SOLO LECTURA)
# -----------------------------

def auditar_ontologia():
    """Devuelve un informe de integridad sin modificar la ontología."""
    recetas = list(onto.Receta.instances())
    recetas_validas = []
    recetas_sin_consulta = []
    recetas_incompletas = []

    for receta in recetas:

        if _consulta_de_receta(receta) is None:

            recetas_sin_consulta.append(receta.name)
            continue

        if (
            not receta.tienePaciente
            or not receta.tieneMedico
            or not receta.incluyeMedicamento
        ):

            recetas_incompletas.append(receta.name)
            continue

        recetas_validas.append(receta.name)

    citas_incompletas = [
        cita.name
        for cita in onto.Cita.instances()
        if not cita.tienePaciente or not cita.tieneMedico
    ]

    consultas_incompletas = [
        consulta.name
        for consulta in onto.Consulta.instances()
        if not consulta.tienePaciente or not consulta.tieneMedico
    ]

    diagnosticos_huerfanos = [
        diagnostico.name
        for diagnostico in onto.Diagnostico.instances()
        if not _referenciada(diagnostico)
    ]

    estudios_huerfanos = [
        estudio.name
        for estudio in onto.EstudioMedico.instances()
        if not _referenciada(estudio)
    ]

    medicamentos_dosis_legada = [
        medicamento.name
        for medicamento in onto.Medicamento.instances()
        if getattr(medicamento, "dosis", None)
    ]

    medicamentos_texto_legado = [
        medicamento.name
        for medicamento in onto.Medicamento.instances()
        if getattr(medicamento, "contraindicaciones", None)
        or getattr(medicamento, "efectosSecundarios", None)
    ]

    medicos_especialidad_legada = [
        medico.name
        for medico in onto.Medico.instances()
        if getattr(medico, "especialidad", None)
    ]

    propiedades_legadas = [
        nombre
        for nombre in PROPIEDADES_LEGADAS
        if getattr(onto, nombre, None) is not None
    ]

    return {
        "recetas_total": len(recetas),
        "recetas_validas": sorted(recetas_validas),
        "recetas_sin_consulta": sorted(recetas_sin_consulta),
        "recetas_incompletas": sorted(recetas_incompletas),
        "citas_incompletas": sorted(citas_incompletas),
        "consultas_incompletas": sorted(consultas_incompletas),
        "diagnosticos_huerfanos": sorted(diagnosticos_huerfanos),
        "estudios_huerfanos": sorted(estudios_huerfanos),
        "medicamentos_dosis_legada": sorted(medicamentos_dosis_legada),
        "medicamentos_texto_legado": sorted(medicamentos_texto_legado),
        "medicos_especialidad_legada": sorted(medicos_especialidad_legada),
        "propiedades_legadas": sorted(propiedades_legadas),
    }

# -----------------------------
# DEPURACIÓN
# -----------------------------

def depurar_ontologia():
    """Aplica la limpieza idempotente y persiste la ontología una sola vez.

    Devuelve un diccionario con las entidades eliminadas o migradas y la ruta
    del respaldo creado antes de escribir.
    """
    respaldo = crear_respaldo()

    with onto:

        contraindicaciones_migradas = _migrar_alertas_legadas()
        dosis_limpiadas = _limpiar_dosis_legada()
        especialidades_migradas = _migrar_especialidades_legadas()

        recetas_eliminadas = _eliminar_recetas_sin_consulta()
        citas_eliminadas = _eliminar_citas_incompletas()
        diagnosticos_eliminados, estudios_eliminados = _eliminar_huerfanos()

        propiedades_eliminadas = _eliminar_propiedades_legadas()
        inverso_corregido = _corregir_inverso_paciente()

    guardar_ontologia()

    return {
        "respaldo": respaldo,
        "contraindicaciones_migradas": contraindicaciones_migradas,
        "dosis_legadas_limpiadas": sorted(dosis_limpiadas),
        "especialidades_migradas": especialidades_migradas,
        "recetas_eliminadas": sorted(recetas_eliminadas),
        "citas_eliminadas": sorted(citas_eliminadas),
        "diagnosticos_eliminados": sorted(diagnosticos_eliminados),
        "estudios_eliminados": sorted(estudios_eliminados),
        "propiedades_eliminadas": sorted(propiedades_eliminadas),
        "inverso_corregido": inverso_corregido,
    }


if __name__ == "__main__":

    import json

    print(json.dumps(auditar_ontologia(), ensure_ascii=False, indent=2))
