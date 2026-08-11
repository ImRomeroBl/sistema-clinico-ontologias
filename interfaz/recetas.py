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

import uuid

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
    # CARGAR MEDICAMENTOS
    # -----------------------------

    medicamentos = []

    for medicamento in onto.Medicamento.instances():

        medicamentos.append(
            medicamento.name
        )

    combo_medicamento["values"] = medicamentos

    # -----------------------------
    # AUTOCOMPLETAR DOSIS
    # -----------------------------

    def actualizar_dosis(event):

        nombre = combo_medicamento.get()

        medicamento = onto.search_one(
            iri="*" + nombre
        )

        entrada_dosis.delete(0, END)

        if (
            medicamento
            and hasattr(medicamento, "dosis")
            and medicamento.dosis
        ):

            entrada_dosis.insert(
                0,
                medicamento.dosis[0]
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

        for receta in onto.Receta.instances():

            if (
                not receta.tienePaciente
                or not receta.tieneMedico
                or not receta.incluyeMedicamento
            ):
                continue

            paciente = receta.tienePaciente[0].nombre[0]

            medico = receta.tieneMedico[0].nombre[0]

            medicamento = receta.incluyeMedicamento[0].name

            dosis = ""

            if (
                hasattr(receta, "dosis")
                and receta.dosis
            ):

                dosis = receta.dosis[0]

            indicaciones = ""

            if (
                hasattr(receta, "indicaciones")
                and receta.indicaciones
            ):

                indicaciones = receta.indicaciones[0]

            tabla.insert(
                "",
                END,
                values=(
                    paciente,
                    medico,
                    medicamento,
                    dosis,
                    indicaciones
                )
            )

    # -----------------------------
    # SELECCIONAR RECETA
    # -----------------------------

    def seleccionar_receta(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        item = tabla.item(seleccion)

        datos = item["values"]

        paciente_nombre = datos[0]
        medico_nombre = datos[1]
        medicamento_nombre = datos[2]
        dosis = datos[3]
        indicaciones = datos[4]

        for receta in onto.Receta.instances():

            if (
                not receta.tienePaciente
                or not receta.tieneMedico
                or not receta.incluyeMedicamento
            ):
                continue

            paciente = receta.tienePaciente[0].nombre[0]

            medico = receta.tieneMedico[0].nombre[0]

            medicamento = receta.incluyeMedicamento[0].name

            if (
                paciente == paciente_nombre
                and medico == medico_nombre
                and medicamento == medicamento_nombre
            ):

                receta_seleccionada[0] = receta

                combo_paciente.set(
                    paciente
                )

                combo_medico.set(
                    medico
                )

                combo_medicamento.set(
                    medicamento
                )

                entrada_dosis.delete(0, END)
                entrada_indicaciones.delete(0, END)

                entrada_dosis.insert(
                    0,
                    dosis
                )

                entrada_indicaciones.insert(
                    0,
                    indicaciones
                )

                break

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

    def agregar_receta():

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

        paciente = onto.search_one(
            nombre=paciente_nombre
        )

        medico = onto.search_one(
            nombre=medico_nombre
        )

        medicamento = onto.search_one(
            iri="*" + medicamento_nombre
        )

        id_receta = f"RECETA_{uuid.uuid4().hex[:8]}"

        nueva_receta = onto.Receta(id_receta)

        nueva_receta.tienePaciente = [paciente]
        nueva_receta.tieneMedico = [medico]
        nueva_receta.incluyeMedicamento = [medicamento]

        nueva_receta.dosis = [dosis]
        nueva_receta.indicaciones = [indicaciones]

        onto.save(file="clinica.owl")

        cargar_recetas()

        limpiar_campos()

        messagebox.showinfo(
            "Correcto",
            "Receta agregada correctamente"
        )

    # -----------------------------
    # MODIFICAR RECETA
    # -----------------------------

    def modificar_receta():

        receta = receta_seleccionada[0]

        if receta is None:

            messagebox.showwarning(
                "Error",
                "Seleccione una receta"
            )

            return

        paciente_nombre = combo_paciente.get()
        medico_nombre = combo_medico.get()
        medicamento_nombre = combo_medicamento.get()

        dosis = entrada_dosis.get()
        indicaciones = entrada_indicaciones.get()

        paciente = onto.search_one(
            nombre=paciente_nombre
        )

        medico = onto.search_one(
            nombre=medico_nombre
        )

        medicamento = onto.search_one(
            iri="*" + medicamento_nombre
        )

        receta.tienePaciente = [paciente]
        receta.tieneMedico = [medico]
        receta.incluyeMedicamento = [medicamento]

        receta.dosis = [dosis]
        receta.indicaciones = [indicaciones]

        onto.save(file="clinica.owl")

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

    def eliminar_receta():

        if receta_seleccionada[0] is None:

            messagebox.showwarning(
                "Error",
                "Seleccione una receta"
            )

            return

        destroy_entity(
            receta_seleccionada[0]
        )

        onto.save(file="clinica.owl")

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
        agregar_receta
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
        modificar_receta
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
        eliminar_receta
    )

    boton_eliminar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_recetas()