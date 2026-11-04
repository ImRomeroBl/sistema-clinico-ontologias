from tkinter import LEFT, messagebox

from interfaz.components.crud_view import VistaCRUD
from interfaz.components.ui import crear_boton_primario, crear_label
from interfaz.theme.colors import TEXT_SECONDARY
from interfaz.theme.fonts import BUTTON_FONT
from logica.consultas import listar_consultas
from logica.estudios import (
    actualizar_estudio,
    asociar_estudio,
    crear_estudio,
    desasociar_estudio,
    eliminar_estudio,
    listar_solicitudes_estudios,
)
from logica.pacientes import listar_pacientes

# -----------------------------
# HELPERS
# -----------------------------

# Ancho y alto comunes de los cinco botones del módulo.
ANCHO_BOTON = 190
ALTO_BOTON = 50
PADDING_BOTON = 10

def _texto_consulta(consulta):
    """Resume una consulta para el combo de asociación."""
    fecha = consulta["fecha"] or "Sin fecha"
    paciente = consulta["paciente"] or "Sin paciente"
    medico = consulta["medico"] or "Sin médico"

    return f"{fecha} · {paciente} · {medico}"

def _opciones_consultas(consultas):
    """Devuelve opciones únicas y sus mapas opción <-> id de consulta."""
    opciones = []
    consulta_por_opcion = {}
    opcion_por_consulta = {}
    vistos = {}

    for consulta in consultas:

        base = _texto_consulta(consulta)

        vistos[base] = vistos.get(base, 0) + 1

        if vistos[base] == 1:
            opcion = base
        else:
            opcion = f"{base} [{consulta['id'][:8]}]"

        opciones.append(opcion)
        consulta_por_opcion[opcion] = consulta["id"]
        opcion_por_consulta[consulta["id"]] = opcion

    return opciones, consulta_por_opcion, opcion_por_consulta

# -----------------------------
# MOSTRAR ESTUDIOS
# -----------------------------

