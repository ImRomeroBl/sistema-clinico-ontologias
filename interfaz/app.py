import customtkinter as ctk

# -----------------------------
# IMPORTAR MODULOS
# -----------------------------
from interfaz.citas import mostrar_citas
from interfaz.consultas import mostrar_consultas
from interfaz.estudios import mostrar_estudios
from interfaz.historial import mostrar_historial
from interfaz.medicamentos import mostrar_medicamentos
from interfaz.medicos import mostrar_medicos
from interfaz.pacientes import mostrar_pacientes
from interfaz.recetas import mostrar_recetas
from interfaz.theme.colors import (
    BACKGROUND,
    BORDER,
    CARD,
    PRIMARY,
    PRIMARY_HOVER,
    SIDEBAR,
    TEXT,
    TEXT_SECONDARY,
)
from interfaz.theme.fonts import BUTTON_FONT, SUBTITLE, TEXT_FONT, TITLE
from logica.citas import listar_citas
from logica.language_manager import language_manager, t
from logica.medicos import listar_medicos
from logica.pacientes import listar_pacientes

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

    ventana.title(t("app.window_title"))

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

    # El sidebar usa grid para reservar siempre espacio a la zona inferior
    # (selector de idioma y versión) y dejar el resto a los botones de menú.
    menu_lateral.grid_columnconfigure(0, weight=1)
    menu_lateral.grid_rowconfigure(2, weight=1)

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
        text=t("app.sidebar.title"),
        font=TITLE,
        text_color=TEXT
    )

    titulo_menu.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=20,
        pady=(28, 6)
    )

    subtitulo_menu = ctk.CTkLabel(
        menu_lateral,
        text=t("app.sidebar.subtitle"),
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY
    )

    subtitulo_menu.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=20,
        pady=(0, 12)
    )

    # -----------------------------
    # CONTENEDOR DE BOTONES
    # -----------------------------

    frame_botones_menu = ctk.CTkFrame(
        menu_lateral,
        fg_color="transparent",
        corner_radius=0
    )

    frame_botones_menu.grid(
        row=2,
        column=0,
        sticky="nsew"
    )

    # -----------------------------
    # FUNCION BOTONES MENU
    # -----------------------------

    botones_menu = []

    def crear_boton_menu(clave, comando):

        boton = ctk.CTkButton(
            frame_botones_menu,
            text=t(clave),
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
            padx=16,
            pady=5
        )

        botones_menu.append((boton, clave))

    # -----------------------------
    # CAMBIO DE VISTA ACTIVA
    # -----------------------------

    vista_actual = {"limpiar": None}

    def abrir_vista(mostrar):
        """Limpia el listener de la vista anterior y monta la nueva."""
        limpiar = vista_actual.get("limpiar")

        if callable(limpiar):
            limpiar()

        vista_actual["limpiar"] = None

        resultado = mostrar(panel_principal)

        if callable(resultado):
            vista_actual["limpiar"] = resultado

    # -----------------------------
    # BOTONES
    # -----------------------------

    crear_boton_menu(
        "menu.patients",
        lambda: abrir_vista(mostrar_pacientes)
    )

    crear_boton_menu(
        "menu.doctors",
        lambda: abrir_vista(mostrar_medicos)
    )

    crear_boton_menu(
        "menu.appointments",
        lambda: abrir_vista(mostrar_citas)
    )

    crear_boton_menu(
        "menu.consultations",
        lambda: abrir_vista(mostrar_consultas)
    )

    crear_boton_menu(
        "menu.prescriptions",
        lambda: abrir_vista(mostrar_recetas)
    )

    crear_boton_menu(
        "menu.medications",
        lambda: abrir_vista(mostrar_medicamentos)
    )

    crear_boton_menu(
        "menu.studies",
        lambda: abrir_vista(mostrar_estudios)
    )

    crear_boton_menu(
        "menu.history",
        lambda: abrir_vista(mostrar_historial)
    )

    # -----------------------------
    # ZONA INFERIOR: IDIOMA + VERSION
    # -----------------------------

    frame_inferior = ctk.CTkFrame(
        menu_lateral,
        fg_color="transparent",
        corner_radius=0
    )

    frame_inferior.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=20,
        pady=(10, 10)
    )

    frame_inferior.grid_columnconfigure(0, weight=1)

    # -----------------------------
    # SEPARADOR
    # -----------------------------

    separador = ctk.CTkFrame(
        frame_inferior,
        height=2,
        fg_color=BORDER
    )

    separador.grid(
        row=0,
        column=0,
        sticky="ew",
        pady=(0, 12)
    )

    # -----------------------------
    # SELECTOR DE IDIOMA
    # -----------------------------

    etiqueta_idioma = ctk.CTkLabel(
        frame_inferior,
        text=t("app.language.label"),
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY,
        anchor="w"
    )

    etiqueta_idioma.grid(
        row=1,
        column=0,
        sticky="ew",
        pady=(0, 6)
    )

    def cambiar_idioma(valor):
        codigo = "en" if valor == "English" else "es"
        language_manager.set_language(codigo)

    selector_idioma = ctk.CTkOptionMenu(
        frame_inferior,
        values=["Español", "English"],
        command=cambiar_idioma,
        width=180,
        height=34,
        corner_radius=8,
        fg_color=PRIMARY,
        button_color=PRIMARY_HOVER,
        button_hover_color=PRIMARY_HOVER,
        dropdown_fg_color=SIDEBAR,
        dropdown_hover_color=PRIMARY_HOVER,
        font=TEXT_FONT
    )

    selector_idioma.grid(
        row=2,
        column=0,
        sticky="ew"
    )

    # -----------------------------
    # FOOTER MENU
    # -----------------------------

    footer = ctk.CTkLabel(
        frame_inferior,
        text=t("app.version"),
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY
    )

    footer.grid(
        row=3,
        column=0,
        sticky="ew",
        pady=(14, 0)
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
        text=t("app.welcome"),
        font=("Inter", 38, "bold"),
        text_color=TEXT
    )

    titulo_inicio.pack(
        pady=(0, 15)
    )

    subtitulo_inicio = ctk.CTkLabel(
        contenedor_inicio,
        text=t("app.welcome_subtitle"),
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

    def crear_card(parent, clave, valor):

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
            text=t(clave),
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

        return card, titulo_card

    # -----------------------------
    # CARDS
    # -----------------------------

    total_pacientes = len(listar_pacientes())
    total_medicos = len(listar_medicos())
    total_citas = len(listar_citas())

    cards_texto = []

    card1, etiqueta_card1 = crear_card(
        contenedor_cards,
        "app.dashboard.patients",
        str(total_pacientes)
    )

    cards_texto.append((etiqueta_card1, "app.dashboard.patients"))

    card1.grid(
        row=0,
        column=0,
        padx=15
    )

    card2, etiqueta_card2 = crear_card(
        contenedor_cards,
        "app.dashboard.doctors",
        str(total_medicos)
    )

    cards_texto.append((etiqueta_card2, "app.dashboard.doctors"))

    card2.grid(
        row=0,
        column=1,
        padx=15
    )

    card3, etiqueta_card3 = crear_card(
        contenedor_cards,
        "app.dashboard.appointments",
        str(total_citas)
    )

    cards_texto.append((etiqueta_card3, "app.dashboard.appointments"))

    card3.grid(
        row=0,
        column=2,
        padx=15
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def update_ui_strings(lang=None):

        ventana.title(t("app.window_title"))

        titulo_menu.configure(text=t("app.sidebar.title"))
        subtitulo_menu.configure(text=t("app.sidebar.subtitle"))
        footer.configure(text=t("app.version"))
        etiqueta_idioma.configure(text=t("app.language.label"))

        for boton, clave in botones_menu:
            boton.configure(text=t(clave))

        selector_idioma.set(
            "English"
            if language_manager.current_language == "en"
            else "Español"
        )

        if contenedor_inicio.winfo_exists():

            titulo_inicio.configure(text=t("app.welcome"))
            subtitulo_inicio.configure(text=t("app.welcome_subtitle"))

            for etiqueta_card, clave in cards_texto:
                etiqueta_card.configure(text=t(clave))

    language_manager.add_listener(update_ui_strings)

    def _al_destruir(event):

        if event.widget is ventana:
            language_manager.remove_listener(update_ui_strings)

    ventana.bind("<Destroy>", _al_destruir, add="+")

    # -----------------------------
    # RETORNAR VENTANA
    # -----------------------------

    return ventana
