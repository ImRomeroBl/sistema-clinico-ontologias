import re

import customtkinter as ctk

from interfaz.theme.colors import (
    BORDER,
    CARD,
    DANGER,
    PRIMARY,
    PRIMARY_HOVER,
    SUCCESS,
    TEXT,
    TEXT_SECONDARY,
    WARNING,
)
from interfaz.theme.fonts import BUTTON_FONT, SUBTITLE, TEXT_FONT

# -----------------------------------
# TITULO PRINCIPAL
# -----------------------------------

def crear_titulo(parent, texto):

    titulo = ctk.CTkLabel(
        parent,
        text=texto,
        font=("Inter", 34, "bold"),
        text_color=TEXT
    )

    return titulo

# -----------------------------------
# SUBTITULO
# -----------------------------------

def crear_subtitulo(parent, texto):

    subtitulo = ctk.CTkLabel(
        parent,
        text=texto,
        font=SUBTITLE,
        text_color=TEXT_SECONDARY
    )

    return subtitulo

# -----------------------------------
# CARD
# -----------------------------------

def crear_card(parent):

    card = ctk.CTkFrame(
        parent,
        fg_color=CARD,
        corner_radius=20,
        border_width=1,
        border_color=BORDER
    )

    return card

# -----------------------------------
# INPUT
# -----------------------------------

def crear_input(parent, placeholder="", width=140):

    entry = ctk.CTkEntry(
        parent,
        height=42,
        width=width,
        corner_radius=10,
        border_color=BORDER,
        fg_color="#0F172A",
        text_color=TEXT,
        placeholder_text=placeholder,
        font=TEXT_FONT
    )

    return entry

# -----------------------------------
# TEXTBOX MULTILINEA
# -----------------------------------

def crear_textbox(parent, height=90, width=320):

    textbox = ctk.CTkTextbox(
        parent,
        height=height,
        width=width,
        corner_radius=10,
        border_width=1,
        border_color=BORDER,
        fg_color="#0F172A",
        text_color=TEXT,
        font=TEXT_FONT,
        wrap="word"
    )

    return textbox

# -----------------------------------
# LABEL FORMULARIO
# -----------------------------------

def crear_label(parent, texto):

    label = ctk.CTkLabel(
        parent,
        text=texto,
        font=TEXT_FONT,
        text_color=TEXT
    )

    return label

# -----------------------------------
# BOTON PRIMARIO
# -----------------------------------

def crear_boton_primario(parent, texto, comando):

    boton = ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color="white",
        font=BUTTON_FONT,
        corner_radius=12,
        height=45
    )

    return boton

# -----------------------------------
# BOTON EXITO
# -----------------------------------

def crear_boton_exito(parent, texto, comando):

    boton = ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        fg_color=SUCCESS,
        hover_color="#059669",
        text_color="white",
        font=BUTTON_FONT,
        corner_radius=12,
        height=45
    )

    return boton

# -----------------------------------
# BOTON WARNING
# -----------------------------------

def crear_boton_warning(parent, texto, comando):

    boton = ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        fg_color=WARNING,
        hover_color="#D97706",
        text_color="white",
        font=BUTTON_FONT,
        corner_radius=12,
        height=45
    )

    return boton

# -----------------------------------
# BOTON DANGER
# -----------------------------------

def crear_boton_danger(parent, texto, comando):

    boton = ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        fg_color=DANGER,
        hover_color="#DC2626",
        text_color="white",
        font=BUTTON_FONT,
        corner_radius=12,
        height=45
    )

    return boton

# -----------------------------------
# FORMATO VISUAL DE TELEFONO
# -----------------------------------

_TECLAS_SIN_FORMATO = frozenset({
    "Left",
    "Right",
    "Up",
    "Down",
    "Home",
    "End",
    "Prior",
    "Next",
    "Tab",
    "ISO_Left_Tab",
    "Shift_L",
    "Shift_R",
    "Control_L",
    "Control_R",
    "Alt_L",
    "Alt_R",
    "Caps_Lock",
    "Escape",
})


def formatear_telefono_visual(valor):
    """Formatea progresivamente un teléfono de hasta 10 dígitos.

    Se usa únicamente como ayuda visual mientras se escribe; la validación
    definitiva y la normalización viven en logica/validaciones.py.
    """

    digitos = re.sub(r"\D", "", str(valor or ""))[:10]

    if len(digitos) <= 3:
        return digitos

    if len(digitos) <= 6:
        return f"{digitos[:3]}-{digitos[3:]}"

    return f"{digitos[:3]}-{digitos[3:6]}-{digitos[6:]}"


def vincular_formato_telefono(entrada):
    """Aplica el formato 222-222-2222 mientras el usuario escribe."""

    def al_escribir(event):

        if getattr(event, "keysym", "") in _TECLAS_SIN_FORMATO:
            return

        actual = entrada.get()
        formateado = formatear_telefono_visual(actual)

        if formateado != actual:

            entrada.delete(0, "end")
            entrada.insert(0, formateado)
            entrada.icursor("end")

    entrada.bind("<KeyRelease>", al_escribir, add="+")
    entrada.bind("<FocusOut>", al_escribir, add="+")


def bloquear_rueda(widget):
    """Evita que la rueda del ratón cambie el valor de un widget."""

    def bloquear(event):
        return "break"

    widget.bind("<MouseWheel>", bloquear, add="+")
    widget.bind("<Button-4>", bloquear, add="+")
    widget.bind("<Button-5>", bloquear, add="+")