import customtkinter as ctk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

from logica.recetas import (
    listar_recetas,
    crear_receta,
    actualizar_receta,
    eliminar_receta
)
from logica.pacientes import listar_pacientes
from logica.medicos import listar_medicos
from logica.medicamentos import (
    listar_medicamentos,
    obtener_dosis_base
)

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_recetas(panel):

    receta_seleccionada = [None]

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
        "Gestión de Recetas"
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
    # PACIENTE
    # -----------------------------

    label_paciente = crear_label(
        form,
        "Paciente"
    )

    label_paciente.grid(
        row=0,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    combo_paciente = ttk.Combobox(
        form,
        font=("Inter", 13),
        width=32
    )

    combo_paciente.grid(
        row=0,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # MEDICO
    # -----------------------------

    label_medico = crear_label(
        form,
        "Médico"
    )

    label_medico.grid(
        row=1,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    combo_medico = ttk.Combobox(
        form,
        font=("Inter", 13),
        width=32
    )

    combo_medico.grid(
        row=1,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # MEDICAMENTO
    # -----------------------------

    label_medicamento = crear_label(
        form,
        "Medicamento"
    )

    label_medicamento.grid(
        row=2,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    combo_medicamento = ttk.Combobox(
        form,
        font=("Inter", 13),
        width=32
    )

    combo_medicamento.grid(
        row=2,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # DOSIS
    # -----------------------------

    label_dosis = crear_label(
        form,
        "Dosis"
    )

    label_dosis.grid(
        row=3,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_dosis = crear_input(
        form,
        "Dosis personalizada"
    )

    entrada_dosis.grid(
        row=3,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # INDICACIONES
    # -----------------------------

    label_indicaciones = crear_label(
        form,
        "Indicaciones"
    )

    label_indicaciones.grid(
        row=4,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_indicaciones = crear_input(
        form,
        "Ingrese indicaciones"
    )

    entrada_indicaciones.grid(
        row=4,
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
            "Paciente",
            "Médico",
            "Medicamento",
            "Dosis",
            "Indicaciones"
        ],

        altura=6
    )

    tabla_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    # -----------------------------
    # CARGAR PACIENTES
    # -----------------------------

    pacientes = []

    for paciente in listar_pacientes():

        pacientes.append(
            paciente["nombre"]
        )

    combo_paciente["values"] = pacientes

    # -----------------------------
    # CARGAR MEDICOS
    # -----------------------------

    medicos = []

    for medico in listar_medicos():

        medicos.append(
            medico["nombre"]
        )

    combo_medico["values"] = medicos

    # -----------------------------
    # CARGAR MEDICAMENTOS
    # -----------------------------

    medicamentos = []

    for medicamento in listar_medicamentos():

        medicamentos.append(
            medicamento["nombre"]
        )

    combo_medicamento["values"] = medicamentos

    # -----------------------------
    # AUTOCOMPLETAR DOSIS
    # -----------------------------

    def actualizar_dosis(event):

        nombre = combo_medicamento.get()

        entrada_dosis.delete(0, END)

        dosis = obtener_dosis_base(nombre)

        if dosis:

            entrada_dosis.insert(
                0,
                dosis
            )

    combo_medicamento.bind(
        "<<ComboboxSelected>>",
        actualizar_dosis
    )

    # -----------------------------
    # CARGAR RECETAS
    # -----------------------------

    def cargar_recetas():

        for item in tabla.get_children():
            tabla.delete(item)

        receta_seleccionada[0] = None

        for receta in listar_recetas():

            tabla.insert(
                "",
                END,
                iid=receta["id"],
                values=(
                    receta["paciente"],
                    receta["medico"],
                    receta["medicamento"],
                    receta["dosis"],
                    receta["indicaciones"]
                )
            )

    # -----------------------------
    # SELECCIONAR RECETA
    # -----------------------------

    def seleccionar_receta(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        receta_id = seleccion[0]

        item = tabla.item(receta_id)

        datos = item["values"]

        receta_seleccionada[0] = receta_id

        combo_paciente.set(datos[0])
        combo_medico.set(datos[1])
        combo_medicamento.set(datos[2])

        entrada_dosis.delete(0, END)
        entrada_indicaciones.delete(0, END)

        entrada_dosis.insert(
            0,
            datos[3]
        )

        entrada_indicaciones.insert(
            0,
            datos[4]
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_receta
    )

    # -----------------------------
    # LIMPIAR CAMPOS
    # -----------------------------

    def limpiar_campos():

        combo_paciente.set("")
        combo_medico.set("")
        combo_medicamento.set("")

        entrada_dosis.delete(0, END)
        entrada_indicaciones.delete(0, END)

    # -----------------------------
    # AGREGAR RECETA
    # -----------------------------

    def on_agregar():

        paciente_nombre = combo_paciente.get()
        medico_nombre = combo_medico.get()
        medicamento_nombre = combo_medicamento.get()

        dosis = entrada_dosis.get()
        indicaciones = entrada_indicaciones.get()

        if (
            paciente_nombre == ""
            or medico_nombre == ""
            or medicamento_nombre == ""
            or dosis == ""
            or indicaciones == ""
        ):

            messagebox.showwarning(
                "Error",
                "Complete todos los campos"
            )

            return

        crear_receta(
            paciente_nombre,
            medico_nombre,
            medicamento_nombre,
            dosis,
            indicaciones
        )

        cargar_recetas()

        limpiar_campos()

        messagebox.showinfo(
            "Correcto",
            "Receta agregada correctamente"
        )

    # -----------------------------
    # MODIFICAR RECETA
    # -----------------------------

    def on_modificar():

        if receta_seleccionada[0] is None:

            messagebox.showwarning(
                "Error",
                "Seleccione una receta"
            )

            return

        actualizar_receta(
            receta_seleccionada[0],
            combo_paciente.get(),
            combo_medico.get(),
            combo_medicamento.get(),
            entrada_dosis.get(),
            entrada_indicaciones.get()
        )

        cargar_recetas()

        limpiar_campos()

        receta_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Receta modificada correctamente"
        )

    # -----------------------------
    # ELIMINAR RECETA
    # -----------------------------

    def on_eliminar():

        if receta_seleccionada[0] is None:

            messagebox.showwarning(
                "Error",
                "Seleccione una receta"
            )

            return

        eliminar_receta(
            receta_seleccionada[0]
        )

        cargar_recetas()

        limpiar_campos()

        receta_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Receta eliminada correctamente"
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
        "Agregar Receta",
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
        "Modificar Receta",
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
        "Eliminar Receta",
        on_eliminar
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_recetas()
