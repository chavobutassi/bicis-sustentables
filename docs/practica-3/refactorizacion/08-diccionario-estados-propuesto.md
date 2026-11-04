# Propuesta unificada de estados y transiciones

Fecha: 25 de octubre de 2026.

Actualizado: 28 de octubre de 2026.

Estado: diseño validado por bloques, todavía no implementado. RN-ALQ-01 a RN-ALQ-09 definen el alquiler, cabecera y situación financiera; RN-BIC-02 completa la administración y RN-INC-01 incorpora el circuito mínimo de incidencias. Los catálogos de bicicleta y detalle tienen ahora siete estados cada uno. Se mantienen cinco estados de cabecera, cuatro situaciones financieras, cinco de orden, cinco de pago y cuatro de reembolso. RN-MAN-01 a RN-MAN-04 definen tipos, trabajo técnico, generación de órdenes y preventivo por calendario; RN-PAG-01/RN-PAG-02 definen movimientos y reintentos. La precisión económica de la sección 8 de RN-INC-01 también está aprobada; siguen pendientes las decisiones de datos, integración e implementación expresamente indicadas. Una aprobación no equivale a código ni a pruebas ejecutadas.

## 1. Propósito

Actualización de aprobación: el usuario confirmó los puntos administrativos 1 a 6 de [RN-BIC-02](20-propuesta-administracion-y-excepciones-bicicletas.md) y después autorizó el circuito mínimo de [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md), tras revisar su coherencia. Se incorporan inactivación, reactivación, baja, cancelación administrativa, trazabilidad y los estados adicionales EXTRAVIADA y CERRADO_POR_INCIDENCIA. El usuario confirmó también la sección 8 de RN-INC-01: se registra la devolución y se detiene el tiempo, pero la liquidación espera las revisiones pendientes que puedan afectar el importe. No se implementó el diseño.

Concretar las reglas de alquiler en estados distinguibles y transiciones controladas antes de corregir el DER. La base es la [revisión del diccionario original](07-revision-diccionario-de-estados.md), sin modificar el Word aportado por el usuario.

El estado del uso, la situación financiera y el estado de cada operación de pago representan hechos diferentes. No deben sustituirse entre sí.

## 2. Detalle de alquiler

Cada detalle representa una bicicleta específica dentro de una contratación.

Los seis nombres iniciales fueron confirmados en [RN-ALQ-09](16-estados-detalle-alquiler.md). RN-BIC-02 amplió CANCELADO con causa administrativa autorizada y RN-INC-01 agregó después CERRADO_POR_INCIDENCIA. El catálogo vigente del diseño tiene siete estados, sin permisos generales para alterar libremente sus destinos.

| Estado aprobado | Significado | Costo de uso |
| --- | --- | --- |
| RESERVADO | Unidad asignada de manera exclusiva; el anticipo requerido todavía no está confirmado | No acumula |
| PENDIENTE_RETIRO | Anticipo requerido confirmado; falta el retiro y sigue vigente el plazo original | No acumula |
| EN_CURSO | Retiro válido confirmado por el backend | Acumula desde su retiro efectivo |
| DEVUELTO | Devolución válida confirmada en una estación con espacio | Por su tiempo real; provisional si existe una incidencia previa pendiente que pueda cambiar el importe |
| CERRADO_POR_INCIDENCIA | ADMIN autorizó terminar excepcionalmente el uso sin devolución normal; se conserva decisión y corte validado | Hasta el corte validado, no hasta la revisión administrativa |
| CANCELADO | Cancelación voluntaria del cliente o administrativa autorizada, sin retiro y dentro del plazo, con causa y actor distinguibles | Cero |
| VENCIDO | Se alcanzó el plazo de 15 minutos sin retirar esa unidad | Cero |

DEVUELTO incluye la devolución anterior o posterior al tiempo estimado. El mayor uso aumenta el costo proporcional con la tarifa contratada, pero no genera una multa. El retraso puede mostrarse comparando fechas, sin necesitar otro estado de uso para facturarlo.

### Correspondencia con el Word y el PDF originales

El [Word original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) ya distingue el contrato individual de la bicicleta y define PENDIENTE_RETIRO después del pago. El [PDF de visión](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>) crea el detalle antes de confirmar el pago. La propuesta precisa esa fase previa mediante RESERVADO, sin habilitar el retiro ni iniciar el tiempo de uso.

