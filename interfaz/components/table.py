from tkinter import BOTH, LEFT, RIGHT, Frame, Y, ttk

from interfaz.theme.colors import PRIMARY

# --------------------------------
# TABLA MODERNA
# --------------------------------

def crear_tabla(
    parent,
    columnas,
    altura=12
):

    # -----------------------------
    # ESTILOS
    # -----------------------------

    style = ttk.Style()

    style.theme_use("default")

    # -----------------------------
    # TREEVIEW GENERAL
    # -----------------------------

    style.configure(

        "Modern.Treeview",

        background="#0F172A",
        foreground="white",

        fieldbackground="#0F172A",

        borderwidth=0,
        rowheight=38,

        font=("Inter", 12)
    )

    # -----------------------------
    # HEADER
    # -----------------------------

    style.configure(

        "Modern.Treeview.Heading",

        background="#1E293B",
        foreground="white",

        relief="flat",

        font=("Inter", 12, "bold"),

        padding=10
    )

    # -----------------------------
    # HOVER HEADER
    # -----------------------------

    style.map(

        "Modern.Treeview.Heading",

        background=[("active", PRIMARY)]
    )

    # -----------------------------
    # SELECCION
    # -----------------------------

    style.map(

        "Modern.Treeview",

        background=[("selected", PRIMARY)],
        foreground=[("selected", "white")]
    )

    # -----------------------------
    # FRAME CONTENEDOR
    # -----------------------------

    frame = Frame(
        parent,
        bg="#0F172A"
    )

    # -----------------------------
    # TREEVIEW
    # -----------------------------

    tabla = ttk.Treeview(

        frame,

        columns=columnas,

        show="headings",

        height=altura,

        style="Modern.Treeview"
    )

    # -----------------------------
    # CONFIGURAR COLUMNAS
    # -----------------------------

    for columna in columnas:

        tabla.heading(
            columna,
            text=columna
        )

        tabla.column(
            columna,
            anchor="center",
            width=180
        )

    # -----------------------------
    # SCROLLBAR
    # -----------------------------

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tabla.yview
    )

    tabla.configure(
        yscrollcommand=scrollbar.set
    )

    # -----------------------------
    # PACK
    # -----------------------------

    tabla.pack(
        side=LEFT,
        fill=BOTH,
        expand=True
    )

    scrollbar.pack(
        side=RIGHT,
        fill=Y
    )

    # -----------------------------
    # RETORNAR
    # -----------------------------

    return frame, tabla