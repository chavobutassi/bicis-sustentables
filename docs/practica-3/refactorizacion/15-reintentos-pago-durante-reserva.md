# RN-PAG-02 Reintentos de pago dentro de la reserva

Fecha de aprobación: 28 de octubre de 2026.

Estado: aprobada para implementar. No implementada en Java ni en la base de datos. Los casos de prueba de este documento se especifican para ejecución futura; no se realizaron cobros ni reembolsos.

## 1. Decisión aprobada

Un rechazo confirmado del anticipo no cancela automáticamente la contratación ni libera sus bicicletas. El cliente puede volver a intentar el pago mientras siga vigente el plazo original de 15 minutos y no haya cancelado la reserva.

El límite de negocio es el tiempo de reserva, no una cantidad de dos intentos. Un segundo rechazo tampoco provoca por sí solo la cancelación. Cada intento conserva su resultado y su trazabilidad conforme a [RN-PAG-01](14-estados-pago-y-reembolso.md).

No se reinicia el reloj al recibir un rechazo, generar otro intento o confirmar un pago. Los mismos 15 minutos cubren tanto pagar como retirar las bicicletas, según [RN-ALQ-03](04-reserva-y-vencimiento.md).

## 2. Efectos del rechazo sobre los estados

| Elemento | Efecto de un rechazo inicial confirmado antes del vencimiento |
| --- | --- |
| Intento de pago | Queda RECHAZADO y se conserva en el historial de operaciones |
| Cabecera del alquiler sin retiros | Sigue RESERVADO mientras conserve unidades con reserva vigente |
| Bicicletas de esa reserva | Siguen RESERVADA, sin ofrecerse a otros clientes |
| Ubicación y capacidad | Las unidades permanecen físicamente en su estación y continúan ocupando lugar |
| Autorización de retiro | No se habilita por un pago rechazado; exige el anticipo requerido confirmado y plazo vigente |
| Vencimiento | Conserva la fecha y hora originales |

El rechazo no inicia el uso, no acumula costo de viaje y no acredita dinero recibido. No se elimina el intento rechazado ni se sobrescribe como aprobado para representar un intento posterior distinto.

Esta regla se refiere al anticipo de una reserva. Rechazar un pago adicional de una liquidación no borra la deuda ni vuelve a reservar la bicicleta; se mantienen RN-ALQ-01 y RN-ALQ-08.

## 3. Condiciones para reintentar sin duplicar cobros

El backend verifica la propiedad de la contratación, su vigencia y el resultado del intento anterior. El reintento posterior a un rechazo es una nueva operación identificable, no una repetición ciega del mismo cobro.

Si el resultado anterior sigue pendiente o es incierto por falta de respuesta, se debe consultar o conciliar antes de permitir otro cobro. Un timeout no se convierte en RECHAZADO para habilitar un segundo intento. Tampoco se crea otro anticipo cuando el requerido ya está confirmado.

La implementación debe impedir que dos clics o solicitudes simultáneas creen cobros incompatibles. Los controles técnicos de frecuencia, las restricciones del proveedor y su integración se definirán al implementar; no se introduce mediante este documento una cancelación por número de rechazos.

## 4. Cancelación y vencimiento

El cliente puede cancelar voluntariamente antes del retiro, sin esperar a consumir los 15 minutos, conforme a [RN-ALQ-05](06-cancelacion-antes-del-retiro.md).

Al alcanzar el vencimiento, ya no se permiten nuevos intentos para habilitar esa reserva ni nuevos retiros sobre ella. Se liberan únicamente las unidades no retiradas. Si nunca hubo retiros, la cabecera queda VENCIDO, no CANCELADO por rechazo de pago.

Un intento iniciado antes del límite no extiende la reserva mientras la pasarela responde. Un pago que se confirma después del vencimiento se registra y concilia sin reactivar la reserva; su devolución se trata conforme a RN-ALQ-03. Si no hubo dinero recibido, no se inventa un reembolso.

Una respuesta tardía de rechazo tampoco puede alterar una bicicleta ya liberada o asignada a otra contratación. Los efectos deben corresponder a la reserva y al intento correctos.

## 5. Ejemplo

- 10:00: se confirma la contratación; el vencimiento se fija a las 10:15.
- 10:04: se confirma el rechazo del primer intento; las bicicletas continúan reservadas.
- 10:07: se confirma un segundo rechazo; quedan ocho minutos y no se cancela por ese motivo.
- 10:10: se confirma un nuevo intento exitoso; el cliente puede retirar hasta antes de las 10:15, no hasta las 10:25.
- 10:15: las unidades que no se retiraron vencen, aunque el anticipo se hubiera pagado antes. Se conserva el tratamiento económico ya aprobado para unidades no utilizadas.

## 6. Contraste con los documentos originales

Se releyeron el [diccionario de estados](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y el [PDF de visión del proyecto](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>) antes de registrar esta decisión. Ambos se conservaron intactos.

El flujo 11a del PDF y la descripción original de CANCELADO en el Word vinculaban el rechazo con la cancelación. La decisión expresa del usuario sustituye ese comportamiento para el anticipo: el rechazo no cambia la reserva ni el estado de sus bicicletas; pueden existir nuevos intentos dentro del mismo plazo.

Se conservan el pago previo al retiro, los estados independientes, el registro de operaciones y la exclusividad de las bicicletas. Las demás excepciones del Word/PDF no quedan aprobadas por extensión.

## 7. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-PAG-02-01 | Primer rechazo confirmado antes de vencer | Se conserva el intento RECHAZADO, la cabecera RESERVADO y las bicicletas RESERVADA |
| CP-PAG-02-02 | Segundo rechazo confirmado con tiempo restante | No se cancela por la cantidad de rechazos; puede iniciarse otro intento válido |
| CP-PAG-02-03 | Se recibe un rechazo y luego se reintenta | El vencimiento original no cambia |
| CP-PAG-02-04 | El anticipo se aprueba a las 10:10 para una reserva que vence a las 10:15 | El pago no extiende el límite de retiro a las 10:25 |
| CP-PAG-02-05 | Se solicita otro cobro con el anterior pendiente o incierto | Se consulta o concilia el anterior antes de habilitar otro cobro |
| CP-PAG-02-06 | Se alcanza el vencimiento sin pagar ni retirar | Se rechaza un nuevo intento sobre esa reserva, se liberan las unidades y la cabecera queda VENCIDO |
| CP-PAG-02-07 | El cliente cancela toda la reserva sin retiros después de un rechazo | Se libera por la cancelación voluntaria y la cabecera queda CANCELADO |
| CP-PAG-02-08 | Un pago iniciado a tiempo se confirma después del vencimiento | Se registra y concilia sin reactivar unidades ni habilitar su retiro |
| CP-PAG-02-09 | Llega un rechazo tardío cuando la bicicleta pertenece a otra reserva | No altera el estado, ubicación ni asignación de la nueva contratación |
| CP-PAG-02-10 | Dos solicitudes simultáneas intentan iniciar el mismo anticipo | No se generan cobros incompatibles o duplicados |

Mercado Pago ya fue elegido como única pasarela y RN-PAG-05 del [documento 32](32-pago-externo-con-mercadopago.md) confirma el checkout externo sin tarjetas locales. RN-PAG-03 del [documento 31](31-revision-pagos-reembolsos-y-medios-guardados.md) ya aprobó el tratamiento de la cancelación parcial durante el anticipo. Siguen pendientes la variante de API, los medios habilitados y los controles/pruebas de integración, no esas decisiones de negocio. No se modificaron código, base de datos ni archivos originales.
