# RN-BIC-02 Administración de bicicletas y límites de incidencias

Fecha de propuesta: 28 de octubre de 2026.

Fecha de aprobación de las reglas administrativas 1 a 6: 28 de octubre de 2026.

Estado: aprobadas las reglas administrativas presentadas como puntos 1 a 6: inactivación, reactivación, baja, cancelación operativa de reservas, protección de viajes y trazabilidad. Se desarrollan en las secciones 2, 3, 4 y 6. Después se aprobó incorporar el circuito mínimo de incidencias de RN-INC-01 en lugar de posponerlo; su precisión económica adicional también fue aprobada. No implementado en Java ni en la base de datos. Los criterios de aceptación están especificados, no ejecutados.

## 1. Base y decisiones que requiere

Se revisaron nuevamente el Word del diccionario de estados, el PDF completo de visión y el DER v4, además de RN-BIC-01, RN-MAN-02 y RN-MAN-04. Se inspeccionaron las tres páginas renderizadas del Word y el diagrama general del PDF. Los originales permanecen intactos.

El Word incluye EXTRAVIADA, DE_BAJA y RETENIDO_SISTEMA con cierre a las 24 horas. El PDF contempla administración de estados, mantenimiento, auditoría y un rechazo de desbloqueo cuando la bicicleta deja de estar habilitada. Ninguna de esas fuentes define suficientemente el cierre económico por pérdida o accidente. Tampoco concede por sí sola un cambio manual libre que sustituya la devolución.

RN-BIC-01 aprobó seis estados operativos iniciales y RN-BIC-02 completa sus permisos administrativos. Posteriormente [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md) incorpora EXTRAVIADA como séptimo estado y un cierre excepcional del detalle; no confunde pérdida con INACTIVA, mantenimiento o baja definitiva. La sección 5 deja asentado ese cambio respecto de la propuesta inicial de posponer incidencias.

## 2. Inactivación temporal y reactivación

Solo ADMIN puede inactivar o reactivar administrativamente. Se exige un motivo no vacío y registrar responsable, fecha y estado anterior y nuevo.

Una bicicleta DISPONIBLE, sin reserva, viaje u orden abierta incompatible, puede pasar a INACTIVA por una decisión temporal, por ejemplo un retiro temporal del servicio. No cambia de ubicación ni deja de ocupar su lugar por esa decisión.

INACTIVA no sustituye a MANTENIMIENTO. Si lo que existe es una falla o una revisión necesaria, se utiliza el recorrido de mantenimiento correspondiente. Tampoco se usa INACTIVA para ocultar una orden abierta o un resultado técnico desfavorable.

Para reactivar una INACTIVA, ADMIN debe resolver el motivo administrativo y comprobar que no existe reserva o viaje incompatible, que su ubicación corresponde a una estación activa válida y que no tiene impedimentos técnicos. Si está apta y la preventiva está vigente, puede pasar a DISPONIBLE.

Si al intentar reactivar existe una preventiva vencida o una falla pendiente, no se ofrece a clientes: se deriva a MANTENIMIENTO para atender la revisión correspondiente, respetando una sola orden abierta. Levantar el motivo administrativo no equivale a acreditar aptitud técnica. La vuelta posterior al servicio sigue la habilitación de RN-MAN-02. La tarea de calendario por sí sola no quita INACTIVA, conforme a RN-MAN-04.

Una estación inválida o una asociación incompatible impiden completar la reactivación, sin aplicar parcialmente sus efectos.

## 3. Baja definitiva y presencia física

Solo ADMIN puede registrar una baja definitiva, con motivo. Se admite desde DISPONIBLE, INACTIVA o MANTENIMIENTO, siempre que la bicicleta no tenga reserva, viaje ni órdenes de mantenimiento abiertas. Si hay una orden abierta que debe abandonarse, ADMIN debe cancelarla antes por la operación autorizada y con motivo; la baja no la cancela silenciosamente ni finge una reparación.

DE_BAJA conserva la bicicleta, sus alquileres, órdenes e historial. No se permite reactivarla desde el panel normal ni eliminar físicamente esos registros. La corrección de una baja cargada por error queda fuera del recorrido normal y no se resuelve creando otro registro que pierda su historia.