- RESERVADO y PENDIENTE_RETIRO separan el anticipo todavía no confirmado del retiro ya autorizado por un anticipo válido. En ambas fases la bicicleta sigue físicamente en la estación y su estado operativo es RESERVADA.
- EN_CURSO representa el retiro efectivo validado, no el solo escaneo de un QR. El alcance físico o simulado del candado continúa pendiente; no se afirma que ya esté implementado.
- DEVUELTA_OK, DEVUELTA_CON_RETRASO y DEVUELTA_CON_FALLA del Word se representan mediante DEVUELTO más las condiciones independientes aprobadas en RN-ALQ-06. Se conserva la información de demora y falla, incluido el caso combinado, sin multa por demora.
- CANCELADO identifica la cancelación voluntaria de una unidad no retirada y, por la ampliación posterior RN-BIC-02, la cancelación administrativa autorizada antes del retiro. VENCIDO identifica que agotó el plazo sin retiro. Se conservan causa y actor; no se pierde la distinción de los nombres originales CANCELADO_POR_USUARIO y CANCELADO_POR_VENCIMIENTO.
- Un rechazo confirmado del anticipo conserva la fase RESERVADO del detalle durante la reserva vigente. Reintentar no inicia el uso ni reinicia los 15 minutos, según RN-PAG-02. La confirmación del pago tampoco reinicia ese plazo.
- RETENIDO_SISTEMA y el cierre forzoso después de 24 horas no se incorporan a este catálogo por falta de una regla aprobada para esa excepción.

No se reutiliza RECHAZADO como estado del detalle: describe un intento de pago. Tampoco se usa MANTENIMIENTO como estado de uso del detalle: describe la condición operativa de la bicicleta después de una devolución con falla reportada, conforme a RN-BIC-01.

### Condiciones de devolución aprobadas

El usuario aprobó conservar DEVUELTO como estado de uso y distinguir dos condiciones independientes: cumplimiento del tiempo estimado y existencia de un reporte de falla. Se documentó en [RN-ALQ-06](09-devolucion-demora-y-fallas.md), incluyendo el bloqueo de la bicicleta para revisión técnica si hay falla reportada.

| Tiempo de devolución | Reporte de falla | Presentación posible en el historial |
| --- | --- | --- |
| Dentro del estimado | Sin falla reportada | Devuelta normalmente |
| Con demora | Sin falla reportada | Devuelta con demora |
| Dentro del estimado | Falla reportada | Devuelta con falla reportada |
| Con demora | Falla reportada | Devuelta con demora y falla reportada |

La demora se obtiene comparando la fecha real con la fecha estimada del detalle, que deben conservarse separadas. No implica una multa ni cambia la tarifa acordada. El reporte de falla, en cambio, es información que debe registrarse; no se deduce de los tiempos.

Se distinguen SIN_FALLA_REPORTADA y FALLA_REPORTADA como condición informada de devolución, acompañando el reporte con su descripción, autor y fecha según las validaciones del recorrido. La ubicación física definitiva de esos datos en el DER se resolverá después. SIN_FALLA_REPORTADA no certifica técnicamente que no exista una avería, y FALLA_REPORTADA no demuestra por sí sola la responsabilidad del cliente.

Para una devolución válida con falla reportada se aprobó una excepción explícita a la disponibilidad normal: se termina el uso y se detiene el costo del cliente, pero la bicicleta queda fuera de alquiler a la espera de revisión técnica. Sigue ocupando el lugar físico de la estación donde se recibió. No se aprueba un cargo por daños ni un diagnóstico automático por el simple reporte.

La excepción aprobada completa las reglas anteriores de devolución. La creación correctiva desde el reporte, la asignación y los permisos, la decisión técnica y la habilitación posterior se completaron después mediante RN-MAN-02 y RN-MAN-03. RN-MAN-04 agrega expresamente que una preventiva vencida también deja la unidad en MANTENIMIENTO al devolver, aunque no haya falla reportada, sin prolongar el costo de uso. Los recorridos adicionales de incidencias siguen separados; no está aprobado todo el módulo por la sola regla de devolución.

### Transiciones propuestas

| Origen | Evento | Destino | Actor y controles | Efectos |
| --- | --- | --- | --- | --- |
| Sin detalle | Confirmar contratación | RESERVADO | Cliente autenticado y activo, sin deuda que impida contratar; disponibilidad verificada de manera atómica | Asigna la unidad, guarda tarifa/cotización, inicia la reserva de 15 minutos y registra historial |
| RESERVADO | Confirmar anticipo requerido | PENDIENTE_RETIRO | Sistema, con confirmación de pago validada y antes del vencimiento | Habilita el retiro; no reinicia el plazo ni cobra tiempo de reserva |
| PENDIENTE_RETIRO | Confirmar retiro | EN_CURSO | Cliente propietario mediante el recorrido autorizado; pago, reserva, unidad y plazo válidos | Guarda fecha real de retiro, inicia su contador y retira la unidad de la ocupación de la estación |
| EN_CURSO | Confirmar devolución válida | DEVUELTO | Propietario o administrador autorizado; estación válida con capacidad | Guarda fecha/estación real y costo y termina el uso; unidad disponible solo sin falla ni preventiva vencida u otro impedimento. Si requiere revisión queda MANTENIMIENTO; revisa el cierre del conjunto |
| EN_CURSO | Autorizar cierre por incidencia | CERRADO_POR_INCIDENCIA | ADMIN; reporte, motivo, corte y estado vigentes comprobados | Termina ese uso con corte validado, conserva tarifa/cotización y deja la unidad fuera de alquiler según el incidente, sin inventar devolución ni cerrar otras unidades |
| RESERVADO o PENDIENTE_RETIRO | Cancelar unidad antes de vencer | CANCELADO | Cliente propietario; todavía no retirada | Libera la exclusividad, conserva ubicación física e historial y aplica RN-ALQ-05 |
| RESERVADO o PENDIENTE_RETIRO | Cancelar por motivo operativo o de seguridad antes de vencer | CANCELADO | ADMIN; motivo y ausencia de retiro comprobados | Conserva costo cero y ubicación; deriva la bicicleta a MANTENIMIENTO o INACTIVA según causa, informa al cliente y trata el anticipo por RN-BIC-02 |
| RESERVADO o PENDIENTE_RETIRO | Alcanzar vencimiento sin retiro | VENCIDO | Sistema; compara plazo persistido y estado vigente | Libera únicamente esa reserva, conserva ubicación física y aplica RN-ALQ-03 |

