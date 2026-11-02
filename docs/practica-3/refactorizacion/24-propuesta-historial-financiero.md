# Historial de estados de pagos y reembolsos

Fecha de revisión: 28 de octubre de 2026.

Estado: incorporación de los dos historiales aprobada expresamente el 28 de octubre de 2026 e incluida en el [DER v5 de trabajo](der-v5-propuesto.mmd), con campos, claves y relaciones. El usuario remarcó la exigencia del profesor de conservar movimientos y fechas, no solo el estado actual. La aprobación comprende esta representación lógica de la trazabilidad financiera; no declara definitivo el resto del DER ni equivale a implementación en Java o en la base de datos.

## 1. Hallazgo del borrador

El DER v4 original tiene historiales para detalle, bicicleta y orden, además de AUDITORIA_SISTEMA. PAGO solo conserva estado actual y fechas de creación/pago. El primer borrador v5 de 24 entidades agregó REEMBOLSO pero no un historial financiero específico: preveía auditoría genérica para los movimientos no cubiertos por los otros historiales. La incorporación aprobada aquí corrige esa falta de representación explícita y amplía el modelo a 26 entidades.

Una auditoría genérica podría satisfacer el requisito si cada evento relevante se registra de manera completa, consultable y consistente. Su sola existencia en el diagrama no lo garantiza. Separar PAGO de REEMBOLSO conserva movimientos distintos, pero no conserva automáticamente el recorrido de estados de cada uno.

La revisión se contrastó con el diccionario original, los apartados de objetivos/requerimientos del PDF y las entidades originales del DER v4. No se atribuye al PDF una obligación literal de dos tablas: la exigencia de trazabilidad del usuario y la estructura elegida justifican esta propuesta.

## 2. Representación aprobada

Se conserva el estado actual en la operación y se incorporan:

- HISTORIAL_ESTADO_PAGO: una secuencia de eventos vinculados a un PAGO concreto.
- HISTORIAL_ESTADO_REEMBOLSO: una secuencia de eventos vinculados a un REEMBOLSO concreto.

El estado actual permite consultar rápidamente cómo está la operación. El historial explica cómo llegó allí, cuándo ocurrió y cuál fue su origen. Según la decisión posterior del 2 de noviembre, AUDITORIA_SISTEMA es exclusiva de acciones administrativas ADMIN y no sustituye estos historiales ni registra los eventos automáticos de la pasarela. El [documento 35](35-auditoria-admin-y-brechas-de-trazabilidad.md) delimita los eventos técnicos sin transición que deben concretarse al integrar pagos.

No es un requisito técnico de Mercado Pago ni la única representación posible. Se eligieron los dos historiales dedicados para mantener el patrón del DER original y relaciones explícitas con cada operación. Su incorporación llevó el modelo de 24 a 26 entidades, sin un catálogo nuevo de estados de reembolso: se conservan los cuatro códigos controlados que ya utiliza REEMBOLSO. La ampliación posterior de identificación del documento 25 lo lleva a 28, sin alterar estos historiales.

## 3. Campos y claves incorporados

Los tipos son lógicos, como en el resto del borrador: no fijan aún longitudes SQL, precisión temporal, generación física de identificadores ni nombres de índices. Salvo las excepciones indicadas, los datos son obligatorios. Las validaciones condicionales se concretarán en el diseño físico y los servicios.

### 3.1 Campos comunes de ambos historiales

| Campo | Tipo lógico y clave | Significado y nulabilidad |
| --- | --- | --- |
| id | int, PK | Identificador único de cada registro de historia |
| fecha_hora_cambio | datetime | Fecha y hora en que el backend registra la transición |
| fecha_hora_evento_externo | datetime | Opcional; momento informado por la pasarela cuando existe y fue validado; no sustituye la fecha de registro |
| actor_usuario_id | int, FK a USUARIO.id | Usuario que ejecuta la acción humana; nulo solamente para origen SISTEMA |
| origen | string | USUARIO o SISTEMA, determinado por el backend |
| fuente | string | Identifica si provino de registro local, notificación validada, consulta o proceso interno; los códigos técnicos se concretarán al integrar |
| referencia_evento_externo | string | Opcional; correlación externa, sin presumir unicidad global ni que un identificador de evento sea siempre el identificador del pago |
| observaciones | text | Opcional cuando no hay un detalle adicional; conserva motivo, rechazo o error saneado cuando corresponde |

