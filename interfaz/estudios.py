from tkinter import LEFT, messagebox

from interfaz.components.crud_view import VistaCRUD
from interfaz.components.ui import crear_boton_primario, crear_label
from interfaz.theme.colors import TEXT_SECONDARY
from logica.consultas import listar_consultas
from logica.estudios import (
    actualizar_estudio,
    asociar_estudio,
    crear_estudio,
    desasociar_estudio,
    eliminar_estudio,
    listar_estudios,
)
from logica.pacientes import listar_pacientes

# -----------------------------
# HELPERS
# -----------------------------

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
    estudios_por_id = {}

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
            "Estudio",
            "Paciente(s)",
            "Consulta(s)",
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

    tabla.column("Estudio", width=240, anchor="w")
    tabla.column("Paciente(s)", width=220, anchor="w")
    tabla.column("Consulta(s)", width=300, anchor="w")
    tabla.column("Estado", width=120, anchor="center")

    vista.widgets["nombre"].configure(width=420)

    combo_paciente = vista.widgets["paciente"]
    combo_consulta = vista.widgets["consulta"]

    combo_paciente.configure(width=38)
    combo_consulta.configure(width=70, state="readonly")

    ayuda = crear_label(
        vista.form,
        "Escriba para filtrar pacientes. La asociación se realiza a través de la consulta seleccionada."
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

        estudios_por_id.clear()
        vista.limpiar_tabla()

        for estudio in listar_estudios():

            estudios_por_id[estudio["id"]] = estudio

            pacientes = ", ".join(
                paciente["nombre"]
                for paciente in estudio["pacientes"]
            ) or "Sin paciente"

            consultas = ", ".join(
                consulta["fecha"] or "Sin fecha"
                for consulta in estudio["consultas"]
            ) or "Sin consulta"

            estado = "Asociado" if estudio["asociado"] else "Sin asociar"

            vista.insertar_fila(
                (
                    estudio["nombre"],
                    pacientes,
                    consultas,
                    estado
                ),
                iid=estudio["id"]
            )

    # -----------------------------
    # SELECCIONAR ESTUDIO
    # -----------------------------

    def seleccionar_estudio(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        estudio_id = seleccion[0]
        estudio = estudios_por_id.get(estudio_id)

        if estudio is None:
            return

        estudio_seleccionado[0] = estudio_id

        vista.set_valor_campo("nombre", estudio["nombre"])

        if estudio["consultas"]:

            primera = estudio["consultas"][0]

            combo_paciente.set(
                opcion_por_paciente_id.get(primera["paciente_id"], "")
            )

            refrescar_consultas()

            combo_consulta.set(
                opcion_por_consulta.get(primera["id"], "")
            )

        else:

            combo_paciente.set("")
            refrescar_consultas()

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_estudio
    )

    def seleccionar_estudio_por_id(estudio_id):

        if not estudio_id or estudio_id not in tabla.get_children():
            return

        tabla.selection_set(estudio_id)
        tabla.focus(estudio_id)
        tabla.see(estudio_id)

        seleccionar_estudio(None)

    # -----------------------------
    # LIMPIAR FORMULARIO
    # -----------------------------

    def limpiar_formulario():

        vista.limpiar_campos()

        combo_paciente.set("")

        refrescar_consultas()

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
        seleccionar_estudio_por_id(estudio_id)

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
        seleccionar_estudio_por_id(estudio_id)

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
        seleccionar_estudio_por_id(estudio_id)

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
        etiqueta_eliminar="Eliminar Estudio"
    )

    boton_asociar = crear_boton_primario(
        vista.frame_botones,
        "Asociar",
        on_asociar
    )

    boton_asociar.pack(
        side=LEFT,
        padx=10
    )

    boton_desasociar = crear_boton_primario(
        vista.frame_botones,
        "Desasociar",
        on_desasociar
    )

    boton_desasociar.pack(
        side=LEFT,
        padx=10
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    limpiar_formulario()
    cargar_estudios()
