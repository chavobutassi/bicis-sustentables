# Revisión de pagos reembolsos y medios guardados

Fecha de revisión: 1 de noviembre de 2026.

Estado actualizado: RN-PAG-03 aprobada el 1 de noviembre de 2026, después de distinguir el carrito de una solicitud de pago ya enviada. La propuesta RN-PAG-04 de medios guardados se descartó para esta versión: el usuario eligió pagar en la pantalla de Mercado Pago sin administrar tarjetas localmente, documentado como RN-PAG-05 en el archivo 32. No se implementaron estos recorridos en Java o MySQL ni se realizaron movimientos de dinero o pruebas de integración.

El modelo lógico vigente conserva 28 entidades y 52 FK/relaciones. PAGO, REEMBOLSO y sus dos historiales ya están incorporados con aprobación. PERFIL_PAGO, MEDIO_PAGO_GUARDADO y su FK desde PAGO no se incorporan: sus campos se conservan en la sección 5 solo como antecedente de una propuesta descartada, no como alcance vigente ni como tareas pendientes.

## 1. Fuentes y alcance de la revisión

Se contrastaron los requerimientos de pagos y métodos vinculados de las páginas 4 y 5 del [PDF original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), el apartado de PAGO del [diccionario original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>), PAGO/USUARIO del [DER v4](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>) y las aprobaciones de esta carpeta. Los originales se mantienen intactos.

Se mantienen pago previo al retiro, intentos rechazados conservados, reintentos dentro de los quince minutos originales, importes y cotización contratados, cancelación de unidades no retiradas, liquidación conjunta, reembolsos separados y trazabilidad financiera. REEMBOLSADO del Word no se reintroduce en PAGO: esa diferencia ya fue aprobada.

La documentación oficial de Mercado Pago consultada el 1 de noviembre distingue cliente externo y tarjetas asociadas en su función de tarjetas guardadas. Esa capacidad no obliga a gestionarlas localmente: el usuario eligió después Checkout Pro con pantalla externa, sin gestión de tarjetas en Turismo Sustentable. La variante de API aún requiere elección y pruebas. Las dos tablas inicialmente propuestas fueron una alternativa de diseño, no una exigencia de Mercado Pago, y quedaron descartadas para este alcance.

## 2. Qué se conserva en el bloque financiero

| Elemento vigente | Representación y condiciones |
| --- | --- |
| PAGO.id | PK local; no es el identificador que asigna la pasarela |
| PAGO.alquiler_id | FK obligatoria; muchos intentos o adicionales pueden pertenecer al mismo alquiler |
| PAGO.estado_pago_id | FK al catálogo de cinco estados aprobado; el cliente no decide libremente su resultado |
| PAGO.finalidad | Distingue ANTICIPO de ADICIONAL; los códigos físicos siguen pendientes, sin otro catálogo propuesto aquí |
| PAGO.monto_ars y moneda | Importe de ese intento, positivo cuando se solicita dinero, ARS y dos decimales; no se sobrescribe tras una cancelación o reembolso |
| PAGO.fecha_creacion y fecha_confirmacion | Registro local y confirmación validada; la segunda queda nula hasta el éxito, sin inventar dinero recibido |
| PAGO.plataforma y entorno | Identifican la integración y separan PRUEBA de PRODUCCION; un resultado simulado no es una confirmación de Mercado Pago |
| PAGO.referencia_externa | Correlación externa opcional antes de obtenerla; su significado e índice exactos se concretan al elegir el producto |
| PAGO.clave_idempotencia y version | Identidad de la operación al reenviarla y control de concurrencia; no equivalen por sí solos a una integración libre de duplicados |
| REEMBOLSO.pago_id | FK obligatoria al pago confirmado de origen; no se duplica alquiler_id ni usuario_id |
| REEMBOLSO.monto_ars, moneda, estado y fechas | Importe positivo en ARS, cuatro estados controlados y fechas propias; solicitar no equivale a devolver dinero |
| REEMBOLSO.motivo, referencia_externa, clave_idempotencia y version | Justificación, conciliación y control de esa devolución, sin modificar el monto del pago original |
| Ambos historiales financieros | Conservan estado anterior/nuevo, fecha local, fecha externa si existe, actor/origen y correlación; estado actual e historial se mantienen en una transacción local |

No hace falta otro historial que duplique los dos ya aprobados. AUDITORIA_SISTEMA cubre hechos relevantes sin transición de estado, incluido el tratamiento de notificaciones repetidas; no se inventan transiciones para llenar un historial.

