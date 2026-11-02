# Pasarela Mercado Pago y desarrollo con pruebas

Fecha: 28 de octubre de 2026.

Estado actualizado al 1 de noviembre de 2026: Mercado Pago es la única pasarela del alcance y la experiencia elegida es Checkout Pro con pantalla externa, según RN-PAG-05 del documento 32. No se pedirán ni administrarán tarjetas desde Turismo Sustentable y se descartaron las dos entidades de medios guardados. Quedan la variante de API y detalles de integración/pruebas. Un adaptador local se conserva solo como antecedente propuesto, no como pasarela autorizada para esta versión. No se crearon cuentas, aplicaciones, credenciales ni código de integración; no se hicieron cobros o reembolsos.

## 1. Qué resuelve cada componente

Mercado Pago ejecuta y comunica las operaciones financieras de la modalidad integrada. Turismo Sustentable conserva las reglas del alquiler: reservar, autorizar el retiro, medir uso, congelar tarifa/cotización, revisar incidencias, liquidar el conjunto y decidir cuánto corresponde cobrar o devolver. La pasarela no conoce por sí sola cuánto tiempo se utilizó cada bicicleta ni cuándo ADMIN validó un corte de uso.

| Registro propio | Qué representa | Vínculo con la pasarela |
| --- | --- | --- |
| PAGO | Cada intento de cobro, su importe, finalidad y resultado validado | Referencias externas, estado conciliado y control de duplicados; no datos completos de una tarjeta |
| REEMBOLSO | Cada devolución de dinero vinculada al pago original | Importe solicitado, estado, referencia del reembolso y confirmación de la pasarela |
| INCIDENCIA | Un hecho operativo del detalle: falla, accidente, pérdida o robo, reporte y decisión | No es una operación de Mercado Pago; su resolución puede afectar el costo antes de liquidar |

Ejemplo ficticio: se confirma un PAGO de ARS 2.000; el costo final validado es ARS 750; corresponde un REEMBOLSO de ARS 1.250 al pago original. El registro de PAGO no se cambia a ARS 750. El reembolso sigue pendiente hasta que se valida su resultado. La misma devolución de dinero puede corresponder a un regreso anticipado sin ninguna incidencia; una incidencia no implica por sí sola un reembolso.

## 2. Por qué conservar registros locales

No se pretende replicar Mercado Pago ni guardar todas sus respuestas. Se conserva lo necesario para vincular sus operaciones al alquiler, explicar el saldo, atender errores y evitar duplicados. Una solicitud enviada no prueba que se haya cobrado o devuelto el dinero, y una pantalla de éxito tampoco sustituye la confirmación del backend.

REEMBOLSO como tabla separada es una propuesta de modelado del DER v5, no un requisito impuesto por Mercado Pago. Podría usarse un modelo unificado de movimientos financieros; con el DER original, una entidad propia hace explícitos la dirección del dinero, el pago de origen y los estados separados. No exige crear una tabla para cada llamada o reintento HTTP. Reenviar la misma operación incierta requiere conciliación e idempotencia, no generar otra devolución ciegamente.

INCIDENCIA es independiente del dinero: autor, detalle afectado, descripción, fechas informada/registrada, decisión de ADMIN, corte validado y recepción física posterior. No se sustituye por el estado de un pago ni por observaciones que se sobrescriban. Se conserva RN-INC-01, incluida la devolución inmediata con importe provisional cuando hay una revisión económica pendiente.

## 3. Cuenta, aplicación y entorno de prueba

La documentación oficial parte de una cuenta de Mercado Pago y de crear/configurar una aplicación en su panel de integración. La aplicación reúne las credenciales y herramientas del producto elegido; no se presupone otra cuenta independiente llamada cuenta de desarrollador.

Hay herramientas de prueba, credenciales, tarjetas y cuentas con saldo ficticio. Qué cuentas y pasos se necesitan depende del producto y del escenario. No se promete que todas las capacidades de producción se reproduzcan de la misma manera. La separación de entornos debe ser explícita y no deducirse de un prefijo de credencial que puede variar por producto.

La experiencia de checkout externo ya está elegida. Quedan la variante de API, los medios que encajen con la reserva de 15 minutos, las notificaciones y conciliación, y verificar específicamente los reembolsos parciales en esa variante. No se supone que un pago tardío reactive la reserva ni que Mercado Pago aplique automáticamente nuestras cancelaciones o reembolsos. RN-PAG-03 ya aprobó cómo tratar una cancelación durante el anticipo.

La intención de usar pruebas no es autorización para mover dinero real. Tampoco confirma por sí sola las exigencias del profesor sobre hardware o sobre una demostración exclusivamente de prueba. No se solicita al usuario que configure la cuenta ahora.

