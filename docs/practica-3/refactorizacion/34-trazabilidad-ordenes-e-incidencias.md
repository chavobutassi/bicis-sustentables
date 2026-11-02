# Antecedente de campos y trazabilidad de órdenes e incidencias

Fecha de revisión: 2 de noviembre de 2026.

Estado: el usuario descartó por ahora HISTORIAL_ATENCION_MANTENIMIENTO para no ampliar la complejidad. Se mantienen las asociaciones operativas de reportes a órdenes y la auditoría de sus reemplazos excepcionales. La propuesta independiente incidencia_corte_id de D07-A no se da por aprobada ni descartada por esa respuesta. No se crea HISTORIAL_INCIDENCIA ni se modifican Mermaid, Java o la base mediante esta revisión.

Actualización posterior del 2 de noviembre: este documento queda como antecedente del modelo de 28 entidades/52 relaciones antes de RN-TRZ-01. La recomendación de auditoría general fue retirada: AUDITORIA_SISTEMA es exclusiva de ADMIN. El usuario aprobó después las cuatro mejoras del documento 35, incorporadas y detalladas en el [documento 36](36-incorporacion-aprobada-trazabilidad-der.md). El historial de orden tiene ahora once campos y nuevo nombre; existe HISTORIAL_INCIDENCIA e incidencia_corte_id en el DER, con 29 entidades/55 relaciones. Las tablas y afirmaciones del cuerpo siguientes describen el momento anterior, no la estructura vigente. HISTORIAL_ATENCION_MANTENIMIENTO sigue descartado; Java y la base no se modificaron.

Los campos de las secciones siguientes se comprobaron contra [el DER lógico vigente](der-v5-propuesto.mmd), no contra tablas nuevas ya creadas en MySQL. El modelo conserva 28 entidades y 52 FK/relaciones; no implica que el backend antiguo ya implemente sus historiales o su auditoría.

## 1. Historial de estados de una orden

Sí existe HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO en el DER. Cada evento pertenece a una orden y conserva su transición. Sus campos actuales son:

| Campo | Tipo y clave del DER | Finalidad |
| --- | --- | --- |
| id | int, PK | Identificador del evento |
| orden_mantenimiento_id | int, FK | Orden cuyo estado cambió |
| estado_anterior_id | int, FK | Estado previo; nulo solo en el registro inicial |
| estado_nuevo_id | int, FK | Estado que queda vigente; obligatorio |
| fecha_hora_cambio | datetime | Fecha/hora del registro de la transición en el backend |
| actor_usuario_id | int, FK | Persona que ejecutó la acción; nulo solo si el origen es SISTEMA |
| origen | string | Distingue USUARIO de SISTEMA, sin inventar un ADMIN para un proceso automático |
| observaciones | text | Motivo y contexto; el motivo es obligatorio al pausar o cancelar |

Esta estructura es adecuada para CREADA, EN_PROCESO, PAUSADA, FINALIZADA y CANCELADA. La creación también tiene su evento, con anterior nulo y nuevo CREADA. La asignación vigente del técnico y los datos del trabajo pertenecen a ORDEN_MANTENIMIENTO, no se copian sin necesidad en cada transición.

El estado actual de la orden y su evento deben confirmarse juntos en una transacción local. Los eventos se añaden y no se editan/borran desde el ABM normal. Fechas, origen y autor se determinan o verifican en el backend. Estas condiciones son necesarias para que el diseño funcione; no están probadas por la sola existencia del dibujo.

## 2. Qué cambios de la orden necesitan auditoría

El historial anterior registra estados, no todas las modificaciones de una orden. Si ADMIN reasigna un técnico en una fase permitida sin cambiar el estado, no corresponde inventar una transición CREADA a CREADA.

En AUDITORIA_SISTEMA deben conservarse los cambios permitidos de técnico, diagnóstico, descripción del trabajo, costo/moneda de repuestos, resultado técnico u otros datos relevantes, con sus valores anteriores/nuevos, responsable, fecha y motivo cuando corresponda. El historial de estados conserva además el contexto de sus transiciones. No se agrega una tabla de asignaciones, repuestos o intervenciones por esta decisión.

