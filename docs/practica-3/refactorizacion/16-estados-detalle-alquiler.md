# RN-ALQ-09 Estados del detalle de alquiler

Fecha de aprobación: 28 de octubre de 2026.

Estado: seis estados iniciales confirmados y ampliación posterior RN-INC-01 con CERRADO_POR_INCIDENCIA; el catálogo de diseño tiene siete estados. La precisión económica de la sección 8 de RN-INC-01 también está aprobada. No implementado en Java ni en una base de datos. Los criterios de aceptación no se ejecutaron.

## 1. Alcance

ALQUILER_DETALLE representa una bicicleta específica dentro de una contratación. Su estado describe el recorrido de esa unidad, no el estado del conjunto, la condición técnica de la bicicleta ni el resultado de un pago.

Esta confirmación cierra el catálogo que se había revisado en la sección 2 del [diccionario de trabajo](08-diccionario-estados-propuesto.md), contrastándolo con el Word, el PDF y las reglas previamente aprobadas. Los documentos originales siguen intactos.

## 2. Catálogo aprobado

| Estado | Significado | Tiempo de uso |
| --- | --- | --- |
| RESERVADO | Bicicleta apartada de forma exclusiva; el anticipo requerido todavía no está confirmado | No acumula |
| PENDIENTE_RETIRO | Anticipo requerido confirmado; falta retirar la unidad dentro del plazo vigente | No acumula |
| EN_CURSO | Retiro efectivo validado por el backend | Acumula desde su retiro real |
| DEVUELTO | Devolución válida registrada | Deja de acumular; costo provisional si existe una incidencia previa pendiente que pueda afectar el importe |
| CERRADO_POR_INCIDENCIA | Cierre excepcional autorizado por ADMIN, con reporte y corte validado, sin devolución normal | Hasta el corte validado; no aumenta por la espera de revisión |
| CANCELADO | Cancelación voluntaria del cliente o administrativa autorizada, antes del retiro y del vencimiento; con causa y actor distinguibles | Cero |
| VENCIDO | Se agotaron los 15 minutos originales sin retirar esa unidad | Cero |

DEVUELTO, CANCELADO, VENCIDO y CERRADO_POR_INCIDENCIA son los cierres del detalle, este último incorporado posteriormente por RN-INC-01. Los ajustes económicos pendientes o una recuperación física posterior no lo convierten nuevamente en un viaje activo.

## 3. Coherencia con las reglas ya aprobadas

RESERVADO y PENDIENTE_RETIRO distinguen la fase anterior y posterior al pago confirmado. En ambas la bicicleta sigue físicamente en su estación, ocupa lugar y tiene estado operativo RESERVADA. Reservar y pagar no inician el contador de uso.

Un rechazo confirmado del anticipo mantiene RESERVADO mientras la reserva siga vigente; no libera la unidad ni impide un nuevo intento válido dentro de los 15 minutos originales, conforme a [RN-PAG-02](15-reintentos-pago-durante-reserva.md). No se reinicia el plazo al reintentar o pagar: cubre pago y retiro según [RN-ALQ-03](04-reserva-y-vencimiento.md).

EN_CURSO exige retiro efectivo validado. Un escaneo aislado de QR no demuestra ese retiro ni sustituye los controles de propiedad, pago, reserva y plazo. El alcance físico o simulado del candado sigue pendiente de definición.

Una unidad EN_CURSO se devuelve mediante el recorrido autorizado; no se cancela para detener el costo de uso. CANCELADO corresponde a una cancelación previa al retiro, mientras que VENCIDO conserva la causa distinta de agotamiento del plazo.

La ampliación aprobada de [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md) incorpora CERRADO_POR_INCIDENCIA como séptimo estado. ADMIN puede cerrar excepcionalmente EN_CURSO con reporte, motivo y corte validado. No se inventa una devolución ni se cierra otra unidad del conjunto. Si la bicicleta se recibe después, se registra recuperación física sin reiniciar el contador ni duplicar la liquidación. La sección 8 también está aprobada: si se devuelve antes de resolver una incidencia que pueda afectar el importe, se conserva DEVUELTO y el fin del tiempo, pero el costo sigue provisional y la liquidación espera esa revisión.