DEVUELTO, CANCELADO, VENCIDO y CERRADO_POR_INCIDENCIA son terminales del detalle. Un pago tardío, una recuperación física posterior o una operación financiera pendiente no los devuelven a un estado de uso. Una nueva contratación crea su propio detalle. La recepción posterior a un cierre excepcional se registra como recuperación, no como una segunda devolución facturable.

Un intento de retiro que llega al vencimiento se rechaza. Un escaneo de QR no basta para cambiar el estado sin las validaciones del backend. El alcance del candado físico sigue pendiente.

### Disponibilidad física y exclusividad

Una bicicleta cuyo detalle está en RESERVADO o PENDIENTE_RETIRO permanece físicamente en su estación y ocupa un lugar, aunque otro cliente no pueda contratarla. El estado operativo de esa bicicleta es RESERVADA; PENDIENTE_RETIRO pertenece al detalle, no al catálogo de la bicicleta. Cancelar o vencer esa reserva no libera un espacio físico: termina su exclusividad. Solo puede ofrecerse nuevamente si no hay impedimentos; si venció la preventiva, pasa a MANTENIMIENTO según RN-MAN-04.

La devolución de un detalle puede ocurrir cuando ya existe una reserva nueva sobre otra unidad del mismo alquiler. Cada transición debe afectar a su detalle y bicicleta, sin liberar asignaciones posteriores por una petición repetida.

## 3. Cabecera del alquiler

La cabecera resume el uso del conjunto, no sustituye los estados financieros.

Los cinco estados de esta sección fueron aprobados por el usuario y se formalizaron en [RN-ALQ-07](10-estados-cabecera-alquiler.md).

| Estado aprobado | Condición |
| --- | --- |
| RESERVADO | No hubo retiros y existe por lo menos un detalle RESERVADO o PENDIENTE_RETIRO |
| EN_PROGRESO | Hubo al menos un retiro y todavía existe un detalle EN_CURSO o pendiente de retiro |
| FINALIZADO | Hubo al menos un retiro y todos los detalles son terminales: DEVUELTO, CANCELADO, VENCIDO o CERRADO_POR_INCIDENCIA |
| CANCELADO | No hubo retiros y una cancelación voluntaria o administrativa autorizada completó el cierre de las unidades; conserva causas y actores |
| VENCIDO | No hubo retiros y el vencimiento cerró las unidades que seguían pendientes; puede incluir otras canceladas previamente |

El historial de retiros se determina por los hechos guardados, no por tener costo mayor que cero. Un retiro y devolución inmediata puede terminar en FINALIZADO aunque su costo redondeado sea cero.

### Eventos del conjunto

- El primer retiro válido cambia RESERVADO a EN_PROGRESO.
- Una devolución parcial no finaliza la cabecera si hay otra unidad en uso o pendiente de retiro.
- La última devolución puede completar el uso y provocar la liquidación.
- Si las usadas ya volvieron, cancelar o vencer la última unidad pendiente también puede completar el uso y provocar la liquidación.
- CANCELADO y VENCIDO sin uso tienen costo real cero. Si hay dinero recibido, se registra la obligación de reintegro sin exigir que este se complete antes de cerrar el uso.
- Un pago tardío no reactiva una cabecera cerrada.

No se utiliza CON_DEUDA como alternativa al estado de uso: un alquiler puede estar FINALIZADO y tener saldo pendiente. La causa de cierre y las transiciones de los detalles quedan disponibles para la auditoría. Las situaciones financieras de la sección siguiente fueron aprobadas por separado en RN-ALQ-08.

## 4. Situación financiera del alquiler

Esta es una dimensión independiente. Su representación como campo, enum o situación calculada se resolverá en el DER, sin obligar a crear una tabla adicional.

Los cuatro nombres y significados se aprobaron en [RN-ALQ-08](11-situacion-financiera-alquiler.md).

