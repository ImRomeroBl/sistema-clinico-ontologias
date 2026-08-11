import customtkinter as ctk
from tkinter import *
from tkinter import messagebox

from owlready2 import destroy_entity

from logica.ontologia import onto

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

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

        for medicamento in onto.Medicamento.instances():

            nombre = medicamento.name

            dosis = ""

            if (
                hasattr(medicamento, "dosis")
                and medicamento.dosis
            ):

                dosis = medicamento.dosis[0]

            descripcion = ""

            if (
                hasattr(medicamento, "descripcion")
                and medicamento.descripcion
            ):

                descripcion = medicamento.descripcion[0]

            tabla.insert(
                "",
                END,
                values=(
                    nombre,
                    dosis,
                    descripcion
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

        nombre = datos[0]

        medicamento = onto.search_one(
            iri="*" + nombre
        )

        if medicamento:

            medicamento_seleccionado[0] = medicamento

            limpiar_campos()

            entrada_nombre.insert(
                0,
                medicamento.name
            )

            if (
                hasattr(medicamento, "dosis")
                and medicamento.dosis
            ):

                entrada_dosis.insert(
                    0,
                    medicamento.dosis[0]
                )

            if (
                hasattr(medicamento, "descripcion")
                and medicamento.descripcion
            ):

                entrada_descripcion.insert(
                    0,
                    medicamento.descripcion[0]
                )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_medicamento
    )

    # -----------------------------
    # AGREGAR MEDICAMENTO
    # -----------------------------

    def agregar_medicamento():

        nombre = entrada_nombre.get().strip()
        dosis = entrada_dosis.get().strip()
        descripcion = entrada_descripcion.get().strip()

        if nombre == "" or dosis == "":

            messagebox.showwarning(
                "Error",
                "Complete nombre y dosis"
            )

            return

        existe = onto.search_one(
            iri="*" + nombre.replace(" ", "_")
        )

        if existe:

            messagebox.showwarning(
                "Duplicado",
                "El medicamento ya existe"
            )

            return

        nuevo = onto.Medicamento(
            nombre.replace(" ", "_")
        )

        nuevo.nombre = [nombre]
        nuevo.dosis = [dosis]

        if descripcion != "":

            nuevo.descripcion = [descripcion]

        onto.save(file="clinica.owl")

        cargar_medicamentos()

        limpiar_campos()

        messagebox.showinfo(
            "Correcto",
            "Medicamento agregado correctamente"
        )

    # -----------------------------
    # MODIFICAR MEDICAMENTO
    # -----------------------------

    def modificar_medicamento():

        medicamento = medicamento_seleccionado[0]

        if medicamento is None:

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

        medicamento.nombre = [nombre]
        medicamento.dosis = [dosis]

        if descripcion != "":

            medicamento.descripcion = [descripcion]

        else:

            medicamento.descripcion = []

        onto.save(file="clinica.owl")

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

    def eliminar_medicamento():

        if medicamento_seleccionado[0] is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        destroy_entity(
            medicamento_seleccionado[0]
        )

        onto.save(file="clinica.owl")

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
        agregar_medicamento
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
        modificar_medicamento
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
        eliminar_medicamento
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_medicamentos()