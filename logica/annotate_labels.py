"""Inyecta etiquetas rdfs:label multi-idioma (@es / @en) en clinica.owl.

El script es idempotente: sólo agrega una etiqueta cuando ese idioma aún no
existe en la entidad. No modifica IRIs, identificadores locales, clases,
propiedades ni individuos: únicamente añade anotaciones rdfs:label.

Uso:
    python -m logica.annotate_labels
    python logica/annotate_labels.py
"""

import re
from pathlib import Path

from owlready2 import World, get_ontology, locstr

# -----------------------------
# RUTA CENTRALIZADA
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_ONTOLOGIA = BASE_DIR / "clinica.owl"


def _uri_ontologia():
    """URI compatible con owlready2 en Windows (file://C:/...)."""
    return "file://" + str(RUTA_ONTOLOGIA).replace("\\", "/")


# -----------------------------
# MAPEO DE ENTIDADES DEL ESQUEMA
# -----------------------------

CLASES = {
    "Medico": ("Médico", "Doctor"),
    "Paciente": ("Paciente", "Patient"),
    "Receta": ("Receta Médica", "Medical Prescription"),
    "Medicamento": ("Medicamento", "Medication"),
    "Consulta": ("Consulta Médica", "Medical Consultation"),
    "EstudioMedico": ("Estudio Médico", "Medical Study"),
    "Cita": ("Cita", "Appointment"),
    "Contraindicacion": ("Contraindicación", "Contraindication"),
    "Diagnostico": ("Diagnóstico Médico", "Medical Diagnosis"),
    "EfectoSecundario": ("Efecto Secundario", "Side Effect"),
    "Especialidad": ("Especialidad", "Specialty"),
    "Persona": ("Persona", "Person"),
    "Analgesico": ("Analgésico", "Analgesic"),
    "Antibiotico": ("Antibiótico", "Antibiotic"),
    "Antiinflamatorio": ("Antiinflamatorio", "Anti-inflammatory"),
}

PROPIEDADES_OBJETO = {
    "atiende": ("atiende", "treats"),
    "tienePaciente": ("tiene paciente", "has patient"),
    "generaReceta": ("genera receta", "generates prescription"),
    "incluyeMedicamento": ("incluye medicamento", "includes medication"),
    "solicitaEstudio": ("solicita estudio", "requests study"),
    "tieneCita": ("tiene cita", "has appointment"),
    "tieneConsulta": ("tiene consulta", "has consultation"),
    "tieneContraindicacion": (
        "tiene contraindicación",
        "has contraindication",
    ),
    "tieneDiagnostico": ("tiene diagnóstico", "has diagnosis"),
    "tieneEfectoSecundario": (
        "tiene efecto secundario",
        "has side effect",
    ),
    "tieneEspecialidad": ("tiene especialidad", "has specialty"),
    "tieneMedico": ("tiene médico", "has doctor"),
}

PROPIEDADES_DATO = {
    "dosis": ("Dosificación", "Personalized Dosage"),
    "edad": ("Edad", "Age"),
    "fecha": ("Fecha", "Date"),
    "hora": ("Hora", "Time"),
    "indicaciones": ("Indicaciones", "Indications"),
    "nombre": ("Nombre", "Name"),
    "notasClinicas": ("Notas Clínicas", "Clinical Notes"),
    "telefono": ("Teléfono", "Phone"),
}

INDIVIDUOS = {
    # Catálogos clínicos
    "Alergia_Penicilina": ("Alergia a la Penicilina", "Penicillin Allergy"),
    "Insuficiencia_Renal": ("Insuficiencia Renal", "Renal Insufficiency"),
    "Hipertension_No_Controlada": (
        "Hipertensión No Controlada",
        "Uncontrolled Hypertension",
    ),
    "Embarazo": ("Embarazo", "Pregnancy"),
    "Mareo": ("Mareo", "Dizziness"),
    "Nauseas": ("Náuseas", "Nausea"),
    "Reacciones_Cutaneas": ("Reacciones Cutáneas", "Skin Reactions"),
    "Cefalea": ("Cefalea", "Headache"),
    "Somnolencia": ("Somnolencia", "Drowsiness"),
    "Amoxicilina": ("Amoxicilina", "Amoxicillin"),
    "Ibuprofeno": ("Ibuprofeno", "Ibuprofen"),
    "Paracetamol": ("Paracetamol", "Paracetamol"),
    "Omeprazol": ("Omeprazol", "Omeprazole"),
    "Cardiologia": ("Cardiología", "Cardiology"),
    "Pediatria": ("Pediatría", "Pediatrics"),
    # Personas de ejemplo
    "ImanolRomeroBlanco": ("Imanol Romero Blanco", "Imanol Romero Blanco"),
    "MarianaRuiz": ("Mariana Ruiz", "Mariana Ruiz"),
    "JoseMedina": ("José Medina", "Jose Medina"),
    "Coach_Y_psicologo": ("Coach y Psicólogo", "Coach and Psychologist"),
}

