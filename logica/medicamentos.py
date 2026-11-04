"""
Lógica de negocio para la gestión de Medicamentos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

El identificador de un medicamento es el nombre interno del individuo (name),
que se mantiene legible (sin espacios) porque es la clave estable usada por las
recetas. El nombre visible se guarda en la propiedad 'nombre'. El tipo de
fármaco se representa con las clases Analgesico, Antibiotico, Antiinflamatorio
o Medicamento (genérico).

Las contraindicaciones y los efectos secundarios se modelan exclusivamente como
individuos de las clases :Contraindicacion y :EfectoSecundario, vinculados al
medicamento mediante las Object Properties :tieneContraindicacion y
:tieneEfectoSecundario.

Las alertas semánticas se calculan con obtener_alertas_medicamento() a partir de
esas relaciones. El contrato incluye el nivel, el color y el detalle de
contraindicaciones y efectos.

No se usan 'descripcion' (no existe en la ontología) ni 'dosis' (pertenece a
Receta). Tampoco se leen ni escriben las antiguas propiedades de texto
'contraindicaciones' y 'efectosSecundarios'.
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


def _etiqueta_instancia(entidad):
    """Devuelve una etiqueta legible para una instancia de catálogo.

    Las instancias de :Contraindicacion y :EfectoSecundario no tienen una
    propiedad 'nombre' en el esquema actual. Se usa su nombre interno
    humanizado (por ejemplo, 'Insuficiencia_Renal' -> 'Insuficiencia Renal').
    """
    nombre = _primer_valor(entidad, "nombre", "")

    if nombre:
        return str(nombre)

    return str(entidad.name).replace("_", " ").strip()


def _listar_catalogo(clase):
    """Devuelve las instancias de una clase de catálogo como id + etiqueta."""
    items = [
        {
            "id": individuo.name,
            "nombre": _etiqueta_instancia(individuo),
        }
        for individuo in clase.instances()
    ]

    items.sort(key=lambda item: item["nombre"].casefold())

    return items


def _buscar_catalogo(clase, referencia):
    """Busca un individuo por su id interno o por su etiqueta visible."""
    if isinstance(referencia, str):

        objetivo = referencia.strip()

        if not objetivo:
            return None

        for individuo in clase.instances():

            if individuo.name == objetivo:
                return individuo

        objetivo_cf = objetivo.casefold()

        for individuo in clase.instances():

            if _etiqueta_instancia(individuo).casefold() == objetivo_cf:
                return individuo

        return None

    for individuo in clase.instances():

        if individuo is referencia:
            return individuo

    return None


def _resolver_catalogo(referencias, clase, campo):
    """Resuelve ids/etiquetas a individuos únicos de un catálogo.

    Lanza ValueError si alguna referencia no existe, antes de modificar la
    ontología.
    """
    if referencias is None:
        return []

    if isinstance(referencias, str):
        referencias = [referencias]

    individuos = []
    vistos = set()

    for referencia in referencias:

        if referencia is None:
            continue

        individuo = _buscar_catalogo(clase, referencia)

        if individuo is None:
            raise ValueError(
                f"El valor '{referencia}' no existe en el catálogo de {campo}."
            )

        if individuo.name not in vistos:

            vistos.add(individuo.name)
            individuos.append(individuo)

    return individuos


def _datos_relacion(medicamento, propiedad, clase):
    """Devuelve los individuos relacionados como id + etiqueta legible."""
    items = [
        {
            "id": individuo.name,
            "nombre": _etiqueta_instancia(individuo),
        }
        for individuo in (getattr(medicamento, propiedad, []) or [])
        if isinstance(individuo, clase)
    ]

    items.sort(key=lambda item: item["nombre"].casefold())

    return items


def _texto_relacion(items):
    """Convierte una lista de relaciones en texto para la tabla."""
    return ", ".join(item["nombre"] for item in items)

# -----------------------------
# CATÁLOGOS SEMÁNTICOS
# -----------------------------

def listar_contraindicaciones():
    """Devuelve el catálogo de individuos de :Contraindicacion."""
    return _listar_catalogo(onto.Contraindicacion)


def listar_efectos_secundarios():
    """Devuelve el catálogo de individuos de :EfectoSecundario."""
    return _listar_catalogo(onto.EfectoSecundario)

# -----------------------------
# ALERTAS SEMÁNTICAS
# -----------------------------

ALERTA_ALTA = "Alta"
ALERTA_MEDIA = "Media"
ALERTA_SIN = "Sin alerta"

# Colores semánticos del contrato de alertas. La interfaz decide su
# representación visual (hexadecimal, tema, etc.) sin acoplar la lógica a ella.
COLOR_ALERTA_ALTA = "red"
COLOR_ALERTA_MEDIA = "orange"
COLOR_ALERTA_SIN = "gray"

_COLORES_ALERTA = {
    ALERTA_ALTA: COLOR_ALERTA_ALTA,
    ALERTA_MEDIA: COLOR_ALERTA_MEDIA,
    ALERTA_SIN: COLOR_ALERTA_SIN,
}


def _normalizar_items_alerta(items):
    """Normaliza relaciones a una lista de {id, nombre} sin duplicados."""
    normalizados = []
    vistos = set()

    for item in items or []:

        if isinstance(item, dict):

            id_item = item.get("id")
            nombre = item.get("nombre") or id_item or ""

        else:

            id_item = None
            nombre = item

        nombre = " ".join(str(nombre or "").split())

        if not nombre:
            continue

        clave = str(id_item) if id_item else nombre.casefold()

        if clave in vistos:
            continue

        vistos.add(clave)
        normalizados.append({
            "id": id_item,
            "nombre": nombre,
        })

    return normalizados


def _datos_alerta(medicamento_instancia):
    """Obtiene las relaciones semánticas de un medicamento.

    Acepta un individuo de Owlready2, su identificador interno o un diccionario
    con la forma devuelta por listar_medicamentos(). Devuelve un diccionario
    interno con los datos normalizados.
    """
    vacio = {
        "contraindicaciones": [],
        "efectos_secundarios": [],
    }

    if medicamento_instancia is None:
        return vacio

    if isinstance(medicamento_instancia, str):

        medicamento_instancia = obtener_medicamento(medicamento_instancia)

        if medicamento_instancia is None:
            return vacio

    if isinstance(medicamento_instancia, dict):

        return {
            "contraindicaciones": _normalizar_items_alerta(
                medicamento_instancia.get("contraindicaciones")
            ),
            "efectos_secundarios": _normalizar_items_alerta(
                medicamento_instancia.get("efectos_secundarios")
            ),
        }

    if not hasattr(medicamento_instancia, "name"):
        return vacio

    return {
        "contraindicaciones": _datos_relacion(
            medicamento_instancia,
            "tieneContraindicacion",
            onto.Contraindicacion,
        ),
        "efectos_secundarios": _datos_relacion(
            medicamento_instancia,
            "tieneEfectoSecundario",
            onto.EfectoSecundario,
        ),
    }


def obtener_alertas_medicamento(medicamento_instancia):
    """Calcula la alerta semántica de un medicamento.

    Prioridad:
      1. Si tiene relaciones :tieneContraindicacion -> "Alta" (red).
      2. Si solo tiene :tieneEfectoSecundario -> "Media" (orange).
      3. Sin relaciones semánticas -> "Sin alerta" (gray).

    Acepta un individuo de Owlready2, su identificador interno o el diccionario
    devuelto por listar_medicamentos(). Nunca modifica la ontología.

    Devuelve exactamente:
      {
          "nivel": "Alta" | "Media" | "Sin alerta",
          "color": "red" | "orange" | "gray",
          "contraindicaciones": [nombres formateados],
          "efectos_secundarios": [nombres formateados],
      }
    """
    datos = _datos_alerta(medicamento_instancia)

    contraindicaciones = datos["contraindicaciones"]
    efectos_secundarios = datos["efectos_secundarios"]

    if contraindicaciones:

        nivel = ALERTA_ALTA

    elif efectos_secundarios:

        nivel = ALERTA_MEDIA

    else:

        nivel = ALERTA_SIN

    return {
        "nivel": nivel,
        "color": _COLORES_ALERTA[nivel],
        "contraindicaciones": [
            item["nombre"]
            for item in contraindicaciones
        ],
        "efectos_secundarios": [
            item["nombre"]
            for item in efectos_secundarios
        ],
    }

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
    """Devuelve los medicamentos con sus relaciones semánticas.

    Cada medicamento incluye:
      - 'contraindicaciones' y 'efectos_secundarios': listas de {id, nombre}.
      - 'contraindicaciones_ids' y 'efectos_secundarios_ids': ids para el
        formulario de selección múltiple.
      - 'contraindicaciones_texto' y 'efectos_secundarios_texto': texto para
        la tabla, construido únicamente a partir de las relaciones semánticas.
    """
    medicamentos = []

    for medicamento in _iterar_medicamentos():

        tipo = _tipo_de(medicamento)

        contraindicaciones = _datos_relacion(
            medicamento,
            "tieneContraindicacion",
            onto.Contraindicacion,
        )

        efectos_secundarios = _datos_relacion(
            medicamento,
            "tieneEfectoSecundario",
            onto.EfectoSecundario,
        )

        medicamentos.append({
            "id": medicamento.name,
            "nombre": _primer_valor(medicamento, "nombre", medicamento.name),
            "tipo": tipo,
            "tipo_label": _ETIQUETAS_MEDICAMENTO[tipo],
            "contraindicaciones": contraindicaciones,
            "contraindicaciones_ids": [
                item["id"]
                for item in contraindicaciones
            ],
            "contraindicaciones_texto": _texto_relacion(
                contraindicaciones
            ),
            "efectos_secundarios": efectos_secundarios,
            "efectos_secundarios_ids": [
                item["id"]
                for item in efectos_secundarios
            ],
            "efectos_secundarios_texto": _texto_relacion(
                efectos_secundarios
            ),
        })

    medicamentos.sort(key=lambda item: item["nombre"].casefold())

    return medicamentos


def crear_medicamento(
    nombre,
    contraindicaciones=None,
    efectos_secundarios=None,
    tipo="generico"
):
    """Valida los datos y crea un medicamento con sus relaciones semánticas.

    'contraindicaciones' y 'efectos_secundarios' aceptan listas de
    identificadores internos o etiquetas visibles de los catálogos
    :Contraindicacion y :EfectoSecundario.

    Lanza ValueError si el nombre ya está en uso, si el tipo no es válido o si
    alguna referencia del catálogo no existe.
    """
    nombre = texto_obligatorio(nombre, "nombre")
    tipo = _normalizar_tipo(tipo)

    contraindicaciones_obj = _resolver_catalogo(
        contraindicaciones,
        onto.Contraindicacion,
        "contraindicaciones",
    )

    efectos_obj = _resolver_catalogo(
        efectos_secundarios,
        onto.EfectoSecundario,
        "efectos secundarios",
    )

    identificador = _slug(nombre)

    if obtener_medicamento(identificador) is not None or _existe_nombre(nombre):
        raise ValueError("Ya existe un medicamento con ese nombre.")

    nuevo = _CLASES_MEDICAMENTO[tipo](identificador)

    nuevo.nombre = [nombre]
    nuevo.tieneContraindicacion = contraindicaciones_obj
    nuevo.tieneEfectoSecundario = efectos_obj

    guardar_ontologia()

    return nuevo


def actualizar_medicamento(
    medicamento_id,
    nuevo_nombre,
    contraindicaciones=None,
    efectos_secundarios=None,
    tipo="generico"
):
    """Actualiza un medicamento (por nombre interno) o devuelve None.

    Las listas de contraindicaciones y efectos secundarios reemplazan las
    relaciones semánticas existentes; las Object Properties son la única
    fuente de verdad.
    """
    medicamento = obtener_medicamento(medicamento_id)

    if medicamento is None:
        return None

    nuevo_nombre = texto_obligatorio(nuevo_nombre, "nombre")
    tipo = _normalizar_tipo(tipo)

    contraindicaciones_obj = _resolver_catalogo(
        contraindicaciones,
        onto.Contraindicacion,
        "contraindicaciones",
    )

    efectos_obj = _resolver_catalogo(
        efectos_secundarios,
        onto.EfectoSecundario,
        "efectos secundarios",
    )

    nuevo_identificador = _slug(nuevo_nombre)
    existente = obtener_medicamento(nuevo_identificador)

    if existente is not None and existente is not medicamento:
        raise ValueError("Ya existe otro medicamento con ese nombre.")

    if _existe_nombre(nuevo_nombre, excluir=medicamento):
        raise ValueError("Ya existe otro medicamento con ese nombre.")

    if _tipo_de(medicamento) != tipo:
        medicamento.is_a = [_CLASES_MEDICAMENTO[tipo]]

    medicamento.nombre = [nuevo_nombre]
    medicamento.tieneContraindicacion = contraindicaciones_obj
    medicamento.tieneEfectoSecundario = efectos_obj

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
