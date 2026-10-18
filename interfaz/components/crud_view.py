"""
Componente base reutilizable para las pantallas de gestión (CRUD).

Abstrae el esqueleto repetido de las vistas: limpieza del panel, contenedor,
título, card, formulario de entradas, buscador opcional, tabla de resultados y
panel de botones Agregar / Modificar / Eliminar.

Cada vista concreta sólo declara:
  - el título,
  - las columnas y la altura de la tabla,
  - la lista de campos del formulario (inputs y/o combos),
  - opcionalmente un buscador,
  - y, tras construir el componente, sus manejadores de eventos.

No contiene lógica de negocio ni accede a la ontología: eso vive en logica/.
"""

import customtkinter as ctk
from tkinter import *
from tkinter import ttk

from interfaz.theme.colors import *
from interfaz.theme.fonts import *

from interfaz.components.ui import (
    crear_titulo,
    crear_card,
    crear_label,
    crear_input,
    crear_boton_exito,
    crear_boton_warning,
    crear_boton_danger
)
from interfaz.components.table import crear_tabla

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

        for indice, campo in enumerate(self.campos):

            etiqueta = crear_label(
                self.form,
                campo["label"]
            )

            etiqueta.grid(
                row=indice,
                column=0,
                padx=15,
                pady=15,
                sticky="w"
            )

            if campo.get("tipo", "input") == "combo":

                widget = ttk.Combobox(
                    self.form,
                    font=("Inter", 13),
                    width=32
                )

                if campo.get("valores"):

                    widget["values"] = campo["valores"]

            else:

                widget = crear_input(
                    self.form,
                    campo.get("placeholder", "")
                )

            widget.grid(
                row=indice,
                column=1,
                padx=15,
                pady=15
            )

            self.widgets[campo["clave"]] = widget

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
        etiqueta_eliminar="Eliminar"
    ):

        self.frame_botones.pack(
            pady=(0, 30)
        )

        boton_agregar = crear_boton_exito(
            self.frame_botones,
            etiqueta_agregar,
            al_agregar
        )

        boton_agregar.pack(
            side=LEFT,
            padx=10
        )

        boton_modificar = crear_boton_warning(
            self.frame_botones,
            etiqueta_modificar,
            al_modificar
        )

        boton_modificar.pack(
            side=LEFT,
            padx=10
        )

        boton_eliminar = crear_boton_danger(
            self.frame_botones,
            etiqueta_eliminar,
            al_eliminar
        )

        boton_eliminar.pack(
            side=LEFT,
            padx=10
        )

    # -----------------------------
    # UTILIDADES DE CAMPOS
    # -----------------------------

    def _limpiar_widget(self, clave):

        campo = None

        for item in self.campos:

            if item["clave"] == clave:
                campo = item
                break

        if campo is None:
            return

        widget = self.widgets[clave]

        if campo.get("tipo", "input") == "combo":

            widget.set("")

        else:

            widget.delete(0, END)

    def limpiar_campo(self, clave):
        """Limpia un único campo del formulario."""
        self._limpiar_widget(clave)

    def limpiar_campos(self):
        """Limpia todos los campos del formulario."""
        for campo in self.campos:
            self._limpiar_widget(campo["clave"])

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
