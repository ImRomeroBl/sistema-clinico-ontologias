"""Combobox editable con filtrado incremental para selección de pacientes."""

import unicodedata
from tkinter import END, TclError, ttk

from interfaz.theme.colors import PRIMARY, TEXT
from interfaz.theme.combobox import configurar_estilo_combobox


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
    """Combobox que filtra sus opciones mientras el usuario escribe.

    El campo permanece editable y conserva el foco mientras se teclea. La
    lista desplegable se abre con la flecha o con la tecla Abajo y muestra
    únicamente las coincidencias. Enter selecciona la primera coincidencia.
    """

    _TECLAS_NAVEGACION = frozenset({
        "Up",
        "Down",
        "Left",
        "Right",
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

    def __init__(self, parent, valores=None, **kwargs):

        self._valores = [
            str(valor)
            for valor in (valores or [])
        ]

        configurar_estilo_combobox(parent.winfo_toplevel())

        kwargs.setdefault("state", "normal")
        kwargs.setdefault("style", "Dark.TCombobox")

        super().__init__(parent, **kwargs)

        self["values"] = self._valores

        self.configure(postcommand=self._preparar_lista)

        self.bind("<KeyRelease>", self._al_escribir, add="+")
        self.bind("<Return>", self._al_presionar_enter, add="+")
        self.bind("<KP_Enter>", self._al_presionar_enter, add="+")
        self.bind("<FocusIn>", self._al_enfocar, add="+")
        self.bind("<<ComboboxSelected>>", self._al_seleccionar, add="+")

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

    def set(self, valor):
        """Fija un valor exacto y restaura todas las opciones."""

        valor = "" if valor is None else str(valor)

        ttk.Combobox.set(self, valor)

        self["values"] = self._valores

    # -----------------------------
    # EVENTOS
    # -----------------------------

    def _preparar_lista(self):
        """Filtra y estiliza la lista justo antes de desplegarla."""

        if self.get() in self._valores:

            self["values"] = self._valores

        else:

            self._filtrar(self.get())

        self._estilizar_lista()
        self.after_idle(self._estilizar_lista)

    def _estilizar_lista(self):
        """Aplica la paleta oscura al listbox interno del combobox."""

        try:

            popdown = self.tk.call(
                "ttk::combobox::PopdownWindow",
                self._w
            )
            listbox = f"{popdown}.f.l"

            self.tk.call(
                listbox,
                "configure",
                "-background", "#0F172A",
                "-foreground", TEXT,
                "-selectbackground", PRIMARY,
                "-selectforeground", TEXT,
                "-borderwidth", 0,
                "-highlightthickness", 0,
                "-font", "Inter 12"
            )

            self.tk.call(
                popdown,
                "configure",
                "-background", "#0F172A"
            )

            self.tk.call(
                f"{popdown}.f.sb",
                "configure",
                "-style", "Dark.Vertical.TScrollbar"
            )

        except TclError:

            pass

    def _al_escribir(self, event):

        if event.keysym in self._TECLAS_NAVEGACION:
            return

        self._filtrar(self.get())

    def _al_enfocar(self, event):

        if self.get() in self._valores:

            self.selection_range(0, END)

        else:

            self["values"] = self._valores

    def _al_seleccionar(self, event):

        self["values"] = self._valores

    def _al_presionar_enter(self, event):

        if not self.get():
            return "break"

        if self.get() in self._valores:

            self["values"] = self._valores
            self.event_generate("<<ComboboxSelected>>")

            return "break"

        filtrados = self._opciones_actuales()

        if not filtrados:
            return "break"

        self.set(filtrados[0])
        self.event_generate("<<ComboboxSelected>>")

        return "break"

    # -----------------------------
    # FILTRADO
    # -----------------------------

    def _filtrar(self, consulta):

        texto = _normalizar(consulta)

        filtrados = [
            valor
            for valor in self._valores
            if not texto or texto in _normalizar(valor)
        ]

        self["values"] = filtrados

    def _opciones_actuales(self):

        actuales = self["values"]

        if isinstance(actuales, str):
            return [actuales] if actuales else []

        return list(actuales)
