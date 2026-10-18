from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
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
        titulo="Gestión de Pacientes",
        columnas=["Nombre", "Edad", "Teléfono"],
        altura=6,
        buscador={
            "label": "Buscar Paciente",
            "placeholder": "Buscar paciente..."
        },
        campos=[
            {"clave": "nombre", "label": "Nombre", "placeholder": "Ingrese nombre"},
            {"clave": "edad", "label": "Edad", "placeholder": "Ingrese edad"},
            {"clave": "telefono", "label": "Teléfono", "placeholder": "Ingrese teléfono"}
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
                "Datos inválidos",
                str(error)
            )

            return

        cargar_pacientes()

        vista.limpiar_campos()

        messagebox.showinfo(
            "Éxito",
            "Paciente agregado correctamente"
        )

    # -----------------------------
    # MODIFICAR PACIENTE
    # -----------------------------

    def on_modificar():

        paciente_id = paciente_seleccionado[0]

        if paciente_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un paciente"
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
                "Datos inválidos",
                str(error)
            )

            return

        if actualizado is None:

            messagebox.showwarning(
                "Error",
                "No se encontró el paciente seleccionado"
            )

            return

        paciente_seleccionado[0] = None

        cargar_pacientes()

        vista.limpiar_campos()

        messagebox.showinfo(
            "Éxito",
            "Paciente modificado correctamente"
        )

    # -----------------------------
    # ELIMINAR PACIENTE
    # -----------------------------

    def on_eliminar():

        paciente_id = paciente_seleccionado[0]

        if paciente_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un paciente"
            )

            return

        eliminar_paciente(paciente_id)

        cargar_pacientes()

        vista.limpiar_campos()

        paciente_seleccionado[0] = None

        messagebox.showinfo(
            "Éxito",
            "Paciente eliminado correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Paciente",
        etiqueta_modificar="Modificar Paciente",
        etiqueta_eliminar="Eliminar Paciente"
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_pacientes()
