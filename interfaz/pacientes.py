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

                vista.insertar_fila((
                    paciente["nombre"],
                    paciente["edad"],
                    paciente["telefono"]
                ))

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

        datos = tabla.item(seleccion[0])["values"]

        paciente_seleccionado[0] = datos[0]

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

        nombre = entrada_nombre.get()
        edad = entrada_edad.get()
        telefono = entrada_telefono.get()

        if (
            nombre == ""
            or edad == ""
            or telefono == ""
        ):

            messagebox.showwarning(
                "Error",
                "Complete todos los campos"
            )

            return

        crear_paciente(
            nombre,
            edad,
            telefono
        )

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

        nombre_antiguo = paciente_seleccionado[0]

        if nombre_antiguo is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un paciente"
            )

            return

        nuevo_nombre = entrada_nombre.get()

        actualizado = actualizar_paciente(
            nombre_antiguo,
            nuevo_nombre,
            entrada_edad.get(),
            entrada_telefono.get()
        )

        if actualizado is None:

            messagebox.showwarning(
                "Error",
                "No se encontró el paciente seleccionado"
            )

            return

        paciente_seleccionado[0] = nuevo_nombre

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

        nombre = paciente_seleccionado[0]

        if nombre is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un paciente"
            )

            return

        eliminar_paciente(nombre)

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
