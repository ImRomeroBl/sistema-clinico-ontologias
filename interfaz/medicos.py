import customtkinter as ctk
from tkinter import *
from tkinter import messagebox

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

from logica.medicos import (
    listar_medicos,
    crear_medico,
    actualizar_medico,
    eliminar_medico
)

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_medicos(panel):

    medico_seleccionado = [None]

    # -----------------------------
    # LIMPIAR PANEL
    # -----------------------------

    for widget in panel.winfo_children():
        widget.destroy()

    panel.configure(fg_color=BACKGROUND)

    # -----------------------------
    # CONTENEDOR PRINCIPAL
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

    # -----------------------------
    # TITULO
    # -----------------------------

    titulo = crear_titulo(
        contenedor,
        "Gestión de Médicos"
    )

    titulo.pack(
        anchor="w",
        pady=(0, 25)
    )

    # -----------------------------
    # CARD PRINCIPAL
    # -----------------------------

    card = crear_card(contenedor)

    card.pack(
        fill="both",
        expand=True
    )

    # -----------------------------
    # FORMULARIO
    # -----------------------------

    form = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    form.pack(
        fill="x",
        padx=30,
        pady=(30, 10)
    )

    # -----------------------------
    # NOMBRE
    # -----------------------------

    label_nombre = crear_label(
        form,
        "Nombre"
    )

    label_nombre.grid(
        row=0,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_nombre = crear_input(
        form,
        "Ingrese nombre"
    )

    entrada_nombre.grid(
        row=0,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # ESPECIALIDAD
    # -----------------------------

    label_especialidad = crear_label(
        form,
        "Especialidad"
    )

    label_especialidad.grid(
        row=1,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_especialidad = crear_input(
        form,
        "Ingrese especialidad"
    )

    entrada_especialidad.grid(
        row=1,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # TELEFONO
    # -----------------------------

    label_telefono = crear_label(
        form,
        "Teléfono"
    )

    label_telefono.grid(
        row=2,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_telefono = crear_input(
        form,
        "Ingrese teléfono"
    )

    entrada_telefono.grid(
        row=2,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # BUSCADOR
    # -----------------------------

    buscador_frame = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    buscador_frame.pack(
        fill="x",
        padx=30,
        pady=(10, 10)
    )

    buscador_label = crear_label(
        buscador_frame,
        "Buscar Médico"
    )

    buscador_label.pack(
        anchor="w",
        pady=(0, 10)
    )

    buscador = crear_input(
        buscador_frame,
        "Buscar médico..."
    )

    buscador.pack(
        fill="x"
    )

    # -----------------------------
    # TABLA
    # -----------------------------

    tabla_frame, tabla = crear_tabla(

        parent=card,

        columnas=[
            "Nombre",
            "Especialidad",
            "Teléfono"
        ],

        altura=6
    )

    tabla_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    # -----------------------------
    # SELECCIONAR MEDICO
    # -----------------------------

    def seleccionar_medico(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        item = tabla.item(seleccion)

        datos = item["values"]

        medico_seleccionado[0] = datos[0]

        entrada_nombre.delete(0, END)
        entrada_especialidad.delete(0, END)
        entrada_telefono.delete(0, END)

        entrada_nombre.insert(
            0,
            datos[0]
        )

        entrada_especialidad.insert(
            0,
            datos[1]
        )

        entrada_telefono.insert(
            0,
            datos[2]
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_medico
    )

    # -----------------------------
    # CARGAR MEDICOS
    # -----------------------------

    def cargar_medicos(filtro=""):

        for item in tabla.get_children():
            tabla.delete(item)

        for medico in listar_medicos():

            nombre = medico["nombre"]

            if filtro.lower() in nombre.lower():

                tabla.insert(
                    "",
                    END,
                    values=(
                        medico["nombre"],
                        medico["especialidad"],
                        medico["telefono"]
                    )
                )

    # -----------------------------
    # FILTRAR MEDICOS
    # -----------------------------

    def buscar_medico(event):

        texto = buscador.get()

        cargar_medicos(texto)

    buscador.bind(
        "<KeyRelease>",
        buscar_medico
    )

    # -----------------------------
    # LIMPIAR CAMPOS
    # -----------------------------

    def limpiar_campos():

        entrada_nombre.delete(0, END)
        entrada_especialidad.delete(0, END)
        entrada_telefono.delete(0, END)

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

        limpiar_campos()

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

        limpiar_campos()

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

        limpiar_campos()

        medico_seleccionado[0] = None

        messagebox.showinfo(
            "Éxito",
            "Médico eliminado correctamente"
        )

    # -----------------------------
    # FRAME BOTONES
    # -----------------------------

    frame_botones = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    frame_botones.pack(
        pady=(0, 30)
    )

    # -----------------------------
    # BOTON AGREGAR
    # -----------------------------

    boton_agregar = crear_boton_exito(
        frame_botones,
        "Agregar Médico",
        on_agregar
    )

    boton_agregar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # BOTON MODIFICAR
    # -----------------------------

    boton_modificar = crear_boton_warning(
        frame_botones,
        "Modificar Médico",
        on_modificar
    )

    boton_modificar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # BOTON ELIMINAR
    # -----------------------------

    boton_eliminar = crear_boton_danger(
        frame_botones,
        "Eliminar Médico",
        on_eliminar
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_medicos()
