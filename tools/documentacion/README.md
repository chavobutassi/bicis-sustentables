# Herramientas de documentación

Estos scripts Python son auxiliares históricos de la maqueta documental. No forman parte del backend, no se ejecutan desde Gradle y no son necesarios para iniciar Turismo Sustentable.

| Script | Función |
| --- | --- |
| `build_practica3_docx.py` | Genera la maqueta inicial del informe de Prácticas III. |
| `enrich_practica3_methodology.py` | Agrega secciones de metodología a esa maqueta. |
| `fix_practica3_docx_numbering.py` | Ajusta listas y numeración de esa maqueta. |

Requieren Python y `python-docx`. Resuelven la carpeta del proyecto a partir de la ubicación del script, no de la carpeta desde la que se ejecutan.

## Precauciones

- Los tres trabajan sobre `docs/practica-3/Maqueta_Documentacion_Practica_3.docx`.
- El generador sobrescribe ese archivo. Los otros dos lo modifican; el agregado de metodología no está preparado para repetirse sin duplicar secciones.
- Antes de ejecutarlos, guardar una copia del Word y cerrar el documento en el editor. No ejecutarlos sobre un informe actualizado que se quiera conservar sin cambios.
- No generan el DER v5 ni el diccionario de estados actualizado y no reemplazan las reglas aprobadas de `docs/practica-3/refactorizacion/`.

El 2 de noviembre de 2026 se trasladaron desde la raíz del repositorio y se ajustaron sus rutas. Se comprobó la sintaxis sin ejecutarlos ni regenerar documentos.
