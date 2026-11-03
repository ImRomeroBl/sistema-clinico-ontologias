"""Panel visual reutilizable para alertas semánticas de medicamentos.

Recibe el diccionario devuelto por obtener_alertas_medicamento() y actualiza
color, título y detalle. No accede a la ontología ni contiene lógica de negocio.
"""

import customtkinter as ctk

from interfaz.theme.colors import BACKGROUND, DANGER, TEXT, WARNING

# -----------------------------
# CONTRATO VISUAL
# -----------------------------

COLORES_FONDO = {
    "red": DANGER,
    "orange": WARNING,
    "gray": "#6B7280",
}

COLORES_TEXTO = {
    "red": TEXT,
    "orange": BACKGROUND,
    "gray": TEXT,
}

TITULOS = {
    "Alta": "● ALERTA ALTA",
    "Media": "● ALERTA MEDIA",
    "Sin alerta": "● SIN ALERTA",
}

MENSAJE_SIN_SELECCION = "Seleccione un medicamento para ver sus alertas."


def formatear_detalle_alerta(alerta):
    """Construye el detalle legible de contraindicaciones y efectos."""
    lineas = []

    contraindicaciones = alerta.get("contraindicaciones") or []
    efectos_secundarios = alerta.get("efectos_secundarios") or []

    if contraindicaciones:
        lineas.append(
            "Contraindicaciones: "
            + ", ".join(str(item) for item in contraindicaciones)
        )

    if efectos_secundarios:
        lineas.append(
            "Efectos secundarios: "
            + ", ".join(str(item) for item in efectos_secundarios)
        )

    if not lineas:
        lineas.append(
            "No se registraron contraindicaciones ni efectos secundarios."
        )

    return "\n".join(lineas)


class PanelAlertasMedicamento(ctk.CTkFrame):
    """Marco dinámico con el nivel y el detalle de alerta de un medicamento."""

    def __init__(
        self,
        parent,
        mensaje_sin_seleccion=MENSAJE_SIN_SELECCION,
        **kwargs
    ):

        kwargs.setdefault("fg_color", COLORES_FONDO["gray"])
        kwargs.setdefault("corner_radius", 10)

        super().__init__(parent, **kwargs)

        self._mensaje_sin_seleccion = mensaje_sin_seleccion

        self.grid_columnconfigure(0, weight=1)

        self.titulo = ctk.CTkLabel(
            self,
            text=TITULOS["Sin alerta"],
            font=("Inter", 13, "bold"),
            text_color=TEXT,
            anchor="w"
        )
        self.titulo.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(8, 0)
        )

        self.detalle = ctk.CTkLabel(
            self,
            text=self._mensaje_sin_seleccion,
            font=("Inter", 12),
            text_color=TEXT,
            anchor="w",
            justify="left",
            wraplength=520
        )
        self.detalle.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(2, 8)
        )

        self.bind("<Configure>", self._ajustar_ancho)

    def _ajustar_ancho(self, event):
        """Adapta el ajuste de línea al ancho real del panel."""
        self.detalle.configure(
            wraplength=max(240, event.width - 24)
        )

    def mostrar(self, alerta):
        """Actualiza el panel con un diccionario de alertas."""
        nivel = alerta.get("nivel", "Sin alerta")
        color = alerta.get("color", "gray")

        self.configure(
            fg_color=COLORES_FONDO.get(color, COLORES_FONDO["gray"])
        )

        color_texto = COLORES_TEXTO.get(color, TEXT)

        self.titulo.configure(
            text=TITULOS.get(nivel, TITULOS["Sin alerta"]),
            text_color=color_texto
        )
        self.detalle.configure(
            text=formatear_detalle_alerta(alerta),
            text_color=color_texto
        )

    def limpiar(self, mensaje=None):
        """Restablece el panel al estado sin selección."""
        self.configure(fg_color=COLORES_FONDO["gray"])
        self.titulo.configure(
            text=TITULOS["Sin alerta"],
            text_color=TEXT
        )
        self.detalle.configure(
            text=mensaje or self._mensaje_sin_seleccion,
            text_color=TEXT
        )