## 3. RN-PAG-03 aprobada sobre cancelación durante el anticipo

### Antes de iniciar un pago externo

Si el usuario quita una bicicleta del carrito y confirma las dos restantes, se solicita el pago por dos, no por tres, y no existe un reembolso de dinero no recibido. Si ya confirmó la reserva pero todavía no se inició una solicitud ni se creó un recurso externo cobrable, se solicita el anticipo de las unidades que aún conservan reserva vigente, sin reescribir la estimación histórica del contrato.

Un eventual intento puramente local con importe anterior se conserva y se invalida localmente de forma trazable antes de generar el correcto; no se inventa una cancelación externa. Que una fila figure CREADO, que el cliente no haya vuelto o que haya ocurrido un timeout no prueba por sí solo que la solicitud nunca llegó al proveedor. Si hay un recurso externo o resultado incierto se aplica el recorrido siguiente, verificando su conciliación/invalidación antes de reemplazarlo.

### Cancelar no modifica el intento externo

Si se cancela una unidad no retirada dentro del plazo vigente, su cancelación y liberación se registran inmediatamente según RN-ALQ-05. El PAGO que ya está en gestión conserva su importe, clave y referencias. No se lo marca CANCELADO por una cancelación local del alquiler ni se presupone que la pasarela dejó de procesarlo.

Tampoco se reescribe el costo estimado inicial del contrato ni sus subtotales históricos para hacerlos coincidir con el nuevo intento. La interfaz debe distinguir estimación original, anticipo solicitado en cada intento y costo definitivo. Cancelar no reinicia los quince minutos.

### Si el intento pendiente se aprueba

Si la confirmación se valida a tiempo, puede habilitar el retiro de las unidades que todavía conservan su reserva, siempre que cubra el anticipo exigible y se cumplan los demás controles. No reactiva las canceladas ni vencidas. El dinero recibido de más se conserva para el ajuste final conjunto; no se crea un reembolso individual inmediato por la unidad cancelada mientras quedan otras pendientes o en uso.

Si se canceló todo sin uso o el plazo terminó, no se habilita un retiro por la aprobación tardía. El dinero se registra y se concilia conforme al costo definitivo del contrato; cuando sea cero corresponde devolver lo recibido. No se devuelve dinero que no fue confirmado.

### Si el intento es rechazado o cancelado de forma confirmada

Antes de iniciar el uso, el nuevo intento se calcula con los subtotales estimados ARS ya congelados de las unidades que todavía conservan reserva vigente. No incluye unidades canceladas o vencidas, no cambia las tarifas, la cotización o la estimación original y no concede otro plazo. El backend puede derivar ese importe; no se propone una columna adicional para duplicarlo.

Un rechazo confirmado habilita evaluar un nuevo intento según RN-PAG-02. Un resultado todavía incierto no habilita otro cobro: primero se concilia. Si ya existe el anticipo requerido confirmado, no se genera otro anticipo por cambiar de pantalla o cancelar una unidad. Si no quedan unidades vigentes no se crea un intento nuevo, y nunca uno de monto cero.

La coordinación con el proveedor queda por integrar. Una confirmación validada tardía o contradictoria se conserva y concilia; no se descarta el dinero recibido porque nuestra pantalla ya muestre otro estado.

### Ejemplo

Tres bicicletas tienen estimaciones de ARS 1.000 cada una. Se inicia un anticipo de ARS 3.000 y, mientras sigue pendiente, se cancela una. Se libera esa bicicleta, pero el intento conserva ARS 3.000.

- Si se aprueba antes del vencimiento, solo pueden retirarse las dos todavía reservadas. Si su costo real conjunto termina siendo ARS 1.500, corresponde reembolsar ARS 1.500 al liquidar; no se reembolsan primero ARS 1.000 y después otros ARS 1.500.
- Si se confirma el rechazo, puede iniciarse un nuevo intento de ARS 2.000 por las dos restantes, dentro del plazo original. El intento rechazado de ARS 3.000 no se edita.
- Si se cancelan todas antes de aprobarse, ninguna vuelve a reservarse por el pago tardío y, sin uso, corresponde devolver los ARS 3.000 cuando efectivamente se confirmen.

## 4. Controles de integridad de los reembolsos

Estos controles desarrollan la conservación del dinero y la ausencia de duplicados ya aprobadas; no agregan una multa, comisión o nueva fórmula de costo:

