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
from logica.pacientes import listar_pacientes

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
        "Historial Clínico"
    )

    titulo.pack(
        anchor="w",
        pady=(0, 10)
    )

    subtitulo = crear_subtitulo(
        contenedor,
        "Consulta el expediente clínico completo del paciente"
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
        "Paciente (escriba para filtrar)"
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
        text="Seleccione un paciente para cargar su historial.",
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

    notebook.add(tab_resumen, text="Resumen")
    notebook.add(tab_consultas, text="Consultas")
    notebook.add(tab_recetas, text="Recetas")
    notebook.add(tab_citas, text="Citas")
    notebook.add(tab_registros, text="Estudios y diagnósticos")

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
        text="Sin paciente seleccionado",
        font=("Inter", 26, "bold"),
        text_color=TEXT,
        anchor="w"
    )

    resumen_nombre.pack(
        anchor="w"
    )

    resumen_detalle = ctk.CTkLabel(
        contenido_resumen,
        text="Edad: —    Teléfono: —",
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

        return tile, valor

    tiles = {}

    definicion_tiles = [
        ("consultas", "Consultas"),
        ("recetas", "Recetas"),
        ("citas", "Citas"),
        ("diagnosticos", "Diagnósticos"),
        ("estudios", "Estudios")
    ]

    for indice, (clave, etiqueta) in enumerate(definicion_tiles):

        tile, valor = crear_tile(frame_tiles, etiqueta)

        tile.grid(
            row=0,
            column=indice,
            padx=6,
            sticky="nsew"
        )

        tiles[clave] = valor

    resumen_ultima = ctk.CTkLabel(
        contenido_resumen,
        text="Sin consultas registradas.",
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
            text="Sin datos cargados.",
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

    try:

        pacientes = listar_pacientes()

    # Frontera de interfaz: cualquier fallo del servicio se muestra sin cerrar la app.
    except Exception as error:  # noqa: BLE001

        pacientes = []
        error_pacientes = error

    vistos = {}

    for paciente in pacientes:

        base = paciente.get("nombre") or paciente.get("id") or "Sin nombre"

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
            text=f"No se pudieron cargar los pacientes: {error_pacientes}"
        )

    elif not opciones:

        combo_paciente.configure(state="disabled")

        estado.configure(
            text="No hay pacientes registrados."
        )

    # -----------------------------
    # HELPERS DE RENDERIZADO
    # -----------------------------

    def limpiar_tabla(tabla):
        """Elimina todas las filas de una tabla."""

        for item in tabla.get_children():
            tabla.delete(item)

    def texto(valor, defecto="Sin registro"):
        """Normaliza un valor para mostrarlo en la interfaz."""

        if valor is None:
            return defecto

        valor = str(valor).strip()

        return valor if valor else defecto

    def cargar_resumen(historial):
        """Carga los datos generales y los conteos del paciente."""

        datos = historial["paciente"]
        conteos = historial["conteos"]

        resumen_nombre.configure(
            text=texto(datos.get("nombre"), "Paciente sin nombre")
        )

        resumen_detalle.configure(
            text=(
                f"Edad: {texto(datos.get('edad'), 'No registrada')}    "
                f"Teléfono: {texto(datos.get('telefono'), 'No registrado')}"
            )
        )

        for clave, etiqueta_valor in tiles.items():
            etiqueta_valor.configure(
                text=str(conteos.get(clave, 0))
            )

        ultima = historial.get("ultima_consulta")

        if ultima is None:

            resumen_ultima.configure(
                text="Sin consultas registradas."
            )

            return

        partes = [
            f"Última consulta: {texto(ultima.get('fecha'), 'Sin fecha')}",
            f"Médico: {texto(ultima.get('medico'), 'Sin médico')}"
        ]

        diagnosticos = ultima.get("diagnosticos") or []

        if diagnosticos:

            nombres = ", ".join(
                texto(diagnostico.get("nombre"), "Sin diagnóstico")
                for diagnostico in diagnosticos
            )

            partes.append(f"Diagnóstico: {nombres}")

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
                texto(diagnostico.get("nombre"), "Sin diagnóstico")
                for diagnostico in (consulta.get("diagnosticos") or [])
            )

            filas.append((
                texto(consulta.get("fecha"), "Sin fecha"),
                texto(consulta.get("medico"), "Sin médico"),
                texto(consulta.get("notas"), "Sin notas"),
                diagnosticos or "Sin diagnóstico"
            ))

        cargar_tabla(
            tabla_consultas,
            estado_consultas,
            filas,
            "Sin consultas registradas para este paciente.",
            f"{len(filas)} consulta(s) registrada(s)."
        )

    def cargar_recetas(historial):
        """Carga la pestaña de recetas."""

        recetas = historial.get("recetas") or []
        filas = []

        for receta in recetas:

            filas.append((
                texto(receta.get("medico"), "Sin médico"),
                texto(receta.get("medicamento"), "Sin medicamento"),
                texto(receta.get("dosis"), "Sin dosis"),
                texto(receta.get("indicaciones"), "Sin indicaciones")
            ))

        cargar_tabla(
            tabla_recetas,
            estado_recetas,
            filas,
            "Sin recetas registradas para este paciente.",
            (
                f"{len(filas)} receta(s) registrada(s). "
                "La ontología no almacena fecha en las recetas."
            )
        )

    def cargar_citas(historial):
        """Carga la pestaña de citas."""

        citas = historial.get("citas") or []
        filas = []

        for cita in citas:

            filas.append((
                texto(cita.get("fecha"), "Sin fecha"),
                texto(cita.get("hora"), "Sin hora"),
                texto(cita.get("medico"), "Sin médico")
            ))

        cargar_tabla(
            tabla_citas,
            estado_citas,
            filas,
            "Sin citas registradas para este paciente.",
            f"{len(filas)} cita(s) registrada(s)."
        )

    def cargar_registros(historial):
        """Carga la pestaña de diagnósticos y estudios."""

        registros = historial.get("registros_clinicos") or []
        filas = []

        for registro in registros:

            filas.append((
                texto(registro.get("tipo"), "Sin tipo"),
                texto(registro.get("nombre"), "Sin descripción"),
                texto(registro.get("fecha"), "Sin fecha"),
                texto(registro.get("medico"), "Sin médico")
            ))

        cargar_tabla(
            tabla_registros,
            estado_registros,
            filas,
            "Sin diagnósticos ni estudios registrados.",
            f"{len(filas)} registro(s) clínico(s)."
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
                f"Paciente: {texto(datos.get('nombre'), 'Sin nombre')}  ·  "
                f"Consultas: {conteos.get('consultas', 0)}  ·  "
                f"Recetas: {conteos.get('recetas', 0)}  ·  "
                f"Citas: {conteos.get('citas', 0)}"
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
                    "Paciente no válido",
                    "Seleccione un paciente de la lista."
                )

            return

        try:

            historial = obtener_historial(paciente_id)

        # Frontera de interfaz: se informa el error sin cerrar la aplicación.
        except Exception as error:  # noqa: BLE001

            messagebox.showerror(
                "Error",
                f"No se pudo cargar el historial:\n{error}"
            )

            estado.configure(
                text="No se pudo cargar el historial."
            )

            return

        if historial is None:

            messagebox.showwarning(
                "Sin datos",
                "El paciente seleccionado no existe."
            )

            estado.configure(
                text="El paciente seleccionado no existe."
            )

            return

        try:

            renderizar(historial)

        # Frontera de interfaz: se informa el error sin cerrar la aplicación.
        except Exception as error:  # noqa: BLE001

            messagebox.showerror(
                "Error",
                f"No se pudo mostrar el historial:\n{error}"
            )

            estado.configure(
                text="No se pudo mostrar el historial."
            )

    combo_paciente.bind(
        "<<ComboboxSelected>>",
        cargar_historial
    )
