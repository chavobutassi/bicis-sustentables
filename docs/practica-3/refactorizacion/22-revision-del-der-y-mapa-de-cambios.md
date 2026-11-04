# Revisión del DER y mapa de cambios

Fecha: 28 de octubre de 2026.

Estado actualizado al 2 de noviembre: DER v5 lógico de trabajo con 29 entidades y 55 FK/relaciones, tras la incorporación aprobada de RN-TRZ-01. Se añade HISTORIAL_INCIDENCIA, se amplía/renombra el historial de orden y se agregan motivo administrativo e incidencia_corte_id. Las reglas anteriores se conservan; el diseño físico, las integraciones y migración siguen pendientes. No se modificaron Java, MySQL, frontend, originales ni la copia del compañero.

## 1. Base de la revisión

Se parte del [DER v4 original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>), que declara 21 entidades, no de un modelo nuevo independiente. Se contrastaron otra vez el [PDF de visión](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), el [diccionario original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y las decisiones RN-ALQ-01 a RN-ALQ-09, RN-MAN-01 a RN-MAN-04, RN-BIC-01/RN-BIC-02, RN-PAG-01/RN-PAG-02 y RN-INC-01.

La aplicación local observada sigue en `ab91d6a` y contiene seis clases persistentes: Usuario, Estacion, Bicicleta, Alquiler, Tarjeta y Suscripcion. Eso es una revisión de archivos, no una consulta del esquema real de MySQL. Su alquiler tiene una sola bicicleta; el DER original ya propone cabecera y detalles. La copia del compañero continúa sin inspeccionar y no se usó como autoridad.

El modelo editable está en [der-v5-propuesto.mmd](der-v5-propuesto.mmd). Conserva conceptualmente las 21 entidades originales, con HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO renombrada/ampliada a HISTORIAL_ORDEN_MANTENIMIENTO, e incorpora ocho: TIPO_MANTENIMIENTO, REEMBOLSO, INCIDENCIA, HISTORIAL_ESTADO_PAGO, HISTORIAL_ESTADO_REEMBOLSO, TIPO_DOCUMENTO, PAIS e HISTORIAL_INCIDENCIA. El primer borrador tenía 24; los historiales financieros lo ampliaron a 26, identificación a 28 y RN-TRZ-01 a 29. No son tablas ya creadas ni una cantidad fijada como requisito.

## 2. Decisiones confirmadas durante esta revisión

El usuario confirmó «Una tarifa por tipo, como en mi DER v4». Por tanto:

- TIPO_BICICLETA administra la tarifa vigente en USD; dos unidades del mismo tipo usan la misma tarifa para contrataciones nuevas.
- BICICLETA no administra una tarifa independiente en el modelo nuevo.
- ALQUILER_DETALLE conserva la tarifa aplicada al confirmar, aunque después cambie el precio del tipo.
- La cotización se congela por ALQUILER, antes del anticipo, y los movimientos se registran en ARS.

Esto conserva la ubicación de la tarifa del DER original y modifica el diseño Java actual, donde cada bicicleta tiene precio propio. El futuro panel administrativo editará esa tarifa por tipo, no por unidad. No se cambia ahora el frontend ni el código vigente.

Al preparar los datos nuevos, si hoy existen bicicletas del mismo tipo con precios diferentes, no se promediarán ni se elegirá una arbitrariamente. Se definirá el precio vigente de cada tipo y se preservarán los precios aplicados históricos. La decisión se registra también en [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md).

Después el usuario aprobó incorporar TIPO_DOCUMENTO y PAIS, documento obligatorio al registrarse con unicidad compuesta de tipo/país/número, y nickname único para iniciar sesión. Email mantiene su restricción única independiente y los circuitos de recuperación y notificaciones. La representación ya está en el Mermaid y se desarrolla en el documento 25, sin modificar el login vigente ni inventar datos del legado.

## 3. Correspondencia con las 21 entidades originales

| Entidad original | Tratamiento propuesto | Motivo y trazabilidad |
| --- | --- | --- |
| PERSONA | Conservar datos personales; reemplazar DNI por tipo y país con FK y número textual; definir unicidad compuesta de los tres | Identificación y obligatoriedad al registrarse aprobadas en el documento 25; formatos y legado se concretan antes de migrar |
| GENERO | Conservar catálogo y código único | Diccionario original; no convertir el combo en texto libre |
| USUARIO | Conservar cuenta, activo y recuperación; incorporar nickname único para el login, separado de email único | Incorporación aprobada en documento 25; no perder recuperación ni referencias por cuenta; adaptar principal y consumidores al implementar |
| ROL | Conservar CLIENTE, ADMIN y TECNICO | Diccionario y reparto de permisos de RN-MAN-02/RN-BIC-02/RN-INC-01 |
| USUARIO_ROL | Conservar relación de varios roles; proponer clave compuesta de usuario y rol | Evitar duplicados y soportar cuentas con ambos roles bajo sus controles |
| ESTACION | Conservar capacidad, coordenadas y baja lógica; espacios libres se calculan | Presencia física, reserva, devolución y capacidad; RN-ALQ-03/RN-BIC-01/RN-BIC-02 |
| TIPO_BICICLETA | Conservar tarifa por tipo y añadir intervalo preventivo | Tarifa confirmada durante esta revisión; RN-ALQ-04/RN-MAN-04 |
| ESTADO_BICICLETA | Conservar catálogo; siete códigos aprobados | RN-BIC-01 más EXTRAVIADA de RN-INC-01 |
| ESTADO_ALQUILER | Conservar cinco estados de uso del conjunto, sin CON_DEUDA | RN-ALQ-07; separar dinero de uso |
| ESTADO_ALQUILER_DETALLE | Conservar catálogo; siete estados de cada unidad | RN-ALQ-09, cancelación administrativa RN-BIC-02 y cierre excepcional RN-INC-01 |
| ESTADO_ORDEN_MANTENIMIENTO | Conservar CREADA, EN_PROCESO, PAUSADA, FINALIZADA y CANCELADA | RN-MAN-01/RN-MAN-02 |
| ESTADO_PAGO | Conservar cinco estados por intento; no usar REEMBOLSADO para sobrescribir el pago | RN-PAG-01/RN-PAG-02 |
| BICICLETA | Conservar unidad, tipo y estado; estación opcional y fecha de alta; proponer retirar el flag redundante de borrado | Viaje fuera de estación, preventiva y DE_BAJA con historial; RN-BIC-01/RN-BIC-02/RN-MAN-04 |
| ORDEN_MANTENIMIENTO | Tipo, creación, resultado y técnico opcional inicial; diagnostico obligatorio al finalizar y costos internos ARS incorporados con aprobación | Trabajo, hallazgo y asignación son hechos separados; RN-MAN-01 a RN-MAN-04 y documento 27 |
| ALQUILER | Conservar cabecera; añadir vencimiento, cotización completa, importes por moneda y fecha de liquidación | RN-ALQ-01 a RN-ALQ-08 y RN-INC-01; cierre operativo no equivale a liquidación |
| ALQUILER_DETALLE | Conserva claves, tipo contratado y unicidad alquiler/bicicleta; agrega incidencia_corte_id opcional, FK/UK, al fundamento del corte | RN-ALQ, RN-INC-01 y RN-TRZ-01; la incidencia debe pertenecer al mismo detalle |
| HISTORIAL_ESTADO_DETALLE | Conservar; proponer estado anterior/nuevo y actor real/origen | No inventar un administrador para vencimientos del sistema ni borrar causas |
| HISTORIAL_ESTADO_BICICLETA | Conservar con actor y origen; no confundir traslado físico con estado | Inventario y trazabilidad de RN-BIC/RN-MAN/RN-INC |
| HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO | Renombrado HISTORIAL_ORDEN_MANTENIMIENTO; conserva estados y agrega acción/valores para cambios permitidos de datos | RN-MAN y RN-TRZ-01; no se crea una segunda tabla ni transiciones ficticias |
| AUDITORIA_SISTEMA | Exclusiva de ADMIN con administrador_id obligatorio; agrega motivo según acción | RN-TRZ-01; no cubre actuaciones técnicas/automáticas ni almacena secretos |
| PAGO | Conservar un registro por intento con importe inmutable, finalidad, referencias y control de duplicados | RN-PAG-01/RN-PAG-02; rechazo no destruye la reserva ni la historia |

Se propone retirar `borrado_bici` del modelo nuevo porque DE_BAJA ya representa el retiro definitivo; no se elimina de una base existente mediante este documento. Su migración requiere revisar conflictos entre flag, estado y alquileres activos. Se conserva provisionalmente `borrado_alquiler` del original como dato de legado/visibilidad, sin permitir que oculte deuda, altere el uso o excluya operaciones de la trazabilidad. No concede un nuevo permiso de borrado.

## 4. Ocho incorporaciones justificadas

| Entidad nueva | Qué conserva | Regla o necesidad |
| --- | --- | --- |
| TIPO_MANTENIMIENTO | PREVENTIVO y CORRECTIVO separados del avance de una orden | Su incorporación ya fue aprobada en RN-MAN-01; no es un estado adicional de bicicleta |
| REEMBOLSO | Importe, moneda, estado y referencia al PAGO original, sin sobrescribirlo | RN-PAG-01 aprueba el movimiento separado; aquí se propone una entidad propia como representación física |
| INCIDENCIA | Reporte del detalle, autor, fechas, decisión de ADMIN, corte validado, revisión y recepción posterior | Entidad incorporada expresamente en RN-INC-01, incluida su sección 8 |
| HISTORIAL_ESTADO_PAGO | Pago, estados anterior/nuevo con FK a ESTADO_PAGO, fechas, actor, origen, fuente y correlación externa | Incorporación autorizada en el documento 24; cada intento conserva su recorrido, incluido el rechazo, sin duplicar cobros |
| HISTORIAL_ESTADO_REEMBOLSO | Reembolso, códigos de estado anterior/nuevo, fechas, actor, origen, fuente y correlación externa | Incorporación autorizada en el documento 24; mantiene la representación controlada de REEMBOLSO.estado sin crear otro catálogo |
| TIPO_DOCUMENTO | PK id, codigo único y nombre; DNI o PASAPORTE | Catálogo aprobado en el documento 25, referenciado por PERSONA con FK obligatoria |
| PAIS | PK id, codigo único y nombre; catálogo compartido de países emisores | Aprobado en el documento 25, referenciado por PERSONA; no se agrega nacionalidad ni una tabla por país |
| HISTORIAL_INCIDENCIA | Once campos: PK de evento, FK a incidencia/actor, acción, estados condicionales, fecha, origen, valores y observaciones | RN-TRZ-01 aprobada; conserva cambios del reporte sin utilizar la auditoría de ADMIN como historial general |

No se agregan tablas de cronómetro, deuda ni espacios libres. Tampoco se agrega una entidad por cada fase de una operación. Los tipos de incidencia, su revisión y los estados de reembolso se muestran inicialmente como códigos controlados en sus entidades; decidir si necesitan catálogos adicionales pertenece al diseño físico. Eso no altera sus significados ni habilita edición libre de estados.

## 5. Cómo se conservan las decisiones difíciles

### Reserva y varios detalles

La contratación confirmada se crea con al menos un detalle y un único vencimiento original a los 15 minutos. Cada unidad tiene su retiro real, duración estimada y devolución. Reintentar o pagar no reinicia ese vencimiento. La exclusividad no es una transacción abierta durante 15 minutos: se persiste y se verifica en cada operación.

La estación de retiro está determinada por la reserva, pero no prueba que ya se retiró. La fecha de retiro y devolución estimada pueden ser nulas antes del retiro real. Una unidad nunca retirada tiene costo real cero al cancelarse o vencer y no recibe una devolución ficticia.

### Precio, moneda y dinero

La tarifa aplicada USD se guarda en cada detalle. ALQUILER conserva ARS por USD, fuente y fechas de aplicación/actualización. Se conservan importes estimados y finales en ambas monedas; PAGO y REEMBOLSO representan dinero ARS, no el costo calculado de uso. Los totales finales no se llenan con cero para aparentar una liquidación antes de poder determinarla.

Se propone calcular la situación financiera en el servicio/DTO a partir del costo final, la fecha de liquidación, las revisiones pendientes y los movimientos confirmados. No se agrega tabla ni columna de situación financiera duplicada en este borrador. Los cuatro nombres aprobados no se eliminan: SIN_LIQUIDAR, SALDO_PENDIENTE, REEMBOLSO_PENDIENTE y SALDADO.

El dinero neto confirmado es la suma de pagos aprobados menos reembolsos confirmados. Mientras haya una incidencia económica pendiente puede existir cabecera FINALIZADO y situación SIN_LIQUIDAR. Un reembolso pendiente no es deuda del cliente y no bloquea nuevas contrataciones. La reparación técnica, por sí sola, no retrasa la liquidación.

PAGO y REEMBOLSO conservan sus importes y estados actuales. Sus historiales registran el estado inicial y las transiciones, no nuevos movimientos de dinero ni copias de importes para volver a sumarlos. Ambos tienen FK a la operación y al actor humano cuando corresponde; el historial de pago tiene además dos FK distintas a ESTADO_PAGO. El historial de reembolso usa los mismos cuatro códigos controlados de su operación porque no existe un catálogo ESTADO_REEMBOLSO en este borrador. Los detalles de campos y cardinalidades están en el documento 24.

### Incidencia, fin del uso y recepción física

No se usa una misma fecha para la interrupción validada, decisión de ADMIN y recepción física. El detalle conserva fecha de devolución normal cuando ocurrió; la incidencia conserva su corte validado y la recepción posterior cuando hubo recuperación después de un cierre excepcional. CERRADO_POR_INCIDENCIA no requiere inventar estación de devolución.

Si el detalle está DEVUELTO pero una incidencia previa puede cambiar su importe, se detiene el tiempo y el subtotal final queda pendiente. El provisional puede calcularse para la pantalla sin guardarlo como definitivo. Al resolver la incidencia, se determina el fin de uso facturable, se conserva la recepción real y se liquida una sola vez al cerrar el conjunto y sus revisiones.

Los códigos iniciales propuestos de revisión son PENDIENTE, VALIDADA y DESCARTADA; describen la decisión sobre la solicitud, no culpa ni diagnóstico técnico. Los tipos propuestos son AVERIA, ACCIDENTE, PERDIDA y ROBO. La bicicleta se obtiene del detalle, sin duplicar ese vínculo en INCIDENCIA. El backend decide si una revisión puede afectar el importe, no un estado de destino elegido libremente por el cliente.

### Reporte de devolución y mantenimiento

La falla informada al devolver se propone conservar en el detalle con descripción, autor y fecha; una incidencia durante el viaje se conserva en INCIDENCIA. No se trata todo reporte de devolución como una solicitud de corte económico. Ambos pueden enlazarse a una orden abierta, manteniendo una sola por bicicleta.

Los enlaces a la orden son referencias operativas: si ADMIN corrige una clasificación cancelando una orden y creando otra, su auditoría conserva la asociación anterior y la nueva, además de mantener las órdenes e historiales. HISTORIAL_INCIDENCIA conserva los cambios autorizados del vínculo de su reporte; el historial de orden ampliado conserva sus datos técnicos. El enlace inicial automático se registra con los hechos de creación que correspondan, sin ADMIN ficticio. No se borran los reportes ni su historia. HISTORIAL_ATENCION_MANTENIMIENTO permanece descartado; automatismos futuros de reasociación no definidos no se dan por autorizados o cubiertos.

### Calendario y aptitud

TIPO_BICICLETA configura el intervalo positivo en meses; BICICLETA aporta fecha de alta inicial y las órdenes aportan la última preventiva satisfactoria. No se duplica inicialmente una columna de última preventiva. Crear o cancelar una orden no reinicia el calendario. Un legado sin referencia fiable requiere revisión inicial y no una fecha inventada.

Una orden puede estar CREADA sin técnico. La ampliación aprobada el 4 de noviembre de 2026 en RN-MAN-02, sección 3.1, permite también PAUSADA sin técnico al inactivar al asignado: ADMIN pausa excepcionalmente una EN_PROCESO y desasigna sus órdenes abiertas, conservando trabajo e historia; las cerradas no cambian. Iniciar/reanudar exige siempre el técnico activo autorizado y asignado. El resultado técnico se conserva aparte del estado de la orden. Un cierre favorable no habilita automáticamente: ADMIN conserva la autorización posterior bajo RN-MAN-02. Se precisa solo la condición de tecnico_id, sin nuevos campos, tablas o relaciones.

### Actor real y automatismos

Los historiales de dominio distinguen origen USUARIO y SISTEMA; el actor es nulo solo para SISTEMA y los eventos humanos requieren su usuario real. AUDITORIA_SISTEMA es la excepción aprobada: exclusiva de ADMIN, con administrador_id obligatorio, motivo según acción y sin origen automático. El técnico no se registra como administrador ficticio y una tarea de vencimiento no se atribuye a una persona inventada. El rol habilitante se verifica al operar sin reescribir intervenciones pasadas. RN-TRZ-01 incorpora historia de incidencias y datos técnicos sin transición, manteniendo estos límites.

## 6. Restricciones que el dibujo no implementa

Estas condiciones deben traducirse a restricciones de datos, operaciones transaccionales y pruebas. Un diagrama o una columna `version` no las garantiza por sí solos.

1. Email y nickname normalizados con unicidades individuales; documento único por (tipo_documento_id, pais_emisor_id, numero_documento), sin declarar únicos sus tres campos por separado. Códigos de catálogos únicos y USUARIO_ROL sin pares duplicados; el registro público no concede roles solicitados por el cliente.
2. Una bicicleta no puede tener dos detalles con exclusividad/uso incompatibles. La creación, retiro, cancelación, vencimiento, cierre y administración deben verificar el estado y bloquear el mismo recurso de forma coherente.
3. Una sola orden CREADA, EN_PROCESO o PAUSADA por bicicleta, también ante peticiones simultáneas.
4. La capacidad se cuenta por presencia física. RESERVADA, MANTENIMIENTO, INACTIVA o DE_BAJA cuentan si siguen en la estación; EN_USO fuera de ella no. No se guarda un contador independiente que pueda desincronizarse.
5. El último espacio de una estación no puede asignarse dos veces. Todos los caminos de entrada, no solo devolver, deben aplicar el mismo control.
6. Una transición y sus hechos de inventario, costo e historia se confirman juntos; no se modifican entidades antes de descubrir una validación que se responderá como error sin revertir.
7. Estado inicial e historial se crean juntos y cada entidad con historial conserva al menos un registro. En los historiales exclusivamente de estado el anterior es nulo solo al crear. En los historiales ampliados de orden/incidencia ambos estados son nulos en eventos exclusivamente de datos; las transiciones exigen anterior/nuevo válidos y diferentes. La creación requiere nuevo inicial y anterior nulo, no una etiqueta que permita omitir historia previa.
8. Importes finales no negativos y montos de pago/reembolso positivos, con dinero ARS y precisión a definir; una operación pendiente no se cuenta como confirmada.
9. Los reembolsos de un pago no pueden exceder lo efectivamente cobrado ni duplicar una obligación por reintento. La comprobación del agregado debe protegerse concurrentemente.
10. Los eventos repetidos de pago, vencimiento, devolución, incidencia o liquidación son idempotentes. La clave local del intento no sustituye conciliar el resultado externo.
11. Solo se liquida cuando los detalles son terminales y no hay revisiones económicas relevantes pendientes. El reporte, su decisión y la liquidación se coordinan para no omitir un aviso ya registrado.
12. Como máximo un cierre/corte autorizado vigente del detalle; la recepción posterior no crea otro cargo. No se admite modificar por el circuito normal una liquidación definitiva para resolver un reclamo posterior no definido.
13. Nullable significa que el hecho aún no ocurrió o que no aplica, no permiso para omitir datos obligatorios de una operación. Por ejemplo, DEVUELTO exige recepción real; CERRADO_POR_INCIDENCIA exige decisión y corte, no devolución ficticia.
14. Inactivar o dar de baja no termina una reserva ni un viaje por sí solo; las operaciones específicas conservan motivo, actor y efecto económico.
15. Un flag de visibilidad o baja lógica nunca elimina un alquiler del cálculo de deuda, de sus pagos ni de la auditoría.
16. Los historiales financieros se añaden, no se editan ni eliminan mediante el ABM normal. El estado actual y su nueva transición se confirman en la misma transacción local, con control de concurrencia. Una notificación duplicada no crea otra transición efectiva; el registro técnico que requiera se concreta en D03 y no se inserta como actuación de ADMIN. Las observaciones no almacenan secretos ni datos de tarjeta.
17. UQ_ALQUILER_BICICLETA es una única restricción sobre (alquiler_id, bicicleta_id), no dos UNIQUE individuales. El detalle conserva tipo_bicicleta_contratado_id fijado al confirmar; no se modifica por reclasificar la unidad ni se usa la tarifa vigente del catálogo para recalcular el pasado.
18. RN-ALQ-10 exige segundos completos del intervalo y subtotales monetarios con dos decimales HALF_UP por detalle y moneda. Los totales son suma de esos subtotales; ARS no se obtiene del subtotal USD ya redondeado. Un valor derivado cero no obliga a crear otra operación financiera.

Las estrategias de bloqueo, orden de adquisición, índices y control optimista se concretarán al diseñar las migraciones y servicios. No se mantienen bloqueos mientras el usuario está en la pasarela ni esperando un correo.

## 7. Decisiones que todavía deben cerrarse por su módulo

| ID | Pendiente | Cómo afecta al diseño |
| --- | --- | --- |
| D01 | Formatos documentales por tipo/país y transición del legado sin documento | Ya aprobados TIPO_DOCUMENTO, PAIS, DNI o pasaporte, obligatoriedad al registrarse y unicidad compuesta; no reabrir esas decisiones. Concretar normalización, datos iniciales y migración sin inventar identidad |
| D02 | Fuente/tipo de cotización, frescura y fallos; precisión física de entradas | RN-ALQ-10 ya aprobó segundos completos y redondeo a dos decimales por moneda/detalle, con totales por suma. Siguen pendientes fuente, tipo, frescura y fallos de cotización; precisiones SQL de tarifa/cotización y timestamps se concretan en D06 |
| D03 | Variante de API de Checkout Pro, correlaciones, medios habilitados, notificaciones, mínimos y pruebas | RN-PAG-03 ya aprobó la cancelación durante un intento en gestión y RN-PAG-05 el checkout externo. Quedan referencias de checkout/orden/pago, correspondencia con transacciones/reintentos, validación de resultados y configuración compatible con el plazo. No confundir la experiencia elegida con una integración probada |
| D04 | Alcance de QR/candado real o simulado; medios guardados ya excluidos de esta versión | El usuario sustituyó la vinculación local del PDF por elegir el medio en Mercado Pago, según RN-PAG-05. No se agregan PERFIL_PAGO, MEDIO_PAGO_GUARDADO ni FK a tarjetas; el cambio debe reflejarse al consolidar la documentación académica. El hardware sigue por definir |
| D05 | Intervalos preventivos iniciales por tipo y detalles de calendario | El campo ya está previsto; los ejemplos de meses no se cargan como política técnica real |
| D06 | Tipos SQL, longitudes, nulabilidad condicional, índices y migración de datos antiguos | Este archivo no ejecuta DDL ni decide cómo recuperar datos históricos inexistentes |
| D07 | Representación de trazabilidad y fundamento del corte aprobada; implementación pendiente | RN-TRZ-01 incorpora historial de incidencia, ampliación/renombre del historial de orden, motivo de auditoría ADMIN e incidencia_corte_id opcional FK/UK. D07-A aprobado; D07-B descartado. Faltan concretar formatos/acciones, restricciones físicas y servicios/pruebas de D06; no otra aprobación de estas cuatro mejoras |
| D08 | Precisión de costos internos de repuestos | La moneda ARS ya fue aprobada en el documento 27 y reflejada en el Mermaid; queda concretar precisión SQL. No confundir repuestos con cargo al cliente ni costos desconocidos con cero |
| D09 | Validaciones de duración estimada y límites acumulados por usuario; composición base ya cerrada | RN-ALQ-11 aprobó origen común, máximo inicial de diez configurable y selección fija, conservando cancelaciones aprobadas. Se trasladó la FK de retiro a la cabecera en el Mermaid. Duración y límites acumulados no se dan por definidos ni implementados |

Las políticas base de reserva, costo real, anticipo, tarifa por tipo y cotización congeladas, devolución, estados, permisos, preventivo e incidencias ya están aprobadas. Los pendientes anteriores no significan volver a discutirlas; son decisiones acotadas para completar datos e integración.

El usuario eligió posteriormente Mercado Pago y planteó una integración futura con herramientas de prueba; se registra en [el documento 23](23-pasarela-mercadopago-y-pruebas.md). El borrador conserva registros propios de pago, reembolso e incidencia: representan su relación con el negocio. El adaptador local sigue propuesto. No se implementaron SDK, credenciales, cobros ni nuevas tablas físicas. El modelo lógico vigente tiene 29 entidades tras RN-TRZ-01.

## 8. Qué se reutiliza y qué no se toca todavía

Se mantienen como punto de partida Java/Spring Boot, MySQL local, frontend, autenticación, BCrypt, correo y recuperación. Se adaptarán DTO, repositorios y servicios por incrementos. Conservar relaciones del DER no significa mantener entradas HTTP que acepten libremente una entidad completa.

Tarjeta y Suscripcion no aparecen en el DER v4 ni se copian automáticamente al nuevo. No se borran ahora de Java o MySQL. La tarjeta actual contiene un campo CVV; no se reutilizará como modelo de una integración de pagos reales. RN-PAG-05 excluyó expresamente la gestión local de tarjetas y descartó las dos entidades propuestas; D04 ya no pide decidir esa incorporación. El tratamiento del legado corresponde al plan de migración, no a borrar datos mediante este análisis.

No se ejecuta el test de contexto actual contra una base no aislada. Antes de implementar se prepara rama de trabajo, respaldo de los datos que deban preservarse y una base de desarrollo separada con migraciones reproducibles. Ninguna de esas acciones se realizó mediante este documento.

## 9. Orden de revisión siguiente

La identificación, el acceso, la baja lógica de estación, mantenimiento, los refuerzos de alquiler y RN-TRZ-01 ya se incorporaron al DER con aprobación. La revisión financiera registra RN-PAG-03 y el checkout externo sin tarjetas locales de RN-PAG-05. Siguen diseño físico/migración y puntos técnicos de integración de D03/D06. Las reglas se contrastan con los casos CP-* especificados, no con clases desconectadas generadas de una vez.

El [documento 25](25-revision-personas-usuarios-y-roles.md) conserva la aprobación de los catálogos, el documento compuesto y el nickname, con sus claves y relaciones integradas. El [documento 26](26-revision-estaciones-tipos-y-bicicletas.md) revisa inventario y registra RN-EST-01 aprobada: baja exclusivamente lógica de estación, sin bicicletas físicas ni retiros pendientes y sin pérdida de referencias. Sigue mantenimiento; las longitudes nuevas, concurrencia y migración no se presentan como implementadas por actualizar el modelo.

La revisión de mantenimiento está en el [documento 27](27-revision-ordenes-e-historial-mantenimiento.md): conserva catálogos, orden e historial y precisa la trazabilidad de cambios sin transición de estado. Diagnostico separado y moneda ARS de repuestos ya fueron aprobados e incorporados a ORDEN_MANTENIMIENTO, sin nuevas entidades o relaciones. Sigue ALQUILER y ALQUILER_DETALLE. El máximo de una orden abierta no se representa con UNIQUE global sobre bicicleta_id, pues la unidad conserva varias órdenes históricas.

El [documento 28](28-revision-alquiler-y-detalles.md) registra ambos refuerzos aprobados e incorporados: UNIQUE(alquiler_id, bicicleta_id) y tipo_bicicleta_contratado_id como FK obligatoria al catálogo de tipos. El modelo tiene 28 entidades y 52 FK/relaciones. La primera no sustituye proteger exclusividad entre cabeceras distintas; la segunda no sustituye la tarifa USD ya congelada. La precisión temporal/monetaria se aprobó después en RN-ALQ-10; sigue composición de contratación y los demás pendientes de D02/D03.

El [documento 30](30-propuesta-composicion-contratacion.md) registra RN-ALQ-11 aprobada: origen único, máximo inicial de diez configurable y selección fija, conservando las cancelaciones vigentes. Se trasladó estacion_retiro_id a ALQUILER como FK obligatoria no UNIQUE a ESTACION.id y se reemplazó la relación de retiro; se mantienen 28 entidades y 52 FK/relaciones. La devolución permanece por detalle. El límite no se representa mediante una tabla nueva ni elimina el control de disponibilidad. La cotización, los intervalos preventivos y ciertos detalles de integración pueden concretarse por módulos sin exigir que todo el backend espere a su resolución; las asociaciones históricas y correlaciones de operaciones externas requieren revisión antes de dar el DER por cerrado. RN-PAG-05 ya excluyó medios guardados locales, sin entidades nuevas. No se implementó todavía el nuevo recorrido.

El [documento 31](31-revision-pagos-reembolsos-y-medios-guardados.md), del 1 de noviembre, revisa PAGO, REEMBOLSO y sus historiales y registra RN-PAG-03 aprobada. RN-PAG-04 y sus dos entidades de medios guardados quedaron descartadas, no pendientes de incorporación. El [documento 32](32-pago-externo-con-mercadopago.md) registra RN-PAG-05: pagar en Mercado Pago y no administrar tarjetas localmente. Se conserva el antecedente y el cambio de alcance del PDF. Los controles de reembolso no requieren otra tabla y desarrollan la conservación del importe y la ausencia de duplicados ya aprobadas. El modelo sigue en 28 entidades y 52 FK/relaciones, con comentarios actualizados; no se ejecutaron SQL ni pruebas de integración.

El [documento 33](33-revision-trazabilidad-incidencias-y-ordenes.md) conserva el antecedente D07 y el [documento 34](34-trazabilidad-ordenes-e-incidencias.md) la revisión del modelo previo de 28/52. Los documentos [35](35-auditoria-admin-y-brechas-de-trazabilidad.md) y [36](36-incorporacion-aprobada-trazabilidad-der.md) registran la aprobación e incorporación de las cuatro mejoras RN-TRZ-01. El modelo vigente tiene 29 entidades y 55 FK/relaciones: historial de incidencia, historial de orden ampliado/renombrado, motivo administrativo e incidencia_corte_id opcional FK/UK del mismo detalle. HISTORIAL_ATENCION_MANTENIMIENTO sigue descartado. Los originales/código/base permanecen sin cambios y no se ejecutaron pruebas de negocio.

La política de precisión temporal/monetaria está aprobada en el [documento 29](29-propuesta-precision-tiempo-y-redondeos.md) y reflejada en comentarios del modelo: segundos completos, HALF_UP a dos decimales por detalle y moneda, sin convertir desde USD redondeado y totales por suma. Sus ejemplos se verificaron aritméticamente. No se añadieron atributos ni cambiaron tipos, claves o relaciones; Java, SQL y datos existentes permanecen sin cambios y los casos de negocio no se ejecutaron.

El diagrama es Mermaid editable, con claves, relaciones y comentarios de opcionalidad; esos comentarios no son DDL. La sintaxis de cardinalidad y claves se contrastó con la [documentación oficial de Mermaid](https://mermaid.js.org/syntax/entityRelationshipDiagram.html). No hay un renderizador Mermaid instalado en el entorno observado; no se presenta una imagen renderizada ni una validación de su motor gráfico. Se verifican por separado sus entidades, referencias y campos mediante comprobaciones estructurales.

Esta revisión no aprueba automáticamente todos los campos propuestos. Permite empezar a validar un DER trazable y no obliga a crear 28 clases o tablas de una vez.

La trazabilidad financiera del [documento 24](24-propuesta-historial-financiero.md) ya fue aprobada para el modelo: se incorporaron ambos historiales al archivo Mermaid y se preservó el resto del borrador. Sigue pendiente implementarlos en los servicios y la base, con registro transaccional, consultas y pruebas; la auditoría genérica no se presenta como sustituto de esos historiales.

## 10. Comprobación estructural inicial

Ejecutada el 28 de octubre de 2026 sobre el texto del modelo y las referencias de la documentación:

- Original: 21 entidades; borrador v5 actualizado: 28; las 21 originales están presentes y las siete incorporaciones coinciden con el mapa anterior.
- Se localizaron 52 relaciones y 52 atributos FK; cada FK tiene una entidad destino declarada y una relación correspondiente, incluso cuando hay varios vínculos con USUARIO, ESTACION o un catálogo de estados.
- Al incorporar la identificación al modelo de 26 entidades, se conservaron exactamente los atributos de las otras 24 entidades y las 49 relaciones previas. Se añadieron TIPO_DOCUMENTO y PAIS, dos FK/relaciones hacia PERSONA, el número documental y nickname. Se retiró únicamente el atributo dni sustituido por la identificación aprobada. Después se aclaró la baja exclusivamente lógica en el comentario de borrado_estacion, sin agregar ni retirar campos, claves o relaciones.
- Las PK de ambos catálogos y sus FK tienen tipo int. Codigo es único en cada catálogo; nickname y email son únicos individualmente. UQ_PERSONA_DOCUMENTO identifica una única restricción compuesta y no tres restricciones independientes.
- Las entidades tienen PK y no repiten nombres de atributos; USUARIO_ROL conserva sus dos columnas de clave compuesta.
- Al consolidar mantenimiento se añadió únicamente diagnostico como text a ORDEN_MANTENIMIENTO y se precisaron los comentarios de costo_repuestos/moneda_repuestos para ARS interno. No cambiaron las PK, FK, unicidades o relaciones del bloque ni de las demás entidades.
- En el refuerzo de alquiler se añadió una FK int de ALQUILER_DETALLE a TIPO_BICICLETA y su relación obligatoria de tipo a muchos detalles. Se conservaron las otras 27 entidades, las 51 relaciones anteriores y todas las PK y UK individuales. UQ_ALQUILER_BICICLETA se identifica en los comentarios del modelo y de sus dos atributos como una sola clave compuesta.
- RN-ALQ-10 se reflejó mediante comentarios globales y de duración/importes. La comparación estructural conserva todos los nombres y tipos de campos, PK, FK, UK y las 52 relaciones previas; no es una modificación de código o de la base.
- La tarifa vigente está en TIPO_BICICLETA y no en BICICLETA. El detalle conserva el precio aplicado, corte de uso y recepción real; la cabecera conserva vencimiento y liquidación independientes.
- Los enlaces relativos a documentos y modelos no presentan destinos inexistentes.

Resultado: comprobación estructural satisfactoria. No es una ejecución del parser gráfico de Mermaid, de SQL, de JPA ni de los casos CP-* del negocio. El diff de los archivos de aplicación no presenta cambios por esta revisión. No se abrió una conexión a la base ni se ejecutó el arranque de Spring.

## 11. Comprobación de RN-TRZ-01 del 2 de noviembre

Se comprobó el modelo actualizado de 29 entidades, 55 columnas FK y 55 relaciones. Las 55 FK tienen destino y tipo compatibles y cada relación se corresponde con una FK identificada. No hay nombres duplicados de entidad o atributo y todas las entidades tienen PK.

Respecto del modelo previo de 28/52, se conservaron íntegramente 25 entidades. Las otras tres solo reciben los cambios aprobados: detalle con incidencia_corte_id, historial de orden renombrado/ampliado y auditoría con motivo. Todos los campos previos conservan nombre, tipo y claves; el nuevo nombre del historial no elimina sus ocho campos. Se conservaron conceptualmente las 52 relaciones anteriores, con el renombre y la opcionalidad condicional del nuevo estado de orden; se añadieron las tres relaciones aprobadas.

Los once campos de cada historial nuevo/ampliado coinciden con sus tablas documentales. La UK opcional del corte está presente, pero no se añadió UNIQUE al detalle de INCIDENCIA ni a su FK de historial, por lo que se conservan varios reportes y eventos. No se incorporó HISTORIAL_ATENCION_MANTENIMIENTO ni una segunda tabla de historial de orden.

El detalle de condiciones y casos futuros está en el documento 36. Los enlaces documentales revisados tienen destino existente. La comprobación es estructural del texto: no ejecuta Mermaid, SQL, JPA o casos de negocio. No se modificó la aplicación ni se conectó una base de datos.
