# Trazabilidad de incidencias reportes y órdenes

Fecha de revisión: 1 de noviembre de 2026.

Estado actualizado al 2 de noviembre: D07-A, incidencia_corte_id, fue aprobada e incorporada al DER lógico mediante RN-TRZ-01. D07-B, HISTORIAL_ATENCION_MANTENIMIENTO, sigue descartado; sus campos/casos son antecedentes, no tareas a implementar. La estructura vigente está en el [documento 36](36-incorporacion-aprobada-trazabilidad-der.md): historial de incidencia, ampliación/renombre del historial de orden, motivo administrativo y FK del corte, con 29 entidades/55 relaciones. No se modifican Java o la base ni los estados, permisos o cálculo aprobados.

AUDITORIA_SISTEMA queda exclusivamente para ADMIN, conforme al [documento 35](35-auditoria-admin-y-brechas-de-trazabilidad.md). Las menciones siguientes a auditoría general de técnicos/sistema o al historial descartado son antecedentes sustituidos, no cobertura vigente. RN-TRZ-01 incorpora los historiales aprobados sin reactivar D07-B.

El modelo previo a RN-TRZ-01 tenía 28 entidades y 52 FK/relaciones. El vigente tiene 29 y 55: dos FK del historial de incidencia y una del corte, sin cinco relaciones del historial de atención descartado. El paso inicialmente propuesto a 29/58 no se adoptó. No se incorporan entidades de tarjetas, descartadas en RN-PAG-05.

## 1. Fuentes y alcance