El recorrido habitual sigue siendo una orden para atender el problema hasta cerrarla. Reasignar, pausar o continuar no requiere una orden nueva. Si ADMIN cancela y crea una sustituta por el recorrido excepcional autorizado, se conservan ambas órdenes y se audita el cambio de enlace anterior/nuevo del reporte, sin otra tabla de atención. Se mantiene como máximo una orden abierta por bicicleta.

## 3. Campos actuales de INCIDENCIA

No existe HISTORIAL_ESTADO_INCIDENCIA ni HISTORIAL_INCIDENCIA en el Mermaid actual. INCIDENCIA conserva el reporte y los datos vigentes de su revisión/recepción mediante estos 21 campos:

| Campo | Tipo y clave del DER | Finalidad |
| --- | --- | --- |
| id | int, PK | Identificador de la incidencia |
| alquiler_detalle_id | int, FK | Unidad contractual afectada; de ella se obtienen bicicleta y propietario |
| registrado_por_id | int, FK | Usuario que cargó el reporte |
| informante_id | int, FK | Informante identificado, si existe; puede ser distinto de quien lo cargó |
| resuelto_por_id | int, FK | ADMIN que decide, opcional hasta la resolución |
| orden_mantenimiento_id | int, FK | Orden asociada, opcional si todavía no corresponde/existe atención de taller |
| tipo | string | El borrador propone AVERIA, ACCIDENTE, PERDIDA o ROBO |
| estado_revision | string | El borrador propone PENDIENTE, VALIDADA o DESCARTADA para la revisión administrativa |
| requiere_revision_economica | boolean | Indica si la revisión puede afectar el importe; lo determina el backend |
| descripcion | text | Relato del hecho, no diagnóstico técnico ni prueba automática |
| lugar_reportado | text | Ubicación informada cuando se conoce, sin inventar GPS o estación |
| fecha_hora_hecho_informada | datetime | Momento del hecho comunicado por el informante; no es el corte autorizado |
| fecha_hora_registro | datetime | Momento en que el sistema registró el reporte |
| fecha_hora_decision | datetime | Momento de revisión/resolución, opcional hasta decidir |
| fecha_hora_corte_validado | datetime | Interrupción validada para el tratamiento económico, cuando corresponda |
| motivo_decision | text | Fundamento obligatorio al resolver, sin atribución automática de culpa |
| fecha_hora_recepcion_fisica | datetime | Recepción/recuperación pertinente a la incidencia, si ocurrió; no reinicia el uso |
| estacion_recepcion_id | int, FK | Estación de ingreso real si corresponde; no estación ficticia |
| recibido_por_id | int, FK | Responsable del registro de la recepción cuando corresponde |
| lugar_recepcion | text | Ubicación de recepción si no fue en una estación |
| version | int | Control de concurrencia; no es un historial de negocio |

Una devolución normal sigue conservando sus fechas y estación en ALQUILER_DETALLE. Las fechas de incidencia no deben sobrescribir o simular esos hechos. La cronología y la forma física de coordinar recepción/corte se completan con D06 y RN-INC-01, no añadiendo una tabla de historia por iniciativa de este listado.

Los datos y sus separaciones son adecuados para el alcance mínimo aprobado. Los campos de responsable/fecha actuales no conservan por sí solos todos sus cambios anteriores. Tampoco basta version: permite detectar conflictos, pero no explica quién cambió qué ni conserva el valor anterior.

## 4. Trazabilidad necesaria de una incidencia

Para mantener el diseño acotado se recomienda utilizar AUDITORIA_SISTEMA, ya prevista, en lugar de agregar ahora un historial específico. Esto no equivale a dejar sin historia la incidencia. Los hechos relevantes que deben poder reconstruirse son:

| Hecho o cambio permitido | Información que debe conservarse |
| --- | --- |
| Registro inicial | Incidencia, detalle afectado, datos permitidos del reporte, registrado por, informante identificado y fecha del backend |
| Corrección autorizada del reporte | Valores anteriores/nuevos de tipo, descripción, lugar o momento informado, con autor y motivo; sin borrar silenciosamente lo comunicado originalmente |
| Estado de revisión | PENDIENTE a VALIDADA/DESCARTADA según corresponda, con responsable y momento de la decisión |
| Determinación de revisión económica | Cambio permitido de requiere_revision_economica y su fundamento; el cliente no controla libremente este indicador |
| Resolución/corte económico | Decisión, motivo, responsable, fecha de resolución y corte validado; cualquier corrección permitida conserva anterior/nuevo y no elude una liquidación definitiva |
| Enlace a mantenimiento | Orden anterior/nueva, fuente del cambio, responsable y motivo del reemplazo autorizado |
| Recepción o recuperación física | Fecha real registrada, estación o lugar, responsable y correcciones permitidas, sin reiniciar el contador |

