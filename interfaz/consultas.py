from tkinter import END, messagebox, ttk

import customtkinter as ctk

from interfaz.components.alert_panel import PanelAlertasMedicamento
from interfaz.components.searchable_combobox import ComboBuscable
from interfaz.components.table import crear_tabla
from interfaz.components.ui import (
    bloquear_rueda,
    crear_boton_danger,
    crear_boton_exito,
    crear_boton_primario,
    crear_boton_warning,
    crear_card,
    crear_input,
    crear_label,
    crear_subtitulo,
    crear_textbox,
    crear_titulo,
)
from interfaz.theme.colors import BACKGROUND, BORDER, CARD, PRIMARY, TEXT
from interfaz.theme.combobox import configurar_estilo_combobox
from logica.consultas import crear_consulta, eliminar_consulta, listar_consultas
from logica.estudios import listar_estudios
from logica.medicamentos import (
    listar_medicamentos,
    obtener_alertas_medicamento,
    obtener_medicamento,
)
from logica.medicos import listar_medicos
from logica.pacientes import listar_pacientes

# -----------------------------
# HELPERS DE UI
# -----------------------------

def _crear_seccion(parent, titulo):
    """Crea una tarjeta visual para una sección del acto médico."""

    seccion = ctk.CTkFrame(
        parent,
        fg_color="#0F172A",
        corner_radius=12,
        border_width=1,
        border_color=BORDER
    )

    seccion.pack(
        fill="x",
        pady=(0, 14)
    )

    etiqueta = crear_label(seccion, titulo)
    etiqueta.configure(
        font=("Inter", 15, "bold"),
        text_color=TEXT
    )
    etiqueta.pack(
        anchor="w",
        padx=16,
        pady=(12, 6)
    )

    contenido = ctk.CTkFrame(
        seccion,
        fg_color="transparent"
    )
    contenido.pack(
        fill="x",
        padx=16,
        pady=(0, 14)
    )

    return contenido


def _crear_combo(parent, valores):
    """Crea un combobox oscuro de selección cerrada y rueda bloqueada."""

    combo = ttk.Combobox(
        parent,
        values=valores,
        state="readonly",
        style="Dark.TCombobox",
        font=("Inter", 13)
    )
    bloquear_rueda(combo)

    return combo


# -----------------------------
# VISTA PRINCIPAL
# -----------------------------

