# RN-ALQ-05: cancelación voluntaria antes del retiro

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada para implementar. No implementada todavía en la nueva versión. Los criterios de aceptación están documentados, pero no se ejecutaron pruebas de la nueva regla.

## 1. Condiciones aprobadas

Durante los 15 minutos de reserva, el cliente puede cancelar una o todas las bicicletas que todavía no retiró.

- Las unidades canceladas liberan inmediatamente su exclusividad, sin esperar al vencimiento original. Quedan disponibles si no tienen otros impedimentos; si la preventiva está vencida, pasan a MANTENIMIENTO según la ampliación aprobada en [RN-MAN-04](19-propuesta-preventivo-por-calendario.md).
- Una unidad no retirada y cancelada no genera costo de uso ni penalización.
- Si se cancela todo sin haber retirado ninguna y existe un anticipo confirmado, corresponde el reembolso total de ese anticipo.
- Si no hubo pago confirmado, se cancela la reserva sin generar un reembolso de dinero no recibido.
- Si ya se retiró alguna bicicleta, se pueden cancelar las restantes que sigan pendientes. El anticipo completo se compara con el costo real de las utilizadas al realizar la liquidación final conjunta.
- Una bicicleta en uso no se puede cancelar para detener la facturación. Debe devolverse a una estación válida con espacio, conforme a las reglas de devolución.
- La contratación y sus cambios se conservan para el historial y la auditoría. No se eliminan los registros para representar una cancelación.

La cancelación no reinicia los 15 minutos ni modifica las tarifas y cotización contratadas. Las unidades retiradas o devueltas conservan sus hechos y costos reales.

## 2. Aplicación al alquiler con varios detalles

La cancelación se aplica a los detalles pendientes de retiro seleccionados por el cliente, no indiscriminadamente a toda la contratación.

Cuando parte de las unidades ya está en uso, cancelar las restantes no convierte las que están en viaje en disponibles ni pone a cero su costo. El alquiler sigue su recorrido hasta que no queden unidades en uso ni pendientes de retiro.

Una vez que se devuelven las unidades utilizadas y se cancelan o vencen las pendientes, puede calcularse la liquidación conjunta de [RN-ALQ-02](03-alquiler-con-varias-bicicletas.md). Si todas las utilizadas ya se habían devuelto, cancelar la última pendiente permite liquidar en ese momento.

Una unidad cancelada continúa físicamente en la estación y sigue ocupando su lugar. Se libera su exclusividad para contratarla, no un espacio físico de la estación.

## 3. Tratamiento del dinero

Se conserva el anticipo original, y el ajuste se registra por separado:

- Cancelación completa sin uso y sin pago confirmado: costo de uso cero, sin reembolso que ejecutar.
- Cancelación completa sin uso y con pago confirmado: costo de uso cero y obligación de reembolso total.
- Cancelación parcial con otras unidades utilizadas: las canceladas tienen costo real cero y sus anticipos siguen incluidos en la liquidación final del conjunto. No hay un reembolso individual por cada unidad cancelada.

El reembolso se determina en ARS con los valores congelados de [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md), sin convertir a una cotización nueva el día de la cancelación o del procesamiento del reintegro.

Cancelar una contratación y confirmar que el dinero se devolvió son hechos distintos. Las unidades se liberan aunque la operación financiera continúe pendiente o falle. Debe poder seguirse y reintentarse de forma segura, sin duplicar devoluciones de dinero.

Si un pago se confirma después de cancelar, se registra el dinero recibido sin reactivar la contratación cancelada. En una cancelación completa sin uso corresponde su reembolso total. Las confirmaciones repetidas no deben duplicar la obligación financiera ni su ejecución.

## 4. Controles derivados para la implementación

- Un cliente solo puede cancelar detalles de una contratación propia. No basta con comprobar que conoce su identificador.
- Se validan estado y plazo en el backend antes de cambiar los registros. Si el plazo ya venció, corresponde la regla de vencimiento, no volver a presentar la reserva como vigente.
- Cancelar y retirar simultáneamente la misma unidad no puede producir ambos resultados. Si se confirma el retiro, ya no se admite esa cancelación. Si se confirma primero la cancelación, el retiro de ese detalle deja de estar autorizado.
- Una petición repetida no debe liberar una bicicleta asignada posteriormente a otra reserva ni crear un segundo reembolso.
- Se guarda qué detalles se cancelaron, quién realizó la operación y cuándo, conservando la contratación original y el motivo/origen del cambio según el diseño de historial y auditoría.
- La cancelación administrativa autorizada se aprobó posteriormente en [RN-BIC-02](20-propuesta-administracion-y-excepciones-bicicletas.md), solo para ADMIN y para unidades no retiradas, con motivo operativo o de seguridad. Conserva costo de uso cero, anticipo y trazabilidad, sin alterar otras unidades en uso. Su causa y actor se distinguen de la cancelación voluntaria del cliente.

