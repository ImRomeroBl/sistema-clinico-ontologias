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
from logica.language_manager import language_manager, t
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

    return contenido, etiqueta


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
    etiquetas_texto = []

    def etiqueta_i18n(parent, clave):
        """Crea una etiqueta y registra su clave para el refresco en caliente."""
        etiqueta = crear_label(parent, t(clave))
        etiquetas_texto.append((etiqueta, clave))
        return etiqueta

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
        t("consultas.title")
    )
    titulo.pack(anchor="w")

    subtitulo = crear_subtitulo(
        contenedor,
        t("consultas.subtitle")
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

    seccion, etiqueta_seccion = _crear_seccion(
        formulario,
        t("consultas.sections.patient")
    )
    etiquetas_texto.append((etiqueta_seccion, "consultas.sections.patient"))
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.patient.label"
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

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.doctor.label"
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

    seccion, etiqueta_seccion = _crear_seccion(
        formulario,
        t("consultas.sections.data")
    )
    etiquetas_texto.append((etiqueta_seccion, "consultas.sections.data"))
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.date.label"
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
        t("consultas.fields.date.placeholder")
    )
    entrada_fecha.grid(
        row=0,
        column=1,
        sticky="ew",
        pady=6
    )

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.notes.label"
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

    seccion, etiqueta_seccion = _crear_seccion(
        formulario,
        t("consultas.sections.diagnosis")
    )
    etiquetas_texto.append((etiqueta_seccion, "consultas.sections.diagnosis"))
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

    seccion, etiqueta_seccion = _crear_seccion(
        formulario,
        t("consultas.sections.prescription")
    )
    etiquetas_texto.append((etiqueta_seccion, "consultas.sections.prescription"))
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.medication.label"
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

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.dose.label"
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
        t("consultas.fields.dose.placeholder")
    )
    entrada_dosis.grid(
        row=2,
        column=1,
        sticky="ew",
        pady=6
    )

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.indications.label"
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
        t("consultas.fields.indications.placeholder")
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

    seccion, etiqueta_seccion = _crear_seccion(
        formulario,
        t("consultas.sections.studies")
    )
    etiquetas_texto.append((etiqueta_seccion, "consultas.sections.studies"))
    seccion.grid_columnconfigure(1, weight=1)

    etiqueta = etiqueta_i18n(
        seccion,
        "consultas.fields.study.label"
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
                t("consultas.messages.no_studies_added")
            )

        lista_estudios.configure(state="disabled")

    def agregar_estudio():

        nombre = combo_estudio.get().strip()

        if not nombre:

            messagebox.showwarning(
                t("consultas.errors.study_required_title"),
                t("consultas.errors.study_required")
            )

            return

        if any(
            estudio.casefold() == nombre.casefold()
            for estudio in estudios_seleccionados
        ):

            messagebox.showwarning(
                t("consultas.errors.study_duplicate_title"),
                t("consultas.errors.study_duplicate")
            )

            return

        estudios_seleccionados.append(nombre)
        combo_estudio.set("")
        actualizar_lista_estudios()

    boton_agregar = crear_boton_primario(
        seccion,
        t("consultas.buttons.add_study"),
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
                t("common.invalid_data"),
                str(error)
            )

            return

        except Exception as error:  # noqa: BLE001 - frontera de interfaz.

            messagebox.showerror(
                t("common.unexpected_error"),
                f"{t('consultas.errors.register')}\n{error}"
            )

            return

        cargar_consultas()
        limpiar_formulario()

        messagebox.showinfo(
            t("common.correct"),
            t("consultas.messages.registered")
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
        t("consultas.buttons.register"),
        on_registrar
    )
    boton_registrar.pack(
        side="left",
        padx=(0, 10)
    )

    boton_limpiar = crear_boton_warning(
        acciones,
        t("consultas.buttons.clear"),
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
        t("consultas.recent_title")
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

    for columna, clave in (
        ("Paciente", "consultas.columns.patient"),
        ("Fecha", "consultas.columns.date"),
        ("Diagnóstico", "consultas.columns.diagnosis"),
    ):
        tabla.heading(columna, text=t(clave))

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
            ) or t("common.no_diagnosis")

            tabla.insert(
                "",
                END,
                iid=consulta["id"],
                values=(
                    consulta["paciente"] or t("common.no_patient"),
                    consulta["fecha"] or t("common.no_date"),
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
        ) or t("common.no_diagnosis")
        estudios_texto = ", ".join(
            item["nombre"]
            for item in consulta["estudios"]
        ) or t("common.no_studies")

        mostrar_detalle(
            f"{t('consultas.detail.patient')} "
            f"{consulta['paciente'] or t('common.no_patient')}\n"
            f"{t('consultas.detail.doctor')} "
            f"{consulta['medico'] or t('common.no_doctor')}\n"
            f"{t('consultas.detail.date')} "
            f"{consulta['fecha'] or t('common.no_date')}\n"
            f"{t('consultas.detail.diagnosis')} {diagnosticos}\n"
            f"{t('consultas.detail.prescription')} "
            f"{receta.get('medicamento') or t('common.no_prescription')} "
            f"— {receta.get('dosis', '')}\n"
            f"{t('consultas.detail.indications')} "
            f"{receta.get('indicaciones') or t('common.no_indications')}\n"
            f"{t('consultas.detail.studies')} {estudios_texto}\n"
            f"{t('consultas.detail.notes')} "
            f"{consulta['notas'] or t('common.no_notes')}"
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_consulta
    )

    def on_eliminar():

        seleccion = tabla.selection()

        if not seleccion:

            messagebox.showwarning(
                t("common.error"),
                t("consultas.messages.select")
            )

            return

        if not messagebox.askyesno(
            t("consultas.confirm.title"),
            t("consultas.confirm.delete")
        ):
            return

        try:

            eliminada = eliminar_consulta(seleccion[0])

        except Exception as error:  # noqa: BLE001 - frontera de interfaz.

            messagebox.showerror(
                t("common.unexpected_error"),
                f"{t('consultas.errors.delete')}\n{error}"
            )

            return

        if not eliminada:

            messagebox.showwarning(
                t("common.error"),
                t("consultas.messages.not_found")
            )

            return

        cargar_consultas()
        limpiar_formulario()

        messagebox.showinfo(
            t("common.correct"),
            t("consultas.messages.deleted")
        )

    boton_eliminar = crear_boton_danger(
        panel_der,
        t("consultas.buttons.delete_selected"),
        on_eliminar
    )
    boton_eliminar.grid(
        row=3,
        column=0,
        sticky="ew"
    )

    # -----------------------------
    # ACTUALIZACION DE IDIOMA
    # -----------------------------

    def update_ui_strings(lang=None):

        titulo.configure(text=t("consultas.title"))
        subtitulo.configure(text=t("consultas.subtitle"))
        etiqueta_tabla.configure(text=t("consultas.recent_title"))

        for etiqueta, clave in etiquetas_texto:
            etiqueta.configure(text=t(clave))

        for columna, clave in (
            ("Paciente", "consultas.columns.patient"),
            ("Fecha", "consultas.columns.date"),
            ("Diagnóstico", "consultas.columns.diagnosis"),
        ):
            tabla.heading(columna, text=t(clave))

        entrada_fecha.configure(
            placeholder_text=t("consultas.fields.date.placeholder")
        )
        entrada_dosis.configure(
            placeholder_text=t("consultas.fields.dose.placeholder")
        )
        entrada_indicaciones.configure(
            placeholder_text=t("consultas.fields.indications.placeholder")
        )

        boton_agregar.configure(text=t("consultas.buttons.add_study"))
        boton_registrar.configure(text=t("consultas.buttons.register"))
        boton_limpiar.configure(text=t("consultas.buttons.clear"))
        boton_eliminar.configure(
            text=t("consultas.buttons.delete_selected")
        )

        if combo_medicamento.get().strip():
            actualizar_panel_alerta()
        else:
            panel_alerta.limpiar()

        seleccion = tabla.selection()
        seleccionada = seleccion[0] if seleccion else None

        cargar_consultas()

        if seleccionada and seleccionada in tabla.get_children():
            tabla.selection_set(seleccionada)
            tabla.focus(seleccionada)
            seleccionar_consulta()

        actualizar_lista_estudios()

    language_manager.add_listener(update_ui_strings)

    # -----------------------------
    # CARGA INICIAL
    # -----------------------------

    actualizar_lista_estudios()
    cargar_consultas()
    limpiar_formulario()

    return lambda: language_manager.remove_listener(update_ui_strings)