La baja administrativa no demuestra que la bicicleta se retiró de la estación. Si sigue físicamente allí, sigue ocupando un lugar aunque ya no se alquile. Solo una salida física efectivamente registrada permite quitar su ubicación actual y liberar ese lugar, conservando estación de origen, actor, fecha y motivo en la trazabilidad. No se borra la ubicación automáticamente por cambiar a DE_BAJA.

Esta condición deberá reflejarse en las consultas de capacidad: no será correcto ignorar una bicicleta físicamente presente solo por un indicador de borrado o por su estado DE_BAJA. La representación de la salida se concretaría en el DER sin inventar un traslado o una devolución.

## 4. Reservas y viajes protegidos

No se permite inactivar, dar de baja o liberar directamente una bicicleta RESERVADA o EN_USO mediante un selector de estados. Se conserva el recorrido de devolución válida. RN-INC-01 incorpora por separado una operación excepcional con reporte, motivo y corte validado; no habilita una devolución ficticia ni un cambio administrativo directo que eluda el contrato.

Para una unidad reservada todavía no retirada, se aprueba una operación específica de cancelación administrativa con motivo operativo o de seguridad, por ejemplo una falla detectada antes del retiro. Solo ADMIN puede ejecutarla. No es necesario esperar a los 15 minutos para impedir un retiro incompatible.

Se aplican los siguientes efectos en una sola operación coherente:

- Cerrar únicamente el detalle afectado como CANCELADO, conservando que el origen fue ADMIN y no el cliente. Si ya venció el plazo, correspondería VENCIDO; si se confirmó primero el retiro, no se permitiría cancelar esa unidad como si siguiera sin retirar.
- Mantener su costo de uso en cero. No reiniciar la reserva ni cambiar tarifas, cotización o movimientos financieros ya confirmados.
- Dejar la bicicleta MANTENIMIENTO si hay una falla o revisión pendiente, con la orden correspondiente y sin duplicar las abiertas. Si la causa es exclusivamente una suspensión administrativa temporal sin impedimento técnico, dejarla INACTIVA.
- Conservar la ubicación física y su ocupación; terminar la exclusividad no libera un espacio de la estación.
- Informar al cliente del motivo y de cómo queda su anticipo. No sustituir automáticamente la bicicleta ni crear otro alquiler sin confirmación del cliente.
- Si ninguna unidad se retiró y todas quedaron cerradas por cancelación, usar cabecera CANCELADO y conservar los motivos de cada detalle. Si hubo retiros, mantener el estado que corresponda a los restantes detalles y cerrar FINALIZADO cuando todos sean terminales.
- Tratar el anticipo con la liquidación conjunta aprobada: con otras unidades en uso, esperar al cierre del conjunto; sin retiros y sin detalles pendientes, registrar el reembolso del anticipo confirmado. Una petición repetida o una confirmación tardía no duplican dinero ni reactivan la reserva.

Esta es una ampliación aprobada a RN-ALQ-05, RN-ALQ-07 y RN-ALQ-09: CANCELADO ya no significa exclusivamente cancelación voluntaria del cliente, sino también cancelación administrativa autorizada antes del retiro, con causa y actor distinguibles. No se agrega un séptimo estado al detalle ni se atribuye esta ampliación a aprobaciones anteriores.

La cancelación operativa por una falla no se confunde con la preventiva que vence por calendario: para ese vencimiento se mantiene el respeto de las reservas previamente aceptadas conforme a RN-MAN-04.

## 5. Incidencias incorporadas por una decisión posterior

Se propuso inicialmente posponer pérdidas y accidentes, pero el usuario pidió analizar una alternativa mínima y después autorizó incorporarla. La decisión vigente es [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md): reporte, revisión por ADMIN, corte validado, CERRADO_POR_INCIDENCIA, EXTRAVIADA y recuperación con revisión técnica. No se implementó todavía.

No se convierte una demora en pérdida automáticamente ni se incorpora RETENIDO_SISTEMA a las 24 horas. No se inventa DEVUELTO ni se generan cargos por daños o reposición por el simple reporte. Se conserva un alcance acotado, sin automatizar asistencia física, seguros o atribución de responsabilidad.

