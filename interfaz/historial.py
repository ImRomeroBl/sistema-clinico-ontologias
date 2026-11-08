"""
Vista de Historial Clínico.

Pantalla de solo lectura que permite seleccionar un paciente y consultar su
expediente en pestañas: resumen, consultas, recetas, citas y registros clínicos
(diagnósticos y estudios). No escribe en la ontología: toda la información se
obtiene de logica/historial.py.

Reutiliza los componentes visuales y la paleta del resto del sistema para
mantener la consistencia con las pantallas de gestión.
"""

from tkinter import messagebox, ttk

import customtkinter as ctk

from interfaz.components.searchable_combobox import ComboBuscable
from interfaz.components.table import crear_tabla
from interfaz.components.ui import (
    crear_card,
    crear_label,
    crear_subtitulo,
    crear_titulo,
)
from interfaz.theme.colors import (
    BACKGROUND,
    BORDER,
    CARD,
    PRIMARY,
    TEXT,
    TEXT_SECONDARY,
)
from interfaz.theme.fonts import TEXT_FONT
from logica.historial import obtener_historial
from logica.language_manager import language_manager, t
from logica.pacientes import listar_pacientes

# -----------------------------
# CLAVES DE COLUMNAS
# -----------------------------

CLAVES_COLUMNAS = {
    "Fecha": "historial.columns.date",
    "Médico": "historial.columns.doctor",
    "Notas": "historial.columns.notes",
    "Diagnósticos": "historial.columns.diagnoses",
    "Medicamento": "historial.columns.medication",
    "Dosis": "historial.columns.dose",
    "Indicaciones": "historial.columns.indications",
    "Hora": "historial.columns.time",
    "Tipo": "historial.columns.type",
    "Descripción": "historial.columns.description",
    "Consulta (fecha)": "historial.columns.consultation_date",
}


def _actualizar_encabezados(tabla):
    """Traduce los encabezados de una tabla conservando sus identificadores."""
    for columna in tabla["columns"]:
        clave = CLAVES_COLUMNAS.get(columna)
        if clave:
            tabla.heading(columna, text=t(clave))


# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_historial(panel):
    """Muestra el historial clínico de solo lectura de un paciente."""

    # -----------------------------
    # LIMPIAR PANEL
    # -----------------------------

    for widget in panel.winfo_children():
        widget.destroy()

    panel.configure(fg_color=BACKGROUND)

    # -----------------------------
    # CONTENEDOR PRINCIPAL
    # -----------------------------

    contenedor = ctk.CTkFrame(
        panel,
        fg_color="transparent"
    )

    contenedor.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=30
    )

    titulo = crear_titulo(
        contenedor,
        t("historial.title")
    )

    titulo.pack(
        anchor="w",
        pady=(0, 10)
    )

    subtitulo = crear_subtitulo(
        contenedor,
        t("historial.subtitle")
    )

    subtitulo.pack(
        anchor="w",
        pady=(0, 20)
    )

    # -----------------------------
    # SELECTOR DE PACIENTE
    # -----------------------------

    card_selector = crear_card(contenedor)

    card_selector.pack(
        fill="x",
        pady=(0, 15)
    )

    frame_selector = ctk.CTkFrame(
        card_selector,
        fg_color="transparent"
    )

    frame_selector.pack(
        fill="x",
        padx=30,
        pady=20
    )

    etiqueta_paciente = crear_label(
        frame_selector,
        t("historial.fields.patient.label")
    )

    etiqueta_paciente.pack(
        side="left",
        padx=(0, 15)
    )

    combo_paciente = ComboBuscable(
        frame_selector,
        valores=[],
        font=("Inter", 13),
        width=52
    )

    combo_paciente.pack(
        side="left"
    )

    estado = ctk.CTkLabel(
        contenedor,
        text=t("historial.messages.empty_selection"),
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY,
        anchor="w",
        justify="left",
        wraplength=1000
    )

    estado.pack(
        anchor="w",
        pady=(0, 10)
    )

    # -----------------------------
    # PESTAÑAS
    # -----------------------------

    notebook = ttk.Notebook(
        contenedor,
        style="Historial.TNotebook"
    )

    notebook.pack(
        fill="both",
        expand=True
    )

    tab_resumen = ctk.CTkFrame(
        notebook,
        fg_color=CARD,
        corner_radius=0
    )

    tab_consultas = ctk.CTkFrame(
        notebook,
        fg_color=CARD,
        corner_radius=0
    )

    tab_recetas = ctk.CTkFrame(
        notebook,
        fg_color=CARD,
        corner_radius=0
    )

    tab_citas = ctk.CTkFrame(
        notebook,
        fg_color=CARD,
        corner_radius=0
    )

    tab_registros = ctk.CTkFrame(
        notebook,
        fg_color=CARD,
        corner_radius=0
    )

    tabs = (
        (tab_resumen, "historial.tabs.summary"),
        (tab_consultas, "historial.tabs.consultations"),
        (tab_recetas, "historial.tabs.prescriptions"),
        (tab_citas, "historial.tabs.appointments"),
        (tab_registros, "historial.tabs.studies_diagnoses"),
    )

    for tab, clave in tabs:
        notebook.add(tab, text=t(clave))

    # -----------------------------
    # PESTAÑA RESUMEN
    # -----------------------------

    contenido_resumen = ctk.CTkFrame(
        tab_resumen,
        fg_color="transparent"
    )

    contenido_resumen.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=30
    )

    resumen_nombre = ctk.CTkLabel(
        contenido_resumen,
        text=t("historial.labels.no_patient_selected"),
        font=("Inter", 26, "bold"),
        text_color=TEXT,
        anchor="w"
    )

    resumen_nombre.pack(
        anchor="w"
    )

    resumen_detalle = ctk.CTkLabel(
        contenido_resumen,
        text=(
            f"{t('historial.labels.age')} —    "
            f"{t('historial.labels.phone')} —"
        ),
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY,
        anchor="w"
    )

    resumen_detalle.pack(
        anchor="w",
        pady=(5, 20)
    )

    frame_tiles = ctk.CTkFrame(
        contenido_resumen,
        fg_color="transparent"
    )

    frame_tiles.pack(
        fill="x",
        pady=(0, 20)
    )

    for columna in range(5):
        frame_tiles.grid_columnconfigure(columna, weight=1)

    def crear_tile(parent, etiqueta):
        """Crea una tarjeta de conteo con valor y título."""

        tile = ctk.CTkFrame(
            parent,
            fg_color=BACKGROUND,
            corner_radius=14,
            border_width=1,
            border_color=BORDER
        )

        valor = ctk.CTkLabel(
            tile,
            text="0",
            font=("Inter", 28, "bold"),
            text_color=TEXT
        )

        valor.pack(
            pady=(15, 5)
        )

        titulo_tile = ctk.CTkLabel(
            tile,
            text=etiqueta,
            font=TEXT_FONT,
            text_color=TEXT_SECONDARY
        )

        titulo_tile.pack(
            pady=(0, 15)
        )

        return tile, valor, titulo_tile

    tiles = {}
    tiles_titulos = {}

    definicion_tiles = [
        ("consultas", "historial.tabs.consultations"),
        ("recetas", "historial.tabs.prescriptions"),
        ("citas", "historial.tabs.appointments"),
        ("diagnosticos", "historial.records.diagnosis"),
        ("estudios", "historial.records.study")
    ]

    for indice, (clave, clave_texto) in enumerate(definicion_tiles):

        tile, valor, titulo_tile = crear_tile(
            frame_tiles,
            t(clave_texto)
        )

        tile.grid(
            row=0,
            column=indice,
            padx=6,
            sticky="nsew"
        )

        tiles[clave] = valor
        tiles_titulos[clave] = (titulo_tile, clave_texto)

    resumen_ultima = ctk.CTkLabel(
        contenido_resumen,
        text=t("historial.empty.consultations_short"),
        font=TEXT_FONT,
        text_color=TEXT_SECONDARY,
        anchor="w",
        justify="left",
        wraplength=1000
    )

    resumen_ultima.pack(
        anchor="w"
    )

    # -----------------------------
    # PESTAÑAS CON TABLAS
    # -----------------------------

    def crear_tabla_historial(tab, columnas, anchos, anclajes=None, altura=8):
        """Crea una tabla de solo lectura con su etiqueta de estado."""

        contenido = ctk.CTkFrame(
            tab,
            fg_color="transparent"
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        estado_tabla = ctk.CTkLabel(
            contenido,
            text=t("historial.labels.no_data_loaded"),
            font=TEXT_FONT,
            text_color=TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=900
        )

        estado_tabla.pack(
            anchor="w",
            pady=(0, 10)
        )

        frame_tabla, tabla = crear_tabla(
            parent=contenido,
            columnas=columnas,
            altura=altura
        )

        _actualizar_encabezados(tabla)

        frame_tabla.pack(
            fill="both",
            expand=True
        )

        for columna, ancho in anchos.items():

            tabla.column(
                columna,
                width=ancho,
                anchor=(anclajes or {}).get(columna, "w")
            )

        return estado_tabla, tabla

    estado_consultas, tabla_consultas = crear_tabla_historial(
        tab_consultas,
        ["Fecha", "Médico", "Notas", "Diagnósticos"],
        {
            "Fecha": 120,
            "Médico": 180,
            "Notas": 420,
            "Diagnósticos": 280
        },
        anclajes={
            "Fecha": "center",
            "Médico": "center"
        }
    )

    estado_recetas, tabla_recetas = crear_tabla_historial(
        tab_recetas,
        ["Médico", "Medicamento", "Dosis", "Indicaciones"],
        {
            "Médico": 180,
            "Medicamento": 180,
            "Dosis": 220,
            "Indicaciones": 400
        },
        anclajes={
            "Médico": "center",
            "Medicamento": "center"
        }
    )

    estado_citas, tabla_citas = crear_tabla_historial(
        tab_citas,
        ["Fecha", "Hora", "Médico"],
        {
            "Fecha": 140,
            "Hora": 140,
            "Médico": 240
        },
        anclajes={
            "Fecha": "center",
            "Hora": "center",
            "Médico": "center"
        }
    )

    estado_registros, tabla_registros = crear_tabla_historial(
        tab_registros,
        ["Tipo", "Descripción", "Consulta (fecha)", "Médico"],
        {
            "Tipo": 120,
            "Descripción": 300,
            "Consulta (fecha)": 160,
            "Médico": 200
        },
        anclajes={
            "Tipo": "center",
            "Consulta (fecha)": "center",
            "Médico": "center"
        }
    )

    # -----------------------------
    # ESTILO DE PESTAÑAS
    # -----------------------------

    style = ttk.Style()

    # Iguala el fondo del área de pestañas con el resto de la paleta.
    style.configure(
        "TNotebook",
        background=CARD,
        borderwidth=0
    )

    style.configure(
        "Historial.TNotebook",
        background=CARD,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0)
    )

    style.configure(
        "Historial.TNotebook.Tab",
        background=BACKGROUND,
        foreground=TEXT_SECONDARY,
        padding=(18, 10),
        font=("Inter", 12, "bold"),
        borderwidth=0
    )

    style.map(
        "Historial.TNotebook.Tab",
        background=[("selected", PRIMARY)],
        foreground=[("selected", "white")]
    )

    # -----------------------------
    # CARGA DE PACIENTES
    # -----------------------------

    pacientes_por_opcion = {}
    opciones = []
    error_pacientes = None
    historial_actual = [None]

    try:

        pacientes = listar_pacientes()

    # Frontera de interfaz: cualquier fallo del servicio se muestra sin cerrar la app.
    except Exception as error:  # noqa: BLE001

        pacientes = []
        error_pacientes = error

    vistos = {}

    for paciente in pacientes:

        base = (
            paciente.get("nombre")
            or paciente.get("id")
            or t("common.no_name")
        )

        vistos[base] = vistos.get(base, 0) + 1

        if vistos[base] == 1:

            opcion = base

        else:

            opcion = f"{base} [{str(paciente.get('id', ''))[:8]}]"

        opciones.append(opcion)
        pacientes_por_opcion[opcion] = paciente.get("id")

    combo_paciente.establecer_valores(opciones)

    if error_pacientes is not None:

        combo_paciente.configure(state="disabled")

        estado.configure(
            text=(
                f"{t('historial.messages.load_patients_error')} "
                f"{error_pacientes}"
            )
        )

    elif not opciones:

        combo_paciente.configure(state="disabled")

        estado.configure(
            text=t("historial.messages.no_patients")
        )

    # -----------------------------
    # HELPERS DE RENDERIZADO
    # -----------------------------

    def limpiar_tabla(tabla):
        """Elimina todas las filas de una tabla."""

        for item in tabla.get_children():
            tabla.delete(item)

    def texto(valor, defecto=None):
        """Normaliza un valor para mostrarlo en la interfaz."""

        if defecto is None:
            defecto = t("common.no_registration")

        if valor is None:
            return defecto

        valor = str(valor).strip()

        return valor if valor else defecto

    def cargar_resumen(historial):
        """Carga los datos generales y los conteos del paciente."""

        datos = historial["paciente"]
        conteos = historial["conteos"]

        resumen_nombre.configure(
            text=texto(
                datos.get("nombre"),
                t("historial.labels.patient_without_name")
            )
        )

        resumen_detalle.configure(
            text=(
                f"{t('historial.labels.age')} "
                f"{texto(datos.get('edad'), t('historial.labels.not_recorded'))}"
                f"    {t('historial.labels.phone')} "
                f"{texto(datos.get('telefono'), t('historial.labels.not_recorded_m'))}"
            )
        )

        for clave, etiqueta_valor in tiles.items():
            etiqueta_valor.configure(
                text=str(conteos.get(clave, 0))
            )

        ultima = historial.get("ultima_consulta")

        if ultima is None:

            resumen_ultima.configure(
                text=t("historial.empty.consultations_short")
            )

            return

        partes = [
            (
                f"{t('historial.labels.last_consultation')} "
                f"{texto(ultima.get('fecha'), t('common.no_date'))}"
            ),
            (
                f"{t('historial.labels.doctor')} "
                f"{texto(ultima.get('medico'), t('common.no_doctor'))}"
            ),
        ]

        diagnosticos = ultima.get("diagnosticos") or []

        if diagnosticos:

            nombres = ", ".join(
                texto(
                    diagnostico.get("nombre"),
                    t("common.no_diagnosis")
                )
                for diagnostico in diagnosticos
            )

            partes.append(
                f"{t('historial.labels.diagnosis')} {nombres}"
            )

        resumen_ultima.configure(
            text="    ·    ".join(partes)
        )

    def cargar_tabla(tabla, estado_tabla, filas, mensaje_vacio, mensaje_conteo):
        """Limpia una tabla, actualiza su estado e inserta las filas indicadas."""

        limpiar_tabla(tabla)

        estado_tabla.configure(
            text=mensaje_conteo if filas else mensaje_vacio
        )

        for fila in filas:
            tabla.insert("", "end", values=fila)

    def cargar_consultas(historial):
        """Carga la pestaña de consultas."""

        consultas = historial.get("consultas") or []
        filas = []

        for consulta in consultas:

            diagnosticos = ", ".join(
                texto(
                    diagnostico.get("nombre"),
                    t("common.no_diagnosis")
                )
                for diagnostico in (consulta.get("diagnosticos") or [])
            )

            filas.append((
                texto(consulta.get("fecha"), t("common.no_date")),
                texto(consulta.get("medico"), t("common.no_doctor")),
                texto(consulta.get("notas"), t("common.no_notes")),
                diagnosticos or t("common.no_diagnosis")
            ))

        cargar_tabla(
            tabla_consultas,
            estado_consultas,
            filas,
            t("historial.empty.consultations"),
            f"{len(filas)} {t('historial.counts.consultations')}"
        )

    def cargar_recetas(historial):
        """Carga la pestaña de recetas."""

        recetas = historial.get("recetas") or []
        filas = []

        for receta in recetas:

            filas.append((
                texto(receta.get("medico"), t("common.no_doctor")),
                texto(
                    receta.get("medicamento"),
                    t("common.no_medication")
                ),
                texto(receta.get("dosis"), t("common.no_dose")),
                texto(
                    receta.get("indicaciones"),
                    t("common.no_indications")
                )
            ))

        cargar_tabla(
            tabla_recetas,
            estado_recetas,
            filas,
            t("historial.empty.prescriptions"),
            f"{len(filas)} {t('historial.counts.prescriptions')}"
        )

    def cargar_citas(historial):
        """Carga la pestaña de citas."""

        citas = historial.get("citas") or []
        filas = []

        for cita in citas:

            filas.append((
                texto(cita.get("fecha"), t("common.no_date")),
                texto(cita.get("hora"), t("common.no_time")),
                texto(cita.get("medico"), t("common.no_doctor"))
            ))

        cargar_tabla(
            tabla_citas,
            estado_citas,
            filas,
            t("historial.empty.appointments"),
            f"{len(filas)} {t('historial.counts.appointments')}"
        )

    def cargar_registros(historial):
        """Carga la pestaña de diagnósticos y estudios."""

        registros = historial.get("registros_clinicos") or []
        filas = []

        for registro in registros:

            tipo = registro.get("tipo")

            if tipo == "Diagnóstico":
                tipo = t("historial.records.diagnosis")
            elif tipo == "Estudio":
                tipo = t("historial.records.study")

            filas.append((
                texto(tipo, t("common.no_type")),
                texto(registro.get("nombre"), t("common.no_description")),
                texto(registro.get("fecha"), t("common.no_date")),
                texto(registro.get("medico"), t("common.no_doctor"))
            ))

        cargar_tabla(
            tabla_registros,
            estado_registros,
            filas,
            t("historial.empty.records"),
            f"{len(filas)} {t('historial.counts.clinical_records')}"
        )

    def renderizar(historial):
        """Actualiza todas las pestañas con el historial recibido."""

        cargar_resumen(historial)
        cargar_consultas(historial)
        cargar_recetas(historial)
        cargar_citas(historial)
        cargar_registros(historial)

        datos = historial["paciente"]
        conteos = historial["conteos"]

        estado.configure(
            text=(
                f"{t('historial.labels.patient')} "
                f"{texto(datos.get('nombre'), t('common.no_name'))}  ·  "
                f"{t('historial.tabs.consultations')}: "
                f"{conteos.get('consultas', 0)}  ·  "
                f"{t('historial.tabs.prescriptions')}: "
                f"{conteos.get('recetas', 0)}  ·  "
                f"{t('historial.tabs.appointments')}: "
                f"{conteos.get('citas', 0)}"
            )
        )

    # -----------------------------
    # EVENTO DE SELECCION
    # -----------------------------

    def cargar_historial(event=None):
        """Carga el historial del paciente seleccionado."""

        opcion = combo_paciente.get()
        paciente_id = pacientes_por_opcion.get(opcion)

        if not paciente_id:

            if opcion:

                messagebox.showwarning(
                    t("historial.messages.invalid_patient_title"),
                    t("historial.messages.select_patient")
                )

            return

        try:

            historial = obtener_historial(paciente_id)

        # Frontera de interfaz: se informa el error sin cerrar la aplicación.
        except Exception as error:  # noqa: BLE001

            historial_actual[0] = None

            messagebox.showerror(
                t("common.error"),
                f"{t('historial.messages.load_error')}\n{error}"
            )

            estado.configure(
                text=t("historial.messages.load_error_short")
            )

            return

        if historial is None:

            historial_actual[0] = None

            messagebox.showwarning(
                t("historial.messages.no_data_title"),
                t("historial.messages.patient_not_found")
            )

            estado.configure(
                text=t("historial.messages.patient_not_found")
            )

            return

        historial_actual[0] = historial

        try:

            renderizar(historial)

        # Frontera de interfaz: se informa el error sin cerrar la aplicación.
        except Exception as error:  # noqa: BLE001

            messagebox.showerror(
                t("common.error"),
                f"{t('historial.messages.display_error')}\n{error}"
            )

            estado.configure(
                text=t("historial.messages.display_error_short")
            )

    combo_paciente.bind(
        "<<ComboboxSelected>>",
        cargar_historial
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def update_ui_strings(lang=None):

        titulo.configure(text=t("historial.title"))
        subtitulo.configure(text=t("historial.subtitle"))
        etiqueta_paciente.configure(
            text=t("historial.fields.patient.label")
        )

        for tab, clave in tabs:
            notebook.tab(tab, text=t(clave))

        for titulo_tile, clave in tiles_titulos.values():
            titulo_tile.configure(text=t(clave))

        for tabla in (
            tabla_consultas,
            tabla_recetas,
            tabla_citas,
            tabla_registros,
        ):
            _actualizar_encabezados(tabla)

        if historial_actual[0] is not None:

            renderizar(historial_actual[0])
            return

        for estado_tabla in (
            estado_consultas,
            estado_recetas,
            estado_citas,
            estado_registros,
        ):
            estado_tabla.configure(
                text=t("historial.labels.no_data_loaded")
            )

        resumen_nombre.configure(
            text=t("historial.labels.no_patient_selected")
        )
        resumen_detalle.configure(
            text=(
                f"{t('historial.labels.age')} —    "
                f"{t('historial.labels.phone')} —"
            )
        )
        resumen_ultima.configure(
            text=t("historial.empty.consultations_short")
        )

        if error_pacientes is not None:
            estado.configure(
                text=(
                    f"{t('historial.messages.load_patients_error')} "
                    f"{error_pacientes}"
                )
            )
        elif not opciones:
            estado.configure(text=t("historial.messages.no_patients"))
        else:
            estado.configure(
                text=t("historial.messages.empty_selection")
            )

    language_manager.add_listener(update_ui_strings)

    return lambda: language_manager.remove_listener(update_ui_strings)
