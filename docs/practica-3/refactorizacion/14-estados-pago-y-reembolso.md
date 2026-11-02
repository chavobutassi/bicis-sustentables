# RN-PAG-01 Estados de pago y reembolso

Fecha de aprobación: 28 de octubre de 2026.

Estado: aprobados los cinco estados de cada intento de pago, los cuatro estados de cada reembolso y la conservación del pago original. Después el usuario eligió Mercado Pago para una integración futura orientada a pruebas, registrada en el documento 23. No se eligió todavía la modalidad concreta ni se implementó la integración; no se realizaron movimientos de dinero.

## 1. Fuentes y alcance de la aprobación

Antes de registrar esta decisión se releyeron completos el [diccionario de estados original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y el [PDF de visión del proyecto](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), y se contrastó el [DER v4 original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>). Los originales se conservaron sin cambios.

El Word ya separaba el resultado del pago del estado del alquiler y contemplaba devoluciones de dinero. El PDF exige pagos digitales vinculados al alquiler, registro de estados y trazabilidad. Esta decisión conserva esos objetivos y precisa las diferencias entre pago aprobado, reembolso parcial y reembolso total conforme a las reglas de cobro ya aprobadas.

La aprobación inicial de estos estados no resolvió por sí sola el efecto del rechazo sobre la reserva. Posteriormente el usuario aprobó [RN-PAG-02](15-reintentos-pago-durante-reserva.md): un rechazo confirmado no cancela ni libera las bicicletas y permite reintentar dentro de los 15 minutos originales, sin reiniciar el plazo. Esta decisión sustituye expresamente la cancelación inmediata del flujo original.

## 2. Estados aprobados de cada intento de pago

| Estado | Significado |
| --- | --- |
| CREADO | Intento registrado localmente, con importe, moneda y finalidad identificados |
| PENDIENTE | Se inició la gestión del pago, pero todavía falta un resultado confirmado y validado |
| APROBADO | El backend validó la confirmación de pago exitoso del proveedor |
| RECHAZADO | El proveedor confirmó el rechazo de ese intento |
| CANCELADO | Se confirmó la cancelación de esa operación de pago |

CREADO identifica la existencia del intento local; no certifica que la solicitud ya haya llegado a la pasarela. PENDIENTE no equivale a dinero cobrado. La integración deberá guardar también las referencias y respuestas externas necesarias para conciliar el resultado.

Un cambio de pantalla o una redirección del navegador no acredita por sí solo el pago. La confirmación se valida en el backend mediante el mecanismo de la modalidad de Mercado Pago que se integre. CANCELADO no se asigna a un pago externo solo porque el alquiler se haya cancelado o vencido.

Estos estados describen cada intento, no la totalidad de los pagos de un alquiler. Un intento rechazado debe conservarse aunque posteriormente exista otro aprobado.

## 3. Estados aprobados de cada operación de reembolso

| Estado | Significado |
| --- | --- |
| PENDIENTE | Devolución de dinero registrada, todavía sin solicitud confirmada al proveedor |
| EN_PROCESO | Solicitud en gestión o con resultado externo todavía pendiente de conciliación |
| CONFIRMADO | El backend validó que el proveedor confirmó la operación de reembolso |
| FALLIDO | Existe un fallo confirmado que requiere atención o un reintento seguro |

Un timeout o la falta de respuesta no prueban que una devolución haya fallado. Antes de repetirla se debe conciliar su resultado para no devolver dos veces el mismo importe. La política concreta de reintentos y la intervención administrativa se definirán con la integración, sin suponer un proveedor ni una frecuencia automática.

CONFIRMADO expresa la confirmación validada del proveedor. No promete que el dinero aparezca inmediatamente en la cuenta bancaria del cliente.

## 4. Relación entre pago y reembolsos

El pago original conserva su importe y su historia. Los reembolsos se registran por separado y vinculados al pago que devuelve el dinero. La revisión posterior del DER utiliza entidades PAGO y REEMBOLSO; el usuario autorizó además incorporar HISTORIAL_ESTADO_PAGO e HISTORIAL_ESTADO_REEMBOLSO con campos, claves y relaciones, como se detalla en el [documento 24](24-propuesta-historial-financiero.md). Esa representación lógica ya figura en el modelo de trabajo, pero no se creó todavía en Java ni en la base de datos.

La devolución parcial o total se determina con los importes de los reembolsos confirmados relacionados, no reemplazando el importe histórico ni sobrescribiendo el pago como REEMBOLSADO. El estado REEMBOLSADO del Word original se sustituye en este diseño por ese registro independiente, aprobado expresamente por el usuario.

No se considera devuelto dinero por el solo hecho de solicitarlo. Los movimientos pendientes, rechazados o fallidos no deben tratarse como un cobro o reembolso confirmado.

## 5. Relación con las reglas del alquiler

Se conservan las reglas ya aprobadas de anticipo, cobro por uso real, tarifa y cotización congeladas, liquidación conjunta y situación financiera independiente:

- Un reembolso pendiente o fallido no reactiva un viaje terminado ni mantiene ocupada una bicicleta ya devuelta válidamente.
- La obligación de devolver dinero sigue existiendo mientras no se complete el reembolso que corresponde. No constituye deuda del cliente.
- Un pago adicional rechazado no elimina el saldo pendiente surgido de la liquidación.
- Un pago confirmado después de cancelarse o vencer una contratación no reactiva sus unidades; debe registrarse y conciliarse conforme a las reglas de devolución del anticipo.
- Los movimientos se registran en ARS conforme a [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md), y solo los confirmados modifican el saldo conforme a [RN-ALQ-08](11-situacion-financiera-alquiler.md).

## 6. Criterios de aceptación

Los siguientes casos quedan especificados para pruebas futuras. No se ejecutaron.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-PAG-01-01 | Se registra un intento local sin resultado externo | No se muestra como cobrado ni habilita un retiro por sí solo |
| CP-PAG-01-02 | El proveedor confirma y el backend valida un pago exitoso | Se registra APROBADO una sola vez para esa operación |
| CP-PAG-01-03 | Se confirma el rechazo de un intento | Se conserva RECHAZADO; no se registra dinero cobrado |
| CP-PAG-01-04 | Se cancela el alquiler mientras la pasarela no ha confirmado su resultado | No se inventa una cancelación externa del pago; se concilia el resultado |
| CP-PAG-01-05 | Se registra un reembolso parcial confirmado | Se conserva el pago original y se identifica el importe efectivamente reembolsado |
| CP-PAG-01-06 | Falta la respuesta a una solicitud de reembolso | No se presupone un fallo ni se repite el movimiento a ciegas |
| CP-PAG-01-07 | Se confirma que falló un reembolso debido al cliente | La obligación permanece y no se bloquea al cliente por esa devolución pendiente |
| CP-PAG-01-08 | Llega un pago confirmado para una contratación vencida sin retiros | Se registra y concilia el dinero sin reactivar la reserva |
| CP-PAG-01-09 | Llega dos veces la misma confirmación de pago o reembolso | No se duplica el movimiento ni su efecto en el saldo |

## 7. Aclaraciones aprobadas y decisiones pendientes

- RN-PAG-03 del [documento 31](31-revision-pagos-reembolsos-y-medios-guardados.md) ya aprobó la cancelación parcial durante el anticipo, distinguiéndola de editar el carrito antes de enviar un pago. Se conserva el intento en gestión y se concilia antes de otro cobro; no está implementado.
- Mercado Pago es la única pasarela y RN-PAG-05 del [documento 32](32-pago-externo-con-mercadopago.md) eligió Checkout Pro con redirección, sin administrar tarjetas localmente. Quedan variante de API, correlaciones, medios compatibles, pruebas e integración. El sustituto local es un antecedente no adoptado, no una segunda pasarela autorizada ni una integración probada.
- Mapeo de respuestas externas a los estados internos, validación de notificaciones, conciliación, límites y reintentos seguros.
- Entidades, restricciones y datos concretos de pagos y reembolsos en el DER revisado. No se fuerza una cantidad fija de tablas.
- Tratamiento de eventos posteriores fuera del recorrido definido, como disputas o contracargos; no se dan por modelados con este catálogo.

La aprobación de nombres y significados no aprueba automáticamente todos los recorridos excepcionales ni todas las transiciones propuestas en otros documentos.