TRADUCCIONES = {}
for _mapa in (CLASES, PROPIEDADES_OBJETO, PROPIEDADES_DATO, INDIVIDUOS):
    TRADUCCIONES.update(_mapa)

# -----------------------------
# HELPERS
# -----------------------------

_ID_UUID = re.compile(r"^(?P<base>.+)_(?P<hex>[0-9a-f]{32})$")
_CAMEL = re.compile(r"(?<!^)(?=[A-Z])")


def _texto_legible(nombre):
    """Convierte un identificador local en un texto legible."""
    texto = _CAMEL.sub(" ", nombre)
    texto = texto.replace("_", " ")
    return re.sub(r"\s+", " ", texto).strip()


def _etiqueta_derivada(entidad):
    """Genera @es/@en para individuos sin traducción explícita.

    Los individuos creados por la aplicación terminan en un UUID; en ese caso
    se usa la etiqueta de su clase directa para evitar exponer el hash. Los
    individuos con nombre legible se humanizan.
    """
    coincidencia = _ID_UUID.match(entidad.name)

    if coincidencia:
        for clase in entidad.is_a:
            if clase.name in CLASES:
                return CLASES[clase.name]

    texto = _texto_legible(
        coincidencia.group("base") if coincidencia else entidad.name
    )
    return texto, texto


def _idiomas_existentes(entidad):
    """Devuelve el conjunto de idiomas ya anotados en la entidad."""
    return {getattr(etiqueta, "lang", None) for etiqueta in entidad.label}


def _asegurar_etiquetas(entidad):
    """Agrega rdfs:label @es y @en sólo si faltan en esa entidad."""
    traduccion = TRADUCCIONES.get(entidad.name)

    if traduccion is None:
        traduccion = _etiqueta_derivada(entidad)

    textos_es, textos_en = traduccion
    existentes = _idiomas_existentes(entidad)
    agregadas = []

    for idioma, texto in (("es", textos_es), ("en", textos_en)):
        if idioma in existentes:
            continue

        entidad.label.append(locstr(texto, lang=idioma))
        agregadas.append(idioma)

    return agregadas


def _entidades(onto):
    """Devuelve todas las entidades del esquema y los individuos."""
    return {
        "clases": sorted(onto.classes(), key=lambda entidad: entidad.name),
        "object_properties": sorted(
            onto.object_properties(),
            key=lambda entidad: entidad.name,
        ),
        "data_properties": sorted(
            onto.data_properties(),
            key=lambda entidad: entidad.name,
        ),
        "individuos": sorted(
            onto.individuals(),
            key=lambda entidad: entidad.name,
        ),
    }


def _validar_mapeo(entidades):
    """Exige traducción explícita para todo el esquema."""
    for categoria in ("clases", "object_properties", "data_properties"):
        faltantes = [
            entidad.name
            for entidad in entidades[categoria]
            if entidad.name not in TRADUCCIONES
        ]

        if faltantes:
            raise RuntimeError(
                f"Faltan traducciones para {categoria}: {faltantes}"
            )


# -----------------------------
# INYECCIÓN
# -----------------------------