La ampliación aprobada en [RN-BIC-02](20-propuesta-administracion-y-excepciones-bicicletas.md) permite también a ADMIN cancelar una unidad todavía no retirada por motivo operativo o de seguridad, conservando costo de uso cero, ajuste del anticipo e historial. No habilita una cancelación de una bicicleta ya EN_CURSO ni agrega un estado al detalle.

DEVUELTO conserva las condiciones independientes de demora y falla reportada de [RN-ALQ-06](09-devolucion-demora-y-fallas.md), incluso combinadas. La demora no genera multa. Una falla reportada detiene igualmente el tiempo del cliente al devolver, pero deja la bicicleta en MANTENIMIENTO para revisión, conforme a RN-BIC-01.

La ampliación aprobada de [RN-MAN-04](19-propuesta-preventivo-por-calendario.md) no agrega estados al detalle: si venció la preventiva, una devolución válida sigue siendo DEVUELTO y detiene el costo, pero la bicicleta queda MANTENIMIENTO aun sin falla. CANCELADO y VENCIDO también terminan la exclusividad sin ofrecer la bicicleta nuevamente si requiere esa revisión. Una reserva aceptada antes del vencimiento preventivo conserva sus 15 minutos originales; no se confirma otra nueva una vez vencida la preventiva.

La cabecera del conjunto mantiene sus estados independientes de RN-ALQ-07 y la liquidación sigue siendo conjunta conforme a RN-ALQ-02. Que un detalle termine no significa que todos los demás hayan terminado.

## 4. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-09-01 | Contratación confirmada, anticipo sin confirmar y plazo vigente | Detalle RESERVADO, bicicleta RESERVADA y sin tiempo de uso acumulado |
| CP-ALQ-09-02 | Anticipo requerido confirmado antes del vencimiento, unidad todavía no retirada | Detalle PENDIENTE_RETIRO, sin inicio del contador ni extensión del plazo |
| CP-ALQ-09-03 | Retiro efectivo autorizado dentro del plazo | Detalle EN_CURSO, inicio real registrado y bicicleta EN_USO fuera de la ocupación de la estación |
| CP-ALQ-09-04 | Devolución válida de una unidad en uso | Detalle DEVUELTO y detención de su contador; se conserva el costo por uso real |
| CP-ALQ-09-05 | Cancelación voluntaria antes del retiro y vencimiento | Detalle CANCELADO, costo de uso cero y liberación de esa reserva |
| CP-ALQ-09-06 | Se alcanza el vencimiento sin retirar la unidad | Detalle VENCIDO, costo de uso cero y liberación de esa reserva, sin liberar otras unidades en uso |
| CP-ALQ-09-07 | Se devuelve con demora y falla reportada | Detalle DEVUELTO con ambas condiciones identificables; bicicleta en MANTENIMIENTO y sin multa automática |
| CP-ALQ-09-08 | Se intenta cancelar una unidad EN_CURSO | No se evita la devolución ni se detiene el uso mediante una cancelación |
| CP-ALQ-09-09 | Se confirma un rechazo del anticipo con la reserva vigente | No se cambia el detalle a CANCELADO ni VENCIDO por el rechazo; se respeta RN-PAG-02 |

## 5. Límites de esta confirmación

La confirmación original aprobó seis estados y sus significados, no permisos administrativos generales. RN-BIC-02 amplió después la cancelación autorizada y RN-INC-01 agregó el séptimo estado CERRADO_POR_INCIDENCIA. Los efectos conservan su fundamento y fecha de aprobación en cada regla, incluida la precisión económica adicional de la sección 8, confirmada expresamente después.

Los permisos manuales de mantenimiento y la habilitación posterior se aprobaron en [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md). RN-MAN-03 aprueba el correctivo desde una devolución con falla, una sola orden abierta y CREADA sin técnico. RN-MAN-04 incorpora el preventivo por calendario, con valores numéricos y detalles técnicos pendientes. RN-BIC-02 aprueba la administración y cancelación operativa antes del retiro. RN-INC-01 incorpora después CERRADO_POR_INCIDENCIA, sin devolución ficticia. La precisión económica de la sección 8 también está aprobada. Siguen pendientes la integración de pagos y QR, los redondeos y el diseño físico del DER. No se incorpora RETENIDO_SISTEMA ni un cierre automático por 24 horas.

No se modificaron código, base de datos, Word ni PDF originales. No se realizaron pagos, reembolsos ni pruebas de ejecución.
