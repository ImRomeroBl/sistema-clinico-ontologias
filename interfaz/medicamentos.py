import customtkinter as ctk
from tkinter import *
from tkinter import messagebox

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

from logica.medicamentos import (
    listar_medicamentos,
    crear_medicamento,
    actualizar_medicamento,
    eliminar_medicamento
)

# --------------------------------
# MOSTRAR MEDICAMENTOS
# --------------------------------

def mostrar_medicamentos(panel):

    medicamento_seleccionado = [None]

    # -----------------------------
    # LIMPIAR PANEL
    # -----------------------------

    for widget in panel.winfo_children():
        widget.destroy()

    panel.configure(
        fg_color=BACKGROUND
    )

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
        "Gestión de Medicamentos"
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
        "Ingrese nombre del medicamento"
    )

    entrada_nombre.grid(
        row=0,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # DOSIS
    # -----------------------------

    label_dosis = crear_label(
        form,
        "Dosis Base"
    )

    label_dosis.grid(
        row=1,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_dosis = crear_input(
        form,
        "Ingrese dosis recomendada"
    )

    entrada_dosis.grid(
        row=1,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # DESCRIPCION
    # -----------------------------

    label_descripcion = crear_label(
        form,
        "Descripción"
    )

    label_descripcion.grid(
        row=2,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_descripcion = crear_input(
        form,
        "Descripción del medicamento"
    )

    entrada_descripcion.grid(
        row=2,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # TABLA
    # -----------------------------

    tabla_frame, tabla = crear_tabla(

        parent=card,

        columnas=[
            "Nombre",
            "Dosis Base",
            "Descripción"
        ],

        altura=7
    )

    tabla_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    # -----------------------------
    # LIMPIAR CAMPOS
    # -----------------------------

    def limpiar_campos():

        entrada_nombre.delete(0, END)
        entrada_dosis.delete(0, END)
        entrada_descripcion.delete(0, END)

    # -----------------------------
    # CARGAR MEDICAMENTOS
    # -----------------------------

    def cargar_medicamentos():

        for item in tabla.get_children():
            tabla.delete(item)

        for medicamento in listar_medicamentos():

            tabla.insert(
                "",
                END,
                values=(
                    medicamento["nombre"],
                    medicamento["dosis"],
                    medicamento["descripcion"]
                )
            )

    # -----------------------------
    # SELECCIONAR MEDICAMENTO
    # -----------------------------

    def seleccionar_medicamento(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        item = tabla.item(seleccion)

        datos = item["values"]

        medicamento_seleccionado[0] = datos[0]

        limpiar_campos()

        entrada_nombre.insert(
            0,
            datos[0]
        )

        entrada_dosis.insert(
            0,
            datos[1]
        )

        entrada_descripcion.insert(
            0,
            datos[2]
        )

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

        limpiar_campos()

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

        limpiar_campos()

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

        limpiar_campos()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            "Correcto",
            "Medicamento eliminado correctamente"
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
        "Agregar Medicamento",
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
        "Modificar Medicamento",
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
        "Eliminar Medicamento",
        on_eliminar
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_medicamentos()
