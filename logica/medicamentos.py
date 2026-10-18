"""
Lógica de negocio para la gestión de Medicamentos.

Encapsula el acceso a la ontología 'clinica.owl' (a través de logica.ontologia)
para que la capa de interfaz no dependa directamente de Owlready2.

El identificador de un medicamento es el nombre del individuo (name), tal como
lo usaba la vista original; la propiedad 'nombre' conserva el texto con espacios.
"""

from owlready2 import destroy_entity

from logica.ontologia import onto, guardar_ontologia

# -----------------------------
# HELPERS INTERNOS
# -----------------------------

def _buscar_medicamento(nombre):
    """Devuelve el individuo Medicamento cuyo nombre de individuo coincide, o None."""
    return onto.search_one(iri="*" + nombre)


def _primer_valor(entidad, propiedad, defecto=""):
    """Devuelve el primer valor de una propiedad de datos, o un valor por defecto."""
    valores = getattr(entidad, propiedad, None)
    if valores:
        return valores[0]
    return defecto

# -----------------------------
# OPERACIONES CRUD
# -----------------------------

def listar_medicamentos():
    """Devuelve una lista de diccionarios con los datos de cada medicamento."""
    medicamentos = []

    for medicamento in onto.Medicamento.instances():

        medicamentos.append({
            "nombre": medicamento.name,
            "dosis": _primer_valor(medicamento, "dosis"),
            "descripcion": _primer_valor(medicamento, "descripcion"),
        })

    return medicamentos

def obtener_dosis_base(nombre):
    """Devuelve la dosis base de un medicamento (por nombre de individuo), o ''."""
    medicamento = _buscar_medicamento(nombre)

    if medicamento is None:
        return ""

    return _primer_valor(medicamento, "dosis")

def crear_medicamento(nombre, dosis, descripcion):
    """Crea un medicamento. Devuelve el individuo creado o None si ya existe."""

    if _buscar_medicamento(nombre.replace(" ", "_")) is not None:
        return None

    nuevo = onto.Medicamento(
        nombre.replace(" ", "_")
    )

    nuevo.nombre = [nombre]
    nuevo.dosis = [dosis]

    if descripcion != "":

        nuevo.descripcion = [descripcion]

    guardar_ontologia()

    return nuevo

def actualizar_medicamento(nombre_actual, nuevo_nombre, nueva_dosis, nueva_descripcion):
    """Actualiza un medicamento existente. Devuelve el individuo o None."""

    medicamento = _buscar_medicamento(nombre_actual)

    if medicamento is None:
        return None

    medicamento.nombre = [nuevo_nombre]
    medicamento.dosis = [nueva_dosis]

    if nueva_descripcion != "":

        medicamento.descripcion = [nueva_descripcion]

    else:

        medicamento.descripcion = []

    guardar_ontologia()

    return medicamento

def eliminar_medicamento(nombre):
    """Elimina un medicamento existente. Devuelve True si existía, False si no."""

    medicamento = _buscar_medicamento(nombre)

    if medicamento is None:
        return False

    destroy_entity(medicamento)

    guardar_ontologia()

    return True
