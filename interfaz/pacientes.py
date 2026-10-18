import customtkinter as ctk
from tkinter import *
from tkinter import messagebox

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

from logica.pacientes import (
    listar_pacientes,
    crear_paciente,
    actualizar_paciente,
    eliminar_paciente
)

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_pacientes(panel):

    paciente_seleccionado = [None]

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
        "Gestión de Pacientes"
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

    formulario = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )

    formulario.pack(
        fill="x",
        padx=30,
        pady=(30, 10)
    )

    # -----------------------------
    # NOMBRE
    # -----------------------------

    label_nombre = crear_label(
        formulario,
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
        formulario,
        "Ingrese nombre"
    )

    entrada_nombre.grid(
        row=0,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # EDAD
    # -----------------------------

    label_edad = crear_label(
        formulario,
        "Edad"
    )

    label_edad.grid(
        row=1,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_edad = crear_input(
        formulario,
        "Ingrese edad"
    )

    entrada_edad.grid(
        row=1,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # TELEFONO
    # -----------------------------

    label_telefono = crear_label(
        formulario,
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
        formulario,
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
        "Buscar Paciente"
    )

    buscador_label.pack(
        anchor="w",
        pady=(0, 10)
    )

    buscador = crear_input(
        buscador_frame,
        "Buscar paciente..."
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
            "Edad",
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
    # SELECCIONAR PACIENTE
    # -----------------------------

    def seleccionar_paciente(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        item = tabla.item(seleccion)

        datos = item["values"]

        paciente_seleccionado[0] = datos[0]

        entrada_nombre.delete(0, END)
        entrada_edad.delete(0, END)
        entrada_telefono.delete(0, END)

        entrada_nombre.insert(
            0,
            datos[0]
        )

        entrada_edad.insert(
            0,
            str(datos[1])
        )

        entrada_telefono.insert(
            0,
            datos[2]
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_paciente
    )

    # -----------------------------
    # CARGAR PACIENTES
    # -----------------------------

    def cargar_pacientes(filtro=""):

        for item in tabla.get_children():
            tabla.delete(item)

        for paciente in listar_pacientes():

            nombre = paciente["nombre"]

            if filtro.lower() in nombre.lower():

                tabla.insert(
                    "",
                    END,
                    values=(
                        paciente["nombre"],
                        paciente["edad"],
                        paciente["telefono"]
                    )
                )

    # -----------------------------
    # FILTRAR
    # -----------------------------

    def filtrar_pacientes(event):

        texto = buscador.get()

        cargar_pacientes(texto)

    buscador.bind(
        "<KeyRelease>",
        filtrar_pacientes
    )

    # -----------------------------
    # LIMPIAR CAMPOS
    # -----------------------------

    def limpiar_campos():

        entrada_nombre.delete(0, END)
        entrada_edad.delete(0, END)
        entrada_telefono.delete(0, END)

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

        limpiar_campos()

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

        limpiar_campos()

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

        limpiar_campos()

        paciente_seleccionado[0] = None

        messagebox.showinfo(
            "Éxito",
            "Paciente eliminado correctamente"
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
        "Agregar Paciente",
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
        "Modificar Paciente",
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
        "Eliminar Paciente",
        on_eliminar
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_pacientes()