| Situación aprobada | Significado |
| --- | --- |
| SIN_LIQUIDAR | Falta terminar el uso o resolver incidencias que puedan cambiar el importe; el ajuste final aún no está determinado y el anticipo puede estar confirmado |
| SALDO_PENDIENTE | La liquidación determinó un importe adicional a cargo del cliente, todavía no cubierto por pagos confirmados |
| REEMBOLSO_PENDIENTE | La liquidación determinó una devolución al cliente, todavía no cubierta por reembolsos confirmados |
| SALDADO | No queda diferencia financiera por resolver frente al costo definitivo y los movimientos confirmados |

Al cerrar el uso, se registra una sola liquidación con tarifas y cotización congeladas. Si el anticipo coincide con el costo real, queda SALDADO sin otro movimiento. Una cancelación sin pagos y sin uso también queda sin saldo por resolver.

Un intento adicional rechazado no crea por sí mismo el costo de la deuda: esta ya surgió de la liquidación. Solo pagos confirmados reducen el saldo deudor. Un fallo de un reembolso mantiene la obligación a favor del cliente, sin convertirla en deuda suya.

El bloqueo de nuevos alquileres se aplica a un SALDO_PENDIENTE de la liquidación, no a un reembolso que la plataforma deba al cliente ni a un mayor costo todavía provisional de un conjunto en uso.

Si ingresa después un pago tardío para una contratación cerrada sin uso, su situación financiera debe reflejar la nueva obligación de reembolso, sin reabrir el uso ni duplicar el cierre original. El modelo debe admitir esa conciliación posterior.

## 5. Bicicleta

Los seis estados operativos iniciales se aprobaron en [RN-BIC-01](13-estados-operativos-bicicleta.md); RN-INC-01 agrega EXTRAVIADA como séptimo. Se conserva la distinción entre inactividad temporal, mantenimiento, pérdida y baja definitiva. RN-MAN-02 regula la habilitación técnica posterior y RN-BIC-02 los permisos administrativos. La migración y los detalles físicos se completarán por separado.

| Estado aprobado | Significado |
| --- | --- |
| DISPONIBLE | En estación, habilitada para alquilar y sin una reserva incompatible |
| RESERVADA | En estación y asignada a una reserva vigente; todavía no se retiró |
| EN_USO | Retirada dentro de un detalle EN_CURSO; no ocupa un lugar en una estación |
| MANTENIMIENTO | Fuera de alquiler por revisión o reparación; el avance del trabajo se sigue en la orden |
| INACTIVA | Fuera de servicio temporalmente por una decisión administrativa, sin representar un viaje ni una baja definitiva |
| DE_BAJA | Retirada definitivamente del servicio, conservando su historia y referencias |
| EXTRAVIADA | Pérdida o robo confirmados y unidad todavía no recuperada; no disponible ni dada de baja automáticamente |

Transiciones normales del alquiler: DISPONIBLE a RESERVADA al contratar; RESERVADA a EN_USO al retirar; EN_USO a DISPONIBLE al devolver válidamente sin falla reportada ni otro impedimento; RESERVADA a DISPONIBLE al cancelar o vencer la reserva correcta si no existe un impedimento. Con falla reportada se termina el uso y la unidad queda en MANTENIMIENTO según RN-ALQ-06 y RN-BIC-01. RN-MAN-04 agrega la preventiva vencida como impedimento: al devolver o liberar esa reserva la bicicleta pasa a MANTENIMIENTO, sin prolongar el uso ni su costo. Tampoco se confirma una reserva nueva cuando la preventiva ya venció.

No se permite poner manualmente en DISPONIBLE una unidad en uso para evitar la devolución. Cambiar un estado operativo tampoco demuestra un traslado físico: la ocupación depende de su ubicación real registrada. Una baja debe tratar su ubicación explícitamente, sin inventar una devolución o un traslado.

RN-INC-01 autoriza EXTRAVIADA solo mediante el circuito de incidencia validado, no por superar el tiempo estimado. Una unidad recuperada pasa a MANTENIMIENTO con ubicación real y revisión, no directamente a DISPONIBLE. ADMIN puede dar de baja una EXTRAVIADA por el recorrido específico con motivo, detalle cerrado y sin órdenes abiertas incompatibles; no simula recepción ni borra historia. No se introduce una transición automática después de 24 horas.

La administración aprobada de RN-BIC-02 reserva a ADMIN la inactivación temporal con motivo, la reactivación bajo controles y la baja definitiva sin reservas, viajes u órdenes abiertas. INACTIVA no sustituye el mantenimiento; una reactivación con necesidad técnica deriva al recorrido MANTENIMIENTO sin ofrecer la unidad. Una DE_BAJA no se reactiva desde el panel normal y conserva su historia. Si sigue físicamente en una estación, sigue ocupando lugar hasta registrar una salida real. RN-INC-01 agrega un cierre excepcional autorizado, no un cambio administrativo directo para eludir el contrato.