- Un reembolso corresponde a un PAGO confirmado y su moneda, plataforma y entorno se obtienen de ese origen. No se utiliza una tarjeta nueva elegida por el cliente para desviar la devolución a otro destino.
- Para cada pago, la suma de reembolsos CONFIRMADO más solicitudes PENDIENTE o EN_PROCESO que ya reservan importe no puede exceder su monto confirmado. Un resultado incierto mantiene su reserva de importe hasta conciliarse; no se marca FALLIDO por un timeout para volver a solicitarlo.
- Además del tope por pago, se comprueba la obligación conjunta del alquiler, descontando reembolsos confirmados y solicitudes vigentes, para no tramitar dos veces el mismo saldo a favor usando pagos de origen distintos.
- Con diferencia cero no se crea un movimiento externo. Las restricciones de mínimos, plazos, medios y disponibilidad del proveedor se validan al integrar; no se redondea arbitrariamente el costo aprobado para ocultarlas.
- El cierre operativo, la devolución física y los costos no se reabren porque el reembolso esté pendiente o falle. Se conserva la obligación de devolver el dinero y su atención segura.

La concurrencia requiere coordinar el alquiler y los pagos de origen al registrar una obligación o solicitud. Una FK, una version o una clave UNIQUE aislada no impiden por sí solas dos reembolsos diferentes que consuman el mismo importe.

## 5. Antecedente descartado RN-PAG-04 para medios guardados

Esta sección conserva la propuesta anterior para explicar la decisión. No está aprobada ni debe implementarse en esta versión. Se sustituye el alcance por [RN-PAG-05](32-pago-externo-con-mercadopago.md): Checkout Pro con redirección, sin perfiles o tarjetas administrados localmente. Los campos y las relaciones siguientes son únicamente el antecedente descartado.

Se propone permitir vincular voluntariamente tarjetas mediante referencias de la pasarela. No es requisito para registrar un usuario ni implica que deba crearse otra cuenta de acceso a Turismo Sustentable. El cliente externo del proveedor no se confunde con el rol CLIENTE ni se interpreta automáticamente como una cuenta personal de Mercado Pago.

La captura y tokenización deben realizarse con los componentes del proveedor de la modalidad elegida. Nuestro modelo no conserva número completo, CVV, contraseñas, Access Tokens ni tokens de uso transitorio. Mostrar una tarjeta guardada no autoriza cobros automáticos: cada pago sigue la interacción y autorización que corresponda, incluido el adicional ya definido sin débito automático.

### PERFIL_PAGO

Representa el vínculo de un USUARIO con el identificador de cliente que reconoce una integración, separado por entorno. Evita repetir el mismo cliente externo en cada tarjeta.

| Campo propuesto | Tipo lógico y clave | Condición |
| --- | --- | --- |
| id | int, PK | Identidad local |
| usuario_id | int, FK a USUARIO.id | Obligatorio; titular del vínculo |
| plataforma | string | Obligatorio; MERCADOPAGO para la integración elegida |
| entorno | string | Obligatorio; PRUEBA o PRODUCCION |
| cliente_externo_id | string | Obligatorio al confirmar el vínculo con el proveedor; no es una credencial |
| fecha_vinculacion | datetime | Momento en que el backend registra el vínculo validado |
| borrado_perfil | boolean | Baja exclusivamente lógica; no elimina pagos o referencias históricas |
| fecha_baja | datetime | Opcional hasta la baja |
| version | int | Coordinación de cambios; la estrategia física se concreta al implementar |

Se proponen UNIQUE(usuario_id, plataforma, entorno) y UNIQUE(plataforma, entorno, cliente_externo_id). Cada una es una restricción compuesta, no un UNIQUE individual por columna. Este alcance supone una integración/cuenta receptora por plataforma y entorno; si se admiten varias, debe ampliarse explícitamente su identificación antes de migrar. Las bajas no permiten reutilizar silenciosamente un perfil para otro usuario.

### MEDIO_PAGO_GUARDADO

Representa una tarjeta vinculada a ese perfil y reconocida por el proveedor. No almacena el instrumento financiero completo ni sustituye las comprobaciones externas al utilizarlo.

