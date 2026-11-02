# Pago externo con Mercado Pago

Fecha de aprobación: 1 de noviembre de 2026.

Estado: RN-PAG-05 aprobada para la refactorización. El usuario confirmó que el comprador debe pagar en la pantalla de Mercado Pago y elegir allí su medio, sin pedir ni administrar tarjetas dentro de Turismo Sustentable. También aprobó RN-PAG-03 del documento 31, después de distinguir el carrito de un pago ya enviado. No se implementó todavía esta integración ni se realizaron cobros o reembolsos.

## 1. Alcance aprobado

La pasarela de esta versión es únicamente Mercado Pago. El flujo elegido corresponde a la experiencia de Checkout Pro con redirección al sitio del proveedor y retorno a Turismo Sustentable. La selección concreta de API y su configuración se completarán al integrar; no se mezclan las variantes Orders y Preferences como si sus recursos o notificaciones fueran equivalentes.

No habrá un formulario propio para ingresar números de tarjeta o CVV, un ABM de tarjetas, una vinculación de tarjetas al perfil local ni una gestión propia de clientes/tarjetas de la pasarela. Los medios que el proveedor ofrezca y que se habiliten se eligen en su checkout. Esto no promete que cualquier medio resulte compatible con una reserva de quince minutos; su configuración queda pendiente de comprobar.

No se incorporan PERFIL_PAGO, MEDIO_PAGO_GUARDADO ni medio_pago_guardado_id en PAGO. La propuesta RN-PAG-04 de medios guardados se descarta para esta versión y se conserva como antecedente en el documento 31, no como requisito pendiente de aprobación.

El modelo lógico permanece en 28 entidades y 52 FK/relaciones. Las reglas aprobadas se reflejan en comentarios del Mermaid sin cambiar entidades, atributos, claves o relaciones por esta decisión. El campo plataforma se aclara como MERCADOPAGO en el alcance vigente; las pruebas automatizadas pueden usar dobles internos sin convertirlos en otra pasarela ofrecida al usuario.

## 2. Cambio respecto de la propuesta original

Las páginas 4 y 5 del [PDF original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>) incluían procesar pagos digitales y vincular métodos a la cuenta del usuario. La decisión actual ajusta ese alcance: se conservan los pagos digitales, pero la selección y administración de instrumentos financieros se delegan a Mercado Pago. No se afirma que Turismo Sustentable haya implementado una gestión local de medios guardados.

La formulación vigente para la documentación refactorizada es: el sistema permite iniciar pagos de anticipos y adicionales mediante redirección a Mercado Pago, validar sus resultados y conservar su trazabilidad y la de los reembolsos, sin administrar tarjetas localmente. Esta decisión sustituye para esta versión la interpretación de vinculación local de medios.

Los originales no se editan mediante esta aprobación. Al consolidar el documento académico deberá mostrarse el cambio de alcance y no presentar ambos requisitos como si siguieran vigentes simultáneamente. La entidad Tarjeta del código antiguo no se reutiliza para esta integración; retirarla y tratar sus datos corresponde al plan de refactorización/migración, no a una eliminación realizada ahora.

## 3. Responsabilidades del proveedor y del sistema

Mercado Pago presenta el entorno de pago, recibe los datos del instrumento financiero y procesa las operaciones de la modalidad integrada. Turismo Sustentable sigue siendo responsable de importes, plazo de reserva, autorización de retiro, cancelaciones, costo real, situación financiera y órdenes de reembolso conforme a las reglas aprobadas.

Se conservan PAGO, REEMBOLSO, HISTORIAL_ESTADO_PAGO e HISTORIAL_ESTADO_REEMBOLSO. Representan las operaciones del alquiler y su trazabilidad, no una copia de la tarjeta ni de toda la información que almacena el proveedor. El importe original de cada intento y cada reembolso no se sobrescribe para ocultar cambios posteriores.

La devolución corresponde al pago de origen; el cliente no elige otra tarjeta para recibirla dentro de nuestra web. Un adicional requiere la acción de pago ya acordada, sin habilitar débito automático por esta integración. Un reembolso solicitado no se muestra como confirmado hasta validar su resultado.

## 4. Flujo de pago previsto

1. En el carrito se seleccionan las unidades. Antes de confirmar puede editarse la selección y el importe se calcula para la selección final; no hay un pago por una bicicleta quitada del carrito.
2. Al confirmar se registra la contratación con sus detalles, origen común, tarifas/cotización y vencimiento original, conforme a RN-ALQ-03/RN-ALQ-11.
3. Cuando corresponde iniciar el pago, el backend determina el importe exigible y registra su operación local. Genera el recurso de checkout de Mercado Pago con los datos necesarios y devuelve el destino autorizado de pago.
4. El usuario paga en Mercado Pago y puede volver a la aplicación con un resultado de éxito, rechazo o pendiente. La pantalla de retorno no decide el estado financiero ni autoriza un retiro.
5. El backend valida las comunicaciones y consulta/concilia el resultado mediante los mecanismos de la modalidad elegida, comprobando relación con el intento/alquiler, cuenta receptora, entorno, importe y moneda. Registra estado e historial sin duplicar efectos.
6. Solo el anticipo requerido confirmado, junto con reserva vigente y demás controles, puede habilitar los retiros pendientes. Ni la redirección ni crear el checkout equivalen a cobrar.