def mostrar_estudios(panel):

    estudio_seleccionado = [None]
    solicitudes_por_fila = {}

    # -----------------------------
    # PACIENTES (FILTRO)
    # -----------------------------

    opciones_pacientes = []
    paciente_por_opcion = {}
    opcion_por_paciente_id = {}
    vistos_pacientes = {}

    for paciente in listar_pacientes():

        base = paciente["nombre"] or paciente["id"]

        vistos_pacientes[base] = vistos_pacientes.get(base, 0) + 1

        if vistos_pacientes[base] == 1:
            opcion = base
        else:
            opcion = f"{base} [{paciente['id'][:8]}]"

        opciones_pacientes.append(opcion)
        paciente_por_opcion[opcion] = paciente["id"]
        opcion_por_paciente_id[paciente["id"]] = opcion

    # -----------------------------
    # CONSULTAS (ASOCIACIÓN)
    # -----------------------------

    opciones_consultas, consultas_por_opcion, opcion_por_consulta = (
        _opciones_consultas(listar_consultas())
    )

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo="Gestión de Estudios Médicos",
        columnas=[
            "Nombre del Estudio",
            "Paciente",
            "Consulta / Fecha",
            "Estado"
        ],
        altura=6,
        campos=[
            {
                "clave": "nombre",
                "label": "Nombre del estudio",
                "placeholder": "Ej. Radiografía de tórax",
                "sticky": "w"
            },
            {
                "clave": "paciente",
                "label": "Paciente (escriba para filtrar)",
                "tipo": "combo_buscable",
                "valores": opciones_pacientes,
                "sticky": "w"
            },
            {
                "clave": "consulta",
                "label": "Consulta (asociar)",
                "tipo": "combo",
                "valores": opciones_consultas,
                "sticky": "w"
            }
        ]
    )

    tabla = vista.tabla

    tabla.column(
        "Nombre del Estudio",
        width=280,
        minwidth=200,
        anchor="w",
        stretch=True
    )
    tabla.column(
        "Paciente",
        width=320,
        minwidth=230,
        anchor="w",
        stretch=True
    )
    tabla.column(
        "Consulta / Fecha",
        width=280,
        minwidth=180,
        anchor="w",
        stretch=True
    )
    tabla.column(
        "Estado",
        width=140,
        minwidth=110,
        anchor="center",
        stretch=False
    )

    vista.widgets["nombre"].configure(width=420)

    combo_paciente = vista.widgets["paciente"]
    combo_consulta = vista.widgets["consulta"]

    combo_paciente.configure(width=38)
    combo_consulta.configure(width=70, state="readonly")

    ayuda = crear_label(
        vista.form,
        "Cada fila representa una solicitud. Escriba para filtrar pacientes; "
        "la asociación se realiza a través de la consulta seleccionada."
    )

    ayuda.configure(text_color=TEXT_SECONDARY)

    ayuda.grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="w",
        padx=15,
        pady=(0, 10)
    )

    # -----------------------------
    # REFRESCAR CONSULTAS
    # -----------------------------

    def refrescar_consultas(event=None):

        consultas_por_opcion.clear()
        opcion_por_consulta.clear()

        paciente_id = paciente_por_opcion.get(combo_paciente.get(), "")

        consultas = [
            consulta
            for consulta in listar_consultas()
            if not paciente_id or consulta["paciente_id"] == paciente_id
        ]

        opciones, por_opcion, por_id = _opciones_consultas(consultas)

        combo_consulta.configure(values=opciones)
        combo_consulta.set("")

        consultas_por_opcion.update(por_opcion)
        opcion_por_consulta.update(por_id)

    combo_paciente.bind(
        "<<ComboboxSelected>>",
        refrescar_consultas
    )

    # -----------------------------
    # CARGAR ESTUDIOS
    # -----------------------------

    def cargar_estudios():
        """Inserta una fila independiente por cada solicitud de estudio."""

        solicitudes_por_fila.clear()
        vista.limpiar_tabla()

        for solicitud in listar_solicitudes_estudios():

            solicitudes_por_fila[solicitud["id"]] = solicitud

            consulta = (
                solicitud["fecha"]
                if solicitud["consulta_id"]
                else "Sin consulta"
            )

            vista.insertar_fila(
                (
                    solicitud["nombre"],
                    solicitud["paciente"],
                    consulta,
                    solicitud["estado"]
                ),
                iid=solicitud["id"]
            )

    # -----------------------------
    # SELECCIONAR ESTUDIO
    # -----------------------------

    def seleccionar_estudio(event=None):
        """Fija estudio, paciente y consulta desde la fila seleccionada."""

        seleccion = tabla.selection()

        if not seleccion:
            return

        solicitud = solicitudes_por_fila.get(seleccion[0])

        if solicitud is None:
            return

        estudio_seleccionado[0] = solicitud["estudio_id"]

        vista.set_valor_campo("nombre", solicitud["nombre"])

        combo_paciente.set(
            opcion_por_paciente_id.get(solicitud["paciente_id"], "")
        )

        refrescar_consultas()

        if solicitud["consulta_id"]:

            combo_consulta.set(
                opcion_por_consulta.get(solicitud["consulta_id"], "")
            )

        else:

            combo_consulta.set("")

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_estudio
    )

    def seleccionar_fila(fila_id=None, estudio_id=None):
        """Selecciona una fila concreta o la primera del estudio indicado."""

        objetivo = None

        if fila_id and fila_id in tabla.get_children():
            objetivo = fila_id

        elif estudio_id:

            for fila in tabla.get_children():

                solicitud = solicitudes_por_fila.get(fila)

                if (
                    solicitud is not None
                    and solicitud["estudio_id"] == estudio_id
                ):
                    objetivo = fila
                    break

        if objetivo is None:
            return

        tabla.selection_set(objetivo)
        tabla.focus(objetivo)
        tabla.see(objetivo)
        seleccionar_estudio()

    # -----------------------------
    # LIMPIAR FORMULARIO
    # -----------------------------

    def limpiar_formulario():

        vista.limpiar_campos()

        combo_paciente.set("")

        refrescar_consultas()

        if tabla.selection():

            tabla.selection_remove(*tabla.selection())

        estudio_seleccionado[0] = None

    # -----------------------------
    # AGREGAR ESTUDIO
    # -----------------------------

    def on_agregar():

        try:

            crear_estudio(
                vista.valor_campo("nombre")
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        cargar_estudios()
        limpiar_formulario()

        messagebox.showinfo(
            "Correcto",
            "Estudio agregado correctamente"
        )

    # -----------------------------
    # MODIFICAR ESTUDIO
    # -----------------------------

    def on_modificar():

        estudio_id = estudio_seleccionado[0]

        if estudio_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un estudio"
            )

            return

        seleccion = tabla.selection()
        fila_id = seleccion[0] if seleccion else None

        try:

            actualizado = actualizar_estudio(
                estudio_id,
                vista.valor_campo("nombre")
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
                "No se encontró el estudio seleccionado"
            )

            return

        cargar_estudios()
        seleccionar_fila(fila_id, estudio_id)

        messagebox.showinfo(
            "Correcto",
            "Estudio modificado correctamente"
        )

    # -----------------------------
    # ELIMINAR ESTUDIO
    # -----------------------------

    def on_eliminar():

        estudio_id = estudio_seleccionado[0]

        if estudio_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un estudio"
            )

            return

        eliminado = eliminar_estudio(estudio_id)

        if not eliminado:

            messagebox.showwarning(
                "Error",
                "No se encontró el estudio seleccionado"
            )

            return

        cargar_estudios()
        limpiar_formulario()

        messagebox.showinfo(
            "Correcto",
            "Estudio eliminado correctamente"
        )

    # -----------------------------
    # ASOCIAR ESTUDIO
    # -----------------------------

    def on_asociar():

        estudio_id = estudio_seleccionado[0]

        if estudio_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un estudio"
            )

            return

        consulta_id = consultas_por_opcion.get(combo_consulta.get())

        if not consulta_id:

            messagebox.showwarning(
                "Error",
                "Seleccione una consulta para asociar"
            )

            return

        try:

            asociar_estudio(estudio_id, consulta_id)

        except ValueError as error:

            messagebox.showwarning(
                "No se puede asociar",
                str(error)
            )

            return

        cargar_estudios()
        seleccionar_fila(
            f"{estudio_id}::{consulta_id}",
            estudio_id
        )

        messagebox.showinfo(
            "Correcto",
            "Estudio asociado a la consulta correctamente"
        )

    # -----------------------------
    # DESASOCIAR ESTUDIO
    # -----------------------------

    def on_desasociar():

        estudio_id = estudio_seleccionado[0]

        if estudio_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un estudio"
            )

            return

        consulta_id = consultas_por_opcion.get(combo_consulta.get())

        if not consulta_id:

            messagebox.showwarning(
                "Error",
                "Seleccione la consulta de la que desea desasociar"
            )

            return

        try:

            desasociado = desasociar_estudio(estudio_id, consulta_id)

        except ValueError as error:

            messagebox.showwarning(
                "No se puede desasociar",
                str(error)
            )

            return

        if not desasociado:

            messagebox.showwarning(
                "Sin cambios",
                "El estudio no está asociado a esa consulta."
            )

            return

        cargar_estudios()
        seleccionar_fila(None, estudio_id)

        messagebox.showinfo(
            "Correcto",
            "Estudio desasociado correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Estudio",
        etiqueta_modificar="Modificar Estudio",
        etiqueta_eliminar="Eliminar Estudio",
        ancho=ANCHO_BOTON,
        alto=ALTO_BOTON,
        fuente=BUTTON_FONT,
        padding=PADDING_BOTON
    )

    for texto, comando in (
        ("Asociar", on_asociar),
        ("Desasociar", on_desasociar)
    ):

        boton = crear_boton_primario(
            vista.frame_botones,
            texto,
            comando
        )

        boton.configure(
            width=ANCHO_BOTON,
            height=ALTO_BOTON,
            font=BUTTON_FONT
        )

        boton.pack(
            side=LEFT,
            padx=PADDING_BOTON,
            pady=4
        )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    limpiar_formulario()
    cargar_estudios()
