from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.language_manager import language_manager, t
from logica.pacientes import (
    actualizar_paciente,
    crear_paciente,
    eliminar_paciente,
    listar_pacientes,
)

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_pacientes(panel):

    paciente_seleccionado = [None]

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo=t("pacientes.title"),
        columnas=["Nombre", "Edad", "Teléfono"],
        altura=6,
        buscador={
            "label": t("pacientes.search.label"),
            "placeholder": t("pacientes.search.placeholder")
        },
        campos=[
            {
                "clave": "nombre",
                "label": t("pacientes.fields.name.label"),
                "placeholder": t("pacientes.fields.name.placeholder"),
                "ancho": 420
            },
            {
                "clave": "edad",
                "label": t("pacientes.fields.age.label"),
                "placeholder": t("pacientes.fields.age.placeholder"),
                "ancho": 420
            },
            {
                "clave": "telefono",
                "label": t("pacientes.fields.phone.label"),
                "placeholder": t("pacientes.fields.phone.placeholder"),
                "tipo": "telefono",
                "ancho": 420
            }
        ]
    )

    tabla = vista.tabla

    entrada_nombre = vista.widgets["nombre"]
    entrada_edad = vista.widgets["edad"]
    entrada_telefono = vista.widgets["telefono"]

    # -----------------------------
    # CARGAR PACIENTES
    # -----------------------------

    def cargar_pacientes(filtro=""):

        vista.limpiar_tabla()

        for paciente in listar_pacientes():

            nombre = paciente["nombre"]

            if filtro.lower() in nombre.lower():

                vista.insertar_fila(
                    (
                        paciente["nombre"],
                        paciente["edad"],
                        paciente["telefono"]
                    ),
                    iid=paciente["id"]
                )

    # -----------------------------
    # FILTRAR
    # -----------------------------

    def filtrar_pacientes(event):

        cargar_pacientes(vista.buscador.get())

    vista.buscador.bind(
        "<KeyRelease>",
        filtrar_pacientes
    )

    # -----------------------------
    # SELECCIONAR PACIENTE
    # -----------------------------

    def seleccionar_paciente(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        paciente_id = seleccion[0]

        datos = tabla.item(paciente_id)["values"]

        paciente_seleccionado[0] = paciente_id

        vista.limpiar_campos()

        entrada_nombre.insert(0, datos[0])
        entrada_edad.insert(0, str(datos[1]))
        entrada_telefono.insert(0, datos[2])

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_paciente
    )

    # -----------------------------
    # AGREGAR PACIENTE
    # -----------------------------

    def on_agregar():

        try:

            crear_paciente(
                entrada_nombre.get(),
                entrada_edad.get(),
                entrada_telefono.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                t("common.invalid_data"),
                str(error)
            )

            return

        cargar_pacientes()

        vista.limpiar_campos()

        messagebox.showinfo(
            t("common.success"),
            t("pacientes.messages.added")
        )

    # -----------------------------
    # MODIFICAR PACIENTE
    # -----------------------------

    def on_modificar():

        paciente_id = paciente_seleccionado[0]

        if paciente_id is None:

            messagebox.showwarning(
                t("common.error"),
                t("pacientes.messages.select")
            )

            return

        try:

            actualizado = actualizar_paciente(
                paciente_id,
                entrada_nombre.get(),
                entrada_edad.get(),
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
                t("pacientes.messages.not_found")
            )

            return

        paciente_seleccionado[0] = None

        cargar_pacientes()

        vista.limpiar_campos()

        messagebox.showinfo(
            t("common.success"),
            t("pacientes.messages.updated")
        )

    # -----------------------------
    # ELIMINAR PACIENTE
    # -----------------------------

    def on_eliminar():

        paciente_id = paciente_seleccionado[0]

        if paciente_id is None:

            messagebox.showwarning(
                t("common.error"),
                t("pacientes.messages.select")
            )

            return

        eliminar_paciente(paciente_id)

        cargar_pacientes()

        vista.limpiar_campos()

        paciente_seleccionado[0] = None

        messagebox.showinfo(
            t("common.success"),
            t("pacientes.messages.deleted")
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar=t("pacientes.buttons.add"),
        etiqueta_modificar=t("pacientes.buttons.modify"),
        etiqueta_eliminar=t("pacientes.buttons.delete")
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def update_ui_strings(lang=None):

        vista.actualizar_textos(
            titulo=t("pacientes.title"),
            encabezados={
                "Nombre": t("pacientes.columns.name"),
                "Edad": t("pacientes.columns.age"),
                "Teléfono": t("pacientes.columns.phone"),
            },
            etiquetas={
                "nombre": t("pacientes.fields.name.label"),
                "edad": t("pacientes.fields.age.label"),
                "telefono": t("pacientes.fields.phone.label"),
            },
            placeholders={
                "nombre": t("pacientes.fields.name.placeholder"),
                "edad": t("pacientes.fields.age.placeholder"),
                "telefono": t("pacientes.fields.phone.placeholder"),
            },
            buscador={
                "label": t("pacientes.search.label"),
                "placeholder": t("pacientes.search.placeholder"),
            }
        )

        vista.actualizar_botones(
            t("pacientes.buttons.add"),
            t("pacientes.buttons.modify"),
            t("pacientes.buttons.delete")
        )

        cargar_pacientes(vista.buscador.get())

    language_manager.add_listener(update_ui_strings)

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_pacientes()

    return lambda: language_manager.remove_listener(update_ui_strings)
