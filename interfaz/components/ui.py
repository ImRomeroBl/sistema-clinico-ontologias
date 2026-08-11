import customtkinter as ctk

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

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

def crear_input(parent, placeholder=""):

    entry = ctk.CTkEntry(
        parent,
        height=42,
        corner_radius=10,
        border_color=BORDER,
        fg_color="#0F172A",
        text_color=TEXT,
        placeholder_text=placeholder,
        font=TEXT_FONT
    )

    return entry

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