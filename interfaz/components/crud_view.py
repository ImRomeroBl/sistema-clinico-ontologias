"""
Componente base reutilizable para las pantallas de gestión (CRUD).

Abstrae el esqueleto repetido de las vistas: limpieza del panel, contenedor,
título, card, formulario de entradas, buscador opcional, tabla de resultados y
panel de botones Agregar / Modificar / Eliminar.

Cada vista concreta sólo declara:
  - el título,
  - las columnas y la altura de la tabla,
  - la lista de campos del formulario (inputs, combos, combos buscables,
    selectores múltiples y textbox),
  - opcionalmente un buscador,
  - y, tras construir el componente, sus manejadores de eventos.

No contiene lógica de negocio ni accede a la ontología: eso vive en logica/.
"""

from tkinter import END, LEFT, ttk

import customtkinter as ctk

from interfaz.components.multi_select import SelectorMultiple
from interfaz.components.searchable_combobox import ComboBuscable
from interfaz.components.table import crear_tabla
from interfaz.components.ui import (
    bloquear_rueda,
    crear_boton_danger,
    crear_boton_exito,
    crear_boton_warning,
    crear_card,
    crear_input,
    crear_label,
    crear_textbox,
    crear_titulo,
    vincular_formato_telefono,
)
from interfaz.theme.colors import BACKGROUND
from interfaz.theme.combobox import configurar_estilo_combobox

# -----------------------------
# COMPONENTE VISTA CRUD
# -----------------------------

