from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.citas import actualizar_cita, crear_cita, eliminar_cita, listar_citas
from logica.medicos import listar_medicos
from logica.pacientes import listar_pacientes

# -----------------------------
# FUNCION PRINCIPAL
# -----------------------------

def mostrar_citas(panel):

    cita_seleccionada = [None]

    # -----------------------------
    # OPCIONES DE LOS COMBOS
    # -----------------------------

    pacientes = []

    for paciente in listar_pacientes():

        pacientes.append(paciente["nombre"])

    medicos = []

    for medico in listar_medicos():

        medicos.append(medico["nombre"])

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo="Gestión de Citas",
        columnas=["Paciente", "Médico", "Fecha", "Hora"],
        altura=7,
        campos=[
            {"clave": "paciente", "label": "Paciente", "tipo": "combo", "valores": pacientes},
            {"clave": "medico", "label": "Médico", "tipo": "combo", "valores": medicos},
            {"clave": "fecha", "label": "Fecha", "placeholder": "Ingrese fecha (AAAA-MM-DD)"},
            {"clave": "hora", "label": "Hora", "placeholder": "Ingrese hora (HH:MM AM/PM)"}
        ]
    )

    tabla = vista.tabla

    combo_paciente = vista.widgets["paciente"]
    combo_medico = vista.widgets["medico"]
    entrada_fecha = vista.widgets["fecha"]
    entrada_hora = vista.widgets["hora"]

    # -----------------------------
    # CARGAR CITAS
    # -----------------------------

    def cargar_citas():

        vista.limpiar_tabla()

        for cita in listar_citas():

            vista.insertar_fila(
                (
                    cita["paciente"],
                    cita["medico"],
                    cita["fecha"],
                    cita["hora"]
                ),
                iid=cita["id"]
            )

    # -----------------------------
    # SELECCIONAR CITA
    # -----------------------------

    def seleccionar_cita(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        cita_id = seleccion[0]

        datos = tabla.item(cita_id)["values"]

        cita_seleccionada[0] = cita_id

        vista.limpiar_campos()

        combo_paciente.set(datos[0])
        combo_medico.set(datos[1])

        entrada_fecha.insert(0, datos[2])
        entrada_hora.insert(0, datos[3])

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_cita
    )

    # -----------------------------
    # AGREGAR CITA
    # -----------------------------

    def on_agregar():

        try:

            crear_cita(
                combo_paciente.get(),
                combo_medico.get(),
                entrada_fecha.get(),
                entrada_hora.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        cargar_citas()

        vista.limpiar_campos()

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

        try:

            actualizado = actualizar_cita(
                cita_seleccionada[0],
                combo_paciente.get(),
                combo_medico.get(),
                entrada_fecha.get(),
                entrada_hora.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        if actualizado is None:

            messagebox.showwarning(
                "Error",
                "No se encontró la cita seleccionada"
            )

            return

        cargar_citas()

        vista.limpiar_campos()

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

        vista.limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            "Correcto",
            "Cita eliminada correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Cita",
        etiqueta_modificar="Modificar Cita",
        etiqueta_eliminar="Eliminar Cita"
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_citas()