def mostrar_consultas(panel):

    for widget in panel.winfo_children():
        widget.destroy()

    panel.configure(fg_color=BACKGROUND)
    configurar_estilo_combobox(panel.winfo_toplevel())

    pacientes = listar_pacientes()
    medicos = listar_medicos()
    medicamentos = listar_medicamentos()
    estudios = listar_estudios()

    opciones_pacientes = [
        paciente.get("nombre") or paciente.get("id", "")
        for paciente in pacientes
    ]
    opciones_medicos = [
        medico.get("nombre") or medico.get("id", "")
        for medico in medicos
    ]
    opciones_medicamentos = [
        medicamento.get("nombre") or medicamento.get("id", "")
        for medicamento in medicamentos
    ]
    opciones_estudios = [
        estudio.get("nombre") or estudio.get("id", "")
        for estudio in estudios
    ]

    consultas_por_id = {}
    estudios_seleccionados = []

    # -----------------------------
    # CONTENEDOR
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

    titulo = crear_titulo(
        contenedor,
        "Consultas Médicas"
    )
    titulo.pack(anchor="w")

    subtitulo = crear_subtitulo(
        contenedor,
        "Registre el acto médico: diagnóstico, prescripción y estudios solicitados."
    )
    subtitulo.pack(
        anchor="w",
        pady=(4, 18)
    )

    card = crear_card(contenedor)
    card.pack(
        fill="both",
        expand=True
    )

    cuerpo = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )
    cuerpo.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=25
    )
    cuerpo.grid_rowconfigure(0, weight=1)
    cuerpo.grid_columnconfigure(0, weight=3, minsize=520)
    cuerpo.grid_columnconfigure(1, weight=2, minsize=330)

    panel_izq = ctk.CTkFrame(
        cuerpo,
        fg_color="transparent"
    )
    panel_izq.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 18)
    )
    panel_izq.grid_rowconfigure(0, weight=1)
    panel_izq.grid_columnconfigure(0, weight=1)

    formulario = ctk.CTkScrollableFrame(
        panel_izq,
        fg_color="transparent",
        scrollbar_button_color=CARD,
        scrollbar_button_hover_color=PRIMARY
    )
    formulario.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    # -----------------------------
    # 1. PACIENTE Y PROFESIONAL
    # -----------------------------

    seccion = _crear_seccion(
        formulario,
        "1. Paciente y profesional"
    )
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = crear_label(
        seccion,
        "Paciente (escriba para filtrar)"
    )
    etiqueta.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    combo_paciente = ComboBuscable(
        seccion,
        valores=opciones_pacientes,
        font=("Inter", 13),
        width=34
    )
    combo_paciente.grid(
        row=0,
        column=1,
        sticky="ew",
        pady=6
    )

    etiqueta = crear_label(
        seccion,
        "Médico (escriba para filtrar)"
    )
    etiqueta.grid(
        row=1,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    combo_medico = ComboBuscable(
        seccion,
        valores=opciones_medicos,
        font=("Inter", 13),
        width=34
    )
    combo_medico.grid(
        row=1,
        column=1,
        sticky="ew",
        pady=6
    )

    # -----------------------------
    # 2. DATOS DE LA CONSULTA
    # -----------------------------

    seccion = _crear_seccion(
        formulario,
        "2. Datos de la consulta"
    )
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = crear_label(
        seccion,
        "Fecha"
    )
    etiqueta.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    entrada_fecha = crear_input(
        seccion,
        "AAAA-MM-DD"
    )
    entrada_fecha.grid(
        row=0,
        column=1,
        sticky="ew",
        pady=6
    )

    etiqueta = crear_label(
        seccion,
        "Notas clínicas"
    )
    etiqueta.grid(
        row=1,
        column=0,
        sticky="nw",
        padx=(0, 12),
        pady=6
    )

    notas = crear_textbox(
        seccion,
        height=90,
        width=420
    )
    notas.grid(
        row=1,
        column=1,
        sticky="ew",
        pady=6
    )

    # -----------------------------
    # 3. DIAGNÓSTICO
    # -----------------------------

    seccion = _crear_seccion(
        formulario,
        "3. Diagnóstico de la visita"
    )
    seccion.grid_columnconfigure(0, weight=1)

    diagnostico = crear_textbox(
        seccion,
        height=70,
        width=420
    )
    diagnostico.grid(
        row=0,
        column=0,
        sticky="ew"
    )

    # -----------------------------
    # 4. PRESCRIPCIÓN
    # -----------------------------

    seccion = _crear_seccion(
        formulario,
        "4. Prescripción"
    )
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = crear_label(
        seccion,
        "Medicamento"
    )
    etiqueta.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    combo_medicamento = _crear_combo(
        seccion,
        opciones_medicamentos
    )
    combo_medicamento.grid(
        row=0,
        column=1,
        sticky="ew",
        pady=6
    )

    # Panel dinámico de alertas semánticas del medicamento seleccionado.
    panel_alerta = PanelAlertasMedicamento(seccion)
    panel_alerta.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="ew",
        pady=(2, 8)
    )

    def actualizar_panel_alerta(event=None):
        """Actualiza color y detalle al cambiar el medicamento seleccionado."""
        referencia = combo_medicamento.get().strip()

        if not referencia:

            panel_alerta.limpiar()

            return

        medicamento = obtener_medicamento(referencia)
        panel_alerta.mostrar(
            obtener_alertas_medicamento(medicamento)
        )

    combo_medicamento.bind(
        "<<ComboboxSelected>>",
        actualizar_panel_alerta
    )

    etiqueta = crear_label(
        seccion,
        "Dosis"
    )
    etiqueta.grid(
        row=2,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    entrada_dosis = crear_input(
        seccion,
        "Ej. 500 mg cada 8 horas"
    )
    entrada_dosis.grid(
        row=2,
        column=1,
        sticky="ew",
        pady=6
    )

    etiqueta = crear_label(
        seccion,
        "Indicaciones"
    )
    etiqueta.grid(
        row=3,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    entrada_indicaciones = crear_input(
        seccion,
        "Ej. Tomar después de las comidas"
    )
    entrada_indicaciones.grid(
        row=3,
        column=1,
        sticky="ew",
        pady=6
    )

    # -----------------------------
    # 5. ESTUDIOS SOLICITADOS
    # -----------------------------

    seccion = _crear_seccion(
        formulario,
        "5. Estudios solicitados"
    )
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = crear_label(
        seccion,
        "Estudio (seleccione o escriba uno nuevo)"
    )
    etiqueta.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 12),
        pady=6
    )

    combo_estudio = ComboBuscable(
        seccion,
        valores=opciones_estudios,
        font=("Inter", 13),
        width=34
    )
    combo_estudio.grid(
        row=0,
        column=1,
        sticky="ew",
        pady=6
    )

    lista_estudios = crear_textbox(
        seccion,
        height=70,
        width=420
    )
    lista_estudios.grid(
        row=2,
        column=0,
        columnspan=2,
        sticky="ew",
        pady=(6, 0)
    )
    lista_estudios.configure(state="disabled")

    def actualizar_lista_estudios():

        lista_estudios.configure(state="normal")
        lista_estudios.delete("1.0", END)

        if estudios_seleccionados:

            lista_estudios.insert(
                "1.0",
                "\n".join(
                    f"• {estudio}"
                    for estudio in estudios_seleccionados
                )
            )

        else:

            lista_estudios.insert(
                "1.0",
                "Aún no hay estudios añadidos."
            )

        lista_estudios.configure(state="disabled")

    def agregar_estudio():

        nombre = combo_estudio.get().strip()

        if not nombre:

            messagebox.showwarning(
                "Estudio requerido",
                "Seleccione o escriba un estudio médico."
            )

            return

        if any(
            estudio.casefold() == nombre.casefold()
            for estudio in estudios_seleccionados
        ):

            messagebox.showwarning(
                "Estudio duplicado",
                "Ese estudio ya está en la solicitud."
            )

            return

        estudios_seleccionados.append(nombre)
        combo_estudio.set("")
        actualizar_lista_estudios()

    boton_agregar = crear_boton_primario(
        seccion,
        "Añadir estudio",
        agregar_estudio
    )
    boton_agregar.grid(
        row=1,
        column=1,
        sticky="w",
        pady=(0, 6)
    )

    # -----------------------------
    # ACCIONES DEL FORMULARIO
    # -----------------------------

    def limpiar_formulario():

        combo_paciente.set("")
        combo_medico.set("")
        entrada_fecha.delete(0, END)
        notas.delete("1.0", END)
        diagnostico.delete("1.0", END)
        combo_medicamento.set("")
        actualizar_panel_alerta()
        entrada_dosis.delete(0, END)
        entrada_indicaciones.delete(0, END)
        combo_estudio.set("")
        estudios_seleccionados.clear()
        actualizar_lista_estudios()

    def on_registrar():

        try:

            crear_consulta(
                paciente_ref=combo_paciente.get(),
                medico_ref=combo_medico.get(),
                fecha=entrada_fecha.get(),
                notas=notas.get("1.0", END).strip(),
                diagnostico=diagnostico.get("1.0", END).strip(),
                estudios=list(estudios_seleccionados),
                medicamento_ref=combo_medicamento.get(),
                dosis=entrada_dosis.get(),
                indicaciones=entrada_indicaciones.get()
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        except Exception as error:  # noqa: BLE001 - frontera de interfaz.

            messagebox.showerror(
                "Error inesperado",
                f"No se pudo registrar la consulta:\n{error}"
            )

            return

        cargar_consultas()
        limpiar_formulario()

        messagebox.showinfo(
            "Correcto",
            "Consulta registrada correctamente."
        )

    acciones = ctk.CTkFrame(
        panel_izq,
        fg_color="transparent"
    )
    acciones.grid(
        row=1,
        column=0,
        sticky="ew",
        pady=(14, 0)
    )

    boton_registrar = crear_boton_exito(
        acciones,
        "Registrar Consulta",
        on_registrar
    )
    boton_registrar.pack(
        side="left",
        padx=(0, 10)
    )

    boton_limpiar = crear_boton_warning(
        acciones,
        "Limpiar",
        limpiar_formulario
    )
    boton_limpiar.pack(side="left")

    # -----------------------------
    # CONSULTAS RECIENTES
    # -----------------------------

    panel_der = ctk.CTkFrame(
        cuerpo,
        fg_color="transparent"
    )
    panel_der.grid(
        row=0,
        column=1,
        sticky="nsew"
    )
    panel_der.grid_rowconfigure(1, weight=1)
    panel_der.grid_columnconfigure(0, weight=1)

    etiqueta_tabla = crear_label(
        panel_der,
        "Consultas recientes"
    )
    etiqueta_tabla.configure(
        font=("Inter", 16, "bold"),
        text_color=TEXT
    )
    etiqueta_tabla.grid(
        row=0,
        column=0,
        sticky="w",
        pady=(0, 10)
    )

    tabla_frame, tabla = crear_tabla(
        panel_der,
        ["Paciente", "Fecha", "Diagnóstico"],
        altura=9
    )
    tabla_frame.grid(
        row=1,
        column=0,
        sticky="nsew"
    )

    tabla.column("Paciente", width=120, anchor="w")
    tabla.column("Fecha", width=90, anchor="center")
    tabla.column("Diagnóstico", width=180, anchor="w")

    detalle = crear_textbox(
        panel_der,
        height=120,
        width=320
    )
    detalle.grid(
        row=2,
        column=0,
        sticky="ew",
        pady=(12, 10)
    )
    detalle.configure(state="disabled")

    def mostrar_detalle(texto=""):

        detalle.configure(state="normal")
        detalle.delete("1.0", END)

        if texto:
            detalle.insert("1.0", texto)

        detalle.configure(state="disabled")

    def cargar_consultas():

        consultas_por_id.clear()

        for item in tabla.get_children():
            tabla.delete(item)

        for consulta in listar_consultas():

            consultas_por_id[consulta["id"]] = consulta

            diagnostico = ", ".join(
                item["nombre"]
                for item in consulta["diagnosticos"]
            ) or "Sin diagnóstico"

            tabla.insert(
                "",
                END,
                iid=consulta["id"],
                values=(
                    consulta["paciente"] or "Sin paciente",
                    consulta["fecha"] or "Sin fecha",
                    diagnostico
                )
            )

        mostrar_detalle()

    def seleccionar_consulta(event=None):

        seleccion = tabla.selection()

        if not seleccion:
            return

        consulta = consultas_por_id.get(seleccion[0])

        if consulta is None:
            return

        receta = consulta.get("receta") or {}
        diagnosticos = ", ".join(
            item["nombre"]
            for item in consulta["diagnosticos"]
        ) or "Sin diagnóstico"
        estudios_texto = ", ".join(
            item["nombre"]
            for item in consulta["estudios"]
        ) or "Sin estudios"

        mostrar_detalle(
            f"Paciente: {consulta['paciente'] or 'Sin paciente'}\n"
            f"Médico: {consulta['medico'] or 'Sin médico'}\n"
            f"Fecha: {consulta['fecha'] or 'Sin fecha'}\n"
            f"Diagnóstico: {diagnosticos}\n"
            f"Receta: {receta.get('medicamento', 'Sin receta')} "
            f"— {receta.get('dosis', '')}\n"
            f"Indicaciones: {receta.get('indicaciones', 'Sin indicaciones')}\n"
            f"Estudios: {estudios_texto}\n"
            f"Notas: {consulta['notas'] or 'Sin notas'}"
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_consulta
    )

    def on_eliminar():

        seleccion = tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                "Error",
                "Seleccione una consulta de la tabla."
            )

            return

        if not messagebox.askyesno(
            "Confirmar eliminación",
            "¿Eliminar la consulta seleccionada y su receta asociada?"
        ):
            return

        try:

            eliminada = eliminar_consulta(seleccion[0])

        except Exception as error:  # noqa: BLE001 - frontera de interfaz.

            messagebox.showerror(
                "Error inesperado",
                f"No se pudo eliminar la consulta:\n{error}"
            )

            return

        if not eliminada:

            messagebox.showwarning(
                "Error",
                "No se encontró la consulta seleccionada."
            )

            return

        cargar_consultas()
        limpiar_formulario()

        messagebox.showinfo(
            "Correcto",
            "Consulta eliminada correctamente."
        )

    boton_eliminar = crear_boton_danger(
        panel_der,
        "Eliminar seleccionada",
        on_eliminar
    )
    boton_eliminar.grid(
        row=3,
        column=0,
        sticky="ew"
    )

    # -----------------------------
    # CARGA INICIAL
    # -----------------------------

    actualizar_lista_estudios()
    cargar_consultas()
    limpiar_formulario()
