# Sistema Clínico Basado en Ontologías
Repositorio que contiene el código fuente en Python y el archivo ontológico `clinica.owl` desarrollado en Protégé para la gestión de recetas médicas.

## Mantenimiento de la ontología

La arquitectura es Encounter-Centric: toda receta debe depender de una consulta
existente. Para auditar o depurar registros residuales:

```powershell
# Solo lectura: informe de integridad
python -m logica.mantenimiento

# Limpieza idempotente con respaldo automático en backups/
python -c "from logica.mantenimiento import depurar_ontologia; print(depurar_ontologia())"
```

La depuración elimina recetas sin consulta, citas incompletas y diagnósticos o
estudios huérfanos; migra los textos legados de contraindicaciones, efectos
secundarios y especialidades a Object Properties; y retira las antiguas
propiedades de datos que ya no usa el sistema.
