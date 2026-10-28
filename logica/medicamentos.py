"""
Lógica de negocio para la gestión de Medicamentos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

El identificador de un medicamento es el nombre interno del individuo (name),
que se mantiene legible (sin espacios) porque es la clave estable usada por las
recetas. El nombre visible se guarda en la propiedad 'nombre'. El tipo de
fármaco se representa con las clases Analgesico, Antibiotico, Antiinflamatorio
o Medicamento (genérico).

No se usan 'descripcion' (no existe en la ontología) ni 'dosis' (pertenece a
Receta). Los valores históricos de dosis en medicamentos se conservan intactos,
pero el catálogo ya no los lee ni los escribe.
"""

from owlready2 import destroy_entity

from logica.ontologia import guardar_ontologia, onto
from logica.validaciones import texto_obligatorio

# -----------------------------
# TIPOS DE MEDICAMENTO
# -----------------------------

TIPOS_MEDICAMENTO = (
    ("generico", "Genérico"),
    ("analgesico", "Analgésico"),
    ("antibiotico", "Antibiótico"),
    ("antiinflamatorio", "Antiinflamatorio"),
)

_CLASES_MEDICAMENTO = {
    "generico": onto.Medicamento,
    "analgesico": onto.Analgesico,
    "antibiotico": onto.Antibiotico,
    "antiinflamatorio": onto.Antiinflamatorio,
}

_ETIQUETAS_MEDICAMENTO = dict(TIPOS_MEDICAMENTO)

_ALIAS_TIPO = {
    "generico": "generico",
    "genérico": "generico",
    "medicamento": "generico",
    "analgesico": "analgesico",
    "analgésico": "analgesico",
    "antibiotico": "antibiotico",
    "antibiótico": "antibiotico",
    "antiinflamatorio": "antiinflamatorio",
}

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)

    if valores:
        return valores[0]

    return defecto


def _texto_opcional(valor):
    """Normaliza un texto opcional a una cadena recortada."""
    if valor is None:
        return ""

    return str(valor).strip()


def _slug(nombre):
    """Convierte un nombre a un identificador interno legible (sin espacios)."""
    return nombre.strip().replace(" ", "_")


def _iterar_medicamentos():
    """Itera todos los medicamentos, incluidas las subclases, sin duplicados."""
    vistos = set()

    for medicamento in onto.Medicamento.instances():

        if medicamento.name not in vistos:

            vistos.add(medicamento.name)

            yield medicamento


def _tipo_de(medicamento):
    """Devuelve la clave interna del tipo de fármaco de un individuo."""
    for clave in ("analgesico", "antibiotico", "antiinflamatorio"):

        if isinstance(medicamento, _CLASES_MEDICAMENTO[clave]):
            return clave

    return "generico"


def _normalizar_tipo(tipo):
    """Valida y normaliza la clave o etiqueta del tipo de medicamento."""
    clave = _texto_opcional(tipo).lower()

    if clave == "":
        return "generico"

    clave = _ALIAS_TIPO.get(clave)

    if clave is None:
        raise ValueError("El tipo de medicamento no es válido.")

    return clave


def _existe_nombre(nombre, excluir=None):
    """Comprueba si otro medicamento ya usa ese nombre visible (sin distinguir mayúsculas)."""
    objetivo = nombre.casefold()

    for medicamento in _iterar_medicamentos():

        if excluir is not None and medicamento is excluir:
            continue

        if medicamento.name.casefold() == objetivo:
            return True

        visible = _primer_valor(medicamento, "nombre", medicamento.name)

        if visible.casefold() == objetivo:
            return True

    return False

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def obtener_medicamento(identificador):
    """Busca por nombre interno (name) o, como respaldo, por el nombre visible."""
    if not identificador:
        return None

    medicamentos = list(_iterar_medicamentos())

    for medicamento in medicamentos:

        if medicamento.name == identificador:
            return medicamento

    for medicamento in medicamentos:

        if _primer_valor(medicamento, "nombre", medicamento.name) == identificador:
            return medicamento

    return None


