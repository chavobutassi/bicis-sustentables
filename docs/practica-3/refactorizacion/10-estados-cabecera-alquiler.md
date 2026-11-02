# RN-ALQ-07: estados de la cabecera del alquiler

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada para implementar. No implementada en la nueva versión ni verificada mediante pruebas de ejecución.

## 1. Alcance

La cabecera ALQUILER resume la contratación y el uso del conjunto de bicicletas. Su estado no sustituye la situación financiera ni el estado operativo de cada bicicleta.

La deuda, un reembolso pendiente o una revisión técnica posterior no mantienen abierto el uso de una bicicleta que ya fue devuelta válidamente.

## 2. Estados aprobados

| Estado | Condición |
| --- | --- |
| RESERVADO | No hubo retiros y todavía queda al menos una unidad reservada o pendiente de retiro |
| EN_PROGRESO | Hubo al menos un retiro y quedan unidades en uso o pendientes de retiro |
| FINALIZADO | Hubo al menos un retiro y todos los detalles terminaron su uso o quedaron cancelados/vencidos |
| CANCELADO | La cancelación voluntaria del cliente o administrativa autorizada completó el cierre de las unidades sin que hubiera retiros; se conservan causas y actores |
| VENCIDO | No hubo retiros y el vencimiento cerró las unidades que todavía estaban reservadas, aunque otras se hubieran cancelado antes |

Se determina si hubo un retiro a partir de los hechos registrados, no de que el costo final sea positivo. Un retiro y devolución inmediata puede tener costo redondeado cero sin convertirse en una cancelación.

## 3. Transiciones y eventos del conjunto

- La contratación confirmada comienza en RESERVADO, con detalles válidos y reserva de 15 minutos conforme a RN-ALQ-03.
- El primer retiro autorizado cambia la cabecera a EN_PROGRESO.
- Una devolución parcial conserva EN_PROGRESO si otra unidad sigue en uso o pendiente de retiro.
- Cuando hubo retiros y todos los detalles quedan terminales, la cabecera pasa a FINALIZADO. Puede producirlo la última devolución, el cierre excepcional de RN-INC-01, la cancelación de la última pendiente o su vencimiento. Los terminales son DEVUELTO, CANCELADO, VENCIDO y CERRADO_POR_INCIDENCIA; finalizar el uso no exige terminar el dinero.
- Si nunca hubo retiros y la cancelación completa el cierre, pasa a CANCELADO. Puede ser voluntaria conforme a RN-ALQ-05 o administrativa autorizada conforme a la ampliación aprobada de [RN-BIC-02](20-propuesta-administracion-y-excepciones-bicicletas.md), con causas y actores distinguibles.
- Si nunca hubo retiros y el vencimiento cierra las pendientes, pasa a VENCIDO conforme a RN-ALQ-03.

La reserva no se mantiene abierta por un reembolso y no se reactiva por un pago que llega tarde. La confirmación de un pago tampoco demuestra que se haya retirado una bicicleta.

No se permite fijar un estado arbitrario de cabecera desde el frontend. El backend lo determina a partir de las operaciones autorizadas, los hechos y los estados de sus detalles.

## 4. Separación financiera y de mantenimiento

Un alquiler FINALIZADO puede tener un adicional por pagar, un reembolso por procesar o ninguna diferencia pendiente. La situación financiera debe indicar cuál de esos casos corresponde.

Los nombres y significados financieros se aprobaron posteriormente en [RN-ALQ-08](11-situacion-financiera-alquiler.md). Su actualización no cambia por sí sola el estado de uso de esta cabecera.

CANCELADO o VENCIDO sin uso tienen costo real de uso cero, pero pueden requerir devolver un anticipo confirmado. El reembolso no es una condición para registrar que la reserva terminó.

Si una bicicleta vuelve con una falla reportada, su detalle queda DEVUELTO y la unidad permanece fuera de alquiler para revisión conforme a RN-ALQ-06. Si ese era el último uso pendiente del conjunto, el alquiler puede quedar FINALIZADO aunque la reparación no haya comenzado ni terminado.

Cerrar el uso habilita la liquidación conjunta de RN-ALQ-02. Los movimientos financieros posteriores conservan su trazabilidad sin reabrir la cabecera. Una repetición de la última devolución no debe duplicar esa liquidación.

## 5. Ejemplos

- Dos bicicletas contratadas; una vuelve y la otra sigue en uso: EN_PROGRESO.
- Una bicicleta vuelve y la otra queda sin retirar hasta vencer: FINALIZADO cuando ya no queda ninguna unidad pendiente de retiro ni en uso.
- Ninguna se retiró; se cancela todo antes del plazo: CANCELADO, aunque quede un reintegro por procesar.
- Ninguna se retiró; se canceló una y el resto venció: VENCIDO.
- Todas las usadas vuelven, la última con falla reportada: FINALIZADO, con esa bicicleta fuera de alquiler para revisión y la situación financiera que resulte de la liquidación.

## 6. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-07-01 | Contratación confirmada sin retiros y con unidades pendientes | Cabecera RESERVADO, independientemente de que el anticipo esté todavía pendiente o ya confirmado |
| CP-ALQ-07-02 | Primer retiro válido | Cabecera EN_PROGRESO, sin iniciar el contador de otras unidades no retiradas |
| CP-ALQ-07-03 | Devolución de una unidad con otra en uso o pendiente de retiro | La cabecera continúa EN_PROGRESO |
| CP-ALQ-07-04 | Todos los detalles están devueltos, cancelados o vencidos y hubo algún retiro | Cabecera FINALIZADO y una única liquidación conjunta |
| CP-ALQ-07-05 | Cancelación completa sin ningún retiro | Cabecera CANCELADO; si hubo anticipo confirmado, la devolución del dinero se gestiona por separado |
| CP-ALQ-07-06 | Vencimiento de las últimas pendientes sin ningún retiro | Cabecera VENCIDO, incluso si parte de las unidades se canceló previamente |
| CP-ALQ-07-07 | El uso terminó y quedó una diferencia por pagar | Cabecera FINALIZADO y deuda representada por separado, sin seguir cobrando tiempo |
| CP-ALQ-07-08 | Última devolución válida con falla reportada | Cabecera FINALIZADO y bicicleta fuera de alquiler para revisión |
| CP-ALQ-07-09 | Llega una confirmación de pago para una reserva ya cancelada o vencida | No reactiva la cabecera; se registra y concilia el dinero según las reglas aprobadas |
| CP-ALQ-07-10 | Hubo retiro y devolución inmediata con costo redondeado cero | FINALIZADO, no CANCELADO por el solo hecho del costo cero |

## 7. Lo que esta aprobación no modifica

Los estados de pago y el mantenimiento se aprobaron por sus reglas específicas. RN-BIC-02 incorpora la cancelación administrativa antes del retiro y [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md) agrega CERRADO_POR_INCIDENCIA como terminal del detalle. No hay un estado nuevo de cabecera. La sección 8 de RN-INC-01 fue confirmada expresamente: la cabecera puede estar FINALIZADO y la situación financiera SIN_LIQUIDAR mientras se resuelve una incidencia previa que pueda cambiar el importe, sin seguir contando tiempo tras la devolución. Sigue pendiente el diseño físico.

La cabecera no se cierra automáticamente por acumular 24 horas sin devolución. Ese cierre forzoso no fue aprobado y no se incorpora mediante estos estados.

No se modificó código, base de datos ni el diccionario Word original. No se realizaron pagos ni reembolsos reales.
