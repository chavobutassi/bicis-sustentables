# RN-ALQ-03: reserva de 15 minutos y vencimiento

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada para implementar. Las pruebas de este documento están especificadas, no ejecutadas. No se modificó código ni base de datos.

## 1. Condiciones aprobadas

1. Al confirmar la contratación, las bicicletas seleccionadas quedan reservadas y ningún otro cliente puede contratarlas durante esa reserva.
2. El cliente tiene 15 minutos desde esa confirmación para pagar el anticipo y retirar las unidades.
3. Reservar y pagar no inician el cómputo del uso. Cada bicicleta comienza a acumular tiempo cuando se confirma su retiro efectivo.
4. Al vencer los 15 minutos, se liberan exclusivamente las unidades que no fueron retiradas. Las bicicletas que ya están en uso continúan sus viajes y no se liberan por ese vencimiento.
5. Una unidad nunca retirada no genera costo de uso. Si se había pagado su anticipo, ese importe forma parte del ajuste final conjunto.
6. Si no se retiró ninguna bicicleta y existe un anticipo confirmado, corresponde el reembolso total de ese anticipo.

La reserva no altera la ubicación física. Una bicicleta reservada sigue ocupando un lugar en su estación, aunque no se ofrezca a otros clientes. Solo el retiro efectivo la saca de la ocupación de la estación.

Ampliación aprobada el 28 de octubre en [RN-MAN-04](19-propuesta-preventivo-por-calendario.md): no se confirma una reserva nueva si la preventiva ya está vencida, aunque la tarea periódica no haya actualizado el estado visible. Si vence durante una reserva previamente aceptada, se respeta su plazo original de 15 minutos; un retiro válido deriva la revisión a la devolución. Si vence o se cancela sin retiro, se libera la exclusividad pero la bicicleta pasa a MANTENIMIENTO cuando corresponda, no a una nueva contratación. Esto solo trata el calendario y no autoriza ignorar fallas.

## 2. Plazo y validación

El vencimiento se calcula como la fecha y hora de confirmación de la contratación más 15 minutos. Se guarda en el backend y no depende del reloj ni de un contador del navegador.

El pago no reinicia ese plazo: los 15 minutos cubren el pago y el retiro, y no son 15 minutos para cada etapa. Reintentar una solicitud tampoco extiende la reserva original.

El 28 de octubre se aprobó [RN-PAG-02](15-reintentos-pago-durante-reserva.md): un rechazo confirmado del anticipo no cancela la contratación ni cambia las bicicletas a disponibles. Pueden realizarse nuevos intentos dentro del mismo plazo, sin un límite de dos intentos como regla de negocio. Un resultado todavía pendiente o incierto se consulta antes de permitir otro cobro. El pago y el retiro deben respetar el vencimiento original.

Para precisar el límite de implementación, el retiro solo puede autorizarse si la hora del backend es anterior al vencimiento y el anticipo requerido está confirmado. Al alcanzar el vencimiento o superarlo, se rechaza un nuevo retiro sobre esa reserva. Esto no impide devolver una unidad que se retiró válidamente antes.

La condición de pago confirmado debe verificarse contra el registro validado por el backend, no solamente contra una pantalla de éxito del navegador. El proveedor y el mecanismo concreto de confirmación aún deben seleccionarse.

## 3. Reserva sin retiros

Si vence el plazo y no se retiró ninguna unidad:

- Se dan por vencidos los detalles pendientes de retiro y se libera su exclusividad.
- Las bicicletas quedan disponibles para una nueva contratación si no tienen preventiva vencida ni otro impedimento, manteniendo su ubicación física. Si requieren la revisión de RN-MAN-04, quedan MANTENIMIENTO sin prolongar la reserva.
- El costo por uso del conjunto es cero.
- Si no hubo pago confirmado, no hay dinero que reembolsar.
- Si hubo pago confirmado, se registra la obligación de reembolso total y se gestiona conforme a RN-ALQ-01.

Un pago que se confirma después del vencimiento no puede reactivar la reserva ni habilitar el retiro de una bicicleta que ya se liberó. Debe registrarse y tratarse económicamente como un anticipo recibido para una contratación sin uso: corresponde su reembolso, sin duplicarlo si se repite la notificación.

## 4. Reserva con retiros parciales

Si se retiraron algunas bicicletas y otras no:

- Las que están en uso continúan acumulando su propio tiempo.
- Las pendientes de retiro vencen y se liberan al alcanzar el límite.
- Las nunca retiradas tienen costo real de uso cero.
- Se espera a que termine el uso de todas las unidades retiradas para liquidar el conjunto, incluyendo los anticipos de las no utilizadas.
- Si todas las unidades retiradas ya se habían devuelto antes del vencimiento, vencer los últimos detalles pendientes permite calcular la liquidación en ese momento.

Esto completa [RN-ALQ-02](03-alquiler-con-varias-bicicletas.md): el conjunto puede liquidarse cuando no queda ninguna unidad en uso ni pendiente de retiro. Un detalle vencido no bloquea indefinidamente el cierre.

## 5. Ejemplo de retiro parcial

Ejemplo ilustrativo: se anticipan ARS 4.000 por dos bicicletas, a un valor contratado de ARS 1.000 por hora durante dos horas cada una. Ese valor en pesos proviene de la tarifa USD y la cotización congeladas según [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md).