| Campo propuesto | Tipo lógico y clave | Condición |
| --- | --- | --- |
| id | int, PK | Identidad local |
| perfil_pago_id | int, FK a PERFIL_PAGO.id | Obligatorio; el usuario y el entorno se obtienen del perfil |
| medio_externo_id | string | Identificador de tarjeta del proveedor, no un token transitorio |
| tipo | string | Tipo validado de tarjeta; códigos concretos según la integración |
| marca | string | Opcional si no se informa; etiqueta para identificarla |
| ultimos_cuatro | string | Cuatro caracteres numéricos informados por el proveedor; no número completo |
| mes_vencimiento | int | Opcional si no se dispone de una fecha validada; de 1 a 12 cuando existe |
| anio_vencimiento | int | Opcional junto con el mes; no se inventa un vencimiento desconocido |
| fecha_vinculacion | datetime | Registro de la asociación validada |
| borrado_medio | boolean | Baja lógica; impide nuevas selecciones locales sin borrar su uso histórico |
| fecha_baja | datetime | Opcional hasta la baja |
| version | int | Control de concurrencia propuesto |

Se propone UNIQUE(perfil_pago_id, medio_externo_id), una sola clave compuesta. No se pretende reconocer el mismo plástico entre usuarios comparando números completos que no se guardan. No se permite mover un medio existente a otro perfil para cambiar la propiedad de su historia.

La baja local impide nuevos usos en Turismo Sustentable; no demuestra que la desvinculación externa ya ocurrió. Si se solicita esta última, su resultado y errores se concilian y auditan. Los pagos previos y sus reembolsos conservan referencias aunque el medio deje de estar disponible. Las altas, bajas y cambios de metadatos se registran en AUDITORIA_SISTEMA con actor/origen, fecha y datos permitidos; no se propone otro historial dedicado.

### Vínculo con PAGO

Se propone agregar medio_pago_guardado_id como FK opcional de PAGO a MEDIO_PAGO_GUARDADO.id. Una tarjeta guardada puede aparecer en muchos pagos históricos y un intento puede no utilizar un medio previamente guardado. REEMBOLSO continúa apuntando solo a PAGO, no a una tarjeta distinta.

Antes de utilizar el vínculo, el backend comprueba que pertenece al usuario del alquiler, que perfil y medio no están dados de baja, que el entorno/plataforma coinciden y que el proveedor permite usarlo. El importe, resultado y referencias de un pago previo no cambian al dar de baja el medio. No se interpreta la FK opcional como permiso para cobrar con una referencia externa ajena enviada por el navegador.

Las referencias y los metadatos parciales también son información privada: no se publican y sus consultas respetan propiedad y permisos. No guardar PAN o CVV no vuelve públicos los identificadores del cliente o de la tarjeta.

Las relaciones propuestas son USUARIO a PERFIL_PAGO, PERFIL_PAGO a MEDIO_PAGO_GUARDADO y MEDIO_PAGO_GUARDADO a PAGO. Las dos primeras son de uno a cero o muchos; cada perfil/medio tiene exactamente un padre. La última permite cero o un medio guardado por PAGO. No se duplican usuario_id en la tarjeta ni alquiler_id en el perfil.

## 6. Producto elegido y decisiones técnicas pendientes

Guardar tarjetas localmente es diferente de ofrecer al comprador los medios disponibles en Mercado Pago. El usuario ya eligió la redirección al checkout del proveedor; no se da por implementada una gestión propia de medios ni se fingen las dos entidades anteriores como sincronizadas. Es un cambio de alcance explícito frente a la vinculación de medios incluida en el PDF, registrado en el documento 32.

La variante de API de Checkout Pro, los reintentos dentro de un checkout y su correspondencia con cada transacción PAGO requieren comprobación. No se aprueba por extensión dividir un intento entre varias tarjetas ni asumir que orden y cobro son lo mismo. Si se necesitan varias referencias se distinguirán sus campos antes de cerrar el diseño físico, sin agregar por ello una tarjeta local.

Siguen pendientes mapeo de estados externos, notificaciones verificadas, conciliación, credenciales, formatos de identificadores, mínimos/plazos de pago o reembolso y comportamiento comprobado del entorno de prueba. No se presupone que todos los reembolsos se puedan demostrar igual que en producción sin verificarlos. La experiencia de Checkout Pro sí está elegida, pero no se conecta una cuenta ni se implementa su API mediante este documento.

## 7. Criterios de aceptación para implementar

Son casos especificados, todavía no ejecutados:

| Caso | Escenario | Resultado esperado según RN-PAG-03 y controles financieros vigentes |
| --- | --- | --- |
| CP-PAG-03-01 | Se cancela una de tres unidades con un anticipo pendiente | Se libera la unidad, se conserva el monto del intento y no se habilita otro cobro incierto |
| CP-PAG-03-02 | Se aprueba a tiempo el intento de ARS 3.000 después de cancelar una unidad | Solo se habilitan unidades vigentes; el excedente se considera en el ajuste conjunto |
| CP-PAG-03-03 | Se rechaza ese intento y quedan dos unidades por ARS 2.000 | Nuevo intento por ARS 2.000, dentro del plazo original; se conserva el rechazo de ARS 3.000 |
| CP-PAG-03-04 | Se cancela todo y llega una aprobación tardía | No se reactiva ni habilita retiro; se registra y concilia la devolución del dinero recibido |
| CP-PAG-03-05 | Dos solicitudes de reembolso intentan consumir el mismo saldo | Se coordina el saldo del alquiler y el cupo de los pagos, sin exceder la obligación ni el dinero confirmado |
| CP-PAG-03-06 | Se quita una unidad del carrito antes de confirmar | Se solicita el pago solo por la selección final; no hay cobro ni reembolso por la unidad quitada |
| CP-PAG-03-07 | Se cancela una reserva antes de iniciar solicitud o recurso externo cobrable | El intento correcto incluye solo unidades vigentes, sin editar la estimación histórica ni extender el plazo |

Los siguientes casos de RN-PAG-04 se conservan solo como antecedente descartado. No son requisitos a implementar ni pruebas de aceptación de esta versión; los vigentes del checkout externo están en el documento 32.

| Caso descartado | Escenario de la propuesta anterior | Resultado que habría requerido aquella propuesta |
| --- | --- | --- |
| CP-PAG-04-01 | Se registra un usuario sin medio guardado | El registro no depende de disponer de un perfil de la pasarela |
| CP-PAG-04-02 | Se vinculan dos tarjetas al mismo perfil | No se duplica el cliente externo; cada tarjeta conserva su referencia propia |
| CP-PAG-04-03 | Un cliente intenta usar un medio de otro usuario o entorno | Rechazo en backend sin enviar un cobro ni exponer sus metadatos |
| CP-PAG-04-04 | Se da de baja un medio usado anteriormente | No permite nuevos usos locales, pero los pagos, reembolsos y su historia permanecen consultables según permisos |
| CP-PAG-04-05 | Se inspeccionan base, auditoría y respuestas HTTP | No contienen PAN completo, CVV, secretos de aplicación ni tokens transitorios persistidos |

## 8. Aprobación y cambio de alcance registrados

El usuario aprobó RN-PAG-03 después de aclarar que quitar una unidad antes de iniciar el pago significa pagar solo por las restantes. No aprobó RN-PAG-04: confirmó que Mercado Pago debe recibir los datos y ofrecer su pantalla de pago, sin pedir ni administrar tarjetas desde Turismo Sustentable. Esa decisión se registra en RN-PAG-05 del documento 32 y descarta las dos entidades propuestas. Los topes y coordinación de reembolsos desarrollan la integridad ya exigida y no agregan tablas.

El DER vigente conserva 28 entidades y 52 FK/relaciones; no está previsto pasar a 30 y 55 por medios guardados dentro de este alcance. Se reflejan las aprobaciones en comentarios del modelo sin cambiar atributos o relaciones. Los campos físicos, la variante concreta de API y la integración no se dan por implementados por extensión.

## 9. Referencias oficiales verificadas

Consulta documental del 1 de noviembre de 2026; no es evidencia de llamadas de API ni pagos ejecutados:

- [Tarjetas guardadas de Checkout API vía Orders](https://www.mercadopago.com.ar/developers/es/docs/checkout-api-orders/payment-management/improve-payment-approval/saved-cards): cliente externo, tarjetas asociadas y nuevas autorizaciones para utilizarlas. Esta documentación no prescribe nuestras tablas ni autoriza conservar datos sensibles.
- [Tarjetas guardadas en Payment Brick](https://www.mercadopago.com.ar/developers/es/docs/checkout-bricks/payment-brick/advanced-features/customers-cards): distingue las referencias de cliente y tarjetas para su presentación.
- [Reembolsos y cancelaciones de Checkout Pro vía Preferences](https://www.mercadopago.com.ar/developers/es/docs/checkout-pro-preferences/additional-settings/refunds-and-cancellations): diferencia devolución total/parcial y restricciones propias de esa modalidad. No se trasladan automáticamente sus endpoints o límites a otro producto.

La documentación vía Payments consultada figura como legacy en su navegación. El documento 32 incorpora las referencias actuales de Checkout Pro para la experiencia externa aprobada. Antes de codificar se verificará la variante de API y sus referencias; no se mezclan ejemplos de Payments, Orders y Preferences como si fueran una misma API.
