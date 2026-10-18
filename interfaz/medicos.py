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

                vista.insertar_fila((
                    medico["nombre"],
                    medico["especialidad"],
                    medico["telefono"]
                ))

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

        datos = tabla.item(seleccion[0])["values"]

        medico_seleccionado[0] = datos[0]

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

        nombre = entrada_nombre.get()
        especialidad = entrada_especialidad.get()
        telefono = entrada_telefono.get()

        if (
            nombre == ""
            or especialidad == ""
            or telefono == ""
        ):

            messagebox.showwarning(
                "Error",
                "Complete todos los campos"
            )

            return

        crear_medico(
            nombre,
            especialidad,
            telefono
        )

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

        nombre_antiguo = medico_seleccionado[0]

        if nombre_antiguo is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un médico"
            )

            return

        nuevo_nombre = entrada_nombre.get()

        actualizado = actualizar_medico(
            nombre_antiguo,
            nuevo_nombre,
            entrada_especialidad.get(),
            entrada_telefono.get()
        )

        if actualizado is None:

            messagebox.showwarning(
                "Error",
                "No se encontró el médico seleccionado"
            )

            return

        medico_seleccionado[0] = nuevo_nombre

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

        nombre = medico_seleccionado[0]

        if nombre is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un médico"
            )

            return

        eliminar_medico(nombre)

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