## 6. Pago y reembolso

Los nombres, significados y separación de operaciones de esta sección se aprobaron el 28 de octubre de 2026 en [RN-PAG-01](14-estados-pago-y-reembolso.md). El mismo día se aprobó por separado [RN-PAG-02](15-reintentos-pago-durante-reserva.md), sobre el rechazo inicial y los reintentos. Los demás recorridos expresamente pendientes no quedan aprobados por extensión.

### Estados aprobados de un intento de pago

| Estado | Significado |
| --- | --- |
| CREADO | Intento local registrado con monto, moneda y finalidad identificados |
| PENDIENTE | Se inició su gestión, pero falta un resultado validado |
| APROBADO | El backend validó el pago exitoso informado por el proveedor |
| RECHAZADO | El proveedor confirmó el rechazo del intento |
| CANCELADO | Se confirmó la cancelación de esa operación de pago, según lo permitido por el proveedor |

CREADO o PENDIENTE pueden terminar en APROBADO, RECHAZADO o CANCELADO según el resultado validado. Los rechazos y cancelaciones del intento no sustituyen el estado operativo de la reserva.

Según RN-PAG-02, un rechazo confirmado del anticipo no cancela la contratación ni libera sus bicicletas. Mientras siga vigente la reserva sin retiros, la cabecera conserva RESERVADO y las bicicletas RESERVADA. Se permite otro intento dentro de los 15 minutos originales; ni un primer ni un segundo rechazo reinician el plazo o provocan por sí solos la cancelación. Un resultado pendiente o incierto se consulta antes de habilitar otro cobro. El vencimiento continúa cubriendo tanto el pago como el retiro.

El cierre de una reserva no demuestra que un pago fue cancelado en la pasarela. Las respuestas tardías y contradictorias deben conciliarse con los hechos financieros, sin ignorar dinero confirmado ni reactivar un alquiler vencido.

Un reembolso no cambia el importe histórico del pago aprobado. La devolución parcial o total se determina con sus movimientos relacionados e importes confirmados, no sobrescribiendo el cargo original.

### Estados aprobados de una operación de reembolso

| Estado | Significado |
| --- | --- |
| PENDIENTE | Obligación/operación de reintegro registrada, todavía sin solicitud confirmada al proveedor |
| EN_PROCESO | Solicitud en gestión o resultado externo todavía no conciliado |
| CONFIRMADO | El proveedor confirmó la operación de reembolso |
| FALLIDO | Se conoce un resultado de fallo que requiere atención o reintento seguro |

Un timeout no prueba que el reembolso falló: puede existir una operación externa que todavía debe consultarse. No se repite un movimiento a ciegas. Un reintento debe referirse a la misma obligación y evitar duplicaciones.

CONFIRMADO describe la respuesta validada de la pasarela, no una promesa sobre el instante en que el banco mostrará el dinero al cliente. El mensaje de interfaz debe respetar esa distinción.

El registro independiente de reembolsos puede implementarse con una entidad propia o un movimiento financiero tipado y enlazado al pago original. La decisión física se tomará al revisar el DER. No se fuerza su número de tablas para conservar 21.

## 7. Orden de mantenimiento

Los cinco estados de la orden y la incorporación de TIPO_MANTENIMIENTO se aprobaron en [RN-MAN-01](12-tipos-y-estados-mantenimiento.md). El reparto de permisos, las transiciones manuales y la habilitación administrativa posterior se aprobaron por separado el 28 de octubre de 2026 en [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md). Las excepciones expresamente pendientes no quedan aprobadas por extensión.

| Estado | Significado | Destinos del recorrido manual aprobado |
| --- | --- | --- |
| CREADA | Orden registrada, trabajo aún no iniciado | EN_PROCESO, CANCELADA |
| EN_PROCESO | Trabajo iniciado por el técnico autorizado | PAUSADA, FINALIZADA, CANCELADA |
| PAUSADA | Trabajo interrumpido y todavía no cerrado | EN_PROCESO, CANCELADA |
| FINALIZADA | Trabajo terminado y resultado registrado | Terminal en el recorrido normal |
| CANCELADA | Orden invalidada, con motivo e historia conservados | Terminal en el recorrido normal |

Se aprobó que PREVENTIVO y CORRECTIVO describan el tipo de trabajo en la orden, mediante el catálogo TIPO_MANTENIMIENTO y la FK tipo_mantenimiento_id. La distinción se conserva sin duplicar cada combinación de tipo y avance en la bicicleta. El [fragmento del modelo](modelo-mantenimiento-catalogos.mmd) muestra la relación aprobada, sin sustituir todavía al DER completo.

Finalizar o cancelar una orden no devuelve automáticamente una bicicleta a DISPONIBLE: hacen falta el resultado técnico, una ubicación válida y la ausencia de restricciones incompatibles. La matriz de permisos debe distinguir la asignación administrativa del trabajo técnico.

### Permisos de mantenimiento aprobados

