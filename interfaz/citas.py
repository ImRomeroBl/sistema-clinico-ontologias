import customtkinter as ctk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

from logica.citas import (
    listar_citas,
    crear_cita,
    actualizar_cita,
    eliminar_cita
)
from logica.pacientes import listar_pacientes
from logica.medicos import listar_medicos

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_citas(panel):

    cita_seleccionada = [None]

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
        "Gestión de Citas"
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
    # FECHA
    # -----------------------------

    label_fecha = crear_label(
        form,
        "Fecha"
    )

    label_fecha.grid(
        row=2,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_fecha = crear_input(
        form,
        "Ingrese fecha"
    )

    entrada_fecha.grid(
        row=2,
        column=1,
        padx=15,
        pady=15
    )

    # -----------------------------
    # HORA
    # -----------------------------

    label_hora = crear_label(
        form,
        "Hora"
    )

    label_hora.grid(
        row=3,
        column=0,
        padx=15,
        pady=15,
        sticky="w"
    )

    entrada_hora = crear_input(
        form,
        "Ingrese hora"
    )

    entrada_hora.grid(
        row=3,
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
            "Fecha",
            "Hora"
        ],

        altura=7
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
    # CARGAR CITAS
    # -----------------------------

    def cargar_citas():

        for item in tabla.get_children():
            tabla.delete(item)

        for cita in listar_citas():

            tabla.insert(
                "",
                END,
                iid=cita["id"],
                values=(
                    cita["paciente"],
                    cita["medico"],
                    cita["fecha"],
                    cita["hora"]
                )
            )

    # -----------------------------
    # SELECCIONAR CITA
    # -----------------------------

    def seleccionar_cita(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        cita_id = seleccion[0]

        item = tabla.item(cita_id)

        datos = item["values"]

        cita_seleccionada[0] = cita_id

        combo_paciente.set(datos[0])
        combo_medico.set(datos[1])

        entrada_fecha.delete(0, END)
        entrada_hora.delete(0, END)

        entrada_fecha.insert(
            0,
            datos[2]
        )

        entrada_hora.insert(
            0,
            datos[3]
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_cita
    )

    # -----------------------------
    # LIMPIAR CAMPOS
    # -----------------------------

    def limpiar_campos():

        combo_paciente.set("")
        combo_medico.set("")

        entrada_fecha.delete(0, END)
        entrada_hora.delete(0, END)

    # -----------------------------
    # AGREGAR CITA
    # -----------------------------

    def on_agregar():

        paciente_nombre = combo_paciente.get()
        medico_nombre = combo_medico.get()

        fecha = entrada_fecha.get()
        hora = entrada_hora.get()

        if (
            paciente_nombre == ""
            or medico_nombre == ""
            or fecha == ""
            or hora == ""
        ):

            messagebox.showwarning(
                "Error",
                "Complete todos los campos"
            )

            return

        crear_cita(
            paciente_nombre,
            medico_nombre,
            fecha,
            hora
        )

        cargar_citas()

        limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Cita agregada correctamente"
        )

    # -----------------------------
    # MODIFICAR CITA
    # -----------------------------

    def on_modificar():

        if not cita_seleccionada[0]:

            messagebox.showwarning(
                "Error",
                "Seleccione una cita"
            )

            return

        actualizar_cita(
            cita_seleccionada[0],
            combo_paciente.get(),
            combo_medico.get(),
            entrada_fecha.get(),
            entrada_hora.get()
        )

        cargar_citas()

        limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Cita modificada correctamente"
        )

    # -----------------------------
    # ELIMINAR CITA
    # -----------------------------

    def on_eliminar():

        if not cita_seleccionada[0]:

            messagebox.showwarning(
                "Error",
                "Seleccione una cita"
            )

            return

        eliminar_cita(cita_seleccionada[0])

        cargar_citas()

        limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Cita eliminada correctamente"
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
        "Agregar Cita",
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
        "Modificar Cita",
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
        "Eliminar Cita",
        on_eliminar
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_citas()
