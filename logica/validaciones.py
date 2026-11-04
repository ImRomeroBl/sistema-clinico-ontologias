"""
Validaciones defensivas de datos para la capa de lógica.

Comprueban y normalizan los valores antes de que los servicios creen o
modifiquen individuos en la ontología. No acceden a la ontología: lanzan
ValueError con mensajes claros cuando un dato no es válido, de modo que la
interfaz pueda mostrarlos y la ontología nunca quede a medio modificar.
"""

import re
from datetime import datetime

# -----------------------------
# CONSTANTES
# -----------------------------

# Formatos de fecha aceptados (se normalizan a AAAA-MM-DD).
FORMATOS_FECHA = ("%Y-%m-%d", "%d/%m/%Y")

EDAD_MINIMA = 1
EDAD_MAXIMA = 130

_RE_HORA_24 = re.compile(r"^([01]?\d|2[0-3]):[0-5]\d$")
_RE_HORA_12 = re.compile(r"^(0?[1-9]|1[0-2]):[0-5]\d\s?[AaPp][Mm]$")
_RE_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")
_RE_TELEFONO = re.compile(r"^[\d\s()+-]+$")

# -----------------------------
# VALIDACIONES
# -----------------------------

def texto_obligatorio(valor, campo):
    """Devuelve el texto recortado o lanza ValueError si está vacío."""
    texto = "" if valor is None else str(valor).strip()

    if texto == "":
        raise ValueError(f"El campo '{campo}' es obligatorio.")

    return texto


def entero_positivo(valor, campo, maximo=None):
    """Convierte a entero positivo; lanza ValueError si no lo es."""
    try:
        numero = int(str(valor).strip())

    except (TypeError, ValueError):
        raise ValueError(f"El campo '{campo}' debe ser un número entero.")

    if numero <= 0:
        raise ValueError(f"El campo '{campo}' debe ser un entero positivo.")

    if maximo is not None and numero > maximo:
        raise ValueError(f"El campo '{campo}' no puede ser mayor que {maximo}.")

    return numero


def validar_edad(valor):
    """Valida la edad (entero positivo y razonable) y la devuelve como int."""
    return entero_positivo(valor, "edad", maximo=EDAD_MAXIMA)


def validar_fecha(valor, campo="fecha"):
    """Valida la fecha y la devuelve normalizada como AAAA-MM-DD."""
    texto = texto_obligatorio(valor, campo)

    for formato in FORMATOS_FECHA:

        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d")

        except ValueError:
            continue

    raise ValueError(
        f"El campo '{campo}' debe ser una fecha válida (AAAA-MM-DD o DD/MM/AAAA)."
    )


def validar_hora(valor, campo="hora"):
    """Valida la hora en formato HH:MM o HH:MM AM/PM y la devuelve recortada."""
    texto = texto_obligatorio(valor, campo)

    if _RE_HORA_24.match(texto) or _RE_HORA_12.match(texto):
        return texto

    raise ValueError(
        f"El campo '{campo}' debe tener el formato HH:MM o HH:MM AM/PM."
    )


def formatear_telefono(valor):
    """Devuelve el teléfono de 10 dígitos con formato ###-###-####.

    Si el valor no contiene exactamente 10 dígitos (por ejemplo, datos
    heredados incompletos), se devuelve el texto original recortado para no
    ocultar información al usuario.
    """
    texto = "" if valor is None else str(valor).strip()
    digitos = re.sub(r"\D", "", texto)

    if len(digitos) != 10:
        return texto

    return f"{digitos[:3]}-{digitos[3:6]}-{digitos[6:]}"


def validar_telefono(valor, campo="teléfono"):
    """Valida un teléfono de 10 dígitos y lo normaliza a ###-###-####."""
    texto = texto_obligatorio(valor, campo)

    if not _RE_TELEFONO.match(texto):
        raise ValueError(
            f"El campo '{campo}' sólo admite números, espacios y los "
            "signos + - ( )."
        )

    if len(re.sub(r"\D", "", texto)) != 10:
        raise ValueError(
            f"El campo '{campo}' debe contener exactamente 10 dígitos."
        )

    return formatear_telefono(texto)


def validar_dosis(valor, campo="dosis"):
    """Exige una cantidad numérica positiva dentro del texto de la dosis."""
    texto = texto_obligatorio(valor, campo)

    numeros = _RE_NUMERO.findall(texto)

    if not numeros:
        raise ValueError(f"El campo '{campo}' debe incluir una cantidad numérica.")

    cantidad = float(numeros[0].replace(",", "."))

    if cantidad <= 0:
        raise ValueError(f"El campo '{campo}' debe ser una cantidad positiva.")

    return texto
