from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.medicamentos import (
    actualizar_medicamento,
    crear_medicamento,
    eliminar_medicamento,
    listar_medicamentos,
)

# --------------------------------
# MOSTRAR MEDICAMENTOS
# --------------------------------

def mostrar_medicamentos(panel):

    medicamento_seleccionado = [None]

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo="Gestión de Medicamentos",
        columnas=["Nombre", "Dosis Base", "Descripción"],
        altura=7,
        campos=[
            {"clave": "nombre", "label": "Nombre", "placeholder": "Ingrese nombre del medicamento"},
            {"clave": "dosis", "label": "Dosis Base", "placeholder": "Ingrese dosis recomendada"},
            {"clave": "descripcion", "label": "Descripción", "placeholder": "Descripción del medicamento"}
        ]
    )

    tabla = vista.tabla

    entrada_nombre = vista.widgets["nombre"]
    entrada_dosis = vista.widgets["dosis"]
    entrada_descripcion = vista.widgets["descripcion"]

    # -----------------------------
    # CARGAR MEDICAMENTOS
    # -----------------------------

    def cargar_medicamentos():

        vista.limpiar_tabla()

        for medicamento in listar_medicamentos():

            vista.insertar_fila(
                (
                    medicamento["nombre"],
                    medicamento["dosis"],
                    medicamento["descripcion"]
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

        datos = tabla.item(medicamento_id)["values"]

        medicamento_seleccionado[0] = medicamento_id

        vista.limpiar_campos()

        entrada_nombre.insert(0, datos[0])
        entrada_dosis.insert(0, datos[1])
        entrada_descripcion.insert(0, datos[2])

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
                entrada_nombre.get(),
                entrada_dosis.get(),
                entrada_descripcion.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        cargar_medicamentos()

        vista.limpiar_campos()

        messagebox.showinfo(
            "Correcto",
            "Medicamento agregado correctamente"
        )

    # -----------------------------
    # MODIFICAR MEDICAMENTO
    # -----------------------------

    def on_modificar():

        medicamento_id = medicamento_seleccionado[0]

        if medicamento_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        try:

            actualizado = actualizar_medicamento(
                medicamento_id,
                entrada_nombre.get(),
                entrada_dosis.get(),
                entrada_descripcion.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        if actualizado is None:

            messagebox.showwarning(
                "Error",
                "No se encontró el medicamento seleccionado"
            )

            return

        cargar_medicamentos()

        vista.limpiar_campos()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            "Correcto",
            "Medicamento modificado correctamente"
        )

    # -----------------------------
    # ELIMINAR MEDICAMENTO
    # -----------------------------

    def on_eliminar():

        medicamento_id = medicamento_seleccionado[0]

        if medicamento_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        eliminar_medicamento(medicamento_id)

        cargar_medicamentos()

        vista.limpiar_campos()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            "Correcto",
            "Medicamento eliminado correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Medicamento",
        etiqueta_modificar="Modificar Medicamento",
        etiqueta_eliminar="Eliminar Medicamento"
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_medicamentos()