Una fila de auditoría identifica entidad_afectada=INCIDENCIA y entidad_id igual al id de esa incidencia. Contiene además accion, actor_usuario_id, origen, fecha_operacion y valores_anteriores/valores_nuevos con datos permitidos. La aplicación debe ofrecer una consulta autorizada de sus eventos para poder mostrar su historia; no basta con sobrescribir INCIDENCIA o con guardar texto inconexo que nadie pueda reconstruir.

Ejemplo ilustrativo: un cambio de estado de la incidencia 35 registra PENDIENTE como anterior, VALIDADA como nuevo, el ADMIN real y la fecha del backend, junto con el motivo y corte aplicables a esa decisión. No se inventa un nuevo evento de estado por una consulta o por repetir la misma petición sin efecto.

El registro inicial, la revisión, la recepción y sus auditorías se coordinan en las transacciones locales correspondientes. Los eventos se conservan sin edición/borrado desde el flujo normal. Su consulta respeta propiedad y permisos; los datos de correlación y las descripciones también son privados. No se almacenan secretos de aplicación o respuestas externas completas mediante una auditoría indiscriminada.

Auditar una modificación no concede permiso para hacerla. No se autoriza cambiar el detalle afectado, reabrir cierres o recalcular una liquidación definitiva por la mera existencia de valores anteriores/nuevos. Se mantienen RN-INC-01, roles y validaciones aprobados.

## 5. Cambios descartados y pendientes independientes

HISTORIAL_ATENCION_MANTENIMIENTO queda descartado por ahora por decisión expresa del usuario. El antecedente de campos y relaciones se conserva marcado como descartado en el documento 33; no se incorporó al Mermaid y no se elimina una tabla existente porque nunca se creó.

No se aprueba ni incorpora un nuevo HISTORIAL_INCIDENCIA por la pregunta del usuario. Con la auditoría prevista se pueden conservar sus movimientos sin agregar entidades. Si más adelante se exige un historial específico con FK por evento o se decide cambiar esa representación, deberá aprobarse como tal; no es obligatorio crear una tabla de historial para cada entidad para obtener trazabilidad.

D07-A, incidencia_corte_id, sigue pendiente de una decisión separada. Esta respuesta descartó el historial de atención, no autorizó añadir aquella FK al detalle. El campo no figura todavía en el DER. Se mantiene explícito el punto para no dar por resuelto el vínculo entre un corte aplicado y la decisión que lo fundamenta cuando existen varios reportes.

## 6. Criterios de aceptación para la implementación

No se ejecutaron estos casos:

- CP-TRZ-03-01: crear una orden y cambiarla de estado conserva evento inicial y cada transición efectiva, coherentes con el estado vigente.
- CP-TRZ-03-02: pausa/cancelación conservan motivos anteriores en sus eventos aunque el resumen de la orden cambie.
- CP-TRZ-03-03: reasignar técnico o modificar diagnóstico/costos en un recorrido permitido registra anterior/nuevo y actor sin inventar otra transición de estado.
- CP-TRZ-03-04: registrar/revisar una incidencia conserva sus datos y la auditoría de los hechos, con fechas informada, registrada, decidida y corte distinguidas.
- CP-TRZ-03-05: una consulta autorizada reconstruye los eventos de la incidencia y sus vínculos de mantenimiento sin depender solo del último valor.
- CP-TRZ-03-06: un reemplazo excepcional de orden conserva ambas órdenes y el enlace anterior/nuevo en auditoría, sin dos abiertas por bicicleta ni cambios en el costo del viaje.
- CP-TRZ-03-07: si falla la auditoría/historial que corresponde, no se confirma aisladamente el cambio de negocio; repetir una petición no duplica su efecto.

No se modifica el modelo, no se ejecuta SQL o Spring y no se declara trazabilidad implementada por describir estos casos.
