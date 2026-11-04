"""Combobox editable con sugerencias en tiempo real.

El componente filtra sus opciones mientras el usuario escribe y muestra un
panel de sugerencias propio. A diferencia del desplegable nativo de ttk, el
panel no roba el foco: el campo sigue recibiendo el texto y la selección sólo
se confirma con un clic o con Enter sobre una sugerencia resaltada.

Enter nunca elige el primer resultado cuando hay varias coincidencias. La
rueda del ratón no modifica el valor del combobox; dentro del panel de
sugerencias únicamente desplaza la vista.
"""

import tkinter as tk
import unicodedata
from tkinter import END, ttk

from interfaz.theme.colors import PRIMARY, TEXT
from interfaz.theme.combobox import configurar_estilo_combobox

# -----------------------------
# CONSTANTES VISUALES
# -----------------------------

FONDO_PANEL = "#0F172A"
ALTO_FILA = 24
MAXIMO_FILAS_VISIBLES = 8

# Teclas que no deben disparar el filtrado incremental.
_TECLAS_SIN_FILTRO = frozenset({
    "Left",
    "Right",
    "Up",
    "Down",
    "Return",
    "KP_Enter",
    "Tab",
    "ISO_Left_Tab",
    "Escape",
    "Home",
    "End",
    "Prior",
    "Next",
    "Shift_L",
    "Shift_R",
    "Control_L",
    "Control_R",
    "Alt_L",
    "Alt_R",
    "Caps_Lock"
})


def _normalizar(texto):
    """Normaliza texto para comparar sin distinguir mayúsculas ni acentos."""

    descompuesto = unicodedata.normalize(
        "NFKD",
        str(texto or "").casefold()
    )

    return "".join(
        caracter
        for caracter in descompuesto
        if not unicodedata.combining(caracter)
    )


