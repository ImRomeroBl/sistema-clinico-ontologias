from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.language_manager import language_manager, t
from logica.medicamentos import (
    TIPOS_MEDICAMENTO,
    actualizar_medicamento,
    crear_medicamento,
    eliminar_medicamento,
    listar_contraindicaciones,
    listar_efectos_secundarios,
    listar_medicamentos,
)

# --------------------------------
# HELPERS
# --------------------------------

CLAVES_TIPO = {
    "generico": "medicamentos.types.generic",
    "analgesico": "medicamentos.types.analgesic",
    "antibiotico": "medicamentos.types.antibiotic",
    "antiinflamatorio": "medicamentos.types.antiinflammatory",
}


def _etiquetas_tipo():
    """Devuelve el mapa clave interna -> etiqueta traducida del tipo."""
    return {
        clave: t(CLAVES_TIPO.get(clave, CLAVES_TIPO["generico"]))
        for clave, _ in TIPOS_MEDICAMENTO
    }


def _resumen(texto, limite=35):
    """Convierte un texto multilínea en una vista previa breve de una línea."""
    texto = " ".join(str(texto or "").split())

    if len(texto) <= limite:
        return texto

    return texto[:limite].rstrip() + "..."

# --------------------------------
# MOSTRAR MEDICAMENTOS
# --------------------------------

