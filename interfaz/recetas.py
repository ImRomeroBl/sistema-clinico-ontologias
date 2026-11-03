"""Visor histórico de Recetas (estrictamente solo lectura).

Este módulo funciona como registro global de auditoría clínica: muestra las
recetas existentes y, al seleccionar una fila, presenta el detalle de la
prescripción junto con las alertas semánticas del medicamento asociado.

No expone formularios ni acciones de creación, modificación o eliminación. Toda
la lectura de datos se delega en logica/recetas.py y logica/medicamentos.py.
"""

from tkinter import END

import customtkinter as ctk

from interfaz.components.alert_panel import PanelAlertasMedicamento
from interfaz.components.table import crear_tabla
from interfaz.components.ui import (
    crear_card,
    crear_label,
    crear_subtitulo,
    crear_textbox,
    crear_titulo,
)
from interfaz.theme.colors import BACKGROUND, TEXT
from logica.medicamentos import (
    obtener_alertas_medicamento,
    obtener_medicamento,
)
from logica.recetas import listar_recetas

COLUMNAS = (
    "Paciente",
    "Médico",
    "Medicamento",
    "Dosis",
    "Indicaciones",
)

ANCHOS_COLUMNA = {
    "Paciente": 130,
    "Médico": 130,
    "Medicamento": 130,
    "Dosis": 100,
    "Indicaciones": 220,
}

MENSAJE_SIN_RECETA = (
    "Seleccione una receta del historial para ver su detalle."
)

MENSAJE_ALERTA_SIN_RECETA = (
    "Seleccione una receta para auditar el medicamento."
)

# -----------------------------
# HELPERS DE PRESENTACIÓN
# -----------------------------

def _formatear_detalle_receta(receta):
    """Devuelve el detalle legible de una receta."""
    return (
        f"Paciente: {receta['paciente'] or 'Sin paciente'}\n"
        f"Médico: {receta['medico'] or 'Sin médico'}\n"
        f"Medicamento: {receta['medicamento'] or 'Sin medicamento'}\n"
        f"Dosis: {receta['dosis'] or 'Sin dosis'}\n"
        f"Indicaciones: {receta['indicaciones'] or 'Sin indicaciones'}"
    )

# -----------------------------
# FUNCIÓN PRINCIPAL
# -----------------------------

