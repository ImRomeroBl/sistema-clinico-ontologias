import customtkinter as ctk

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

# -----------------------------
# IMPORTAR MODULOS
# -----------------------------

from interfaz.pacientes import mostrar_pacientes
from interfaz.medicos import mostrar_medicos
from interfaz.citas import mostrar_citas
from interfaz.recetas import mostrar_recetas
from interfaz.medicamentos import mostrar_medicamentos

# -----------------------------
# CREAR INTERFAZ
# -----------------------------

def crear_interfaz():

    # -----------------------------
    # CONFIGURACION GLOBAL
    # -----------------------------

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # -----------------------------
    # VENTANA PRINCIPAL
    # -----------------------------

    ventana = ctk.CTk()

    ventana.title("Sistema Clínico Ontológico")

    ventana.geometry("1400x800")

    ventana.minsize(1200, 700)

    ventana.configure(fg_color=BACKGROUND)

    # -----------------------------
    # MENU LATERAL
    # -----------------------------

    menu_lateral = ctk.CTkFrame(
        ventana,
        width=260,
        fg_color=SIDEBAR,
        corner_radius=0
    )

    menu_lateral.pack(
        side="left",
        fill="y"
    )

    menu_lateral.pack_propagate(False)

    # -----------------------------
    # PANEL PRINCIPAL
    # -----------------------------

    panel_principal = ctk.CTkFrame(
        ventana,
        fg_color=BACKGROUND,
        corner_radius=0
    )

    panel_principal.pack(
        side="right",
        expand=True,
        fill="both"
    )

    # -----------------------------
    # TITULO MENU
    # -----------------------------

    titulo_menu = ctk.CTkLabel(
        menu_lateral,
        text="Sistema Clínico",
        font=TITLE,
        text_color=TEXT
    )

    titulo_menu.pack(
        pady=(40, 10)
    )

    subtitulo_menu = ctk.CTkLabel(
        menu_lateral,
        text="Panel Ontológico Médico",
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY
    )

    subtitulo_menu.pack(
        pady=(0, 30)
    )

    # -----------------------------
    # FUNCION BOTONES MENU
    # -----------------------------

    def crear_boton_menu(texto, comando):

        boton = ctk.CTkButton(
            menu_lateral,
            text=texto,
            command=comando,
            height=50,
            corner_radius=12,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER,
            text_color="white",
            font=BUTTON_FONT,
            anchor="w"
        )

        boton.pack(
            fill="x",
            padx=20,
            pady=8
        )

    # -----------------------------
    # BOTONES
    # -----------------------------

    crear_boton_menu(
        "👤  Pacientes",
        lambda: mostrar_pacientes(panel_principal)
    )

    crear_boton_menu(
        "🩺  Médicos",
        lambda: mostrar_medicos(panel_principal)
    )

    crear_boton_menu(
        "📅  Citas",
        lambda: mostrar_citas(panel_principal)
    )

    crear_boton_menu(
        "📄  Recetas",
        lambda: mostrar_recetas(panel_principal)
    )

    crear_boton_menu(
        "💊  Medicamentos",
        lambda: mostrar_medicamentos(panel_principal)
    )

    # -----------------------------
    # SEPARADOR
    # -----------------------------

    separador = ctk.CTkFrame(
        menu_lateral,
        height=2,
        fg_color=BORDER
    )

    separador.pack(
        fill="x",
        padx=20,
        pady=30
    )

    # -----------------------------
    # FOOTER MENU
    # -----------------------------

    footer = ctk.CTkLabel(
        menu_lateral,
        text="Sistema Clínico v1.0",
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY
    )

    footer.pack(
        side="bottom",
        pady=20
    )

    # -----------------------------
    # PANTALLA INICIAL
    # -----------------------------

    contenedor_inicio = ctk.CTkFrame(
        panel_principal,
        fg_color="transparent"
    )

    contenedor_inicio.pack(
        expand=True
    )

    titulo_inicio = ctk.CTkLabel(
        contenedor_inicio,
        text="Bienvenido al Sistema Clínico",
        font=("Inter", 38, "bold"),
        text_color=TEXT
    )

    titulo_inicio.pack(
        pady=(0, 15)
    )

    subtitulo_inicio = ctk.CTkLabel(
        contenedor_inicio,
        text="Sistema Ontológico para Gestión Médica",
        font=SUBTITLE,
        text_color=TEXT_SECONDARY
    )

    subtitulo_inicio.pack(
        pady=(0, 40)
    )

    # -----------------------------
    # CARDS DASHBOARD
    # -----------------------------

    contenedor_cards = ctk.CTkFrame(
        contenedor_inicio,
        fg_color="transparent"
    )

    contenedor_cards.pack()

    # -----------------------------
    # FUNCION CREAR CARD
    # -----------------------------

    def crear_card(parent, titulo, valor):

        card = ctk.CTkFrame(
            parent,
            width=220,
            height=130,
            fg_color=CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER
        )

        card.pack_propagate(False)

        titulo_card = ctk.CTkLabel(
            card,
            text=titulo,
            font=TEXT_FONT,
            text_color=TEXT_SECONDARY
        )

        titulo_card.pack(
            pady=(25, 10)
        )

        valor_card = ctk.CTkLabel(
            card,
            text=valor,
            font=("Inter", 32, "bold"),
            text_color=TEXT
        )

        valor_card.pack()

        return card

    # -----------------------------
    # CARDS
    # -----------------------------

    card1 = crear_card(
        contenedor_cards,
        "Pacientes",
        "120"
    )

    card1.grid(
        row=0,
        column=0,
        padx=15
    )

    card2 = crear_card(
        contenedor_cards,
        "Médicos",
        "25"
    )

    card2.grid(
        row=0,
        column=1,
        padx=15
    )

    card3 = crear_card(
        contenedor_cards,
        "Citas",
        "48"
    )

    card3.grid(
        row=0,
        column=2,
        padx=15
    )

    # -----------------------------
    # RETORNAR VENTANA
    # -----------------------------

    return ventana