## 5. Ejemplo ilustrativo

Se anticipan ARS 4.000 por dos bicicletas, a un valor contratado de ARS 1.000 por hora durante dos horas cada una.

El ejemplo supone que no hay preventiva vencida ni otro impedimento para volver a ofrecer la bicicleta cancelada.

- El cliente retira una bicicleta dentro de los 15 minutos y cancela la otra antes de vencer el plazo.
- La bicicleta cancelada queda disponible en su estación, con costo de uso cero.
- La bicicleta retirada se devuelve después de 45 minutos de uso y cuesta ARS 750.
- La liquidación del conjunto compara ARS 4.000 anticipados con ARS 750 reales: corresponde reembolsar ARS 3.250.

No se factura el tiempo de espera de la bicicleta cancelada ni se liquida individualmente su anticipo mientras la otra todavía está en uso.

## 6. Criterios de aceptación

Estas pruebas están especificadas, no ejecutadas.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-05-01 | Se cancela una reserva vigente sin pago ni retiros, con unidades sin impedimentos técnicos | Detalles cancelados, unidades disponibles y sin reembolso ficticio |
| CP-ALQ-05-02 | Se cancela todo, sin retiros y con un anticipo confirmado | Costo de uso cero y una obligación de reembolso por el anticipo total confirmado |
| CP-ALQ-05-03 | Una bicicleta está en uso y se cancela otra pendiente de retiro | La primera sigue su viaje y la segunda se libera con costo cero, sin liquidación individual de su anticipo |
| CP-ALQ-05-04 | Se cancela la última pendiente cuando todas las utilizadas ya se devolvieron | Se habilita una sola liquidación final conjunta |
| CP-ALQ-05-05 | Se intenta cancelar una bicicleta que está en uso | Se rechaza la cancelación; debe utilizarse el recorrido de devolución |
| CP-ALQ-05-06 | Se inspecciona la estación de una unidad cancelada sin retiro | La bicicleta sigue ocupando un lugar físico, aunque está disponible para contratar |
| CP-ALQ-05-07 | Se repite la cancelación o una confirmación de pago | No se duplica un reembolso ni se altera una nueva asignación de la bicicleta |
| CP-ALQ-05-08 | Un cliente intenta cancelar detalles de otro cliente | Se rechaza la operación sin cambiar la reserva ni la disponibilidad |
| CP-ALQ-05-09 | El reembolso falla o queda pendiente | Las unidades canceladas no vuelven a reservarse por el reembolso; su disponibilidad depende de sus impedimentos técnicos y el estado financiero refleja la obligación pendiente |
| CP-ALQ-05-10 | Se confirma un pago después de una cancelación completa sin uso | Se registra y corresponde su reembolso, sin reactivar la reserva |
| CP-ALQ-05-11 | Se ejecuta el ejemplo con anticipo ARS 4.000, una unidad cancelada y otra usada 45 minutos a ARS 1.000/h | Costo real del conjunto ARS 750 y reembolso correspondiente ARS 3.250 |
| CP-ALQ-05-12 | Se consulta la contratación cancelada desde las funciones autorizadas de historial/auditoría | Se conservan la contratación, sus detalles y los cambios, sin borrado para representar la cancelación |

## 7. Límites

Esta regla se aplica a la cancelación normal de unidades aún no retiradas dentro de una reserva vigente. RN-BIC-02 amplía el recorrido a la cancelación administrativa autorizada antes del retiro; no permite cancelar una bicicleta ya retirada para detener su uso. La resolución de averías durante un viaje, pérdida de la bicicleta y cancelaciones de pagos en la pasarela antes de su captura siguen requiriendo sus propios recorridos y permisos.

No se realizaron pagos ni reembolsos reales. No se modificó código ni base de datos.