Se contrastaron los objetivos y requerimientos de mantenimiento, auditoría y consistencia de las páginas 3 a 5 del [PDF original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), las órdenes y roles del [diccionario original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y las entidades de orden, detalle, historial y auditoría del [DER v4](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>). Los originales se conservan intactos.

Se revisaron también [RN-MAN-03](18-generacion-y-organizacion-ordenes.md), [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md), la [revisión de mantenimiento](27-revision-ordenes-e-historial-mantenimiento.md), la [revisión de alquiler](28-revision-alquiler-y-detalles.md) y el Mermaid vigente. Las dos mejoras son decisiones de representación propuestas por esta revisión, no tablas exigidas literalmente por el PDF.

## 2. Hechos que deben seguir separados

| Hecho | Representación vigente | Qué no significa por sí solo |
| --- | --- | --- |
| Falla comunicada al devolver | Campos de reporte de ALQUILER_DETALLE con descripción, fecha y autor | No demuestra avería, culpa, corte anterior al regreso ni cargo por daños |
| Incidente durante el viaje | INCIDENCIA, con registro, revisión administrativa y fechas propias | No congela el cobro unilateralmente ni constituye un diagnóstico técnico |
| Trabajo de taller | ORDEN_MANTENIMIENTO, con tipo, técnico, diagnóstico, trabajo y resultado | No es la revisión administrativa del costo ni habilita automáticamente la bicicleta |
| Evolución de una orden | HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO | No identifica por sí solo todos los cambios de vinculación de reportes |
| Modificaciones sin transición de estado | AUDITORIA_SISTEMA, con valores permitidos anteriores/nuevos, actor y fecha | Su mera existencia no prueba que los eventos se registren completos o tengan FK históricas |

La devolución con falla detiene el tiempo y sigue RN-MAN-03. La incidencia previa de efecto económico puede dejar el costo provisional hasta su decisión, aunque ya se haya devuelto. La reparación técnica no prolonga el cobro ni obliga a esperar para liquidar cuando el único pendiente es de taller. Los repuestos internos no se imputan automáticamente al cliente.

Si se avisa durante el viaje y después se devuelve, la incidencia no se borra ni se transforma en un simple checkbox de la devolución. Si además se registra un reporte al devolver, se conservan ambos hechos y pueden atenderse mediante la misma orden, sin duplicar órdenes abiertas ni ajustes económicos.

## 3. Hallazgos del modelo lógico vigente

### Fundamento del corte económico

ALQUILER_DETALLE conserva fecha_hora_fin_uso y sus costos; INCIDENCIA apunta al detalle y conserva su decisión/corte validado. Sin embargo, el detalle no referencia directamente cuál incidencia fundamentó el corte aplicado. Como admite varias incidencias, buscar una por coincidencia de fechas o tomar la última no constituye una relación inequívoca.

RN-INC-01 ya exige un vínculo con la decisión y un solo cierre autorizado por detalle. Precisar esa referencia no agrega un tipo de incidente, otra liquidación o una nueva autorización para modificar el costo.

### Historia de atención de un reporte

ALQUILER_DETALLE.orden_mantenimiento_id e INCIDENCIA.orden_mantenimiento_id representan el enlace operativo actual o último. Si una orden se cancela y se reemplaza, cambiar esas FK no conserva por sí solo el enlace anterior. Conservar todas las órdenes tampoco permite saber automáticamente qué reporte pasó por cada una.

El diseño compacto ya prevé auditar el cambio anterior/nuevo. Una auditoría completa y consultable podría satisfacer la trazabilidad sin agregar una tabla; no se presenta como inútil. Su límite es que entidad_id y valores_anteriores/nuevos de la auditoría son referencias contextuales, no FK directas a reportes y órdenes. Para conservar esas relaciones explícitamente y facilitar su consulta, se recomienda el historial específico siguiente.

## 4. D07-A aprobada Incidencia que fundamenta el corte

Se incorporó incidencia_corte_id a ALQUILER_DETALLE como int, FK opcional a INCIDENCIA.id y UNIQUE cuando tenga valor. Una incidencia puede fundamentar el corte aplicado de cero o un detalle; cada detalle tiene cero o una incidencia determinante. No se declara UNIQUE alquiler_detalle_id en INCIDENCIA: el detalle sigue admitiendo varios reportes históricos.

La FK se asigna solo si una decisión validada fundamenta el corte excepcional/anticipado aplicado, y debe corresponder al mismo detalle que referencia la incidencia. No se recibe libremente desde el formulario ni se determina tomando la primera o última incidencia. Las condiciones de pertenencia y de decisión se comprueban transaccionalmente; la unicidad por sí sola no las garantiza.

- En CERRADO_POR_INCIDENCIA identifica la decisión que fundamenta el cierre y su corte, sin simular una devolución.
- En DEVUELTO puede identificar una incidencia previa cuyo corte anterior fue validado. Se conserva DEVUELTO y la fecha física de recepción; no se vuelve a cerrar el uso para guardar la decisión económica.
- En un regreso normal sin corte por incidencia, la referencia queda nula y rige la recepción. Revisar o descartar un reporte no obliga a completar esta FK.
- Una incidencia puramente técnica o una orden de mantenimiento no adquieren efecto económico por estar relacionadas con la bicicleta.

El corte aplicado del detalle debe ser coherente con la decisión referenciada y no extender tiempo después de una recepción ya registrada. Los demás reportes se conservan, cada uno con su revisión; no se descartan solo para dejar una referencia determinante. La liquidación sigue esperando todas las revisiones que puedan afectar su importe.

Esta FK no autoriza sustituir libremente decisiones/costos ya validados ni introduce ajustes posteriores a una liquidación definitiva. Cierre, revisión y liquidación se coordinan para evitar dos cierres o aplicaciones incompatibles; los cambios permitidos conservan auditoría. El detalle puede existir antes que la incidencia porque la nueva FK es opcional y solo se completa al resolver; la FK existente de INCIDENCIA al detalle se mantiene.

## 5. Propuesta D07-B de historial de atención

Antecedente descartado por ahora el 2 de noviembre. La propuesta siguiente no se incorpora ni se considera pendiente de implementación. Se mantiene la auditoría completa de las asociaciones, conforme al [documento 34](34-trazabilidad-ordenes-e-incidencias.md).

Se propone HISTORIAL_ATENCION_MANTENIMIENTO. Registra la primera asociación real de un reporte a una orden y sus reemplazos posteriores. No es otro historial de estados ni una copia del diagnóstico. Se mantienen las dos FK operativas actuales, con el mismo patrón de dato vigente más historia ya utilizado en pagos y órdenes.

| Campo propuesto | Tipo lógico y clave | Condición |
| --- | --- | --- |
| id | int, PK | Identificador del evento |
| alquiler_detalle_id | int, FK a ALQUILER_DETALLE.id | Solo para un reporte de falla al devolver; nulo cuando la fuente es una incidencia |
| incidencia_id | int, FK a INCIDENCIA.id | Solo para un reporte durante el viaje; nulo cuando la fuente es el reporte de devolución |
| orden_anterior_id | int, FK a ORDEN_MANTENIMIENTO.id | Nulo únicamente en la primera asociación; luego coincide con el enlace que se reemplaza |
| orden_nueva_id | int, FK a ORDEN_MANTENIMIENTO.id | Obligatorio; orden a la que queda asociado el reporte |
| fecha_hora_cambio | datetime | Registro del evento por el backend; no reemplaza la fecha original del reporte |
| actor_usuario_id | int, FK a USUARIO.id | Obligatorio para una acción humana; nulo solo para origen SISTEMA |
| origen | string | USUARIO o SISTEMA, determinado por el backend |
| motivo | text | Explica la asociación automática o el reemplazo autorizado; no vacío |

Exactamente una de alquiler_detalle_id e incidencia_id debe tener valor. Si se referencia una incidencia, su detalle y bicicleta se obtienen a través de ella: no se completa también alquiler_detalle_id para duplicar ese origen. Si se referencia directamente el detalle debe existir el reporte de devolución correspondiente. Esta exclusión se concretará en restricciones físicas y validaciones, no en la apariencia del diagrama.

Se proponen cinco relaciones desde el historial: fuente de devolución opcional, fuente de incidencia opcional, orden anterior opcional, orden nueva obligatoria y actor opcional solo para SISTEMA. Cada fuente u orden puede aparecer en varios eventos históricos; no se declara UNIQUE global sobre esos identificadores. Cada fila tiene una sola fuente efectiva por la exclusión indicada.

No se añaden bicicleta_id, alquiler_id, técnico actual o estado de la orden en cada evento: se consultan por sus relaciones. El evento registra quién cambió el enlace, no quién está actualmente asignado a la orden. Una creación automática conserva origen SISTEMA y no inventa un ADMIN; el autor del reporte permanece en su fuente.

### Consistencia de dato vigente e historial

La primera asociación registra orden_anterior_id nulo. En un reemplazo, la orden anterior debe coincidir con la FK operativa actual y la nueva ser distinta. La actualización del enlace y la inserción de historia se confirman en una misma transacción local. Si una parte falla no queda un cambio parcial. La nueva orden debe pertenecer a la misma bicicleta y estar habilitada para recibir la atención conforme al recorrido aprobado.

Las filas se añaden y no se editan o borran desde el ABM normal. Una petición repetida que no cambia el enlace no inventa otro evento de asociación; su recepción técnica puede auditarse. Las operaciones concurrentes deben coordinar el reporte, la bicicleta y las órdenes para conservar un enlace coherente y como máximo una orden abierta por unidad.

Cancelar o finalizar una orden no vacía automáticamente las FK del reporte. Pueden seguir mostrando su última orden asociada, ahora cerrada. El cambio de estado ya queda en el historial de esa orden. Si corresponde una sustituta real, se registra el cambio de enlace; no se reabre ni se elimina la anterior. Mantener una referencia a una orden cerrada no significa que siga abierta o trabajando.

Este historial no autoriza desvincular arbitrariamente una falla sin atención, moverla a otra bicicleta ni eludir permisos. ADMIN conserva las acciones administrativas y el sistema las asociaciones automáticas previstas. TECNICO no obtiene por esta tabla facultad para cancelar/reclasificar órdenes o modificar el corte del alquiler.

## 6. Ejemplo de lectura

Un reporte queda asociado a la orden 20. ADMIN realiza el recorrido autorizado de cancelación con motivo y creación de la orden sustituta 21. El enlace actual del reporte apunta a 21, pero la historia conserva:

| Evento | Orden anterior | Orden nueva | Autor u origen | Motivo |
| --- | --- | --- | --- | --- |
| Asociación inicial | Sin orden | 20 | SISTEMA si fue automática | Atención del reporte recibido |
| Reemplazo | 20 | 21 | ADMIN que lo autorizó | Motivo real de la sustitución |

La orden 20 conserva su cancelación y trabajo/costos registrados; la 21 tiene su propio recorrido. El reporte no se borra ni se convierte en uno nuevo para ocultar el cambio. Si existía una incidencia que fundamentó el corte económico, sustituir la orden no cambia esa decisión, el tiempo de uso ni el dinero.

## 7. Reglas que no se modifican ni se duplican

- Reporte, diagnóstico técnico y decisión administrativa siguen siendo hechos distintos. DESCARTADA respecto del cierre económico no equivale a declarar la bicicleta apta ni a negar necesariamente una falla.
- Una bicicleta conserva como máximo una orden abierta. Varios reportes pueden compartirla; un nuevo reporte no cambia automáticamente PREVENTIVO a CORRECTIVO.
- Una orden preventiva por calendario o una manual puede no tener reportes de alquiler. No se crea una incidencia ficticia para justificarla.
- Una incidencia de pérdida/robo puede no tener aún una orden. La ausencia de orden no impide conservar su reporte, decisión y recuperación; no se finge trabajo sobre una unidad ausente.
- HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO conserva los estados. HISTORIAL_ATENCION_MANTENIMIENTO conservaría las asociaciones. Las reasignaciones de técnico y cambios de trabajo/diagnóstico/costos siguen en auditoría, sin transiciones ficticias.
- AUDITORIA_SISTEMA también debe conservar registro/revisión/recepción de INCIDENCIA, decisiones y cambios permitidos con anterior/nuevo, responsable y fecha. No se propone otro historial de incidencia por esta revisión ni se declara que sus campos actuales basten por sí solos para toda la trazabilidad.
- Las consultas y acciones respetan propiedad y roles ya aprobados. La existencia de historia no habilita a clientes a consultar reportes ajenos ni a modificar órdenes o decisiones.

La precisión SQL y las cronologías adicionales pendientes siguen en D06. El límite adicional de corte no posterior al registro del reporte, que figura expresamente como propuesta en RN-INC-01, no se da por aprobado mediante la incorporación de una FK.

## 8. Criterios de aceptación propuestos

Son especificaciones pendientes de implementación y ejecución:

| Caso | Escenario | Resultado esperado si se aprueban los refuerzos |
| --- | --- | --- |
| CP-TRZ-02-01 | Varios incidentes pertenecen a un detalle | Se conservan todos y se identifica inequívocamente el que fundamenta el corte aplicado, cuando existe |
| CP-TRZ-02-02 | Se intenta asociar el corte a una incidencia de otro detalle o sin decisión válida | Rechazo sin alterar uso, costo, estado o liquidación |
| CP-TRZ-02-03 | Se valida un corte anterior después de la devolución física | Sigue DEVUELTO, conserva recepción real y referencia la decisión aplicable sin otro cierre |
| CP-TRZ-02-04 | Se asocia por primera vez un reporte a una orden | Se guarda el enlace vigente y un evento inicial, de forma atómica |
| CP-TRZ-02-05 | Se reemplaza una orden por el recorrido autorizado | Se conserva la orden anterior y el cambio anterior/nuevo con autor, fecha y motivo |
| CP-TRZ-02-06 | El evento intenta tener dos fuentes o ninguna | Rechazo por exclusión de origen; una referencia a INCIDENCIA no duplica su detalle |
| CP-TRZ-02-07 | Se repite la misma petición o concurren dos reemplazos | No se inventan asociaciones duplicadas ni se pierde un cambio; dato vigente e historia son coherentes |
| CP-TRZ-02-08 | Falla la inserción del evento de asociación | No se confirma únicamente el cambio de FK operativa |
| CP-TRZ-02-09 | Varios reportes apuntan a una misma orden | Se conservan sus fuentes sin crear otra orden abierta por repetición |
| CP-TRZ-02-10 | Se cancela/finaliza una orden o se reasigna técnico | Cada hecho conserva su historia apropiada; no se borra el reporte ni se altera el costo del alquiler |

## 9. Decisión vigente y antecedentes

D07-A está aprobada e incorporada como FK opcional/UK y una relación con INCIDENCIA. D07-B sigue descartada; los criterios que exigen filas de HISTORIAL_ATENCION_MANTENIMIENTO no son pruebas de aceptación actuales. El historial de incidencia aprobado conserva los eventos y cambios autorizados del reporte, y la auditoría ADMIN sus acciones administrativas, según el documento 36.

El documento 34 conserva el antecedente de revisión de 28/52. Posteriormente el usuario confirmó auditoría exclusivamente ADMIN y aprobó las cuatro mejoras del documento 35, incorporadas mediante RN-TRZ-01 en el documento 36. El Mermaid vigente tiene 29 entidades y 55 FK/relaciones; no se crean tablas físicas, no se modifican servicios/pantallas ni se migran datos por actualizar el modelo.