Estado del bloque: reparto aprobado expresamente por el usuario el 28 de octubre de 2026 en RN-MAN-02, incluida la autorización posterior por ADMIN para volver al servicio. El 4 de noviembre aprobó además la pausa administrativa excepcional y la orden PAUSADA sin técnico al inactivar al asignado, según la sección 3.1 de RN-MAN-02. No implementado. Se releyeron el Word de estados y el PDF de visión completos y se contrastó el DER v4 al preparar la propuesta inicial que recibió aprobación; las ampliaciones son decisiones posteriores, no atribuciones a esos originales.

El Word define la orden como seguimiento del trabajo técnico, independiente de su tipo, y permite un resultado final que no necesariamente devuelve la bicicleta a operación. El PDF requiere órdenes e historial, acciones de técnicos y administración con trazabilidad; el DER incluye una asignación mediante `tecnico_id`. Esas fuentes no fijan una matriz exhaustiva ni exigen una aprobación administrativa adicional para volver al servicio. La distribución siguiente, incluida esa aprobación, fue aceptada expresamente por el usuario como decisión posterior, no como una atribución literal a los originales.

| Acción manual | Permiso aprobado y alcance |
| --- | --- |
| Crear una orden PREVENTIVA o CORRECTIVA | ADMIN; comienza en CREADA y conserva el tipo de trabajo |
| Asignar o reasignar técnico | ADMIN, con la orden CREADA o PAUSADA; el técnico elegido debe estar activo y tener rol TECNICO |
| Consultar órdenes y su historial | ADMIN consulta todas; TECNICO consulta las asignadas a él |
| Iniciar o reanudar el trabajo | TECNICO asignado: CREADA o PAUSADA a EN_PROCESO |
| Registrar diagnóstico, trabajo y costos del mantenimiento | TECNICO asignado, durante el trabajo; conserva la trazabilidad de lo registrado |
| Pausar | TECNICO asignado: EN_PROCESO a PAUSADA, con motivo obligatorio |
| Pausar excepcionalmente al inactivar al técnico asignado | ADMIN: EN_PROCESO a PAUSADA, con motivo y desasignación; solo para ese recorrido de baja lógica |
| Finalizar | TECNICO asignado: EN_PROCESO a FINALIZADA, registrando trabajo realizado y resultado técnico, incluida la aptitud de la bicicleta |
| Cancelar una orden abierta | ADMIN: CREADA, EN_PROCESO o PAUSADA a CANCELADA, con motivo obligatorio y sin borrar la orden |
| Autorizar la vuelta al servicio después del mantenimiento | ADMIN, mediante una operación específica que exige conformidad técnica y los controles de disponibilidad indicados debajo |

Nadie inicia o reanuda el trabajo sin una asignación válida. Si se necesita reasignar mientras está EN_PROCESO, primero se pausa; la reasignación no borra al actor ni los trabajos anteriores. Posteriormente se aprobó en RN-MAN-03 que una orden CREADA pueda estar todavía sin técnico; el DER debe respetar esa posibilidad sin permitir trabajo técnico sin asignación.

Al inactivar al técnico asignado, una orden CREADA se conserva CREADA sin técnico; una EN_PROCESO pasa a PAUSADA sin técnico mediante la excepción administrativa aprobada; una PAUSADA conserva su estado y se desasigna. FINALIZADA y CANCELADA no cambian, ni pierden su técnico histórico. La misma orden conserva inicio, trabajo, diagnóstico y costos; la bicicleta sigue fuera de alquiler. ADMIN asigna luego un técnico activo con rol TECNICO, que debe iniciar o reanudar expresamente. No se crea un estado «pendiente de asignación» ni otra orden. La baja, los cambios y sus evidencias se confirman juntos con protección de concurrencia. Historial de orden y auditoría conservan motivo, fecha, actor ADMIN y valores anteriores/nuevos según RN-MAN-02, sección 3.1, y RN-TRZ-01.

CLIENTE no administra órdenes ni cambia sus estados. Conserva la posibilidad ya aprobada de informar una falla al devolver. Un usuario con solo rol ADMIN no se considera técnico por ese solo hecho; si reúne también TECNICO y la asignación correspondiente, puede ejecutar las acciones técnicas bajo esos controles.

### Resultado técnico y vuelta al servicio aprobados

El técnico registra si la bicicleta quedó apta o no apta y la justificación del resultado. Finalizar representa terminar el trabajo de esa orden, no certificar automáticamente que desaparecieron todos los impedimentos de la unidad.

Se aprobó reservar a ADMIN una autorización explícita posterior para pasar la bicicleta de MANTENIMIENTO a DISPONIBLE. El backend debe comprobar que la revisión vigente haya resuelto los impedimentos técnicos de esa bicicleta, que no existan órdenes abiertas o fallas sin resolver que bloqueen su uso, que esté físicamente registrada en una estación activa válida y que no exista una restricción administrativa incompatible. El mero estado FINALIZADA no basta.