Una respuesta o notificación validada de la pasarela se registra con origen SISTEMA, sin inventar un usuario administrador ni atribuir al cliente la aprobación del cobro. El actor identifica quién ejecutó esta transición, no necesariamente quién contrató el alquiler.

### 3.2 Campos propios de HISTORIAL_ESTADO_PAGO

| Campo | Tipo lógico y clave | Relación y nulabilidad |
| --- | --- | --- |
| pago_id | int, FK a PAGO.id | Obligatorio; cada registro pertenece a exactamente un intento de pago |
| estado_anterior_id | int, FK a ESTADO_PAGO.id | Opcional únicamente en el registro inicial; después identifica el estado que se abandona |
| estado_nuevo_id | int, FK a ESTADO_PAGO.id | Obligatorio; estado que queda vigente por esta transición |

Cada PAGO tiene uno o muchos registros de historia porque se registra también su creación. Un código de ESTADO_PAGO puede aparecer en cero o muchos eventos como estado anterior o nuevo; son dos relaciones diferentes al mismo catálogo. Cada evento tiene cero o un actor humano y cada USUARIO puede intervenir en muchos eventos.

### 3.3 Campos propios de HISTORIAL_ESTADO_REEMBOLSO

| Campo | Tipo lógico y clave | Relación y nulabilidad |
| --- | --- | --- |
| reembolso_id | int, FK a REEMBOLSO.id | Obligatorio; cada registro pertenece a exactamente una operación de reembolso |
| estado_anterior | string | Opcional únicamente en el registro inicial; mismos códigos controlados de REEMBOLSO.estado |
| estado_nuevo | string | Obligatorio; PENDIENTE, EN_PROCESO, CONFIRMADO o FALLIDO |

Cada REEMBOLSO tiene uno o muchos registros de historia, incluido su estado inicial. La relación con USUARIO tiene la misma opcionalidad que en el historial del pago. Los estados de este historial no son FK porque el modelo ya representa REEMBOLSO.estado mediante códigos controlados, no mediante un catálogo ESTADO_REEMBOLSO. No se agrega ese catálogo ni se permite texto arbitrario por esta incorporación.

No se duplican alquiler_id ni pago_id en el historial de reembolso: el alquiler se obtiene por REEMBOLSO → PAGO → ALQUILER. Tampoco se copia el importe en cada transición, ya que pertenece a la operación y no cambia por guardar su historial.

Los importes y monedas se conservan en sus operaciones originales. Un reembolso no modifica el monto del pago; guardar un historial no habilita cambios libres de importes ni atribución automática de responsabilidad.

## 4. Ejemplo de lectura

Ejemplo ilustrativo de un mismo pago:

| Hora de registro | Estado anterior | Estado nuevo | Fuente |
| --- | --- | --- | --- |
| 10:00:00 | Sin estado | CREADO | Solicitud registrada por el backend |
| 10:00:02 | CREADO | PENDIENTE | Inicio de gestión externa |
| 10:00:09 | PENDIENTE | APROBADO | Resultado validado por el backend |

La fila de PAGO puede mostrar APROBADO, pero los tres registros anteriores no se pierden. Un reembolso sigue su propia historia, por ejemplo PENDIENTE, EN_PROCESO y CONFIRMADO; no se mezcla con el recorrido del cobro.

Si un intento fue rechazado y el cliente inicia otro válido dentro del plazo de reserva, el primer PAGO y su historial permanecen; el nuevo intento crea su propia operación e historia conforme a RN-PAG-02. No se sobrescribe el rechazo con el resultado de otra operación.

## 5. Controles necesarios al implementar