def anotar():
    """Carga, anota y guarda la ontología. Devuelve un resumen de la ejecución."""
    if not RUTA_ONTOLOGIA.exists():
        raise FileNotFoundError(f"No existe la ontología: {RUTA_ONTOLOGIA}")

    onto = get_ontology(_uri_ontologia()).load()
    entidades = _entidades(onto)
    _validar_mapeo(entidades)

    iri_original = str(onto.base_iri)
    bytes_antes = RUTA_ONTOLOGIA.stat().st_size

    resumen = {}
    total_en = 0

    for categoria, lista in entidades.items():
        nuevas_en = 0
        nuevas_es = 0

        for entidad in lista:
            agregadas = _asegurar_etiquetas(entidad)

            if "en" in agregadas:
                nuevas_en += 1
            if "es" in agregadas:
                nuevas_es += 1

        resumen[categoria] = {
            "total": len(lista),
            "nuevas_es": nuevas_es,
            "nuevas_en": nuevas_en,
        }
        total_en += nuevas_en

    onto.save(file=str(RUTA_ONTOLOGIA))

    if str(onto.base_iri) != iri_original:
        raise RuntimeError("El IRI base cambió durante el guardado.")

    resumen["total_en"] = total_en
    resumen["iri"] = iri_original
    resumen["bytes_antes"] = bytes_antes
    resumen["bytes_despues"] = RUTA_ONTOLOGIA.stat().st_size

    return resumen


# -----------------------------
# VERIFICACIÓN
# -----------------------------

def verificar(iri_original=None, entidades_esperadas=None):
    """Recarga en un World aislado y valida etiquetas e IRIs."""
    if not RUTA_ONTOLOGIA.exists():
        raise FileNotFoundError(f"No existe la ontología: {RUTA_ONTOLOGIA}")

    world = World()
    onto = world.get_ontology(_uri_ontologia()).load()
    entidades = _entidades(onto)

    problemas = []
    total = 0
    total_en = 0

    for categoria, lista in entidades.items():
        for entidad in lista:
            total += 1
            idiomas = _idiomas_existentes(entidad)

            if "es" not in idiomas:
                problemas.append(f"{categoria}:{entidad.name} sin @es")
            if "en" not in idiomas:
                problemas.append(f"{categoria}:{entidad.name} sin @en")
            else:
                total_en += 1

            duplicados = [
                idioma
                for idioma in ("es", "en")
                if sum(
                    1
                    for etiqueta in entidad.label
                    if getattr(etiqueta, "lang", None) == idioma
                )
                > 1
            ]

            if duplicados:
                problemas.append(
                    f"{categoria}:{entidad.name} duplicado {duplicados}"
                )

    if iri_original is not None and str(onto.base_iri) != iri_original:
        problemas.append(
            f"IRI base alterado: {onto.base_iri} != {iri_original}"
        )

    if entidades_esperadas is not None:
        actuales = {
            (categoria, entidad.name)
            for categoria, lista in entidades.items()
            for entidad in lista
        }

        if actuales != entidades_esperadas:
            problemas.append("El conjunto de entidades cambió tras el guardado.")

    if problemas:
        raise RuntimeError(
            "Verificación fallida:\n  - " + "\n  - ".join(problemas)
        )

    return {
        "total": total,
        "total_en": total_en,
        "base_iri": str(onto.base_iri),
    }


# -----------------------------
# EJECUCIÓN DIRECTA
# -----------------------------

def main():
    print(f"Ontología: {RUTA_ONTOLOGIA}")

    onto = get_ontology(_uri_ontologia()).load()
    iri_original = str(onto.base_iri)
    entidades_esperadas = {
        (categoria, entidad.name)
        for categoria, lista in _entidades(onto).items()
        for entidad in lista
    }

    resumen = anotar()

    print("\nEntidades anotadas:")
    for categoria in (
        "clases",
        "object_properties",
        "data_properties",
        "individuos",
    ):
        datos = resumen[categoria]
        print(
            f"  {categoria:20s} total={datos['total']:3d}"
            f"  nuevas @es={datos['nuevas_es']:3d}"
            f"  nuevas @en={datos['nuevas_en']:3d}"
        )

    print(f"\nTotal de entidades que recibieron @en: {resumen['total_en']}")
    print(f"IRI base conservado: {resumen['iri']}")
    print(
        f"Tamaño del archivo: {resumen['bytes_antes']} -> "
        f"{resumen['bytes_despues']} bytes"
    )

    resultado = verificar(iri_original, entidades_esperadas)

    print("\nVerificación en World aislado:")
    print(f"  entidades leídas: {resultado['total']}")
    print(f"  entidades con @en: {resultado['total_en']}")
    print(f"  IRI base: {resultado['base_iri']}")
    print("\nOK: etiquetas @es/@en verificadas sin alterar los IRIs.")


if __name__ == "__main__":
    main()