def listar_medicamentos():
    """Devuelve nombre, tipo, contraindicaciones y efectos secundarios."""
    medicamentos = []

    for medicamento in _iterar_medicamentos():

        tipo = _tipo_de(medicamento)

        medicamentos.append({
            "id": medicamento.name,
            "nombre": _primer_valor(medicamento, "nombre", medicamento.name),
            "tipo": tipo,
            "tipo_label": _ETIQUETAS_MEDICAMENTO[tipo],
            "contraindicaciones": _primer_valor(medicamento, "contraindicaciones"),
            "efectos_secundarios": _primer_valor(medicamento, "efectosSecundarios"),
        })

    medicamentos.sort(key=lambda item: item["nombre"].casefold())

    return medicamentos


def crear_medicamento(
    nombre,
    contraindicaciones="",
    efectos_secundarios="",
    tipo="generico"
):
    """Valida los datos y crea un medicamento con id interno único.

    Lanza ValueError si el nombre ya está en uso o si el tipo no es válido.
    """
    nombre = texto_obligatorio(nombre, "nombre")
    contraindicaciones = _texto_opcional(contraindicaciones)
    efectos_secundarios = _texto_opcional(efectos_secundarios)
    tipo = _normalizar_tipo(tipo)

    identificador = _slug(nombre)

    if obtener_medicamento(identificador) is not None or _existe_nombre(nombre):
        raise ValueError("Ya existe un medicamento con ese nombre.")

    nuevo = _CLASES_MEDICAMENTO[tipo](identificador)

    nuevo.nombre = [nombre]

    if contraindicaciones:
        nuevo.contraindicaciones = [contraindicaciones]

    if efectos_secundarios:
        nuevo.efectosSecundarios = [efectos_secundarios]

    guardar_ontologia()

    return nuevo


def actualizar_medicamento(
    medicamento_id,
    nuevo_nombre,
    contraindicaciones="",
    efectos_secundarios="",
    tipo="generico"
):
    """Actualiza un medicamento (por nombre interno) o devuelve None."""
    medicamento = obtener_medicamento(medicamento_id)

    if medicamento is None:
        return None

    nuevo_nombre = texto_obligatorio(nuevo_nombre, "nombre")
    contraindicaciones = _texto_opcional(contraindicaciones)
    efectos_secundarios = _texto_opcional(efectos_secundarios)
    tipo = _normalizar_tipo(tipo)

    nuevo_identificador = _slug(nuevo_nombre)
    existente = obtener_medicamento(nuevo_identificador)

    if existente is not None and existente is not medicamento:
        raise ValueError("Ya existe otro medicamento con ese nombre.")

    if _existe_nombre(nuevo_nombre, excluir=medicamento):
        raise ValueError("Ya existe otro medicamento con ese nombre.")

    if _tipo_de(medicamento) != tipo:
        medicamento.is_a = [_CLASES_MEDICAMENTO[tipo]]

    medicamento.nombre = [nuevo_nombre]
    medicamento.contraindicaciones = [contraindicaciones] if contraindicaciones else []
    medicamento.efectosSecundarios = [efectos_secundarios] if efectos_secundarios else []

    guardar_ontologia()

    return medicamento


def eliminar_medicamento(medicamento_id):
    """Elimina un medicamento si ninguna receta lo incluye.

    Devuelve True si existía, False si no. Lanza ValueError si está en uso.
    """
    medicamento = obtener_medicamento(medicamento_id)

    if medicamento is None:
        return False

    recetas = [
        receta
        for receta in onto.Receta.instances()
        if medicamento in (receta.incluyeMedicamento or [])
    ]

    if recetas:
        raise ValueError(
            "No se puede eliminar el medicamento porque está incluido en "
            f"{len(recetas)} receta(s)."
        )

    destroy_entity(medicamento)

    guardar_ontologia()

    return True