- Registrar el estado inicial junto con la operación. Cada transición posterior debe actualizar el estado actual e insertar su historial en la misma transacción local.
- Conservar los eventos como registros añadidos; no permitir su edición/borrado desde el ABM normal. Una corrección deja un evento adicional con motivo y autor, sin reescribir silenciosamente la historia. Esto no equivale a una garantía criptográfica contra un administrador de base de datos.
- Mantener coherencia entre el estado actual y la última transición efectiva. El registro y el orden de aplicación se controlan en el backend, no con el reloj del cliente.
- Diferenciar movimientos, transiciones y eventos técnicos. Una notificación repetida no crea otro pago, reembolso ni transición efectiva idéntica. Su recepción y tratamiento se concretan en D03 mediante un registro técnico separado de la auditoría exclusiva de ADMIN, sin duplicar el efecto económico.
- Una consulta, reintento HTTP o cambio de detalle externo sin nuevo estado tampoco obliga a inventar una transición. Definir qué eventos técnicos son relevantes y cómo conservar su referencia a la operación al integrar, sin atribuirlos ficticiamente a ADMIN ni dar por implementada su trazabilidad.
- No aplicar ciegamente un evento atrasado que contradiga el estado ya validado. Su conciliación depende de la modalidad de integración elegida; no se asume que la hora de llegada es la hora efectiva del proveedor.
- No guardar contraseñas, Access Tokens, encabezados de autorización, CVV ni respuestas externas completas sin saneamiento. Los datos de correlación no sustituyen validar el resultado externo.
- Mantener el rol autorizado de cada operación. Un cliente no obtiene un endpoint para marcar su pago APROBADO por la existencia de estas tablas.

## 6. Criterios de aceptación propuestos

No son pruebas ejecutadas ni evidencia de que estos historiales ya existan:

- CP-TRZ-01-01: crear un pago o reembolso produce también su evento inicial.
- CP-TRZ-01-02: varias transiciones conservan todas las fechas, estados y orígenes; consultar el estado actual no borra eventos anteriores.
- CP-TRZ-01-03: si falla el registro del historial, no se confirma parcialmente el nuevo estado.
- CP-TRZ-01-04: dos solicitudes concurrentes no crean transiciones contradictorias ni duplican dinero.
- CP-TRZ-01-05: repetir una notificación no crea otra transición efectiva ni otro movimiento; se puede explicar su tratamiento técnico.
- CP-TRZ-01-06: un nuevo intento tras rechazo no sustituye la operación rechazada ni su historia.
- CP-TRZ-01-07: el historial de reembolso conserva el vínculo al pago original a través de REEMBOLSO; el importe inicial no se sobrescribe.
- CP-TRZ-01-08: las consultas autorizadas permiten reconstruir qué se solicitó, qué resultado se validó y cuándo, sin exponer secretos ni operaciones ajenas.

## 7. Aprobación e incorporación al modelo

El 28 de octubre de 2026 el usuario autorizó agregar ambos historiales con campos, claves primarias y foráneas y relaciones, sin alterar el resto del DER. En esa incorporación se añadieron al Mermaid dos entidades, seis atributos FK y seis relaciones. Las 24 entidades previas, sus atributos y sus relaciones se conservaron en ese paso; los cambios posteriores de PERSONA y USUARIO fueron aprobados por separado y se documentan en el archivo 25.

El modelo quedó en 26 entidades y 49 relaciones al agregar los historiales y luego en 28 entidades y 51 relaciones tras la identificación. La referencia al tipo contratado del [documento 28](28-revision-alquiler-y-detalles.md) lo amplió después a 28 entidades y 52 relaciones, sin alterar estos historiales. Su existencia en el diagrama no acredita todavía trazabilidad funcionando: faltan operaciones transaccionales, restricciones físicas, consultas autorizadas y pruebas de ejecución.

La próxima etapa es depurar el DER por bloques según el orden del documento 22, manteniendo sus decisiones pendientes identificadas. No se crean tablas en MySQL, no se modifican las reglas económicas aprobadas ni se ejecutan llamadas a Mercado Pago. Los originales se conservan intactos.
