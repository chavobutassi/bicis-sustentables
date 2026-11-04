# Propuestas de mejora futura a partir de la versión del compañero

Fecha: 3 de noviembre de 2026.

Estado: propuestas documentadas a pedido del desarrollador, pendientes de confirmación. La autorización para anotarlas no equivale a aprobarlas para implementar ni a autorizar cambios automáticos en Java, SQL o Git.

El DER v5 sigue teniendo 29 entidades y 55 FK/relaciones. Este documento no modifica el Mermaid, su exportación TXT, el diccionario de estados ni las reglas de cobro, reserva, devolución, incidencia y mantenimiento aprobadas.

## 1. Origen y límites

Se compararon, en modo lectura, las entregas `entrega-v3.2-registro-imagenes-admin` y `entrega-v3.6-correos-y-libro-diario`, ubicadas junto al proyecto principal. La v3.6 incorpora cola de correos, comprobantes y cierre diario, y pasa de 24 a 27 tablas. Tiene documentación y evidencia adjunta de 59 pruebas y verificaciones de QA; esas ejecuciones no se reprodujeron durante esta revisión.

La implementación principal continúa en TurismoSustentable, rama codex/refactorizacion-practicas-iii. Las propuestas rescatan mecanismos, no adoptan íntegramente la copia del compañero, sus tablas o sus reglas. En particular, no se incorporan su garantía, métodos de pago guardados, cancelación automática ante rechazo ni liquidación individual por bicicleta.

Referencias de diseño vigentes: [pagos e integración](32-pago-externo-con-mercadopago.md), [historial financiero](24-propuesta-historial-financiero.md), [usuarios y roles](25-revision-personas-usuarios-y-roles.md), [auditoría exclusiva de ADMIN](35-auditoria-admin-y-brechas-de-trazabilidad.md) y [DER v5](der-v5-propuesto.mmd). La implementación y sus pruebas efectivamente revisadas se registran en [el documento 37](37-implementacion-entidades.md).

## 2. Resumen para decidir

| ID | Propuesta | Naturaleza | Cambio previsto en el DER | Situación |
| --- | --- | --- | --- | --- |
| MF-01 | Robustecer el cliente de Mailjet | Mejora técnica | Ninguno | Recomendada; pendiente de planificar el bloque |
| MF-02 | Reintentos seguros e idempotencia | Control técnico de reglas existentes | Pagos/reembolsos ya tienen claves; otras operaciones requieren diseño específico | No sustituye la aprobación existente; implementación pendiente |
| MF-03 | Protección CSRF integrada con el frontend | Mejora de seguridad | Ninguno | Recomendada; pendiente de adaptar ambos lados |
| MF-04 | Ampliar pruebas de errores, permisos y concurrencia | Verificación | Ninguno por sí misma | Recomendada; casos futuros, no resultados ejecutados |
| MF-05 | Separar vistas personales y gestión administrativa | Organización de consultas y permisos | Ninguno | Recomendada; sin ampliar autoridades de CLIENTE o TECNICO |
| MF-06 | Cola persistente de correos | Nueva capacidad técnica persistente | Propuesta de NOTIFICACION_CORREO | Requiere aprobación de alcance y posterior diseño de campos/FK |
| MF-07 | Comprobantes consultables | Nueva consulta para el usuario | Opción simple sin tabla nueva; original conservado requeriría diseño de COMPROBANTE | Requiere elegir modalidad |
| MF-08 | Reporte financiero por período y CSV | Nueva función administrativa | Inicialmente ninguno | Requiere aprobación de alcance |
| MF-09 | Conservar al menos un ADMIN activo | Regla de negocio administrativa | Ninguno inicialmente | Requiere aprobación expresa |
| MF-10 | Cierres diarios congelados | Ampliación del módulo financiero | Posible CIERRE_DIARIO y sus relaciones, todavía no diseñados | Recomendación: posponer; no es alcance aprobado |

El paquete técnico MF-01 a MF-05 no redefine cómo se cobra un alquiler. Puede confirmarse como prioridad de mejora sin reaprobar las reglas ya acordadas. No se debe confundir esa confirmación con una autorización general para editar el proyecto: se conserva el trabajo manual por bloques.

## 3. Paquete técnico recomendado

### MF-01. Mailjet: respuesta real del proveedor y tiempos máximos de espera

- Qué haría: limitar cuánto espera la aplicación por la conexión/respuesta del proveedor y comprobar el resultado de cada mensaje, no solamente el código HTTP.
- Qué modificaría: CorreoService, configuración de tiempos de espera y pruebas del cliente HTTP. Se conserva la integración por HTTPS y las credenciales fuera del código.
- Qué no cambia: destinatarios, reglas económicas, flujo del alquiler ni tablas del DER.
- Verificación futura: mensaje aceptado, mensaje rechazado, falta de credenciales y error de conexión. Una aceptación del proveedor no se presentará como confirmación de lectura o llegada a la bandeja principal.

