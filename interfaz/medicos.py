from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
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
        titulo="Gestión de Médicos",
        columnas=["Nombre", "Especialidad", "Teléfono"],
        altura=6,
        buscador={
            "label": "Buscar Médico",
            "placeholder": "Buscar médico..."
        },
        campos=[
            {"clave": "nombre", "label": "Nombre", "placeholder": "Ingrese nombre"},
            {"clave": "especialidad", "label": "Especialidad", "placeholder": "Ingrese especialidad"},
            {"clave": "telefono", "label": "Teléfono", "placeholder": "Ingrese teléfono"}
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
                "Datos inválidos",
                str(error)
            )

            return

        cargar_medicos()

        vista.limpiar_campos()

        messagebox.showinfo(
            "Éxito",
            "Médico agregado correctamente"
        )

    # -----------------------------
    # MODIFICAR MEDICO
    # -----------------------------

    def on_modificar():

        medico_id = medico_seleccionado[0]

        if medico_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un médico"
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
                "Datos inválidos",
                str(error)
            )

            return

        if actualizado is None:

            messagebox.showwarning(
                "Error",
                "No se encontró el médico seleccionado"
            )

            return

        medico_seleccionado[0] = None

        cargar_medicos()

        vista.limpiar_campos()

        messagebox.showinfo(
            "Éxito",
            "Médico modificado correctamente"
        )

    # -----------------------------
    # ELIMINAR MEDICO
    # -----------------------------

    def on_eliminar():

        medico_id = medico_seleccionado[0]

        if medico_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un médico"
            )

            return

        eliminar_medico(medico_id)

        cargar_medicos()

        vista.limpiar_campos()

        medico_seleccionado[0] = None

        messagebox.showinfo(
            "Éxito",
            "Médico eliminado correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Médico",
        etiqueta_modificar="Modificar Médico",
        etiqueta_eliminar="Eliminar Médico"
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_medicos()