class VistaCRUD:

    def __init__(
        self,
        panel,
        titulo,
        columnas,
        campos,
        altura=6,
        buscador=None
    ):

        self.panel = panel
        self.campos = campos
        self.widgets = {}

        # -----------------------------
        # LIMPIAR PANEL
        # -----------------------------

        for widget in panel.winfo_children():
            widget.destroy()

        panel.configure(fg_color=BACKGROUND)

        # -----------------------------
        # CONTENEDOR PRINCIPAL
        # -----------------------------

        self.contenedor = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        self.contenedor.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        # -----------------------------
        # TITULO
        # -----------------------------

        self.titulo = crear_titulo(
            self.contenedor,
            titulo
        )

        self.titulo.pack(
            anchor="w",
            pady=(0, 25)
        )

        # -----------------------------
        # CARD PRINCIPAL
        # -----------------------------

        self.card = crear_card(self.contenedor)

        self.card.pack(
            fill="both",
            expand=True
        )

        # -----------------------------
        # FORMULARIO
        # -----------------------------

        self.form = ctk.CTkFrame(
            self.card,
            fg_color="transparent"
        )

        self.form.pack(
            fill="x",
            padx=30,
            pady=(30, 10)
        )

        self._crear_campos()

        # -----------------------------
        # BUSCADOR (OPCIONAL)
        # -----------------------------

        self.buscador = None

        if buscador is not None:
            self._crear_buscador(buscador)

        # -----------------------------
        # TABLA
        # -----------------------------

        self.tabla_frame, self.tabla = crear_tabla(
            parent=self.card,
            columnas=columnas,
            altura=altura
        )

        self.tabla_frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # -----------------------------
        # ESTILO DE COMBOS
        # -----------------------------

        self._estilizar_combos()

        # -----------------------------
        # PANEL DE BOTONES (se empaqueta al final)
        # -----------------------------

        self.frame_botones = ctk.CTkFrame(
            self.card,
            fg_color="transparent"
        )

    # -----------------------------
    # CONSTRUCCION DE CAMPOS
    # -----------------------------

    def _crear_campos(self):

        usa_grupos = any(
            campo.get("grupo", 0) > 0
            for campo in self.campos
        )

        if usa_grupos:

            self.form.grid_columnconfigure(1, weight=1)
            self.form.grid_columnconfigure(3, weight=1)

        else:

            self.form.grid_columnconfigure(1, weight=1, minsize=360)

        filas = {}

        for campo in self.campos:

            grupo = campo.get("grupo", 0)
            fila = filas.get(grupo, 0)
            filas[grupo] = fila + 1

            etiqueta = crear_label(
                self.form,
                campo["label"]
            )

            etiqueta.grid(
                row=fila,
                column=grupo * 2,
                padx=15,
                pady=15,
                sticky="w"
            )

            tipo = campo.get("tipo", "input")

            if tipo == "combo_buscable":

                widget = ComboBuscable(
                    self.form,
                    valores=campo.get("valores", []),
                    font=("Inter", 13),
                    width=32
                )

            elif tipo == "combo":

                widget = ttk.Combobox(
                    self.form,
                    font=("Inter", 13),
                    width=32
                )

                if campo.get("valores"):

                    widget["values"] = campo["valores"]

            elif tipo == "multiple":

                widget = SelectorMultiple(
                    self.form,
                    opciones=campo.get("opciones", campo.get("valores", [])),
                    height=campo.get("altura", 120),
                    width=campo.get("ancho", 320)
                )

            elif tipo == "texto":

                widget = crear_textbox(
                    self.form,
                    height=campo.get("altura", 90),
                    width=campo.get("ancho", 320)
                )

            elif tipo == "telefono":

                widget = crear_input(
                    self.form,
                    campo.get("placeholder", ""),
                    width=campo.get("ancho", 360 if not usa_grupos else 140),
                )
                vincular_formato_telefono(widget)

            else:

                widget = crear_input(
                    self.form,
                    campo.get("placeholder", ""),
                    width=campo.get("ancho", 360 if not usa_grupos else 140),
                )

            sticky = campo.get("sticky")

            if sticky is None:

                if usa_grupos or tipo in ("texto", "multiple"):
                    sticky = "ew"
                else:
                    sticky = "w"

            widget.grid(
                row=fila,
                column=grupo * 2 + 1,
                padx=15,
                pady=15,
                sticky=sticky
            )

            self.widgets[campo["clave"]] = widget

    # -----------------------------
    # ESTILO DE COMBOS
    # -----------------------------

    def _estilizar_combos(self):

        configurar_estilo_combobox(
            self.form.winfo_toplevel()
        )

        for campo in self.campos:

            if campo.get("tipo", "input") in (
                "combo",
                "combo_buscable"
            ):

                widget = self.widgets[campo["clave"]]
                widget.configure(style="Dark.TCombobox")
                bloquear_rueda(widget)

    # -----------------------------
    # BUSCADOR
    # -----------------------------

    def _crear_buscador(self, buscador):

        frame = ctk.CTkFrame(
            self.card,
            fg_color="transparent"
        )

        frame.pack(
            fill="x",
            padx=30,
            pady=(10, 10)
        )

        etiqueta = crear_label(
            frame,
            buscador["label"]
        )

        etiqueta.pack(
            anchor="w",
            pady=(0, 10)
        )

        self.buscador = crear_input(
            frame,
            buscador.get("placeholder", "")
        )

        self.buscador.pack(
            fill="x"
        )

        if buscador.get("callback") is not None:

            self.buscador.bind(
                "<KeyRelease>",
                buscador["callback"]
            )

    # -----------------------------
    # PANEL DE BOTONES
    # -----------------------------

    def crear_botones(
        self,
        al_agregar,
        al_modificar,
        al_eliminar,
        etiqueta_agregar="Agregar",
        etiqueta_modificar="Modificar",
        etiqueta_eliminar="Eliminar",
        ancho=None,
        alto=None,
        fuente=None,
        padding=12
    ):

        self.frame_botones.pack(
            pady=(10, 30)
        )

        botones = [
            crear_boton_exito(
                self.frame_botones,
                etiqueta_agregar,
                al_agregar
            ),
            crear_boton_warning(
                self.frame_botones,
                etiqueta_modificar,
                al_modificar
            ),
            crear_boton_danger(
                self.frame_botones,
                etiqueta_eliminar,
                al_eliminar
            ),
        ]

        for boton in botones:

            if ancho is not None:
                boton.configure(width=ancho)

            if alto is not None:
                boton.configure(height=alto)

            if fuente is not None:
                boton.configure(font=fuente)

            boton.pack(
                side=LEFT,
                padx=padding,
                pady=4
            )

    # -----------------------------
    # UTILIDADES DE CAMPOS
    # -----------------------------

    def _campo(self, clave):
        """Devuelve la definición de un campo por su clave."""

        for item in self.campos:

            if item["clave"] == clave:
                return item

        return None

    def _limpiar_widget(self, clave):
        """Limpia un campo delegando en su tipo."""

        self.set_valor_campo(clave, "")

    def limpiar_campos(self):
        """Limpia todos los campos del formulario."""
        for campo in self.campos:
            self._limpiar_widget(campo["clave"])

    def valor_campo(self, clave):
        """Devuelve el valor actual de una entrada, combo, textbox o selector."""

        campo = self._campo(clave)

        if campo is None:
            return ""

        widget = self.widgets[clave]
        tipo = campo.get("tipo", "input")

        if tipo == "multiple":
            return widget.get_seleccionados()

        if tipo == "texto":
            return widget.get("1.0", "end-1c")

        return widget.get()

    def set_valor_campo(self, clave, valor):
        """Asigna un valor a un campo según su tipo."""

        campo = self._campo(clave)

        if campo is None:
            return

        widget = self.widgets[clave]
        tipo = campo.get("tipo", "input")

        if tipo == "multiple":

            widget.set_seleccionados(valor or [])
            return

        valor = "" if valor is None else str(valor)

        if tipo in ("combo", "combo_buscable"):

            widget.set(valor)

        elif tipo == "texto":

            widget.delete("1.0", END)
            widget.insert("1.0", valor)

        else:

            widget.delete(0, END)
            widget.insert(0, valor)

    # -----------------------------
    # UTILIDADES DE TABLA
    # -----------------------------

    def limpiar_tabla(self):
        """Elimina todas las filas de la tabla."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def insertar_fila(self, valores, iid=None):
        """Inserta una fila en la tabla; permite fijar el iid (clave estable)."""
        if iid is None:
            self.tabla.insert("", END, values=valores)
        else:
            self.tabla.insert("", END, iid=iid, values=valores)