La copia v3.6 ya contiene una implementación y pruebas de este mecanismo. Se adaptaría a nuestros métodos y contratos, sin reemplazar todo el servicio ni perder bienvenida, recuperación y tickets existentes.

### MF-02. Idempotencia y reintentos seguros

- Qué haría: reconocer un reenvío de la misma operación para no generar dos efectos. La misma clave con otros datos debe rechazarse; una operación nueva debe tener una identidad diferente.
- Qué modificaría: servicios de pagos/reembolsos, llamadas a la pasarela, contratos de las operaciones afectadas, manejo de reintentos del frontend y pruebas. Deshabilitar un botón solo es una ayuda visual, no el control definitivo.
- Qué ya existe en el diseño: PAGO y REEMBOLSO tienen clave_idempotencia. Se conserva su unicidad y no se crean intentos nuevos ciegamente después de una respuesta incierta.
- Qué requiere concretar: operaciones como reserva y devolución deberán tener una estrategia propia al implementarse. No se autoriza por este documento una tabla genérica de operaciones ni nuevas columnas sin revisar su necesidad.
- Qué no se copiará: usar AUDITORIA_SISTEMA como almacenamiento general de operaciones de clientes o procesos automáticos. Esa tabla sigue siendo exclusiva de ADMIN.
- Verificación futura: doble clic, pérdida de respuesta, misma clave con otro monto, confirmación externa repetida y solicitudes simultáneas. Un timeout no demuestra que el proveedor no haya procesado la operación.

### MF-03. CSRF con sesiones de navegador

- Qué haría: comprobar un token CSRF en las solicitudes que modifican datos, para proteger el uso de la sesión por cookies.
- Qué modificaría: WebAuthorization, la inicialización/lectura del token y las peticiones del frontend, incluidos login, logout, registro y recuperación cuando corresponda. Backend y frontend se adaptarán juntos.
- Qué no cambia: roles admitidos, acceso por propietario, reglas del negocio ni tablas.
- Verificación futura: solicitudes con token válido, ausente y vencido, cierre de sesión y formularios públicos. La integración externa de Mercado Pago requiere definir sus rutas y validación propia; no se deshabilitará CSRF para toda la API como solución a un webhook.

### MF-04. Pruebas y evidencia reproducible

- Qué haría: convertir los errores y casos de borde relevantes en pruebas repetibles, reutilizando escenarios del compañero que coincidan con nuestro contrato.
- Qué modificaría: src/test, fixtures, configuración aislada de integración y documentación de evidencias. No se copiarán expectativas de garantía, cancelación por rechazo o estados incompatibles.
- Qué no cambia: ninguna tabla o regla de negocio por el solo hecho de agregar pruebas.
- Casos prioritarios: errores del proveedor de correo, reenvíos, accesos ajenos, dos reservas sobre una bicicleta, devoluciones al último espacio y modificaciones simultáneas de roles.
- Precaución: las pruebas de integración utilizarán una base aislada; no se ejecutará indiscriminadamente contextLoads contra la base anterior ni se registrarán pruebas del compañero como ejecutadas en nuestro proyecto.

### MF-05. Vistas propias y administración general separadas

- Qué haría: Mis viajes, Mis pagos y los futuros comprobantes personales mostrarían los del usuario conectado, también si tiene ADMIN. La consulta de todos los usuarios quedaría en la gestión administrativa correspondiente.
- Qué modificaría: consultas, endpoints/DTO cuando sea necesario, navegación y pruebas de permisos/propiedad. No depende solamente de ocultar botones.
- Qué no cambia: ADMIN mantiene sus permisos administrativos; un cliente no obtiene acceso global. No se requieren tablas nuevas.
- Verificación futura: ADMIN con alquiler propio y ajeno, dos clientes diferentes, acceso directo por ID y rutas administrativas sin autorización.

## 4. Decisiones funcionales que requieren aprobación

### MF-06. Cola persistente de correos

Qué haría:

- Guardar el aviso pendiente junto con la operación de negocio y procesar el envío después de confirmar esa operación.
- Conservar estado, cantidad de intentos y error saneado; permitir reintentos controlados y revisión administrativa.
- Evitar crear varias notificaciones para el mismo evento mediante una clave de evento única.
- No revertir un registro, pago o devolución por un fallo del proveedor de correo.

Qué modificaría:

- Proponer NOTIFICACION_CORREO, con PK propia, vínculo al usuario destinatario, identidad del evento, tipo, datos mínimos del mensaje, estado y fechas/intentos. Las longitudes, nulabilidad, claves y códigos se presentarían antes de modificar el DER.
- Agregar modelo, repositorio y servicios de cola/despacho, configuración, pruebas y una consulta administrativa de estados/reintentos. Los permisos del acceso al contenido deberán definirse expresamente.
- Adaptar los puntos que generan bienvenida y avisos/tickets de alquiler. La recuperación requiere tratamiento específico: no se copiarán tokens secretos a registros generales ni se guardarán enlaces de recuperación sin revisar su protección y vencimiento.

Límites:

- La propuesta base conserva el estado actual y el seguimiento del envío. Un contador y el último error no constituyen un historial completo de cada intento. Si se exige ese historial, se propondrá una estructura adicional antes de cerrar el diseño, no se lo dará por resuelto ni se agregará silenciosamente otra tabla.
- La identidad única del evento no garantiza cero entregas duplicadas ante una respuesta de red ambigua. Se definirán recuperación, límite de reintentos y procesamiento concurrente.
- No se copiará sin revisión el envío HTTP manteniendo bloqueos largos de la operación de negocio. La confirmación local y el transporte externo tienen responsabilidades distintas.

Aprobación solicitada: incorporar esta capacidad y preparar su ampliación del DER. No supone aprobar de antemano un esquema físico o un catálogo de estados que todavía no se presentó.

### MF-07. Comprobantes consultables: elegir modalidad

Objetivo común: que el titular pueda consultar e imprimir una constancia de sus operaciones, además del correo recibido. Se utilizarán importes y referencias almacenados, sin recalcular con la tarifa o cotización actuales ni presentar pendientes como dinero confirmado. ADMIN tendrá su consulta autorizada, sin acceso para otros clientes.

Opción A, recomendada inicialmente: comprobante simple generado desde los registros.

- Qué haría: mostrar una constancia consultable de pagos/reembolsos y del alquiler asociado, con identificadores, fechas, importes y estados claramente diferenciados.
- Qué modificaría: servicio/DTO de consulta, endpoint autorizado, plantilla/pantalla e impresión, pruebas y acceso desde Mis pagos.
- DER: no requiere inicialmente otra tabla si los datos necesarios ya están conservados. No garantiza reproducir exactamente el HTML o las etiquetas personales de una emisión anterior.

Opción B: conservar el documento original emitido.

- Qué agregaría sobre A: guardar el contenido original, identidad de emisión y, si se adopta, su huella de integridad para consultar el mismo documento más adelante.
- Qué modificaría: proponer COMPROBANTE o una estructura equivalente, con PK, relaciones al titular/alquiler y referencias financieras que se definan al diseñarlo; almacenamiento protegido, permisos y pruebas adicionales.
- DER: sí implica una ampliación que se deberá presentar y aprobar con campos y FK. No se incorpora ahora la estructura del compañero sin adaptarla.

Ninguna opción se presenta como factura fiscal o contabilidad completa. Una huella almacenada junto al documento es un control de integridad, no una garantía absoluta frente a quien pueda alterar ambos en la base.

Aprobación solicitada: elegir A o B. Documentar ambas opciones no aprueba ninguna de ellas; la recomendación de menor alcance es A.

### MF-08. Reporte financiero operativo por período y CSV

Qué haría:

- Dar a ADMIN un filtro por fechas y un detalle de cobros confirmados y reembolsos confirmados, con referencias a pagos y alquileres.
- Mostrar sus totales y el neto cobrado menos reembolsado. Mostrar deudas y reembolsos pendientes por separado, con un criterio de fecha explícito.
- Permitir descargar CSV con caracteres correctamente codificados, celdas escapadas y protección frente a fórmulas introducidas como texto.

Qué modificaría:

- Consultas sobre PAGO/REEMBOLSO y sus fechas de confirmación, servicio de reporte, DTO, endpoint exclusivo ADMIN, vista/filtros y pruebas.
- No sumar inicialmente MOVIMIENTO_PAGO ni CIERRE_DIARIO. Los historiales explican transiciones; no se cuentan como operaciones monetarias nuevas. Cada pago/reembolso se contabiliza una sola vez según su identidad y confirmación.
- Usar un criterio de zona horaria documentado; el cálculo por fecha no se deducirá del navegador ni de la fecha de creación del alquiler. Las operaciones de prueba y producción no se mezclarán.

Ejemplo ficticio: ARS 20.000 de cobros confirmados y ARS 5.000 de reembolsos confirmados dan ARS 15.000 netos de esos movimientos. No es, por esa sola cuenta, ganancia del negocio ni saldo disponible en Mercado Pago.

Límite: es un reporte operativo consultable, no un cierre contable ni un documento congelado. No cambiará costos o estados del alquiler para hacer coincidir sus totales.

Aprobación solicitada: incorporar el reporte y el CSV, inicialmente sin cierres persistentes y sin nuevas tablas.

### MF-09. Proteger al último ADMIN activo

