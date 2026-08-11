from interfaz.app import ventana
from logica.ontologia import onto

# -------------------------
# MOSTRAR DATOS EN CONSOLA
# -------------------------

print("=== PACIENTES ===")

for paciente in onto.Paciente.instances():
    print(paciente)

# -------------------------

print("\n=== MEDICOS ===")

for medico in onto.Medico.instances():
    print(medico)

# -------------------------

print("\n=== CITAS ===")

for cita in onto.Cita.instances():
    print(cita)

# -------------------------

print("\n=== RECETAS ===")

for receta in onto.Receta.instances():
    print(receta)

# -------------------------

print("\n=== MEDICAMENTOS ===")

for medicamento in onto.Medicamento.instances():
    print(medicamento)

# -------------------------
# RELACIONES
# -------------------------

print("\n=== RELACIONES ===")

# Paciente -> Cita
for paciente in onto.Paciente.instances():

    if hasattr(paciente, "tieneCita"):

        for cita in paciente.tieneCita:
            print(f"{paciente} tiene la cita {cita}")

# -------------------------

# Medico -> Cita
for medico in onto.Medico.instances():

    if hasattr(medico, "atiende"):

        for cita in medico.atiende:
            print(f"{medico} atiende la cita {cita}")

# -------------------------

# Receta -> Medicamento
for receta in onto.Receta.instances():

    if hasattr(receta, "incluyeMedicamento"):

        for medicamento in receta.incluyeMedicamento:
            print(f"{receta} incluye {medicamento}")

# -------------------------
# EJECUTAR INTERFAZ
# -------------------------

ventana.mainloop()