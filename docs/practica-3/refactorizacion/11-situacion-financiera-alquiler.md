# RN-ALQ-08: situación financiera del alquiler

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada para implementar. No implementada en la nueva versión ni verificada mediante pruebas de ejecución.

## 1. Alcance

La situación financiera indica si falta calcular el ajuste del conjunto, si el cliente debe dinero, si corresponde un reembolso o si ya no existe diferencia por resolver.

Es independiente de la cabecera operativa de [RN-ALQ-07](10-estados-cabecera-alquiler.md) y del estado de cada intento de pago o reembolso. Se calcula o actualiza con los importes y hechos validados, no con la intención del usuario ni con un mensaje de éxito del navegador.

## 2. Situaciones aprobadas

| Situación | Significado |
| --- | --- |
| SIN_LIQUIDAR | Falta terminar el uso o resolver incidencias pendientes que puedan afectar el importe y determinar el ajuste final. El anticipo puede estar confirmado |
| SALDO_PENDIENTE | El costo definitivo supera los importes netos confirmados y el cliente debe una diferencia |
| REEMBOLSO_PENDIENTE | Los importes netos confirmados superan el costo definitivo y la plataforma debe devolver una diferencia al cliente |
| SALDADO | No queda dinero por cobrar ni devolver frente al costo definitivo y los movimientos confirmados |

Un anticipo pagado no convierte por sí solo la situación en SALDADO: falta saber el tiempo real y terminar el uso o resolver las unidades pendientes de retiro.

## 3. Liquidación y cambios posteriores

Al terminar el uso y resolver las incidencias pendientes que puedan afectar el importe, se fija el costo real con tarifa y cotización congeladas y se compara con el dinero neto confirmado en ARS. La ampliación aprobada de [RN-INC-01, sección 8](21-propuesta-minima-incidencias-en-viaje.md) permite cabecera FINALIZADO con situación SIN_LIQUIDAR mientras se revisa ese efecto económico: no se prolonga la devolución ni el tiempo de uso. Una revisión técnica posterior, sin una incidencia económica pendiente, no retrasa por sí sola la liquidación.

Dinero neto confirmado significa pagos aprobados recibidos menos reembolsos confirmados. Los intentos pendientes, rechazados o no conciliados no se cuentan como movimientos exitosos.

- Si el costo y el dinero neto coinciden, queda SALDADO.
- Si el costo es mayor, queda SALDO_PENDIENTE por la diferencia.
- Si el dinero neto es mayor, queda REEMBOLSO_PENDIENTE por la diferencia.

Un pago adicional confirmado reduce el saldo deudor. Un intento rechazado no lo cancela. Cuando se cubre la diferencia completa, pasa a SALDADO.

Un reembolso confirmado reduce la obligación a favor del cliente. Solicitarlo o reintentarlo no basta para considerar que ya se completó. Mientras falte devolver parte de lo debido, continúa REEMBOLSO_PENDIENTE. El estado de la operación concreta informa si está en proceso o falló.

En una contratación cancelada o vencida sin uso y sin pagos confirmados, costo y dinero recibido son cero: no existe diferencia y corresponde SALDADO. Si hubo anticipo confirmado, corresponde REEMBOLSO_PENDIENTE hasta completar el reintegro.

Si llega después un pago confirmado para una contratación cerrada sin uso, se registra el dinero y se reconoce la obligación de devolverlo. Puede cambiar de SALDADO a REEMBOLSO_PENDIENTE por ese hecho nuevo, sin reactivar la reserva ni repetir la liquidación del uso.

## 4. Efectos sobre el acceso y la operación

