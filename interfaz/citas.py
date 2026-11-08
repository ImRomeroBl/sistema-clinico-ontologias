from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.citas import actualizar_cita, crear_cita, eliminar_cita, listar_citas
from logica.language_manager import language_manager, t
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
        titulo=t("citas.title"),
        columnas=["Paciente", "Médico", "Fecha", "Hora"],
        altura=7,
        campos=[
            {
                "clave": "paciente",
                "label": t("citas.fields.patient.label"),
                "tipo": "combo_buscable",
                "valores": pacientes
            },
            {
                "clave": "medico",
                "label": t("citas.fields.doctor.label"),
                "tipo": "combo_buscable",
                "valores": medicos
            },
            {
                "clave": "fecha",
                "label": t("citas.fields.date.label"),
                "placeholder": t("citas.fields.date.placeholder")
            },
            {
                "clave": "hora",
                "label": t("citas.fields.time.label"),
                "placeholder": t("citas.fields.time.placeholder")
            }
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
                t("common.invalid_data"),
                str(error)
            )

            return

        cargar_citas()

        vista.limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            t("common.correct"),
            t("citas.messages.added")
        )

    # -----------------------------
    # MODIFICAR CITA
    # -----------------------------

    def on_modificar():

        if not cita_seleccionada[0]:

            messagebox.showwarning(
                t("common.error"),
                t("citas.messages.select")
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
                t("common.invalid_data"),
                str(error)
            )

            return

        if actualizado is None:

            messagebox.showwarning(
                t("common.error"),
                t("citas.messages.not_found")
            )

            return

        cargar_citas()

        vista.limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            t("common.correct"),
            t("citas.messages.updated")
        )

    # -----------------------------
    # ELIMINAR CITA
    # -----------------------------

    def on_eliminar():

        if not cita_seleccionada[0]:

            messagebox.showwarning(
                t("common.error"),
                t("citas.messages.select")
            )

            return

        eliminar_cita(cita_seleccionada[0])

        cargar_citas()

        vista.limpiar_campos()

        cita_seleccionada[0] = None

        messagebox.showinfo(
            t("common.correct"),
            t("citas.messages.deleted")
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar=t("citas.buttons.add"),
        etiqueta_modificar=t("citas.buttons.modify"),
        etiqueta_eliminar=t("citas.buttons.delete")
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def update_ui_strings(lang=None):

        vista.actualizar_textos(
            titulo=t("citas.title"),
            encabezados={
                "Paciente": t("citas.columns.patient"),
                "Médico": t("citas.columns.doctor"),
                "Fecha": t("citas.columns.date"),
                "Hora": t("citas.columns.time"),
            },
            etiquetas={
                "paciente": t("citas.fields.patient.label"),
                "medico": t("citas.fields.doctor.label"),
                "fecha": t("citas.fields.date.label"),
                "hora": t("citas.fields.time.label"),
            },
            placeholders={
                "fecha": t("citas.fields.date.placeholder"),
                "hora": t("citas.fields.time.placeholder"),
            }
        )

        vista.actualizar_botones(
            t("citas.buttons.add"),
            t("citas.buttons.modify"),
            t("citas.buttons.delete")
        )

    language_manager.add_listener(update_ui_strings)

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    cargar_citas()

    return lambda: language_manager.remove_listener(update_ui_strings)