El ejemplo supone que no hay preventiva vencida ni otros impedimentos para volver a ofrecer la unidad liberada.

- 10:00: se confirma la contratación; vence a las 10:15.
- 10:02: se confirma el anticipo de ARS 4.000.
- 10:05: se retira la primera bicicleta; comienza su tiempo de uso.
- 10:15: la segunda nunca se retiró; vence su reserva y queda disponible, con costo de uso cero.
- 10:50: se devuelve la primera; utilizó 45 minutos y cuesta ARS 750.
- La liquidación total resulta ARS 750 frente a ARS 4.000 anticipados: corresponde reembolsar ARS 3.250.

No se cobra el tiempo que la primera bicicleta estuvo solamente reservada ni se factura un uso ficticio de la segunda.

## 6. Condiciones técnicas para respetar la regla

Estas condiciones derivan del comportamiento aprobado; no representan código ya implementado.

- La asignación de unidades y la validación de exclusividad deben ser transaccionales para impedir que dos solicitudes obtengan la misma bicicleta.
- No se mantiene una transacción o un bloqueo de base de datos durante los 15 minutos. Se persisten la reserva y su vencimiento, y cada operación crítica vuelve a validarlos.
- El vencimiento debe poder procesarse después de un reinicio o aunque el usuario cierre la página. Su mecanismo concreto de ejecución todavía se definirá al implementar.
- Antes de permitir un retiro o una nueva asignación se verifica el vencimiento, aunque una tarea de limpieza todavía no haya actualizado el estado visible.
- Un retiro y un vencimiento concurrentes deben producir un único resultado válido: o la unidad se retiró a tiempo y queda en uso, o venció sin retiro y se libera. Nunca ambos.
- El vencimiento no debe liberar una bicicleta que ya fue asignada a una reserva posterior.
- Los reintentos de vencimiento, liquidación o notificaciones de pago no deben generar reembolsos duplicados.
- Deben persistirse la fecha de confirmación, el vencimiento y el estado de cada detalle, conservando los hechos en el historial. Los nombres de los estados se fijarán al corregir el DER.
- Terminar el uso del conjunto y terminar el reembolso son hechos diferentes. Un reembolso pendiente no vuelve a reservar ni a alquilar las bicicletas.

## 7. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-03-01 | Otra persona solicita una bicicleta con reserva vigente | No obtiene una segunda reserva incompatible sobre la misma unidad |
| CP-ALQ-03-02 | Una unidad está reservada pero no retirada | No se ofrece a otros clientes, sigue ocupando su estación y no acumula tiempo de uso |
| CP-ALQ-03-03 | Retiro con anticipo confirmado antes del vencimiento | Comienza el uso de esa unidad y deja de ocupar un lugar en la estación de retiro |
| CP-ALQ-03-04 | Retiro cuando el backend alcanza o supera el vencimiento | Se rechaza el retiro sobre la reserva vencida |
| CP-ALQ-03-05 | Vencimiento sin pagos ni retiros | Se liberan las unidades, costo real cero y no se genera un reembolso inexistente |
| CP-ALQ-03-06 | Vencimiento con anticipo confirmado y ningún retiro | Se liberan las unidades y se registra un reembolso por la totalidad confirmada |
| CP-ALQ-03-07 | Vencimiento con una bicicleta en uso y otra sin retiro | Solo se libera la no retirada; la que está en uso continúa su viaje |
| CP-ALQ-03-08 | Todas las unidades retiradas ya volvieron, pero queda otra pendiente hasta el vencimiento | Al vencer la última pendiente se habilita una única liquidación conjunta |
| CP-ALQ-03-09 | Caso del ejemplo: anticipo ARS 4.000, una unidad usada 45 minutos y otra vencida sin retiro | Costo real total ARS 750 y reembolso correspondiente ARS 3.250 |
| CP-ALQ-03-10 | Pago confirmado después del vencimiento sin retiros | No reactiva la reserva; se registra y genera la obligación de reembolso correspondiente una sola vez |
| CP-ALQ-03-11 | Se reintenta el vencimiento o llega repetida una notificación de pago | No se duplican liquidaciones ni reembolsos, ni se modifica una nueva reserva de la unidad |
| CP-ALQ-03-12 | El cliente cierra la página o la aplicación se reinicia durante la reserva | El vencimiento persistido sigue siendo obligatorio y no se reinicia el plazo |

## 8. Decisiones que esta aprobación no incluye

- La cancelación voluntaria antes del vencimiento se aprobó posteriormente en [RN-ALQ-05](06-cancelacion-antes-del-retiro.md), sin necesidad de esperar a que transcurran los 15 minutos.
- La política de monedas y congelación se aprobó posteriormente en RN-ALQ-04. Quedan pendientes la fuente/tipo de cotización, su antigüedad admisible, tratamiento de fallos y redondeos.
- Máximo de unidades por alquiler y si la selección inicial debe pertenecer a una sola estación.
- Proveedor y medios de pago admitidos, modalidad de pruebas o producción.
- Control de un candado físico o simulación para la entrega.

No se realizaron pagos, reembolsos ni cambios de base de datos.