- Solo SALDO_PENDIENTE impide nuevas contrataciones, conforme a RN-ALQ-01.
- REEMBOLSO_PENDIENTE no bloquea al cliente: es dinero que la plataforma le debe.
- SIN_LIQUIDAR no constituye por sí mismo una deuda vencida ni bloquea nuevas contrataciones de acuerdo con esta regla.
- El bloqueo por saldo pendiente no impide ingresar, pagar ni devolver bicicletas de contrataciones que ya están en uso.
- La gestión de dinero no reabre un viaje terminado, no reactiva un contador ni devuelve una bicicleta a EN_USO.
- La revisión técnica de una bicicleta ya devuelta no mantiene la situación SIN_LIQUIDAR por sí sola.

## 5. Ejemplo

Anticipo confirmado: ARS 4.000. Costo real del conjunto: ARS 3.750.

Al terminar el uso, la cabecera queda FINALIZADO y la situación financiera REEMBOLSO_PENDIENTE por ARS 250. Se registra y gestiona ese reembolso.

Si el reembolso falla, sigue REEMBOLSO_PENDIENTE. Cuando se confirma la devolución de los ARS 250, el dinero neto confirmado es ARS 3.750 y la situación pasa a SALDADO. La cabecera sigue FINALIZADO en todos esos pasos.

## 6. Datos y controles necesarios

Debe poder identificarse el costo definitivo, los pagos confirmados, los reembolsos confirmados y los importes todavía por cobrar o devolver, siempre con su moneda.

La situación puede persistirse o derivarse de esos hechos, según el diseño final del DER. Esta aprobación fija su significado, no obliga a crear una tabla adicional ni a almacenar valores redundantes sin controles de coherencia.

Las notificaciones y solicitudes repetidas no pueden sumarse dos veces. La actualización financiera debe respetar el registro de cada operación y la conciliación de resultados externos inciertos.

No se inventan pagos confirmados para alquileres históricos de la versión anterior. Su tratamiento se decidirá con la migración o la carga de demostración.

## 7. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-08-01 | Anticipo confirmado y todavía existen usos o retiros pendientes | SIN_LIQUIDAR, aunque el intento de pago inicial esté APROBADO |
| CP-ALQ-08-02 | Se liquida un conjunto cuyo costo coincide con el anticipo confirmado | SALDADO, sin generar otro movimiento por diferencia |
| CP-ALQ-08-03 | Se liquida con costo real mayor al importe neto confirmado | SALDO_PENDIENTE por la diferencia y bloqueo de nuevas contrataciones |
| CP-ALQ-08-04 | Se rechaza un intento de pago adicional | La deuda sigue SALDO_PENDIENTE y no se reabre el uso |
| CP-ALQ-08-05 | Se confirma el pago adicional que cubre la deuda completa | SALDADO; desaparece el bloqueo por esa deuda |
| CP-ALQ-08-06 | Se liquida con costo real menor al anticipo confirmado | REEMBOLSO_PENDIENTE por la diferencia, sin bloquear al cliente por esa situación |
| CP-ALQ-08-07 | El reembolso se solicita, falla o todavía no se confirmó completamente | Continúa REEMBOLSO_PENDIENTE por el importe aún no confirmado como devuelto |
| CP-ALQ-08-08 | Se confirma el reembolso completo debido | SALDADO; el estado operativo de la cabecera no cambia |
| CP-ALQ-08-09 | Cancelación o vencimiento sin uso ni pagos confirmados | SALDADO, con costo cero y sin reembolso ficticio |
| CP-ALQ-08-10 | Pago confirmado que llega después de una cancelación completa sin uso | Se reconoce REEMBOLSO_PENDIENTE, sin reactivar la reserva |
| CP-ALQ-08-11 | Se recibe dos veces la misma confirmación de pago o reembolso | El dinero confirmado no se cuenta dos veces y no produce una diferencia artificial |

## 8. Límites

Siguen pendientes el proveedor de pago, la representación definitiva de cada movimiento en el DER y excepciones como contracargos, pagos no esperados o ajustes administrativos. No se aprueban cobros automáticos, multas ni cargos por daños mediante estos nombres de situación financiera.

No se modificó código, base de datos ni los documentos originales del usuario. No se realizaron pagos ni reembolsos reales.