Regla propuesta: no permitir desactivar una cuenta ni retirarle ADMIN cuando eso dejaría al sistema sin ningún administrador activo.

Qué haría: conservar al menos una cuenta habilitada para administrar la plataforma. No equivale a prohibir para siempre cualquier cambio sobre cualquier administrador.

Qué modificaría: servicio de cambios de roles/estado de cuenta, validaciones transaccionales, respuesta de conflicto, mensajes del panel, auditoría administrativa y pruebas. No requiere inicialmente otra tabla ni cambia los códigos CLIENTE, ADMIN y TECNICO.

Condiciones:

- Se comprueba en el backend; no basta con deshabilitar un botón o consultar un contador antes de guardar.
- Debe mantenerse ante dos cambios simultáneos: una comprobación de cantidad sin coordinación transaccional no demuestra proteger la regla.
- La baja de cuentas sigue siendo lógica y las referencias históricas no se borran.
- No se adoptan automáticamente otras restricciones del compañero, como impedir todo cambio de rol propio o toda desactivación con deuda; esas políticas son decisiones distintas.

Aprobación solicitada: incorporar esta regla y su trazabilidad, sin modificar el DER inicialmente.

## 5. MF-10. Cierres diarios congelados: propuesta a posponer

El libro diario de la copia v3.6 añade algo distinto del reporte MF-08: guarda el cierre, sus totales y detalle, y rechaza movimientos nuevos para una fecha cerrada.

Si se adoptara, habría que definir cierres automáticos/manuales, fechas y zona horaria, confirmaciones tardías de la pasarela, ajustes/correcciones, concurrencia y permisos. Podría requerir CIERRE_DIARIO y estructuras relacionadas, todavía no diseñadas ni aprobadas. No se copiarán sus reglas basadas en garantía o dinero simulado.

Recomendación: posponer esta ampliación y comenzar con MF-08. No es una condición técnica para que funcionen alquileres y pagos; una exigencia académica expresa deberá revisarse antes de cambiar su prioridad. No se evalúan en este documento obligaciones contables legales de un negocio real.

Confirmación solicitada: mantener los cierres congelados fuera del alcance inicial de estas mejoras y revisarlos después. No se considera que la aprobación del reporte MF-08 incluya cierres.

## 6. Respuesta de aprobación que falta

Para registrar decisiones sin ambigüedad se requiere confirmar:

1. Si se prioriza el paquete técnico MF-01 a MF-05, distinguiendo controles ya exigidos por las reglas aprobadas de su implementación todavía pendiente.
2. MF-06: si se incorpora la cola persistente y se prepara su propuesta de tabla/relaciones.
3. MF-07: si se elige comprobante simple A o documento original conservado B.
4. MF-08: si se incorpora el reporte financiero por período y CSV sin cierres.
5. MF-09: si se aprueba la protección del último ADMIN activo.
6. MF-10: si se confirma posponer los cierres diarios congelados.

Puede responderse por ID o en conjunto. Una aprobación de la función no se presentará como código implementado, pruebas superadas ni aprobación de campos físicos aún no definidos.

## 7. Orden de trabajo propuesto y salvaguardas

- Conservar el desarrollo principal y el DER v5 como referencia. No reemplazar carpetas ni ejecutar el SQL del compañero sobre nuestra base.
- Retomar el bloque manual de roles donde quedó. Registrar estas mejoras no obliga a interrumpirlo ni a incorporar todos los extras antes de cerrar funcionalidades básicas.
- Aplicar seguridad, reintentos y pruebas junto con el módulo que corresponda. Los cambios del cliente Mailjet se pueden aislar sin rehacer su lógica de negocio.
- Si se aprueban MF-06 o la opción B de MF-07, presentar primero sus campos, PK/FK, unicidad, nulabilidad, acceso y retención antes de modificar el Mermaid y su TXT en conjunto.
- No mover dinero real, enviar correos externos o modificar datos como parte de esta documentación. Cualquier implementación posterior seguirá la modalidad manual, salvo autorización puntual del desarrollador.

## 8. Referencias técnicas consultadas en la revisión

- [Mailjet: resultado y errores de cada mensaje](https://dev.mailjet.com/docs/email-api/send-api-v31/send-api-errors).
- [Mercado Pago: idempotencia y prevención de duplicados](https://www.mercadopago.com.ar/developers/es/news/2023/01/04/Idempotency-key-usage-will-be-mandatory). Los endpoints y requisitos concretos se comprobarán para la variante que se integre.
- [Spring Security: protección CSRF](https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html). Se adaptará a la versión usada por el proyecto, sin implicar una actualización de Spring Boot.
- [Mercado Pago: alcance del reporte de liquidaciones](https://www.mercadopago.com.ar/developers/es/docs/reports/released-money/introduction). Nuestro reporte no se confundirá con saldo disponible o contabilidad fiscal.
