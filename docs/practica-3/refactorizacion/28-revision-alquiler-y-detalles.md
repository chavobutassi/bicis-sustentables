# Revisión de alquiler y detalles

Fecha: 28 de octubre de 2026.

Estado: unicidad alquiler/bicicleta, FK al tipo contratado, RN-ALQ-10 y RN-ALQ-11 aprobadas e incorporadas. El 2 de noviembre RN-TRZ-01 incorpora además incidencia_corte_id opcional FK/UK de la incidencia determinante del mismo detalle. El modelo completo queda en 29 entidades y 55 FK/relaciones por las cuatro mejoras de trazabilidad. Se conservan cobro real, origen único en cabecera, máximo inicial de diez configurable y selección fija. Java y la base siguen sin cambios; los casos de negocio no se ejecutaron.

## 1. Fuentes y situación actual

Se contrastaron el [DER v4 original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>), los apartados de visión y requerimientos del [PDF](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), el [diccionario original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y las aprobaciones posteriores de esta carpeta. Las multas, el cierre forzoso a las 24 horas y FINALIZADO dependiente del pago del Word no se reintroducen: quedaron sustituidos por reglas aprobadas.

El código actual sigue teniendo un Alquiler por bicicleta y un DTO de creación con bicicletaId y duracionEnHoras. Conserva un precio aplicado, pero no implementa todavía cabecera y detalles, la reserva nueva de 15 minutos ni la liquidación económica conjunta. Sus consultas de estadísticas agrupan por el tipo actual de la bicicleta. Son hechos observados en archivos; no se ejecutó la aplicación ni se consultó MySQL.

La estructura cabecera/detalle del DER original y del v5 es adecuada para la visión del proyecto y las devoluciones independientes. No hace falta agregar entidades para deuda, demora o cotización por esta revisión.

## 2. Claves y relaciones del bloque

ALQUILER conserva id como PK, usuario_id como FK obligatoria a USUARIO.id y estado_alquiler_id como FK obligatoria a ESTADO_ALQUILER.id. Con RN-ALQ-11 incorpora estacion_retiro_id como FK obligatoria a ESTACION.id, no UNIQUE, para el origen común. Una cuenta puede tener muchas contrataciones históricas y cada contratación pertenece a una cuenta identificada por su id, no por un email o nickname que pueda cambiar.

ALQUILER_DETALLE conserva id como PK y las FK a su cabecera, bicicleta, estado de detalle y estación de devolución, e incorpora la FK al tipo contratado. La estación de retiro se obtiene ahora de su cabecera, sin otra columna duplicada en el detalle. Una cabecera confirmada tiene entre uno y diez detalles según el máximo inicial configurable; cada detalle pertenece a exactamente una cabecera. Una bicicleta tiene muchos detalles históricos: no debe marcarse bicicleta_id como UNIQUE global. La unicidad aprobada se aplica al par alquiler_id/bicicleta_id. Las FK y ese par único no impiden por sí solos dos reservas activas bajo cabeceras diferentes.

estacion_retiro_id es obligatoria en ALQUILER y representa la estación contratada para todas sus unidades, sin afirmar que ya hubo retiro. estacion_devolucion_id sigue en ALQUILER_DETALLE y es opcional hasta una recepción normal válida. orden_mantenimiento_id y reportado_por_id son referencias opcionales del reporte de devolución; no se usan para inventar una devolución ni un técnico. El usuario propietario se obtiene de la cabecera, sin duplicar otro usuario_id en cada detalle.

HISTORIAL_ESTADO_DETALLE conserva su PK y FK al detalle, estados anterior/nuevo y actor. La creación y cada transición válida dejan historia en la misma transacción local. El estado de cabecera se reconstruye del conjunto de detalles y sus hechos; las acciones administrativas tienen además AUDITORIA_SISTEMA, exclusivamente de ADMIN. No se atribuyen a esa auditoría operaciones del cliente o sistema. Los fundamentos económicos por incidencia conservan ahora la FK del corte y el historial del reporte según RN-TRZ-01.

incidencia_corte_id es int, FK opcional a INCIDENCIA.id y UK cuando tenga valor. La incidencia debe pertenecer al mismo detalle y fundamentar un corte validado; la FK simple y la UK no verifican por sí solas esa condición cruzada. La relación es cero o uno en ambos extremos y no sustituye INCIDENCIA.alquiler_detalle_id, obligatoria y no UNIQUE para permitir varios reportes. Ver las condiciones de creación/validación y el ciclo opcional de referencias en el documento 36.

## 3. ALQUILER y el significado de sus campos

| Campo o grupo existente | Significado y condiciones |
| --- | --- |
| id, usuario_id, estado_alquiler_id | Identidad, contratante y resumen operativo; el frontend no decide libremente el propietario o estado |
| estacion_retiro_id | FK obligatoria al origen común contratado, según RN-ALQ-11; se conserva históricamente y no prueba que ya se retiraron las unidades |
| fecha_hora_creacion | Confirmación de la contratación, no la apertura de una pantalla o carrito sin confirmar |
| fecha_hora_vencimiento_reserva | Creación más 15 minutos originales; no cambia por pagar o reintentar y no es el fin del uso de las unidades |
| fecha_hora_cierre | Nula mientras quedan usos o retiros pendientes; cierre operativo del conjunto cuando corresponde FINALIZADO, CANCELADO o VENCIDO |
| fecha_hora_cancelacion | Opcional; identifica la cancelación completa de cabecera, no la cancelación aislada de una de sus unidades |
| fecha_hora_liquidacion | Opcional hasta determinar el costo definitivo conjunto, con todos los detalles terminales y sin revisiones económicas pendientes; no significa pago ni reembolso completados |
| cotizacion_ars_por_usd | Valor positivo congelado al confirmar, antes del anticipo; una única cotización para toda la contratación |
| fuente_cotizacion | Fuente del valor realmente aplicado, sin secretos de integración |
| fecha_hora_aplicacion_cotizacion | Momento en que el sistema aplica ese valor al contrato |
| fecha_hora_actualizacion_fuente | Opcional si el proveedor no informa su fecha; no se inventa ni se confunde con la aplicación local |
| costo_estimado_usd, costo_estimado_ars | Estimación inicial calculada por backend desde los detalles y sus valores contratados; no demuestra dinero cobrado |
| costo_final_usd, costo_final_ars | Pendientes hasta liquidar; cero solo cuando el costo definitivo realmente es cero, no para ocultar una evaluación pendiente |
| borrado_alquiler | Dato de legado/visibilidad; no equivale a CANCELADO, no elimina filas ni permite omitir deuda, pagos o historia |
| version | Control optimista propuesto; debe coordinarse con las operaciones sobre detalles, no se presenta como protección automática del agregado |

Los totales de cabecera y los subtotales se mantienen por operaciones del backend. Si se persisten ambos, se validan sus sumas y redondeos; no se reciben como montos autoritativos desde el navegador. La situación financiera sigue derivándose de liquidación y movimientos confirmados, sin otra columna redundante o tabla nueva por iniciativa de esta revisión.

## 4. ALQUILER_DETALLE y el significado de sus campos

| Campo o grupo existente | Significado y condiciones |
| --- | --- |
| id, alquiler_id, bicicleta_id, estado_alquiler_detalle_id | Identidad de un recorrido individual, unidad y estado de uso; no se confunde con estado técnico o resultado de pago |
| tipo_bicicleta_contratado_id | FK obligatoria a TIPO_BICICLETA.id, copiada por el backend al confirmar y conservada como referencia histórica aunque cambie el tipo actual de la unidad |
| estacion_devolucion_id | Opcional hasta la recepción normal confirmada; estación activa válida con capacidad; un cierre excepcional no inventa esta estación |
| orden_mantenimiento_id | Enlace operativo de la atención del reporte; su reasignación debe conservarse en auditoría conforme a D07 |
| incidencia_corte_id | FK opcional y UK a INCIDENCIA.id; identifica la decisión validada que fundamenta el corte y debe pertenecer al mismo detalle; no se acepta libremente del cliente |
| precio_por_hora_aplicado_usd | Tarifa del tipo copiada al confirmar; permanece fija aunque el catálogo cambie |
| duracion_estimada_segundos | Duración contratada de referencia, positiva; no es mínimo de uso. RN-ALQ-10 define segundos completos y redondeos monetarios por detalle, sin bloques |
| fecha_hora_retiro | Opcional antes del retiro real; exige autorización, reserva vigente y anticipo requerido confirmado |
| fecha_hora_devolucion_estimada | Se determina desde el retiro real de esa unidad y su duración estimada, no desde la creación o retiro de otra bicicleta |
| fecha_hora_devolucion_real | Recepción física normal validada; se conserva aunque una incidencia autorice luego un corte económico anterior |
| fecha_hora_fin_uso | Corte facturable validado: normalmente recepción real, excepcionalmente el corte autorizado; puede quedar pendiente mientras se revisa el importe, sin que siga corriendo el contador tras una recepción ya registrada |
| fecha_hora_cierre_detalle | Nula antes de una transición terminal; fecha del cierre operativo, que no siempre coincide con recepción o decisión económica |
| subtotal_estimado_usd, subtotal_estimado_ars | Estimación de esa unidad con la tarifa y cotización contratadas; no es un pago independiente |
| subtotal_real_usd, subtotal_real_ars | Costo definitivo al validarlo; pueden estar pendientes con una revisión económica relevante, incluso en DEVUELTO |
| falla_reportada, descripcion_falla, fecha_reporte_falla, reportado_por_id | Reporte de falla del recorrido de devolución, con contexto y autor; no prueba una avería ni niega incidencias previas si no se reportó otra al devolver |
| origen_cierre, motivo_cierre | Distinguen CLIENTE, ADMIN o SISTEMA y la causa pertinente; el responsable concreto queda en historial/auditoría y los motivos son obligatorios cuando así lo exige la operación aprobada |
| version | Control de concurrencia de la unidad contractual; no sustituye coordinar bicicleta, estación y cabecera |

Para CANCELADO o VENCIDO sin retiro se fija costo real cero y se conservan los hechos de cierre, pero no se inventan retiro, devolución o corte de uso. El costo cero no permite deducir por sí solo que nunca hubo retiro: una devolución inmediata puede producir un importe redondeado cero y seguir siendo DEVUELTO.

La demora se obtiene de devolución estimada frente a recepción real; no exige otro estado o booleano que pueda contradecir las fechas. Puede coexistir con falla reportada. Una incidencia previa se consulta por INCIDENCIA: el booleano del reporte al devolver no sustituye esa consulta ni determina por sí solo si el conjunto puede liquidarse.

## 5. Tres cierres distintos y sus controles

Cerrar el uso de una unidad, cerrar operativamente el conjunto y terminar los movimientos de dinero son hechos diferentes. La primera bicicleta devuelta deja de cobrar y puede liberar su exclusividad sin esperar a las demás; la cabecera no termina mientras quedan detalles en uso o pendientes de retiro. El ajuste financiero es conjunto, no un reembolso/adicional por cada recepción intermedia.

Si todos los detalles son terminales pero una incidencia previa puede afectar el importe, la cabecera puede estar FINALIZADO y la situación SIN_LIQUIDAR. Ejemplo aprobado: retiro 10:00, interrupción reportada 10:45, recepción 11:00 y revisión 12:00. La recepción detiene el tiempo a las 11:00. Si se valida el corte anterior, se factura hasta 10:45; si se descarta, hasta 11:00, nunca hasta la revisión de las 12:00. La fecha física no se sobrescribe con la económica y DEVUELTO no se reemplaza después por CERRADO_POR_INCIDENCIA.

fecha_hora_fin_uso nula durante esa revisión no significa bicicleta todavía en uso. El servicio debe respetar la recepción y mostrar un costo provisional sin continuar con el reloj actual; el costo final se guarda después de validar el corte. Esa distinción ya fue aprobada y no añade un estado.

Una vez fijado el costo, los pagos/reembolsos confirmados actualizan el saldo sin recalcular silenciosamente el tiempo o reabrir detalles. Un anticipo tardío sobre una contratación cerrada sin uso puede cambiar SALDADO a REEMBOLSO_PENDIENTE por dinero recibido después, sin repetir la liquidación ni reactivar la reserva.

Las operaciones de última devolución, cancelación, vencimiento y decisión de incidencia deben coordinar la cabecera, los detalles y sus recursos antes de decidir que se puede liquidar. Actualizar únicamente un hijo no garantiza que se incremente la version de la cabecera: los servicios deben bloquear o actualizar el agregado de forma coherente y persistir el cierre/costo antes de depender de la pasarela.

## 6. Refuerzos aprobados e incorporados

### Una bicicleta una vez por contratación

Se define UQ_ALQUILER_BICICLETA = UNIQUE(alquiler_id, bicicleta_id), aprobada e identificada en los comentarios del Mermaid y de ambos atributos. Evita repetir la misma unidad en dos detalles de la misma contratación y cobrar o reservar dos veces una selección duplicada. No son UNIQUE individuales sobre alquiler_id o bicicleta_id, porque una cabecera agrupa varias unidades y cada unidad tiene muchos alquileres históricos. La futura migración deberá materializar una sola restricción sobre el conjunto: la declaración del dibujo no la ejecuta en la base actual.

Esta decisión aprobada implica que volver a contratar la misma bicicleta para otro recorrido requiere otra contratación, no agregarle un segundo detalle de esa unidad al mismo alquiler. No resuelve por sí sola la exclusividad entre dos cabeceras diferentes; esa condición exige el control transaccional sobre la bicicleta ya previsto en RN-ALQ-03.

### Conservar el tipo contratado

Se incorporó tipo_bicicleta_contratado_id como FK obligatoria de ALQUILER_DETALLE a TIPO_BICICLETA.id, ambos de tipo lógico int. Se copia del tipo de la unidad al confirmar y no se actualiza cuando luego se reclasifica la bicicleta. El catálogo puede tener cero o muchos detalles asociados y cada detalle nuevo tiene exactamente un tipo contratado. No se declara UNIQUE esta FK ni se crea otra tabla.

El precio aplicado ya protege el cálculo frente a una nueva tarifa. Esta FK adicional protege otra cosa: saber bajo qué tipo se contrató y poder consultar el historial/estadísticas sin depender del tipo actual de la unidad. No reemplaza precio_por_hora_aplicado_usd ni autoriza consultar la tarifa vigente para recalcular el pasado. Tampoco congela por sí sola el texto de un código de catálogo que luego se renombre: los cambios de etiquetas necesitan su trazabilidad correspondiente.

El tipo actual de BICICLETA sigue sirviendo a su administración y política preventiva; el tipo contratado es una referencia histórica del contrato. La redundancia es deliberada y temporal, no dos campos actuales que deban cambiarse juntos. Ese dato no debe aceptarse libremente del formulario.

Con ambas incorporaciones el modelo conserva 28 entidades y pasa de 51 a 52 FK/relaciones. Se añadió un campo y una relación, se aclararon dos atributos y se declaró explícitamente la unicidad compuesta; no se marcaron sus columnas como UK individuales. Las PK y las demás entidades y relaciones se conservaron. Esto acredita la incorporación al modelo lógico, no una migración ni comportamiento ya implementado.

## 7. Pendientes que no deben desaparecer del diseño

- D02/D06: [RN-ALQ-10](29-propuesta-precision-tiempo-y-redondeos.md) ya aprobó segundos completos y dos decimales HALF_UP por detalle/moneda con totales por suma. Faltan concretar precisión física de entradas, límites y timestamps; la escala de subtotales no resuelve esos otros datos.
- D02: fuente/tipo de cotización, frescura admisible y fallo del proveedor. La obligación de congelarla ya está aprobada; la API de la aplicación anterior no cierra esa elección.
- RN-ALQ-11 ya cerró origen común, máximo inicial de diez configurable y selección fija, con estación de retiro en cabecera. No se fijan todavía mínimos/máximos de duración estimada ni límites acumulados de unidades o contrataciones por usuario. La unicidad aprobada solo cierra la repetición de la misma bicicleta dentro de esa contratación y no sustituye la disponibilidad ni esos otros controles.
- D03: correlaciones y controles de integración del anticipo. RN-PAG-03 del documento 31 ya aprobó la cancelación parcial durante el intento: no se sobrescribe su importe ni se abre otro cobro con resultado incierto. RN-PAG-05 eligió checkout externo sin tarjetas locales. Quedan API y comprobaciones de vigencia/conciliación, respetando plazo y dinero recibido.
- D06: migración de alquileres antiguos con una bicicleta, timestamps, precio, tipo contratado o cotización no disponibles y sin comprobantes de pago del módulo nuevo. No se inventan anticipos, documentos ni cotizaciones o tipos históricos; el tipo actual de una unidad no prueba por sí solo cuál se contrató antes.
- Identificación visible histórica: la FK a una bicicleta conserva su identidad interna, no necesariamente el código mostrado antes de un cambio. La reproducción exacta de etiquetas exige una política de códigos estables o datos de comprobante conservados; no se añaden snapshots extra por iniciativa de este análisis.

incidencia_corte_id del [documento 33](33-revision-trazabilidad-incidencias-y-ordenes.md) fue aprobada e incorporada mediante RN-TRZ-01, junto con HISTORIAL_INCIDENCIA, la ampliación del historial de orden y motivo en la auditoría ADMIN. Las condiciones y claves vigentes están en el [documento 36](36-incorporacion-aprobada-trazabilidad-der.md). HISTORIAL_ATENCION_MANTENIMIENTO sigue descartado. La FK ya existe en el DER lógico, no en Java ni en una migración ejecutada. Conservar DEVUELTO y su fecha física y esperar las revisiones relevantes antes de liquidar sigue aprobado sin cambios.

Mercado Pago ya fue elegido, como registra el documento 23. Lo pendiente es su modalidad concreta, pruebas e integración, no elegir de nuevo el proveedor. La validación antigua de duración estimada de una a 24 horas tampoco se interpreta como un cierre automático a las 24 horas ni como un límite nuevo aprobado para el modelo refactorizado.

## 8. Criterios para implementar y verificar

Son especificaciones, no pruebas ejecutadas:

- CP-DER-ALQ-01: la cabecera confirmada tiene al menos un detalle y sus FK/estados apuntan a registros válidos, sin una creación parcial.
- CP-DER-ALQ-02: cada retiro tiene su inicio y devolución estimada propios; no empieza a cobrar por la reserva o pago.
- CP-DER-ALQ-03: una recepción parcial no liquida ni cierra unidades que siguen pendientes; cancelar/vencer una unidad nunca retirada no inventa uso.
- CP-DER-ALQ-04: una recepción con revisión económica pendiente detiene el reloj, conserva fechas físicas y posterga solo el importe/ajuste definitivo.
- CP-DER-ALQ-05: dos cierres concurrentes no duplican liquidación, movimientos ni historia; el mismo recurso no se reserva dos veces entre contrataciones distintas.
- CP-DER-ALQ-06: un pago tardío se conserva y concilia sin reabrir el contrato; borrar lógicamente no excluye dinero ni deuda de las consultas pertinentes.
- CP-DER-ALQ-07: repetir una bicicleta dentro de la misma contratación se rechaza; su uso en otras contrataciones históricas sigue permitido.
- CP-DER-ALQ-08: cambiar el tipo actual de una bicicleta no cambia el tipo contratado ni la tarifa aplicada de su detalle histórico.

## 9. Aprobación y siguiente definición

El usuario confirmó «apruebo las dos mejoras». Se incorporaron unicidad alquiler/bicicleta y FK al tipo contratado, sin nuevas tablas ni cambio del cobro por tiempo real. RN-ALQ-10 aprobó después precisión/redondeos y RN-ALQ-11 la composición, origen en cabecera y máximo inicial de diez configurable. RN-PAG-05 descartó medios guardados locales y RN-TRZ-01 incorporó posteriormente la FK del corte y sus mejoras de trazabilidad. Siguen detalles físicos/de integración D03/D06, no una incorporación pendiente de tarjetas. La comprobación estructural no ejecuta SQL ni casos de negocio; Java y la base permanecen sin cambios.