def mostrar_medicamentos(panel):

    medicamento_seleccionado = [None]
    medicamentos_por_id = {}

    etiquetas_tipo = _etiquetas_tipo()
    tipo_por_etiqueta = {
        etiqueta: clave
        for clave, etiqueta in etiquetas_tipo.items()
    }
    tipos = list(etiquetas_tipo.values())

    contraindicaciones = listar_contraindicaciones()
    efectos_secundarios = listar_efectos_secundarios()

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo=t("medicamentos.title"),
        columnas=[
            "Nombre",
            "Tipo",
            "Contraindicaciones",
            "Efectos Secundarios"
        ],
        altura=6,
        campos=[
            {
                "clave": "nombre",
                "label": t("medicamentos.fields.name.label"),
                "placeholder": t("medicamentos.fields.name.placeholder"),
                "grupo": 0
            },
            {
                "clave": "tipo",
                "label": t("medicamentos.fields.type.label"),
                "tipo": "combo",
                "valores": tipos,
                "grupo": 1
            },
            {
                "clave": "contraindicaciones",
                "label": t("medicamentos.fields.contraindications.label"),
                "tipo": "multiple",
                "opciones": contraindicaciones,
                "altura": 130,
                "grupo": 0
            },
            {
                "clave": "efectos_secundarios",
                "label": t("medicamentos.fields.side_effects.label"),
                "tipo": "multiple",
                "opciones": efectos_secundarios,
                "altura": 130,
                "grupo": 1
            }
        ]
    )

    tabla = vista.tabla

    tabla.column("Nombre", width=200, anchor="w")
    tabla.column("Tipo", width=140, anchor="center")
    tabla.column("Contraindicaciones", width=330, anchor="w")
    tabla.column("Efectos Secundarios", width=330, anchor="w")

    for columna, clave in (
        ("Nombre", "medicamentos.columns.name"),
        ("Tipo", "medicamentos.columns.type"),
        ("Contraindicaciones", "medicamentos.columns.contraindications"),
        ("Efectos Secundarios", "medicamentos.columns.side_effects"),
    ):
        tabla.heading(columna, text=t(clave))

    combo_tipo = vista.widgets["tipo"]
    combo_tipo.configure(state="readonly")

    # -----------------------------
    # HELPERS DEL FORMULARIO
    # -----------------------------

    def tipo_seleccionado():
        return tipo_por_etiqueta.get(combo_tipo.get(), "generico")

    def limpiar_formulario():
        vista.limpiar_campos()
        combo_tipo.set(etiquetas_tipo["generico"])

    # -----------------------------
    # CARGAR MEDICAMENTOS
    # -----------------------------

    def cargar_medicamentos():

        medicamentos_por_id.clear()
        vista.limpiar_tabla()

        for medicamento in listar_medicamentos():

            medicamentos_por_id[medicamento["id"]] = medicamento

            vista.insertar_fila(
                (
                    medicamento["nombre"],
                    etiquetas_tipo.get(
                        medicamento["tipo"],
                        medicamento["tipo_label"]
                    ),
                    _resumen(medicamento["contraindicaciones_texto"]),
                    _resumen(medicamento["efectos_secundarios_texto"])
                ),
                iid=medicamento["id"]
            )

    # -----------------------------
    # SELECCIONAR MEDICAMENTO
    # -----------------------------

    def seleccionar_medicamento(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        medicamento_id = seleccion[0]
        medicamento = medicamentos_por_id.get(medicamento_id)

        if medicamento is None:
            return

        medicamento_seleccionado[0] = medicamento_id

        vista.limpiar_campos()

        vista.set_valor_campo("nombre", medicamento["nombre"])
        vista.set_valor_campo("tipo", medicamento["tipo_label"])
        vista.set_valor_campo(
            "contraindicaciones",
            medicamento["contraindicaciones_ids"]
        )
        vista.set_valor_campo(
            "efectos_secundarios",
            medicamento["efectos_secundarios_ids"]
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_medicamento
    )

    # -----------------------------
    # AGREGAR MEDICAMENTO
    # -----------------------------

    def on_agregar():

        try:

            crear_medicamento(
                vista.valor_campo("nombre"),
                vista.valor_campo("contraindicaciones"),
                vista.valor_campo("efectos_secundarios"),
                tipo_seleccionado()
            )

        except ValueError as error:

            messagebox.showwarning(
                t("common.invalid_data"),
                str(error)
            )

            return

        cargar_medicamentos()
        limpiar_formulario()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            t("common.correct"),
            t("medicamentos.messages.added")
        )

    # -----------------------------
    # MODIFICAR MEDICAMENTO
    # -----------------------------

    def on_modificar():

        medicamento_id = medicamento_seleccionado[0]

        if medicamento_id is None:

            messagebox.showwarning(
                t("common.error"),
                t("medicamentos.messages.select")
            )

            return

        try:

            actualizado = actualizar_medicamento(
                medicamento_id,
                vista.valor_campo("nombre"),
                vista.valor_campo("contraindicaciones"),
                vista.valor_campo("efectos_secundarios"),
                tipo_seleccionado()
            )

        except ValueError as error:

            messagebox.showwarning(
                t("common.invalid_data"),
                str(error)
            )

            return

        if actualizado is None:

            messagebox.showwarning(
                t("common.error"),
                t("medicamentos.messages.not_found")
            )

            return

        cargar_medicamentos()
        limpiar_formulario()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            t("common.correct"),
            t("medicamentos.messages.updated")
        )

    # -----------------------------
    # ELIMINAR MEDICAMENTO
    # -----------------------------

    def on_eliminar():

        medicamento_id = medicamento_seleccionado[0]

        if medicamento_id is None:

            messagebox.showwarning(
                t("common.error"),
                t("medicamentos.messages.select")
            )

            return

        try:

            eliminado = eliminar_medicamento(medicamento_id)

        except ValueError as error:

            messagebox.showwarning(
                t("medicamentos.messages.cannot_delete"),
                str(error)
            )

            return

        if not eliminado:

            messagebox.showwarning(
                t("common.error"),
                t("medicamentos.messages.not_found")
            )

            return

        cargar_medicamentos()
        limpiar_formulario()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            t("common.correct"),
            t("medicamentos.messages.deleted")
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar=t("medicamentos.buttons.add"),
        etiqueta_modificar=t("medicamentos.buttons.modify"),
        etiqueta_eliminar=t("medicamentos.buttons.delete"),
        ancho=240,
        alto=50,
        fuente=("Inter", 14, "bold"),
        padding=14
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def actualizar_combo_tipos():
        """Traduce las opciones del combo conservando el tipo elegido."""

        seleccionado = tipo_seleccionado()
        nuevas = _etiquetas_tipo()

        etiquetas_tipo.clear()
        etiquetas_tipo.update(nuevas)

        tipo_por_etiqueta.clear()
        tipo_por_etiqueta.update({
            etiqueta: clave
            for clave, etiqueta in etiquetas_tipo.items()
        })

        combo_tipo.configure(values=list(etiquetas_tipo.values()))
        combo_tipo.set(
            etiquetas_tipo.get(seleccionado, etiquetas_tipo["generico"])
        )

    def update_ui_strings(lang=None):

        actualizar_combo_tipos()

        vista.actualizar_textos(
            titulo=t("medicamentos.title"),
            encabezados={
                "Nombre": t("medicamentos.columns.name"),
                "Tipo": t("medicamentos.columns.type"),
                "Contraindicaciones": t(
                    "medicamentos.columns.contraindications"
                ),
                "Efectos Secundarios": t(
                    "medicamentos.columns.side_effects"
                ),
            },
            etiquetas={
                "nombre": t("medicamentos.fields.name.label"),
                "tipo": t("medicamentos.fields.type.label"),
                "contraindicaciones": t(
                    "medicamentos.fields.contraindications.label"
                ),
                "efectos_secundarios": t(
                    "medicamentos.fields.side_effects.label"
                ),
            },
            placeholders={
                "nombre": t("medicamentos.fields.name.placeholder"),
            }
        )

        vista.actualizar_botones(
            t("medicamentos.buttons.add"),
            t("medicamentos.buttons.modify"),
            t("medicamentos.buttons.delete")
        )

        for clave in ("contraindicaciones", "efectos_secundarios"):
            widget = vista.widgets.get(clave)
            if hasattr(widget, "actualizar_textos"):
                widget.actualizar_textos()

        seleccionado = medicamento_seleccionado[0]
        cargar_medicamentos()

        if seleccionado and seleccionado in tabla.get_children():
            tabla.selection_set(seleccionado)
            tabla.focus(seleccionado)

    language_manager.add_listener(update_ui_strings)

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    limpiar_formulario()
    cargar_medicamentos()

    return lambda: language_manager.remove_listener(update_ui_strings)
