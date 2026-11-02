from tkinter import messagebox

from interfaz.components.crud_view import VistaCRUD
from logica.medicamentos import (
    TIPOS_MEDICAMENTO,
    actualizar_medicamento,
    crear_medicamento,
    eliminar_medicamento,
    listar_medicamentos,
)

# --------------------------------
# HELPERS
# --------------------------------

def _resumen(texto, limite=35):
    """Convierte un texto multilínea en una vista previa breve de una línea."""
    texto = " ".join(str(texto or "").split())

    if len(texto) <= limite:
        return texto

    return texto[:limite].rstrip() + "..."

# --------------------------------
# MOSTRAR MEDICAMENTOS
# --------------------------------

def mostrar_medicamentos(panel):

    medicamento_seleccionado = [None]
    medicamentos_por_id = {}

    tipos = [etiqueta for _, etiqueta in TIPOS_MEDICAMENTO]
    tipo_por_etiqueta = {
        etiqueta: clave
        for clave, etiqueta in TIPOS_MEDICAMENTO
    }

    # -----------------------------
    # ESTRUCTURA BASE
    # -----------------------------

    vista = VistaCRUD(
        panel,
        titulo="Gestión de Medicamentos",
        columnas=[
            "Nombre",
            "Tipo",
            "Contraindicaciones",
            "Efectos Secundarios"
        ],
        altura=7,
        campos=[
            {
                "clave": "nombre",
                "label": "Nombre",
                "placeholder": "Ingrese nombre del medicamento",
                "grupo": 0
            },
            {
                "clave": "tipo",
                "label": "Tipo",
                "tipo": "combo",
                "valores": tipos,
                "grupo": 1
            },
            {
                "clave": "contraindicaciones",
                "label": "Contraindicaciones",
                "tipo": "texto",
                "altura": 90,
                "grupo": 0
            },
            {
                "clave": "efectos_secundarios",
                "label": "Efectos secundarios",
                "tipo": "texto",
                "altura": 90,
                "grupo": 1
            }
        ]
    )

    tabla = vista.tabla

    tabla.column("Nombre", width=200, anchor="w")
    tabla.column("Tipo", width=140, anchor="center")
    tabla.column("Contraindicaciones", width=330, anchor="w")
    tabla.column("Efectos Secundarios", width=330, anchor="w")

    combo_tipo = vista.widgets["tipo"]
    combo_tipo.configure(state="readonly")

    # -----------------------------
    # HELPERS DEL FORMULARIO
    # -----------------------------

    def tipo_seleccionado():
        return tipo_por_etiqueta.get(combo_tipo.get(), "generico")

    def limpiar_formulario():
        vista.limpiar_campos()
        combo_tipo.set("Genérico")

    # -----------------------------
    # CARGAR MEDICAMENTOS
    # -----------------------------

    def cargar_medicamentos():

        medicamentos_por_id.clear()
        vista.limpiar_tabla()

        for medicamento in listar_medicamentos():

            medicamentos_por_id[medicamento["id"]] = medicamento

            vista.insertar_fila(
                (
                    medicamento["nombre"],
                    medicamento["tipo_label"],
                    _resumen(medicamento["contraindicaciones"]),
                    _resumen(medicamento["efectos_secundarios"])
                ),
                iid=medicamento["id"]
            )

    # -----------------------------
    # SELECCIONAR MEDICAMENTO
    # -----------------------------

    def seleccionar_medicamento(event):

        seleccion = tabla.selection()

        if not seleccion:
            return

        medicamento_id = seleccion[0]
        medicamento = medicamentos_por_id.get(medicamento_id)

        if medicamento is None:
            return

        medicamento_seleccionado[0] = medicamento_id

        vista.limpiar_campos()

        vista.set_valor_campo("nombre", medicamento["nombre"])
        vista.set_valor_campo("tipo", medicamento["tipo_label"])
        vista.set_valor_campo(
            "contraindicaciones",
            medicamento["contraindicaciones"]
        )
        vista.set_valor_campo(
            "efectos_secundarios",
            medicamento["efectos_secundarios"]
        )

    tabla.bind(
        "<<TreeviewSelect>>",
        seleccionar_medicamento
    )

    # -----------------------------
    # AGREGAR MEDICAMENTO
    # -----------------------------

    def on_agregar():

        try:

            crear_medicamento(
                vista.valor_campo("nombre"),
                vista.valor_campo("contraindicaciones"),
                vista.valor_campo("efectos_secundarios"),
                tipo_seleccionado()
            )

        except ValueError as error:

            messagebox.showwarning(
                "Datos inválidos",
                str(error)
            )

            return

        cargar_medicamentos()
        limpiar_formulario()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            "Correcto",
            "Medicamento agregado correctamente"
        )

    # -----------------------------
    # MODIFICAR MEDICAMENTO
    # -----------------------------

    def on_modificar():

        medicamento_id = medicamento_seleccionado[0]

        if medicamento_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        try:

            actualizado = actualizar_medicamento(
                medicamento_id,
                vista.valor_campo("nombre"),
                vista.valor_campo("contraindicaciones"),
                vista.valor_campo("efectos_secundarios"),
                tipo_seleccionado()
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
                "No se encontró el medicamento seleccionado"
            )

            return

        cargar_medicamentos()
        limpiar_formulario()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            "Correcto",
            "Medicamento modificado correctamente"
        )

    # -----------------------------
    # ELIMINAR MEDICAMENTO
    # -----------------------------

    def on_eliminar():

        medicamento_id = medicamento_seleccionado[0]

        if medicamento_id is None:

            messagebox.showwarning(
                "Error",
                "Seleccione un medicamento"
            )

            return

        try:

            eliminado = eliminar_medicamento(medicamento_id)

        except ValueError as error:

            messagebox.showwarning(
                "No se puede eliminar",
                str(error)
            )

            return

        if not eliminado:

            messagebox.showwarning(
                "Error",
                "No se encontró el medicamento seleccionado"
            )

            return

        cargar_medicamentos()
        limpiar_formulario()

        medicamento_seleccionado[0] = None

        messagebox.showinfo(
            "Correcto",
            "Medicamento eliminado correctamente"
        )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    vista.crear_botones(
        on_agregar,
        on_modificar,
        on_eliminar,
        etiqueta_agregar="Agregar Medicamento",
        etiqueta_modificar="Modificar Medicamento",
        etiqueta_eliminar="Eliminar Medicamento"
    )

    # -----------------------------
    # CARGAR DATOS
    # -----------------------------

    limpiar_formulario()
    cargar_medicamentos()