Si el resultado es no apta, permanece fuera de alquiler. ADMIN no puede sustituir esa conclusión por un cambio libre de estado ni habilitarla usando un resultado favorable anterior a una falla nueva. Cancelar una orden tampoco acredita una revisión favorable ni libera por sí solo la bicicleta.

Esta autorización no equivale a trasladar físicamente una unidad ni a crear capacidad en una estación. Tampoco permite liberar una bicicleta EN_USO, intervenir una reserva vigente sin su recorrido específico o reactivar DE_BAJA como si se tratara de mantenimiento.

FINALIZADA y CANCELADA son terminales en el recorrido manual aprobado; no se reabren ni se alteran para ocultar su historia. Los cambios de estado, asignaciones, motivos y autorizaciones deben conservar actor real, fecha y evento. El backend valida rol, asignación y estado de origen; ocultar un botón en el frontend no sustituye esos controles.

### Criterios para verificar los permisos

Estos escenarios se especifican para futuras pruebas del bloque aprobado; no se ejecutaron. Sus identificadores y resultados esperados se registran en RN-MAN-02:

- Un técnico no asignado no puede iniciar, modificar ni finalizar la orden de otro.
- Un cliente no puede consultar el listado técnico ni cambiar una orden mediante una petición directa.
- Un administrador sin el rol técnico y la asignación no puede registrar una finalización técnica como si hubiese realizado el trabajo.
- Una reasignación mientras el trabajo está EN_PROCESO se rechaza hasta que se pause.
- Una pausa o cancelación sin motivo se rechaza.
- La inactivación del técnico pausa y desasigna las órdenes conforme a RN-MAN-02, sección 3.1, sin perder trabajo, habilitar bicicletas ni alterar órdenes cerradas; fuera de esa excepción ADMIN no obtiene un permiso general para pausar.
- Finalizar con resultado no apta no habilita la bicicleta.
- Una orden FINALIZADA sin conformidad técnica vigente, con otra orden bloqueante o con ubicación inválida no permite la vuelta al servicio.
- Una autorización administrativa repetida no duplica la transición ni omite una falla registrada posteriormente.

Esta matriz cubre las acciones manuales. La creación desde reportes, el máximo de una orden abierta y la asignación inicial opcional se aprobaron posteriormente en RN-MAN-03, de manera independiente. RN-MAN-04 añade las condiciones del preventivo por calendario. RN-INC-01 añade las incidencias y la recuperación con revisión, conservando la separación entre cierre administrativo del viaje y aptitud técnica.

### Origen y organización de órdenes aprobados

Estado: tres reglas aprobadas expresamente por el usuario el 28 de octubre de 2026 en [RN-MAN-03](18-generacion-y-organizacion-ordenes.md). Se contrastaron con el Word, el PDF y el DER originales antes de formularlas. No implementadas.

El Word ya plantea el bloqueo para reparación al reportar una falla y el PDF incluye el ingreso de una bicicleta reportada al módulo de mantenimiento. Ninguno fijaba por sí solo la generación automática de una orden, un máximo de órdenes abiertas o una asignación inicial opcional. El usuario aprobó estas precisiones posteriores:

1. Al registrar una devolución válida con falla reportada, el sistema conserva DEVUELTO en el detalle, termina su tiempo de uso y deja la bicicleta en MANTENIMIENTO, como ya está aprobado. Además garantiza que el reporte quede atendido por una orden abierta: si no existe, crea automáticamente una orden de tipo CORRECTIVO y estado CREADA, vinculada al reporte y a su bicicleta. Crear la orden no confirma la avería ni atribuye responsabilidad al cliente.
2. Admitir como máximo una orden abierta por bicicleta, considerando abiertas CREADA, EN_PROCESO y PAUSADA. Si ya existe una, se incorpora el reporte a su atención y se conserva su origen, sin crear una duplicada ni cambiar automáticamente el tipo de trabajo. ADMIN puede resolver una orden que no corresponda mediante el recorrido de cancelación con motivo y creación de la que corresponda, conservando ambas en la historia. Una nueva falla no se elimina por existir una revisión anterior.
3. Permitir que una orden CREADA todavía no tenga técnico asignado. ADMIN realiza la asignación posterior, y no se puede iniciar o reanudar sin un técnico válido conforme a RN-MAN-02.

Las órdenes preventivas conservan la creación manual por ADMIN. El usuario aprobó además su generación automática por calendario y tipo, y después las condiciones de aplicación en [RN-MAN-04](19-propuesta-preventivo-por-calendario.md): no interrumpir viajes ni reservas ya aceptadas por el solo calendario; bloquear nuevas reservas vencidas; derivar a mantenimiento al devolver o liberar la reserva; conservar una sola orden abierta y atender el correctivo antes de la preventiva pendiente. La referencia es la última preventiva satisfactoria, o el alta real de una bicicleta nueva; una unidad antigua sin referencia fiable requiere revisión inicial. Solo ADMIN configura intervalos positivos en meses calendario. Los valores numéricos de ejemplo no son definitivos; falta consolidar datos y detalles técnicos en el DER.

