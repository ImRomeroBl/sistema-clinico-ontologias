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

            vista.insertar_fila((
                medicamento["nombre"],
                medicamento["dosis"],
                medicamento["descripcion"]
            ))

    # -----------------------------
    # SELECCIONAR MEDICAMENTO
    # -----------------------------

    def seleccionar_medicamento(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        datos = tabla.item(seleccion[0])["values"]

        medicamento_seleccionado[0] = datos[0]

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

        nombre = entrada_nombre.get().strip()
        dosis = entrada_dosis.get().strip()
        descripcion = entrada_descripcion.get().strip()

        if nombre == "" or dosis == "":

            messagebox.showwarning(
                "Error",
                "Complete nombre y dosis"
            )

            return

        nuevo = crear_medicamento(
            nombre,
            dosis,
            descripcion
        )

        if nuevo is None:

            messagebox.showwarning(
                "Duplicado",
                "El medicamento ya existe"
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

        nombre_actual = medicamento_seleccionado[0]

        if nombre_actual is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        nombre = entrada_nombre.get().strip()
        dosis = entrada_dosis.get().strip()
        descripcion = entrada_descripcion.get().strip()

        if nombre == "" or dosis == "":

            messagebox.showwarning(
                "Error",
                "Complete nombre y dosis"
            )

            return

        actualizar_medicamento(
            nombre_actual,
            nombre,
            dosis,
            descripcion
        )

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

        if medicamento_seleccionado[0] is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        eliminar_medicamento(
            medicamento_seleccionado[0]
        )

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
