# Documentación de Prácticas III

## Ubicaciones

- [Refactorización](refactorizacion/00-indice-y-estado.md): decisiones, reglas de negocio y estado de avance. El modelo de trabajo es [der-v5-propuesto.mmd](refactorizacion/der-v5-propuesto.mmd).
- [Entregables](entregables/): DER v5 exportado en TXT y diccionario de estados actualizado en Word.
- Los Word de esta carpeta conservan la maqueta del informe y los manuales de Git/GitHub para trabajar en equipo.
- `muestra-anual/`: presentación y recursos de la muestra de carreras; se conservan como material histórico, no como especificación vigente.
- [Herramientas de documentación](../../tools/documentacion/README.md): scripts auxiliares separados del código de la aplicación.

Las reglas aprobadas para implementar no deben confundirse con funcionalidades ya implementadas o probadas en Java.

## Organización del 2 de noviembre de 2026

Se trasladaron los scripts útiles de documentación a `tools/documentacion/`. Las vistas previas `.render-check*`, la prueba `.codex-write-test` y los dos scripts mínimos de prueba `generate_documentation_mockup*.py` se apartaron a `.local-artifacts/limpieza-2026-11-02/`, dentro de la raíz del proyecto. Ese respaldo conserva las rutas de origen y queda excluido de Git y del contexto Docker; no hay borrado permanente.

Se conservaron el código, los documentos finales, el DER, el diccionario de estados, la presentación, `.git/`, `gradle/wrapper/`, las carpetas de IntelliJ, `build/` y `.gradle/`. No se inició la aplicación, no se ejecutaron migraciones y no se modificaron bases de datos. La organización de archivos no implementa la refactorización del backend.