def mostrar_recetas(panel):
    """Muestra el historial de recetas en modo auditoría de solo lectura."""

    for widget in panel.winfo_children():
        widget.destroy()

    panel.configure(fg_color=BACKGROUND)

    recetas_por_id = {}

    # -----------------------------
    # CONTENEDOR
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
        "Auditoría de Recetas"
    )
    titulo.pack(anchor="w")

    subtitulo = crear_subtitulo(
        contenedor,
        "Visor histórico de solo lectura. Seleccione una receta para "
        "consultar las alertas semánticas de su medicamento."
    )
    subtitulo.pack(
        anchor="w",
        pady=(4, 18)
    )

    card = crear_card(contenedor)
    card.pack(
        fill="both",
        expand=True
    )

    cuerpo = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )
    cuerpo.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=25
    )
    cuerpo.grid_rowconfigure(0, weight=1)
    cuerpo.grid_columnconfigure(0, weight=3, minsize=640)
    cuerpo.grid_columnconfigure(1, weight=2, minsize=330)

    # -----------------------------
    # HISTORIAL DE RECETAS
    # -----------------------------

    panel_izq = ctk.CTkFrame(
        cuerpo,
        fg_color="transparent"
    )
    panel_izq.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 18)
    )
    panel_izq.grid_rowconfigure(1, weight=1)
    panel_izq.grid_columnconfigure(0, weight=1)

    etiqueta_historial = crear_label(
        panel_izq,
        "Historial global de recetas"
    )
    etiqueta_historial.configure(
        font=("Inter", 16, "bold"),
        text_color=TEXT
    )
    etiqueta_historial.grid(
        row=0,
        column=0,
        sticky="w",
        pady=(0, 10)
    )

    tabla_frame, tabla = crear_tabla(
        panel_izq,
        list(COLUMNAS),
        altura=14
    )
    tabla_frame.grid(
        row=1,
        column=0,
        sticky="nsew"
    )

    for columna, ancho in ANCHOS_COLUMNA.items():

        tabla.column(
            columna,
            width=ancho,
            anchor="center" if columna == "Dosis" else "w"
        )

    # -----------------------------
    # AUDITORÍA DE LA RECETA SELECCIONADA
    # -----------------------------

    panel_der = ctk.CTkFrame(
        cuerpo,
        fg_color="transparent"
    )
    panel_der.grid(
        row=0,
        column=1,
        sticky="nsew"
    )
    panel_der.grid_rowconfigure(3, weight=1)
    panel_der.grid_columnconfigure(0, weight=1)

    etiqueta_auditoria = crear_label(
        panel_der,
        "Auditoría de la receta seleccionada"
    )
    etiqueta_auditoria.configure(
        font=("Inter", 16, "bold"),
        text_color=TEXT
    )
    etiqueta_auditoria.grid(
        row=0,
        column=0,
        sticky="w",
        pady=(0, 10)
    )

    panel_alerta = PanelAlertasMedicamento(
        panel_der,
        mensaje_sin_seleccion=MENSAJE_ALERTA_SIN_RECETA
    )
    panel_alerta.grid(
        row=1,
        column=0,
        sticky="ew",
        pady=(0, 12)
    )

    etiqueta_detalle = crear_label(
        panel_der,
        "Datos de la prescripción"
    )
    etiqueta_detalle.configure(
        font=("Inter", 13, "bold"),
        text_color=TEXT
    )
    etiqueta_detalle.grid(
        row=2,
        column=0,
        sticky="w",
        pady=(0, 6)
    )

    detalle = crear_textbox(
        panel_der,
        height=150,
        width=320
    )
    detalle.grid(
        row=3,
        column=0,
        sticky="nsew"
    )
    detalle.configure(state="disabled")

    # -----------------------------
    # EVENTOS
    # -----------------------------

    def mostrar_detalle(texto):
        """Escribe texto en el visor de detalle sin permitir edición."""

        detalle.configure(state="normal")
        detalle.delete("1.0", END)

        if texto:
            detalle.insert("1.0", texto)

        detalle.configure(state="disabled")

    def limpiar_seleccion():
        """Restablece el detalle y el panel de alertas."""

        mostrar_detalle(MENSAJE_SIN_RECETA)
        panel_alerta.limpiar()

    def seleccionar_receta(event=None):
        """Actualiza el detalle y las alertas al seleccionar una fila."""

        seleccion = tabla.selection()

        if not seleccion:

            limpiar_seleccion()

            return

        receta = recetas_por_id.get(seleccion[0])

        if receta is None:

            limpiar_seleccion()

            return

        mostrar_detalle(
            _formatear_detalle_receta(receta)
        )

        medicamento = obtener_medicamento(
            receta.get("medicamento_id")
            or receta.get("medicamento")
        )

        panel_alerta.mostrar(
            obtener_alertas_medicamento(medicamento)
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_receta
    )

    def cargar_recetas():
        """Carga el historial completo y limpia la selección anterior."""

        for item in tabla.get_children():
            tabla.delete(item)

        recetas_por_id.clear()

        for receta in listar_recetas():

            recetas_por_id[receta["id"]] = receta

            tabla.insert(
                "",
                END,
                iid=receta["id"],
                values=(
                    receta["paciente"],
                    receta["medico"],
                    receta["medicamento"],
                    receta["dosis"],
                    receta["indicaciones"]
                )
            )

        limpiar_seleccion()

    # -----------------------------
    # CARGA INICIAL
    # -----------------------------

    cargar_recetas()
