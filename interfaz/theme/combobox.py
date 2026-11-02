"""Estilos compartidos para los combos de la interfaz."""

from tkinter import ttk

from interfaz.theme.colors import BORDER, PRIMARY, TEXT, TEXT_SECONDARY


def configurar_estilo_combobox(root):
    """Aplica la paleta oscura a los combos y a sus listas desplegables."""

    style = ttk.Style(root)

    style.configure(
        "Dark.TCombobox",
        fieldbackground="#0F172A",
        background="#0F172A",
        foreground=TEXT,
        arrowcolor=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        selectbackground=PRIMARY,
        selectforeground=TEXT,
        insertcolor=TEXT,
        padding=6
    )

    style.map(
        "Dark.TCombobox",
        fieldbackground=[
            ("readonly", "#0F172A"),
            ("disabled", "#0F172A")
        ],
        foreground=[
            ("readonly", TEXT),
            ("disabled", TEXT_SECONDARY)
        ],
        background=[("active", "#0F172A")],
        selectbackground=[("readonly", PRIMARY)],
        selectforeground=[("readonly", TEXT)]
    )

    style.configure(
        "Dark.Vertical.TScrollbar",
        background="#1E293B",
        troughcolor="#0F172A",
        bordercolor="#0F172A",
        arrowcolor=TEXT
    )

    style.map(
        "Dark.Vertical.TScrollbar",
        background=[("active", PRIMARY)]
    )

    root.option_add("*TCombobox*Listbox.background", "#0F172A")
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
    root.option_add("*TCombobox*Listbox.selectForeground", TEXT)
