from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD

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
    # OPCIONES DE LOS COMBOS
    # -----------------------------

    pacientes = []

    for paciente in listar_pacientes():

        pacientes.append(paciente["nombre"])

    medicos = []

    for medico in listar_medicos():

        medicos.append(medico["nombre"])

    medicamentos = []

    for medicamento in listar_medicamentos():

        medicamentos.append(medicamento["nombre"])

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo="Gestión de Recetas",
        columnas=[
            "Paciente",
            "Médico",
            "Medicamento",
            "Dosis",
            "Indicaciones"
        ],
        altura=6,
        campos=[
            {"clave": "paciente", "label": "Paciente", "tipo": "combo", "valores": pacientes},
            {"clave": "medico", "label": "Médico", "tipo": "combo", "valores": medicos},
            {"clave": "medicamento", "label": "Medicamento", "tipo": "combo", "valores": medicamentos},
            {"clave": "dosis", "label": "Dosis", "placeholder": "Dosis personalizada"},
            {"clave": "indicaciones", "label": "Indicaciones", "placeholder": "Ingrese indicaciones"}
        ]
    )

    tabla = vista.tabla

    combo_paciente = vista.widgets["paciente"]
    combo_medico = vista.widgets["medico"]
    combo_medicamento = vista.widgets["medicamento"]
    entrada_dosis = vista.widgets["dosis"]
    entrada_indicaciones = vista.widgets["indicaciones"]

    # -----------------------------
    # AUTOCOMPLETAR DOSIS
    # -----------------------------

    def actualizar_dosis(event):

        vista.limpiar_campo("dosis")

        dosis = obtener_dosis_base(combo_medicamento.get())

        if dosis:

            entrada_dosis.insert(0, dosis)

    combo_medicamento.bind(
        "<<ComboboxSelected>>",
        actualizar_dosis
    )

    # -----------------------------
    # CARGAR RECETAS
    # -----------------------------

    def cargar_recetas():

        vista.limpiar_tabla()

        receta_seleccionada[0] = None

        for receta in listar_recetas():

            vista.insertar_fila(
                (
                    receta["paciente"],
                    receta["medico"],
                    receta["medicamento"],
                    receta["dosis"],
                    receta["indicaciones"]
                ),
                iid=receta["id"]
            )

    # -----------------------------
    # SELECCIONAR RECETA
    # -----------------------------

    def seleccionar_receta(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        receta_id = seleccion[0]

        datos = tabla.item(receta_id)["values"]

        receta_seleccionada[0] = receta_id

        vista.limpiar_campos()

        combo_paciente.set(datos[0])
        combo_medico.set(datos[1])
        combo_medicamento.set(datos[2])

        entrada_dosis.insert(0, datos[3])
        entrada_indicaciones.insert(0, datos[4])

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_receta
    )

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

        vista.limpiar_campos()

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

        vista.limpiar_campos()

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

        vista.limpiar_campos()

        receta_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Receta eliminada correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Receta",
        etiqueta_modificar="Modificar Receta",
        etiqueta_eliminar="Eliminar Receta"
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_recetas()