No se conserva una transacción o bloqueo de base de datos durante todo el tiempo que el comprador permanece en Mercado Pago. Las transacciones locales coordinan los cambios del negocio y sus historiales; las operaciones externas y sus respuestas requieren seguimiento e idempotencia.

Si el usuario no vuelve al sitio o cierra la pestaña, el resultado debe poder conciliarse igualmente. Cambiar parámetros del retorno, reutilizar una notificación o recibir eventos fuera de orden no debe duplicar cobros/reembolsos ni habilitar un viaje sin pago validado.

## 5. Cancelaciones y pagos tardíos

RN-PAG-03 queda aprobada con la distinción de momentos indicada en el documento 31. Quitar una unidad del carrito antes de confirmar implica pagar solo la selección final. Cancelar una reserva antes de iniciar cualquier solicitud externa implica solicitar solo el anticipo de las unidades aún reservadas, conservando la estimación histórica del contrato.

Si ya existe un pago en proceso o un recurso externo que puede seguir recibiendo dinero, no se presupone que cerrar la pestaña o cancelar localmente detuvo el cobro. Se conserva el importe del intento y se concilia su resultado. Al reemplazar un checkout con importe anterior deberán comprobarse su invalidación/ausencia de operación incierta conforme a la modalidad, sin abrir cobros incompatibles a ciegas.

Si se confirma a tiempo, solo pueden retirarse unidades que sigan reservadas. El excedente se trata en el ajuste conjunto. Ante rechazo o cancelación confirmados se puede evaluar un nuevo intento por las restantes dentro del plazo original. Cancelar todo o vencer la reserva impide retiros posteriores aunque llegue dinero después; se registra y concilia sin reactivar unidades.

## 6. Lo que aún requiere integración y diseño físico

Quedan por elegir y comprobar la variante de API de Checkout Pro, las credenciales de prueba, los medios habilitados, las URLs de retorno/notificación, el mapeo de estados y las consultas autorizadas. La experiencia de redirección ya está elegida; no queda pendiente volver a decidir entre pantalla externa y gestión de tarjetas propia.

Se distinguirán los identificadores del recurso de checkout, orden y pago real que utilice esa API. No se introduce una FK a una tarjeta guardada ni se asume que una preferencia, una orden, un intento local y cada transacción externa siempre coinciden uno a uno. La representación precisa de las correlaciones, su unicidad, la gestión de reintentos o pagos divididos y cualquier campo adicional se revisarán antes de dar por definitivo el esquema físico de PAGO.

Se verificarán mínimos/plazos de cobro y reembolso y su funcionamiento en pruebas. Los pagos pendientes que superen los quince minutos no amplían la reserva: se aplican RN-ALQ-03/RN-PAG-03. No se modifican silenciosamente costos o vencimientos para adaptarlos a un proveedor.

Las claves privadas son configuración protegida del backend. No se guardan datos completos de tarjeta, CVV o tokens transitorios de tarjeta en nuestro modelo, auditoría o respuestas. Las referencias de las operaciones y los datos mínimos del pagador que se requieran también son privados y deben protegerse.

## 7. Criterios de aceptación

Son especificaciones para implementar, no pruebas ejecutadas:

| Caso | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-PAG-05-01 | Se inicia el anticipo o un adicional | La aplicación genera la operación autorizada y dirige al usuario a Mercado Pago, sin pedir datos de tarjeta en un formulario propio |
| CP-PAG-05-02 | Se modifican parámetros del retorno para simular éxito | El backend no marca APROBADO ni habilita un retiro por esos parámetros |
| CP-PAG-05-03 | Llega una confirmación validada y compatible con el intento | Se actualizan operación e historial una sola vez, con importe/moneda y vínculo correctos |
| CP-PAG-05-04 | El comprador cierra la pestaña antes de volver | La conciliación puede actualizar el pago sin depender del retorno del navegador |
| CP-PAG-05-05 | Se cancela una unidad y llega el pago original | Se aplica RN-PAG-03 sin reactivar la unidad ni duplicar el ajuste |
| CP-PAG-05-06 | Se consulta el perfil del usuario | No ofrece un ABM local de tarjetas ni declara falsamente que están vinculadas al sistema |
| CP-PAG-05-07 | Se revisan registros de pago y reembolso | Se conservan importes, referencias y estados/historiales, sin necesitar una tarjeta local para reconstruir los movimientos |

## 8. Evidencia de la aprobación y documentación oficial

El usuario confirmó el 1 de noviembre que aprueba el tratamiento explicado de cancelación durante el anticipo y que quiere pagar en la pantalla de Mercado Pago, sin pedir ni administrar tarjetas desde Turismo Sustentable. Esa es la autoridad para ajustar el alcance y descartar las dos entidades, no la mera disponibilidad de una API.

La documentación oficial consultada ese día respalda la experiencia de redirección de Checkout Pro:

- [Redirigir al comprador al checkout](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-orders/web-integration/redirect-buyer-to-checkout?scope=prod).
- [Configurar URLs de retorno](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-orders/web-integration/configure-back-urls?scope=prod).
- [Configurar notificaciones de pago](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-orders/notifications?scope=prod).

Los enlaces de Orders verifican que existe ese flujo; no equivalen a elegir o implementar esa API. No se conectó una cuenta, no se generaron credenciales y no se ejecutaron pagos, reembolsos, migraciones o pruebas de negocio. Java y los archivos originales permanecen sin cambios.