La revisión detectó la devolución física anterior a la decisión del aviso. El usuario confirmó después la sección 8 de RN-INC-01: se conserva DEVUELTO, no se sigue contando tiempo y se espera la validación económica antes de liquidar si el incidente puede cambiar el importe. Se amplía expresamente la regla económica anterior, sin modificar ni borrar el anticipo.

## 6. Controles y criterios de aceptación de las reglas aprobadas

El backend debe comprobar rol activo, estado vigente y relaciones antes de mutar la entidad. La operación y su trazabilidad se confirman juntas. Una carrera entre reserva, retiro, cancelación o baja debe tener un solo resultado válido. Repetir una petición no duplica el historial de transición ni altera asignaciones posteriores. Las acciones automáticas conservan su origen de sistema, sin inventar un administrador humano.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-BIC-02-01 | Una cuenta sin rol ADMIN intenta inactivar, reactivar o dar de baja por HTTP | Acceso rechazado, sin mutaciones parciales |
| CP-BIC-02-02 | ADMIN inactiva una disponible sin impedimentos y con motivo | INACTIVA, motivo e historial; misma ubicación y ocupación |
| CP-BIC-02-03 | ADMIN reactiva una inactiva sin restricciones y con estación válida | DISPONIBLE, con autorización registrada |
| CP-BIC-02-04 | Al reactivar se detecta preventiva vencida o falla pendiente | No se ofrece la unidad; pasa al recorrido MANTENIMIENTO sin duplicar órdenes |
| CP-BIC-02-05 | Se intenta una baja con viaje, reserva u orden abierta | Se rechaza la baja directa, sin cerrar ni borrar sus asociaciones |
| CP-BIC-02-06 | ADMIN registra una baja válida y la unidad sigue en la estación | DE_BAJA, historia conservada y lugar todavía ocupado hasta registrar salida física |
| CP-BIC-02-07 | Se intenta reactivar una DE_BAJA desde el panel normal | Operación no permitida |
| CP-BIC-02-08 | ADMIN cancela una unidad reservada por falla antes de su retiro | Detalle CANCELADO con origen y motivo; costo cero, bicicleta MANTENIMIENTO, anticipo tratado sin pérdida ni duplicación |
| CP-BIC-02-09 | Cancelación administrativa y retiro llegan simultáneamente | Solo se confirma uno; no hay cancelación de una unidad ya retirada ni retiro sobre una cancelación confirmada |
| CP-BIC-02-10 | Se cancela por causa administrativa todo el conjunto sin retiros y con anticipo confirmado | Cabecera CANCELADO, motivos distinguibles y obligación de reembolso registrada una sola vez |
| CP-BIC-02-11 | Se repite una cancelación o llega después una confirmación de pago | No se reactiva la reserva ni se duplica el ajuste; se conserva el dinero confirmado y su tratamiento |
| CP-BIC-02-12 | Se intenta liberar por un cambio administrativo directo una unidad EN_USO que no se devolvió | Se rechaza el cambio; no se inventa una devolución ni se elude el viaje activo |

Los casos de esta tabla especifican la verificación de las reglas administrativas aprobadas. Requieren implementación y ejecución futura; no se ejecutaron. El circuito de incidencias y su precisión económica se documentan por separado en RN-INC-01.

## 7. Paso al DER

Las condiciones administrativas y la incorporación mínima de incidencias ya están aprobadas para el diseño. El catálogo de bicicleta y el de detalle pasan de seis a siete estados por RN-INC-01, manteniendo sus causas distinguibles. La precisión económica identificada también fue confirmada; el recorrido de negocio queda definido y puede consolidarse en el DER, con sus decisiones físicas y técnicas pendientes. Debe representar cancelación, incidencia, actor y motivo, historial, órdenes, fechas y presencia física sin indicadores contradictorios.

Los nombres y tipos de columnas no quedan fijados por esta propuesta. Tampoco se elimina el circuito de incidencias de la visión futura. El proveedor de pagos, hardware, redondeos, configuración preventiva y migración siguen siendo decisiones pendientes de sus respectivas etapas.

No se modificaron Java, la base de datos ni los archivos Word, PDF y DER originales. No se ejecutaron pruebas del nuevo alcance.