class ComboBuscable(ttk.Combobox):
    """Combobox editable con sugerencias y selección explícita."""

    def __init__(self, parent, valores=None, **kwargs):

        self._valores = [
            str(valor)
            for valor in (valores or [])
        ]
        self._opciones_visibles = []
        self._indice_resaltado = -1
        self._ventana_sugerencias = None
        self._lista_sugerencias = None

        configurar_estilo_combobox(parent.winfo_toplevel())

        kwargs.setdefault("state", "normal")
        kwargs.setdefault("style", "Dark.TCombobox")

        super().__init__(parent, **kwargs)

        self["values"] = self._valores

        self.bind("<KeyRelease>", self._al_escribir, add="+")
        self.bind("<Return>", self._al_presionar_enter, add="+")
        self.bind("<KP_Enter>", self._al_presionar_enter, add="+")
        self.bind("<Down>", self._al_bajar, add="+")
        self.bind("<Up>", self._al_subir, add="+")
        self.bind("<Escape>", self._al_escape, add="+")
        self.bind("<FocusIn>", self._al_enfocar, add="+")
        self.bind("<FocusOut>", self._al_desenfocar, add="+")
        self.bind("<Button-1>", self._al_clic, add="+")
        self.bind("<<ComboboxSelected>>", self._al_seleccionar, add="+")

        for secuencia in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind(secuencia, self._bloquear_rueda, add="+")

    # -----------------------------
    # API
    # -----------------------------

    def establecer_valores(self, valores):
        """Reemplaza el catálogo completo de opciones."""

        self._valores = [
            str(valor)
            for valor in (valores or [])
        ]

        self["values"] = self._valores
        self._ocultar_sugerencias()

    def set(self, valor):
        """Fija un valor exacto y restaura todas las opciones."""

        valor = "" if valor is None else str(valor)

        ttk.Combobox.set(self, valor)

        self["values"] = self._valores
        self._ocultar_sugerencias()

    def destroy(self):
        """Elimina también el panel flotante de sugerencias."""

        if (
            self._ventana_sugerencias is not None
            and self._ventana_sugerencias.winfo_exists()
        ):

            self._ventana_sugerencias.destroy()

        super().destroy()

    # -----------------------------
    # EVENTOS DEL CAMPO
    # -----------------------------

    def _al_escribir(self, event):

        if event.keysym in _TECLAS_SIN_FILTRO:
            return

        texto = self.get()
        opciones = self._filtrar(texto)

        if texto and texto not in self._valores and opciones:

            self._mostrar_sugerencias(opciones)

        else:

            self._ocultar_sugerencias()

    def _al_presionar_enter(self, event):

        if (
            self._esta_visible()
            and 0 <= self._indice_resaltado < len(self._opciones_visibles)
        ):

            self._seleccionar_opcion(
                self._opciones_visibles[self._indice_resaltado]
            )

            return "break"

        texto = self.get().strip()

        if not texto:

            self._ocultar_sugerencias()

            return "break"

        if texto in self._valores:

            self["values"] = self._valores
            self._ocultar_sugerencias()
            self.event_generate("<<ComboboxSelected>>")

            return "break"

        opciones = self._filtrar(texto)

        if len(opciones) == 1:

            self._seleccionar_opcion(opciones[0])

            return "break"

        if opciones:

            # Varias coincidencias: no se elige ninguna automáticamente.
            self._mostrar_sugerencias(opciones)

        return "break"

    def _al_bajar(self, event):

        if not self._esta_visible():

            self._mostrar_sugerencias(
                self._filtrar(self.get())
            )

        if self._opciones_visibles:

            if self._indice_resaltado < 0:

                self._resaltar(0)

            else:

                self._resaltar(
                    min(
                        self._indice_resaltado + 1,
                        len(self._opciones_visibles) - 1
                    )
                )

        return "break"

    def _al_subir(self, event):

        if not self._esta_visible():

            self._mostrar_sugerencias(
                self._filtrar(self.get())
            )

        if self._opciones_visibles:

            if self._indice_resaltado < 0:

                self._resaltar(len(self._opciones_visibles) - 1)

            else:

                self._resaltar(max(self._indice_resaltado - 1, 0))

        return "break"

    def _al_escape(self, event):

        self._ocultar_sugerencias()

        if self.get() not in self._valores:

            self["values"] = self._valores

        return "break"

    def _al_enfocar(self, event):

        if self.get() in self._valores:

            self.selection_range(0, END)

        else:

            self["values"] = self._valores

    def _al_desenfocar(self, event):

        self._ocultar_sugerencias()

    def _al_clic(self, event):
        """Sustituye el desplegable nativo al pulsar la flecha del combo."""

        if self.identify(event.x, event.y) == "Combobox.rightdownarrow":

            self.focus_set()

            if self._esta_visible():

                self._ocultar_sugerencias()

            else:

                self._mostrar_sugerencias(
                    self._filtrar(self.get())
                )

            return "break"

        return None

    def _al_seleccionar(self, event):

        self["values"] = self._valores
        self._ocultar_sugerencias()

    def _bloquear_rueda(self, event):
        """Impide que la rueda cambie el valor seleccionado."""

        return "break"

    # -----------------------------
    # PANEL DE SUGERENCIAS
    # -----------------------------

    def _crear_panel(self):
        """Crea el toplevel y el listbox del panel de sugerencias."""

        if (
            self._ventana_sugerencias is not None
            and self._ventana_sugerencias.winfo_exists()
        ):

            return

        ventana = tk.Toplevel(self)
        ventana.withdraw()
        ventana.overrideredirect(True)
        ventana.configure(background=PRIMARY)
        ventana.attributes("-topmost", True)

        contenedor = tk.Frame(
            ventana,
            background=FONDO_PANEL,
            borderwidth=0,
            highlightthickness=0
        )
        contenedor.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        lista = tk.Listbox(
            contenedor,
            background=FONDO_PANEL,
            foreground=TEXT,
            selectbackground=PRIMARY,
            selectforeground=TEXT,
            borderwidth=0,
            highlightthickness=0,
            exportselection=False,
            activestyle="none",
            takefocus=0,
            font=("Inter", 12)
        )
        barra = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=lista.yview,
            style="Dark.Vertical.TScrollbar"
        )
        lista.configure(yscrollcommand=barra.set)

        lista.pack(
            side="left",
            fill="both",
            expand=True
        )
        barra.pack(
            side="right",
            fill="y"
        )

        # El clic no mueve el foco; la selección se resuelve al soltar.
        lista.bind("<ButtonPress-1>", self._al_presionar_sugerencia)
        lista.bind("<ButtonRelease-1>", self._al_soltar_sugerencia)
        lista.bind("<MouseWheel>", self._al_rodar_sugerencias)
        lista.bind("<Button-4>", self._al_rodar_sugerencias)
        lista.bind("<Button-5>", self._al_rodar_sugerencias)

        self._ventana_sugerencias = ventana
        self._lista_sugerencias = lista

    def _mostrar_sugerencias(self, opciones):
        """Muestra el panel con las opciones indicadas."""

        opciones = list(opciones or [])

        if not opciones:

            self._ocultar_sugerencias()

            return

        self._crear_panel()

        self._opciones_visibles = opciones
        self._indice_resaltado = -1

        self._lista_sugerencias.delete(0, END)

        for opcion in opciones:

            self._lista_sugerencias.insert(END, opcion)

        self._lista_sugerencias.selection_clear(0, END)

        self._posicionar_panel()
        self._ventana_sugerencias.deiconify()
        self._ventana_sugerencias.lift()
        self.focus_set()

    def _posicionar_panel(self):
        """Coloca el panel justo debajo del campo, o encima si no cabe."""

        self.update_idletasks()

        ancho = max(self.winfo_width(), 180)
        filas = max(
            1,
            min(len(self._opciones_visibles), MAXIMO_FILAS_VISIBLES)
        )
        alto = filas * ALTO_FILA + 4
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()

        if y + alto > self.winfo_screenheight():

            y = self.winfo_rooty() - alto

        self._ventana_sugerencias.geometry(
            f"{ancho}x{alto}+{x}+{y}"
        )

    def _ocultar_sugerencias(self):
        """Oculta el panel sin confirmar ninguna opción."""

        self._indice_resaltado = -1
        self._opciones_visibles = []

        if (
            self._ventana_sugerencias is not None
            and self._ventana_sugerencias.winfo_exists()
        ):

            self._ventana_sugerencias.withdraw()

    def _esta_visible(self):
        """Indica si el panel de sugerencias está desplegado."""

        return bool(
            self._ventana_sugerencias is not None
            and self._ventana_sugerencias.winfo_exists()
            and self._ventana_sugerencias.winfo_ismapped()
        )

    def _resaltar(self, indice):
        """Resalta una sugerencia sin modificar el texto del campo."""

        if not self._opciones_visibles:
            return

        indice = max(0, min(indice, len(self._opciones_visibles) - 1))
        self._indice_resaltado = indice

        self._lista_sugerencias.selection_clear(0, END)
        self._lista_sugerencias.selection_set(indice)
        self._lista_sugerencias.activate(indice)
        self._lista_sugerencias.see(indice)

    def _al_presionar_sugerencia(self, event):
        """Evita que el listbox robe el foco al hacer clic."""

        return "break"

    def _al_soltar_sugerencia(self, event):
        """Confirma la sugerencia sobre la que se soltó el clic."""

        if not self._opciones_visibles:
            return "break"

        indice = self._lista_sugerencias.nearest(event.y)

        if 0 <= indice < len(self._opciones_visibles):

            self._seleccionar_opcion(
                self._opciones_visibles[indice]
            )

        return "break"

    def _al_rodar_sugerencias(self, event):
        """Desplaza la vista del panel sin alterar la selección."""

        if event.num == 4:

            self._lista_sugerencias.yview_scroll(-1, "units")

        elif event.num == 5:

            self._lista_sugerencias.yview_scroll(1, "units")

        else:

            paso = -1 if event.delta > 0 else 1
            self._lista_sugerencias.yview_scroll(paso, "units")

        return "break"

    def _seleccionar_opcion(self, opcion):
        """Confirma una opción concreta y notifica al resto de la vista."""

        ttk.Combobox.set(self, opcion)
        self["values"] = self._valores
        self._ocultar_sugerencias()
        self.event_generate("<<ComboboxSelected>>")

    # -----------------------------
    # FILTRADO
    # -----------------------------

    def _filtrar(self, consulta):
        """Actualiza las opciones del combo y devuelve las coincidencias."""

        texto = _normalizar(consulta)

        filtrados = [
            valor
            for valor in self._valores
            if not texto or texto in _normalizar(valor)
        ]

        self["values"] = filtrados

        return filtrados
