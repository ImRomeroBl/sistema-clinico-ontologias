from interfaz.app import crear_interfaz
from logica.language_manager import t
from logica.ontologia import onto

# -------------------------
# MOSTRAR DATOS EN CONSOLA
# -------------------------

print(t("main.console.patients"))

for paciente in onto.Paciente.instances():
    print(paciente)

# -------------------------

print("\n" + t("main.console.doctors"))

for medico in onto.Medico.instances():
    print(medico)

# -------------------------

print("\n" + t("main.console.appointments"))

for cita in onto.Cita.instances():
    print(cita)

# -------------------------

print("\n" + t("main.console.prescriptions"))

for receta in onto.Receta.instances():
    print(receta)

# -------------------------

print("\n" + t("main.console.medications"))

for medicamento in onto.Medicamento.instances():
    print(medicamento)

# -------------------------
# RELACIONES
# -------------------------

print("\n" + t("main.console.relations"))

# Paciente -> Cita
for paciente in onto.Paciente.instances():

    if hasattr(paciente, "tieneCita"):

        for cita in paciente.tieneCita:
            print(t("main.relations.patient_appointment").format(
                patient=paciente,
                appointment=cita
            ))

# -------------------------

# Medico -> Cita
for medico in onto.Medico.instances():

    if hasattr(medico, "atiende"):

        for cita in medico.atiende:
            print(t("main.relations.doctor_appointment").format(
                doctor=medico,
                appointment=cita
            ))

# -------------------------

# Receta -> Medicamento
for receta in onto.Receta.instances():

    if hasattr(receta, "incluyeMedicamento"):

        for medicamento in receta.incluyeMedicamento:
            print(t("main.relations.prescription_medication").format(
                prescription=receta,
                medication=medicamento
            ))

# -------------------------
# EJECUTAR INTERFAZ
# -------------------------

ventana = crear_interfaz()

ventana.mainloop()