El sistema es el origen de la orden automática; el cliente es el autor del reporte. No se inventa una acción humana administrativa para representar ese evento. Repetir la misma devolución o el mismo reporte no debe crear otra orden ni alterar una intervención posterior. Dos solicitudes concurrentes tampoco deben crear dos órdenes abiertas para la misma bicicleta.

La aprobación no habilita mantenimiento manual sobre una unidad EN_USO o RESERVADA para eludir sus reglas. RN-BIC-02 permite una cancelación administrativa específica de una reserva todavía no retirada. RN-INC-01 autoriza un cierre excepcional durante el uso bajo sus controles, no una cancelación ni un cambio arbitrario. Las relaciones físicas de reporte, orden e historial se concretarán en el DER.

## 8. Condiciones comunes a las transiciones

- Validar usuario, autorización, estado de origen y condiciones de negocio antes de modificar entidades administradas.
- Realizar la transición, sus efectos de inventario, costo e historial dentro de una operación local coherente.
- Proteger retiros, devoluciones, cancelaciones y vencimientos frente a solicitudes simultáneas.
- No mantener bloqueos de base de datos durante la navegación por una pasarela ni durante esperas de servicios externos.
- Evitar repetir liquidaciones y movimientos económicos por peticiones o notificaciones duplicadas.
- Registrar el actor y origen del cambio. Un proceso automático no es un administrador humano ficticio.
- No permitir que el cliente envíe arbitrariamente el estado de destino como reemplazo de una operación autorizada.
- Conservar los hechos históricos y movimientos originales; no borrar una contratación para simular su cancelación.

## 9. Validación pendiente antes del código

Los puntos administrativos 1 a 6 de RN-BIC-02 y el circuito mínimo RN-INC-01 están aprobados para el diseño. La cancelación administrativa amplía CANCELADO y las incidencias agregan EXTRAVIADA y CERRADO_POR_INCIDENCIA, con causas y actores distinguibles. No se consideran implementados.

Permanecen pendientes:

- La corrección administrativa de una baja registrada por error sigue fuera del recorrido normal. La sección 8 de RN-INC-01 ya está aprobada: devolver no espera a la revisión; la liquidación sí espera si el incidente puede cambiar el importe.
- Los valores numéricos iniciales de los intervalos de RN-MAN-04 y sus detalles físicos/técnicos de cálculo y ejecución. Las condiciones para reservas, viajes, datos sin historial y coordinación de órdenes ya fueron aprobadas. RN-MAN-03 también aprueba el correctivo desde devolución, una sola orden abierta y la asignación opcional durante CREADA; falta consolidar sus relaciones físicas en el DER.
- La integración y sus controles de cancelación/reintento. RN-PAG-03 ya aprobó el recorrido cuando se cancela una unidad durante el anticipo, distinguiéndolo del carrito y conservando el intento en gestión. RN-PAG-02 mantiene los reintentos tras un rechazo confirmado; las reglas no equivalen a una integración probada.
- Condiciones de consulta/frescura de la cotización y precisiones físicas de entradas. RN-ALQ-10 ya aprobó segundos completos, dos decimales HALF_UP por detalle/moneda y suma de líneas, sin mínimo de uso.
- Validaciones de duración estimada y límites acumulados por usuario. RN-ALQ-11 ya aprobó una estación de retiro por cabecera, máximo inicial de diez configurable y selección fija, preservando las cancelaciones previas. No cambia los estados ni las devoluciones independientes.
- Variante de API e integración de Checkout Pro, medios habilitados y hardware real o simulado. RN-PAG-05 ya eligió pantalla externa de Mercado Pago sin administrar tarjetas localmente; los medios guardados no son un pendiente de esta versión.
- La representación física de la situación financiera y de cada reembolso.
- El tratamiento de pagos/datos históricos al migrar: no deben inventarse pagos confirmados para alquileres de la versión anterior, que no tenía este módulo financiero.

Se aprobaron los catálogos iniciales, el alquiler y la devolución, la cabecera y situación financiera, mantenimiento, pagos/reembolsos y reintentos. RN-MAN-04 incorpora el preventivo por calendario; RN-BIC-02 completa la administración y RN-INC-01 amplía a siete los estados de bicicleta y detalle mediante el circuito mínimo de incidencias. Su precisión económica adicional también está aprobada. Continúan pendientes los valores numéricos y detalles técnicos señalados y los demás puntos de esta sección para consolidar el DER. Las excepciones no se consideran aprobadas por extensión.

No se cambió el documento Word original, código ni base de datos. No se ejecutaron pruebas de estas transiciones; las verificaciones deberán enlazarse con los criterios CP-ALQ de las reglas aprobadas y ampliarse para cada transición.
