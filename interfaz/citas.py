import customtkinter as ctk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import *
from interfaz.components.table import crear_tabla

from logica.ontologia import onto
from owlready2 import *

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

    for paciente in onto.Paciente.instances():

        pacientes.append(
            paciente.nombre[0]
        )

    combo_paciente["values"] = pacientes

    # -----------------------------
    # CARGAR MEDICOS
    # -----------------------------

    medicos = []

    for medico in onto.Medico.instances():

        medicos.append(
            medico.nombre[0]
        )

    combo_medico["values"] = medicos

    # -----------------------------
    # CARGAR CITAS
    # -----------------------------

    def cargar_citas():

        for item in tabla.get_children():
            tabla.delete(item)

        for cita in onto.Cita.instances():

            if (
                not cita.tienePaciente
                or not cita.tieneMedico
            ):
                continue

            paciente = cita.tienePaciente[0].nombre[0]

            medico = cita.tieneMedico[0].nombre[0]

            fecha = ""

            hora = ""

            if cita.fecha:
                fecha = cita.fecha[0]

            if cita.hora:
                hora = cita.hora[0]

            tabla.insert(
                "",
                END,
                values=(
                    paciente,
                    medico,
                    fecha,
                    hora
                )
            )

    # -----------------------------
    # SELECCIONAR CITA
    # -----------------------------

    def seleccionar_cita(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        item = tabla.item(seleccion)

        datos = item["values"]

        paciente_nombre = datos[0]
        medico_nombre = datos[1]
        fecha = datos[2]
        hora = datos[3]

        for cita in onto.Cita.instances():

            if (
                not cita.tienePaciente
                or not cita.tieneMedico
            ):
                continue

            paciente = cita.tienePaciente[0].nombre[0]
            medico = cita.tieneMedico[0].nombre[0]

            fecha_cita = ""
            hora_cita = ""

            if cita.fecha:
                fecha_cita = cita.fecha[0]

            if cita.hora:
                hora_cita = cita.hora[0]

            if (
                paciente == paciente_nombre
                and medico == medico_nombre
                and fecha == fecha_cita
                and hora == hora_cita
            ):

                cita_seleccionada[0] = cita

                combo_paciente.set(paciente)
                combo_medico.set(medico)

                entrada_fecha.delete(0, END)
                entrada_hora.delete(0, END)

                entrada_fecha.insert(
                    0,
                    fecha
                )

                entrada_hora.insert(
                    0,
                    hora
                )

                break

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

    def agregar_cita():

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

        paciente = onto.search_one(
            nombre=paciente_nombre
        )

        medico = onto.search_one(
            nombre=medico_nombre
        )

        nueva_cita = onto.Cita(
            f"Cita_{len(onto.Cita.instances()) + 1}"
        )

        nueva_cita.fecha = [fecha]
        nueva_cita.hora = [hora]

        nueva_cita.tienePaciente = [paciente]
        nueva_cita.tieneMedico = [medico]

        onto.save(file="clinica.owl")

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

    def modificar_cita():

        if not cita_seleccionada[0]:

            messagebox.showwarning(
                "Error",
                "Seleccione una cita"
            )

            return

        paciente_nombre = combo_paciente.get()
        medico_nombre = combo_medico.get()

        fecha = entrada_fecha.get()
        hora = entrada_hora.get()

        paciente = onto.search_one(
            nombre=paciente_nombre
        )

        medico = onto.search_one(
            nombre=medico_nombre
        )

        cita_seleccionada[0].fecha = [fecha]
        cita_seleccionada[0].hora = [hora]

        cita_seleccionada[0].tienePaciente = [paciente]
        cita_seleccionada[0].tieneMedico = [medico]

        onto.save(file="clinica.owl")

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

    def eliminar_cita():

        if not cita_seleccionada[0]:

            messagebox.showwarning(
                "Error",
                "Seleccione una cita"
            )

            return

        destroy_entity(cita_seleccionada[0])

        onto.save(file="clinica.owl")

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
        agregar_cita
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
        modificar_cita
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
        eliminar_cita
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_citas()