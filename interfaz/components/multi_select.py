"""Selector múltiple reutilizable para catálogos de la ontología.

Muestra una lista desplazable de casillas y permite obtener los identificadores
seleccionados. No contiene lógica de negocio: recibe las opciones ya resueltas
por la capa de lógica.
"""

import tkinter as tk

import customtkinter as ctk

from interfaz.theme.colors import (
    BORDER,
    CARD,
    PRIMARY,
    PRIMARY_HOVER,
    TEXT,
    TEXT_SECONDARY,
)

# -----------------------------
# SELECTOR MÚLTIPLE
# -----------------------------

class SelectorMultiple(ctk.CTkScrollableFrame):
    """Lista de checkboxes con selección múltiple por identificador."""

    def __init__(
        self,
        parent,
        opciones=None,
        height=120,
        width=320,
        **kwargs
    ):

        kwargs.setdefault("fg_color", "#0F172A")
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        kwargs.setdefault("scrollbar_button_color", CARD)
        kwargs.setdefault("scrollbar_button_hover_color", PRIMARY)

        super().__init__(
            parent,
            width=width,
            height=height,
            **kwargs
        )

        # El scrollbar vertical de CTkScrollableFrame trae una longitud por
        # defecto de 200 px que impone un alto mínimo mayor al solicitado y
        # desborda el formulario. Se ajusta a la altura real del selector.
        self._scrollbar.configure(
            height=max(40, height - 20)
        )

        self._variables = {}
        self._etiquetas = {}
        self._checks = []
        self._etiqueta_vacio = None

        self.set_opciones(opciones or [])

    # -----------------------------
    # NORMALIZACIÓN
    # -----------------------------

    def _normalizar_opcion(self, opcion):
        """Acepta (id, etiqueta) o {'id': ..., 'nombre': ...}."""

        if isinstance(opcion, dict):

            id_opcion = opcion.get("id", "")
            etiqueta = opcion.get("nombre", id_opcion)

        else:

            try:
                id_opcion, etiqueta = opcion

            except (TypeError, ValueError):
                return None, None

        id_opcion = "" if id_opcion is None else str(id_opcion).strip()
        etiqueta = str(etiqueta or id_opcion).strip()

        if not id_opcion:
            return None, None

        return id_opcion, (etiqueta or id_opcion)

    # -----------------------------
    # API
    # -----------------------------

    def set_opciones(self, opciones):
        """Reemplaza las opciones conservando las selecciones que sigan existiendo."""

        if isinstance(opciones, dict):
            opciones = [opciones]

        elif isinstance(opciones, str):
            opciones = [(opciones, opciones)]

        seleccionados = set(self.get_seleccionados())

        for check in self._checks:
            check.destroy()

        self._checks.clear()
        self._variables.clear()
        self._etiquetas.clear()

        if self._etiqueta_vacio is not None:
            self._etiqueta_vacio.destroy()
            self._etiqueta_vacio = None

        vistos = set()

        for opcion in opciones:

            id_opcion, etiqueta = self._normalizar_opcion(opcion)

            if id_opcion is None or id_opcion in vistos:
                continue

            vistos.add(id_opcion)

            variable = tk.IntVar(
                master=self,
                value=1 if id_opcion in seleccionados else 0
            )

            check = ctk.CTkCheckBox(
                self,
                text=etiqueta,
                variable=variable,
                onvalue=1,
                offvalue=0,
                font=("Inter", 12),
                text_color=TEXT,
                fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER,
                border_color=BORDER,
                checkbox_width=18,
                checkbox_height=18,
            )

            check.pack(
                anchor="w",
                padx=10,
                pady=3
            )

            self._checks.append(check)
            self._variables[id_opcion] = variable
            self._etiquetas[id_opcion] = etiqueta

        if not self._variables:

            self._etiqueta_vacio = ctk.CTkLabel(
                self,
                text="Sin opciones disponibles",
                font=("Inter", 12),
                text_color=TEXT_SECONDARY,
                anchor="w",
            )

            self._etiqueta_vacio.pack(
                anchor="w",
                padx=10,
                pady=8
            )

    def get_seleccionados(self):
        """Devuelve los identificadores marcados, en el orden del catálogo."""
        return [
            id_opcion
            for id_opcion, variable in self._variables.items()
            if variable.get() == 1
        ]

    def set_seleccionados(self, ids):
        """Marca únicamente los identificadores indicados."""

        if isinstance(ids, str):
            ids = [ids]

        seleccionados = {
            str(item).strip()
            for item in (ids or [])
            if item is not None
        }

        for id_opcion, variable in self._variables.items():

            variable.set(1 if id_opcion in seleccionados else 0)

    def limpiar(self):
        """Desmarca todas las opciones."""
        self.set_seleccionados([])