Las claves privadas permanecerán fuera del frontend, repositorio, auditoría y respuestas HTTP. No se almacenan números de tarjeta ni CVV para reemplazar el servicio. RN-PAG-05 cerró el alcance de medios: el comprador los elige en Mercado Pago y Turismo Sustentable no administra tarjetas locales ni copia la entidad Tarjeta actual. No se presenta esa decisión como una vinculación de medios implementada dentro de nuestra aplicación.

La revisión del 1 de noviembre está en el [documento 31](31-revision-pagos-reembolsos-y-medios-guardados.md). Su propuesta inicial de PERFIL_PAGO y MEDIO_PAGO_GUARDADO quedó descartada al elegir el usuario pagar en la pantalla de Mercado Pago, sin gestionar tarjetas localmente. La decisión vigente y su diferencia frente al requisito del PDF están en [RN-PAG-05](32-pago-externo-con-mercadopago.md). La documentación de tarjetas guardadas queda como referencia del análisis anterior, no como función a implementar.

## 4. Antecedente de sustituto local no adoptado

La propuesta siguiente se conserva como antecedente. No amplía el alcance aprobado de una única pasarela Mercado Pago ni autoriza una simulación pública que marque pagos como reales. Utilizar dobles internos para pruebas automatizadas no equivale a ofrecer otra pasarela al usuario.

Se propone separar la lógica del alquiler del acceso a la pasarela mediante una interfaz, por ejemplo PasarelaPago. Un adaptador local podría simular cobros, resultados pendientes/rechazados y reembolsos; después un adaptador de Mercado Pago usaría el mismo contrato de negocio. Los nombres y la implementación quedan pendientes.

La simulación no sería solamente devolver éxito en todos los casos. Debería permitir probar los resultados que afectan al alquiler, conservar los mismos registros y respetar la ausencia de duplicados. Se activaría únicamente en desarrollo/pruebas, identificando proveedor SIMULADA y entorno de prueba, sin exponer al cliente una operación pública para marcar su pago como aprobado.

Un adaptador local no equivale a integrar Mercado Pago en su entorno de pruebas. La primera opción prueba nuestra lógica sin contactar la pasarela; la segunda verifica la comunicación real con sus herramientas de prueba. En documentación y demostraciones se distinguirán expresamente.

No se implementa ninguno ahora. Se propone conservar esa separación al escribir los servicios para no rehacer el dominio cuando llegue la integración.

## 5. Impacto en el DER y las decisiones vigentes

La elección de Mercado Pago no agrega una tabla llamada MercadoPago: se mantienen PAGO, REEMBOLSO e INCIDENCIA. Se actualiza el proveedor previsto y se propone identificar el entorno del pago; el reembolso hereda proveedor y entorno de su pago de origen. Las referencias exactas de orden/transacción/reembolso se completarán al elegir el producto. El primer borrador tenía 24 entidades; los historiales financieros del documento 24 lo ampliaron a 26 por trazabilidad propia. Posteriormente los catálogos de identificación del [documento 25](25-revision-personas-usuarios-y-roles.md) lo llevaron a 28, sin nuevos requisitos de la pasarela ni cambios de los movimientos financieros.

No cambia la tarifa por tipo, la cotización congelada, el cobro por tiempo validado, la liquidación conjunta ni la revisión previa de incidencias que puedan afectar el importe. Mercado Pago es la única pasarela y Checkout Pro la experiencia elegida. Siguen pendientes la variante de API, los medios habilitados, pruebas concretas, integración y migración. No se incorporan entidades de tarjetas por la decisión actual.

## Fuentes oficiales consultadas

Verificación de documentación el 28 de octubre de 2026, no una prueba de integración:

- [Primeros pasos y acceso al panel](https://www.mercadopago.com.ar/developers/es/docs/getting-started).
- [Aplicación, recursos y separación de entornos](https://www.mercadopago.com.ar/developers/es/docs/your-integrations/application-details).
- [Cuentas de prueba, tarjetas y saldo ficticio](https://www.mercadopago.com.ar/developers/es/docs/your-integrations/test/accounts).
- [Creación de aplicaciones y credenciales](https://www.mercadopago.com.ar/developers/es/news/2025/11/17/Create-your-applications-in-Mercado-Pago-with-a-simpler-and-guided-flow).
- [Reembolsos totales y parciales](https://www.mercadopago.com.ar/developers/es/docs/sales-processing/cancellations-and-refunds).

Los endpoints, eventos y restricciones deberán verificarse de nuevo contra la modalidad elegida al integrar. No se ejecutaron pruebas de API ni se conectaron cuentas.
