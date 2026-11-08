from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.language_manager import language_manager, t
from logica.medicos import (
    actualizar_medico,
    crear_medico,
    eliminar_medico,
    listar_medicos,
)

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_medicos(panel):

    medico_seleccionado = [None]

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo=t("medicos.title"),
        columnas=["Nombre", "Especialidad", "Teléfono"],
        altura=6,
        buscador={
            "label": t("medicos.search.label"),
            "placeholder": t("medicos.search.placeholder")
        },
        campos=[
            {
                "clave": "nombre",
                "label": t("medicos.fields.name.label"),
                "placeholder": t("medicos.fields.name.placeholder"),
                "ancho": 420
            },
            {
                "clave": "especialidad",
                "label": t("medicos.fields.specialty.label"),
                "placeholder": t("medicos.fields.specialty.placeholder"),
                "ancho": 420
            },
            {
                "clave": "telefono",
                "label": t("medicos.fields.phone.label"),
                "placeholder": t("medicos.fields.phone.placeholder"),
                "tipo": "telefono",
                "ancho": 420
            }
        ]
    )

    tabla = vista.tabla

    entrada_nombre = vista.widgets["nombre"]
    entrada_especialidad = vista.widgets["especialidad"]
    entrada_telefono = vista.widgets["telefono"]

    # -----------------------------
    # CARGAR MEDICOS
    # -----------------------------

    def cargar_medicos(filtro=""):

        vista.limpiar_tabla()

        for medico in listar_medicos():

            nombre = medico["nombre"]

            if filtro.lower() in nombre.lower():

                vista.insertar_fila(
                    (
                        medico["nombre"],
                        medico["especialidad"],
                        medico["telefono"]
                    ),
                    iid=medico["id"]
                )

    # -----------------------------
    # FILTRAR MEDICOS
    # -----------------------------

    def buscar_medico(event):

        cargar_medicos(vista.buscador.get())

    vista.buscador.bind(
        "<KeyRelease>",
        buscar_medico
    )

    # -----------------------------
    # SELECCIONAR MEDICO
    # -----------------------------

    def seleccionar_medico(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        medico_id = seleccion[0]

        datos = tabla.item(medico_id)["values"]

        medico_seleccionado[0] = medico_id

        vista.limpiar_campos()

        entrada_nombre.insert(0, datos[0])
        entrada_especialidad.insert(0, datos[1])
        entrada_telefono.insert(0, datos[2])

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_medico
    )

    # -----------------------------
    # AGREGAR MEDICO
    # -----------------------------

    def on_agregar():

        try:

            crear_medico(
                entrada_nombre.get(),
                entrada_especialidad.get(),
                entrada_telefono.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                t("common.invalid_data"),
                str(error)
            )

            return

        cargar_medicos()

        vista.limpiar_campos()

        messagebox.showinfo(
            t("common.success"),
            t("medicos.messages.added")
        )

    # -----------------------------
    # MODIFICAR MEDICO
    # -----------------------------

    def on_modificar():

        medico_id = medico_seleccionado[0]

        if medico_id is None:

            messagebox.showwarning(
                t("common.error"),
                t("medicos.messages.select")
            )

            return

        try:

            actualizado = actualizar_medico(
                medico_id,
                entrada_nombre.get(),
                entrada_especialidad.get(),
                entrada_telefono.get()
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
                t("medicos.messages.not_found")
            )

            return

        medico_seleccionado[0] = None

        cargar_medicos()

        vista.limpiar_campos()

        messagebox.showinfo(
            t("common.success"),
            t("medicos.messages.updated")
        )

    # -----------------------------
    # ELIMINAR MEDICO
    # -----------------------------

    def on_eliminar():

        medico_id = medico_seleccionado[0]

        if medico_id is None:

            messagebox.showwarning(
                t("common.error"),
                t("medicos.messages.select")
            )

            return

        try:

            eliminado = eliminar_medico(medico_id)

        except ValueError as error:

            messagebox.showwarning(
                t("medicos.messages.cannot_delete"),
                str(error)
            )

            return

        if not eliminado:

            messagebox.showwarning(
                t("common.error"),
                t("medicos.messages.not_found")
            )

            return

        cargar_medicos()

        vista.limpiar_campos()

        medico_seleccionado[0] = None

        messagebox.showinfo(
            t("common.success"),
            t("medicos.messages.deleted")
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar=t("medicos.buttons.add"),
        etiqueta_modificar=t("medicos.buttons.modify"),
        etiqueta_eliminar=t("medicos.buttons.delete")
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def update_ui_strings(lang=None):

        vista.actualizar_textos(
            titulo=t("medicos.title"),
            encabezados={
                "Nombre": t("medicos.columns.name"),
                "Especialidad": t("medicos.columns.specialty"),
                "Teléfono": t("medicos.columns.phone"),
            },
            etiquetas={
                "nombre": t("medicos.fields.name.label"),
                "especialidad": t("medicos.fields.specialty.label"),
                "telefono": t("medicos.fields.phone.label"),
            },
            placeholders={
                "nombre": t("medicos.fields.name.placeholder"),
                "especialidad": t("medicos.fields.specialty.placeholder"),
                "telefono": t("medicos.fields.phone.placeholder"),
            },
            buscador={
                "label": t("medicos.search.label"),
                "placeholder": t("medicos.search.placeholder"),
            }
        )

        vista.actualizar_botones(
            t("medicos.buttons.add"),
            t("medicos.buttons.modify"),
            t("medicos.buttons.delete")
        )

        cargar_medicos(vista.buscador.get())

    language_manager.add_listener(update_ui_strings)

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_medicos()

    return lambda: language_manager.remove_listener(update_ui_strings)
