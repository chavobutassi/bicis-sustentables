# Incorporación aprobada de trazabilidad al DER

Fecha: 2 de noviembre de 2026.

Regla de diseño: RN-TRZ-01.

Estado: las cuatro mejoras fueron aprobadas expresamente por el usuario e incorporadas al [DER lógico de trabajo](der-v5-propuesto.mmd). El modelo pasa de 28 entidades y 52 FK/relaciones a 29 entidades y 55 FK/relaciones. No se ejecutaron migraciones ni se modificó Java, configuración, frontend o datos. Incorporación al diseño no significa funcionalidad implementada o probada en la aplicación.

## 1. Alcance de la aprobación

1. Crear HISTORIAL_INCIDENCIA.
2. Ampliar el historial existente de la orden con acción y valores anteriores/nuevos, y renombrarlo HISTORIAL_ORDEN_MANTENIMIENTO.
3. Agregar motivo a AUDITORIA_SISTEMA, manteniéndola exclusiva de acciones administrativas ADMIN.
4. Agregar incidencia_corte_id a ALQUILER_DETALLE como referencia opcional a la incidencia que fundamenta el corte aplicado.

Se parte del modelo inmediatamente anterior de 28/52 y del [documento 35](35-auditoria-admin-y-brechas-de-trazabilidad.md). Se conservan las decisiones aprobadas del PDF, DER v4 y diccionario contrastadas en esa revisión; sus originales permanecen intactos. HISTORIAL_ATENCION_MANTENIMIENTO sigue descartado y no se añade otra tabla para asignaciones, diagnósticos o estados de incidencia.

## 2. Historial de incidencia

HISTORIAL_INCIDENCIA conserva eventos del reporte, no nuevas incidencias ni movimientos de dinero. La tabla INCIDENCIA sigue mostrando los datos vigentes. Su historial permite reconstruir cómo llegaron a esos valores, sin sobrescribir eventos anteriores.

| Campo | Tipo y clave | Condición y razón |
| --- | --- | --- |
| id | int, PK | Identifica un evento; no se reutiliza el id de la incidencia como PK del historial |
| incidencia_id | int, FK a INCIDENCIA.id | Obligatorio, no UNIQUE; permite muchos eventos para el mismo reporte |
| accion | string | Obligatoria; código de la operación permitida que originó el evento, determinado por backend |
| estado_anterior | string | Mismos códigos controlados de INCIDENCIA.estado_revision; nulo al crear y en eventos solo de datos |
| estado_nuevo | string | Mismos códigos; obligatorio en creación/transición, nulo en eventos solo de datos |
| fecha_hora_cambio | datetime | Obligatoria; registro del backend, no momento informado del hecho, de decisión ni de corte |
| actor_usuario_id | int, FK a USUARIO.id | Obligatorio para acción humana; nulo únicamente con origen SISTEMA |
| origen | string | USUARIO o SISTEMA; obligatorio y determinado por backend |
| valores_anteriores | text | Datos permitidos antes del cambio; nulo en la creación; estructura validada, sin secretos |
| valores_nuevos | text | Datos permitidos registrados o modificados; estructura validada, sin aceptar una entidad arbitraria del cliente |
| observaciones | text | Contexto y motivo; obligatorio cuando lo exige la operación, por ejemplo una corrección o decisión justificada |

Los estados no son FK porque el DER vigente no contiene un catálogo de estados de incidencia: utiliza códigos en INCIDENCIA.estado_revision. Se conserva ese criterio, sin añadir un catálogo ni inventar estados por esta aprobación. Los valores estructurados sirven para conservar los datos permitidos que cambian, no para ocultar relaciones obligatorias o sustituir los estados explícitos del evento.

Los eventos incluyen registro, revisión, correcciones permitidas, fundamento económico/corte, recepción o recuperación y cambios autorizados del vínculo con la orden. El registro inicial conserva un resumen permitido de lo recibido y sus responsables. La corrección conserva anterior/nuevo y motivo; no borra el relato original ni concede al cliente nuevas facultades de edición. Las decisiones administrativas conservan además su auditoría de ADMIN. No se habilita reapertura libre o reliquidación definitiva por existir un historial.

No se duplica cada campo actual en una columna histórica distinta. La forma física de serializar y validar los datos de valores_anteriores/nuevos se concretará en D06; su declaración lógica text no determina todavía un tipo JSON específico de un motor.

## 3. Ampliación del historial de orden

HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO se renombra HISTORIAL_ORDEN_MANTENIMIENTO, conservando su identidad conceptual y los ocho campos previos. Se añaden tres: accion, valores_anteriores y valores_nuevos. No se conservan dos entidades paralelas ni se crean varias órdenes para registrar avances.

| Campo | Tipo y clave | Condición y razón |
| --- | --- | --- |
| id | int, PK | Identificador del evento, conservado |
| orden_mantenimiento_id | int, FK a ORDEN_MANTENIMIENTO.id | Obligatorio, no UNIQUE; muchos eventos de la misma orden |
| accion | string | Nuevo; código obligatorio de la operación, sin inferirla solamente del texto de observaciones |
| estado_anterior_id | int, FK a ESTADO_ORDEN_MANTENIMIENTO.id | Conservado; nulo al crear y en eventos solo de datos; obligatorio en una transición |
| estado_nuevo_id | int, FK al mismo catálogo | Conservado; obligatorio al crear/transicionar y nulo en eventos solo de datos |
| fecha_hora_cambio | datetime | Conservado; fecha del registro en backend |
| actor_usuario_id | int, FK a USUARIO.id | Conservado; usuario real en una acción humana, nulo solo para SISTEMA |
| origen | string | Conservado; USUARIO o SISTEMA, no un ADMIN ficticio para tareas automáticas |
| observaciones | text | Conservado; motivo y contexto, con obligatoriedad según la operación |
| valores_anteriores | text | Nuevo; datos permitidos previos; nulo al crear |
| valores_nuevos | text | Nuevo; datos permitidos registrados o modificados |

La asignación de técnico conserva anterior/nuevo y ADMIN real. Los cambios autorizados del diagnóstico, trabajo, observaciones o costo interno conservan sus valores y el actor técnico real, aunque la orden mantenga su estado. La identidad del actor no se sustituye por el técnico actualmente asignado a la orden.

Los datos modificados en la misma operación que una transición pueden conservarse en ese mismo evento, sin duplicar la acción. Los valores estructurados son necesarios cuando hay datos relevantes que registrar/corregir; no se obliga a duplicar todos los datos de la orden en cada transición exclusivamente de estado. La creación conserva sus datos iniciales pertinentes.

El cambio de nombre no habilita edición libre de órdenes cerradas, reasignaciones en fases prohibidas o acciones técnicas por ADMIN sin sus requisitos. Permanecen PREVENTIVO/CORRECTIVO, los cinco estados de orden, diagnóstico obligatorio al finalizar, costos internos ARS, autorización posterior de ADMIN y máximo de una orden abierta por bicicleta.

## 4. Estados y nulabilidad condicional de los dos historiales

| Clase de evento | Estado anterior | Estado nuevo | Datos del evento |
| --- | --- | --- | --- |
| Creación | Nulo | Estado inicial válido | Resumen inicial permitido; valores_anteriores nulo |
| Transición efectiva | Obligatorio, igual al estado vigente previo | Obligatorio y diferente, transición autorizada | Motivo/contexto y datos adicionales que cambien |
| Modificación exclusivamente de datos | Nulo | Nulo | Debe existir un cambio efectivo permitido con anterior/nuevo; no una consulta o repetición sin efecto |

Las columnas conservan FK al catálogo en el historial de orden aunque puedan ser nulas en determinados eventos. El historial de incidencia conserva códigos controlados equivalentes a su entidad. No se registra EN_PROCESO a EN_PROCESO ni PENDIENTE a PENDIENTE como transición para guardar una modificación. Un estado anterior sin nuevo, o un nuevo sin anterior fuera de la creación, no es un evento válido.

El tipo de acción, su contexto y la existencia del evento inicial deben concordar: no basta aceptar la etiqueta CREACION para omitir un estado anterior cuando ya existe historia. Las condiciones se implementarán mediante restricciones aplicables y servicios transaccionales; el dibujo no ejecuta esa validación.

## 5. Motivo de la auditoría administrativa

AUDITORIA_SISTEMA incorpora motivo como text. Es opcional para cambios rutinarios y no vacío cuando la regla exige justificar la operación, por ejemplo una baja, una cancelación administrativa o una decisión excepcional. accion identifica qué se hizo; motivo explica por qué; valores_anteriores/nuevos conservan qué cambió. No se crean PK o FK nuevas por este campo.

administrador_id sigue siendo FK obligatoria a USUARIO.id. El backend debe verificar el permiso ADMIN para la acción concreta y obtener al responsable autenticado. La FK no verifica roles por sí sola. No se incorpora origen SISTEMA a esta tabla ni se atribuyen a ADMIN trabajos del técnico o notificaciones de Mercado Pago. No se permite auditar contraseñas, hashes, enlaces/tokens de recuperación, credenciales o datos de tarjeta.

## 6. Incidencia que fundamenta el corte

ALQUILER_DETALLE incorpora incidencia_corte_id como int, FK opcional a INCIDENCIA.id y UK cuando tenga valor, según D07-A. La PK del detalle y todas sus FK anteriores se mantienen. INCIDENCIA.alquiler_detalle_id sigue siendo FK obligatoria y no UNIQUE: un detalle puede conservar varios reportes.

La FK nueva distingue los reportes existentes de aquel que fundamenta el corte económico aplicado. Un detalle tiene cero o una incidencia determinante y una incidencia puede fundamentar cero o un detalle. La UK deja explícito que el mismo reporte no se reutiliza como fundamento de dos detalles, aunque la validación de pertenencia debe impedirlo también.

Condiciones aprobadas que la FK sola no garantiza:

- La incidencia existe y su alquiler_detalle_id coincide con el id del detalle que la referencia. No basta con que ambos registros existan.
- La decisión está validada por ADMIN y realmente fundamenta el corte aplicado; no se selecciona automáticamente la primera/última incidencia ni se acepta libremente desde el navegador.
- En CERRADO_POR_INCIDENCIA se conserva la decisión que justifica el cierre excepcional, sin inventar una recepción física.
- En DEVUELTO puede conservarse una incidencia previa con corte anterior validado; no se cambia DEVUELTO ni se reemplaza la fecha física por el corte económico.
- En una devolución normal sin corte por incidencia, o si el reporte se descarta, la referencia puede quedar nula. Un reporte puramente técnico no adquiere efecto económico por tener una orden.
- El fin de uso facturable y el corte referenciado son coherentes con los límites de uso/recepción aprobados. No se duplica un efecto económico ni se reabre una liquidación definitiva mediante un cambio de enlace.
- Se conservan los demás reportes y se esperan todas las revisiones económicas relevantes antes de liquidar conjuntamente.

Existe un ciclo lógico de referencias: INCIDENCIA pertenece a ALQUILER_DETALLE y el detalle puede referenciar una incidencia determinante. No es una relación de creación simultánea obligatoria: primero se crea el detalle con incidencia_corte_id nulo, luego el reporte y, al validar el fundamento, se completa la referencia. La migración física deberá ordenar la creación de tablas/FK de forma compatible; no se ejecuta aquí.

La pertenencia al mismo detalle debe comprobarse transaccionalmente y protegerse frente a cambios concurrentes. En D06 se concretará además la restricción física que corresponda al motor, incluida una posible FK compuesta con su clave referenciada si se adopta; no se afirma que una FK simple o UK ya garantice ese cruce. No se añade ahora una clave compuesta nueva no dibujada.

## 7. Relaciones y por qué existen

| Entidades | Cardinalidad lógica | Columna FK y razón |
| --- | --- | --- |
| INCIDENCIA a HISTORIAL_INCIDENCIA | Una incidencia tiene uno o muchos eventos; cada evento tiene una incidencia | incidencia_id, obligatorio; conserva la evolución por reporte |
| USUARIO a HISTORIAL_INCIDENCIA | Un usuario puede tener muchos eventos; un evento tiene cero o un usuario | actor_usuario_id, nulo solo para SISTEMA; preserva al actor real |
| ORDEN_MANTENIMIENTO a HISTORIAL_ORDEN_MANTENIMIENTO | Una orden tiene uno o muchos eventos; cada evento tiene una orden | orden_mantenimiento_id, obligatorio; relación conservada bajo el nuevo nombre |
| ESTADO_ORDEN_MANTENIMIENTO al historial de orden | Cada catálogo puede aparecer en muchos eventos; cada referencia del evento es opcional según su clase | estado_anterior_id y estado_nuevo_id, dos FK distintas al mismo catálogo |
| USUARIO al historial de orden | Un usuario puede actuar en muchos eventos; cada evento admite cero o un usuario | actor_usuario_id, conservado; no se limita a ADMIN |
| INCIDENCIA a ALQUILER_DETALLE como fundamento | Cero o uno en ambos extremos | incidencia_corte_id, FK opcional y UK; no sustituye la relación obligatoria del reporte con su detalle |
| USUARIO a AUDITORIA_SISTEMA | Un usuario puede tener muchos eventos administrativos; cada evento tiene un usuario | administrador_id obligatorio, conservado; el permiso ADMIN se comprueba al operar |

Las FK históricas no se configuran para borrar en cascada los eventos desde el ABM normal. Las bajas lógicas conservan registros e identidad del actor aunque cambien sus permisos. Las referencias contextuales dentro de valores_anteriores/nuevos no se presentan como nuevas FK físicas ni se cuentan como tales.

## 8. Conservación del resto y próximos controles

La ampliación afecta únicamente a tres entidades existentes y a una nueva:

- ALQUILER_DETALLE: una FK opcional/UK, sin tocar tarifa, tiempos, importes o sus claves previas.
- HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO: renombre, tres campos nuevos y nulabilidad condicional de estados; conserva los ocho campos anteriores, sus tipos y claves.
- AUDITORIA_SISTEMA: un campo motivo; se mantienen sus claves y alcance ADMIN.
- HISTORIAL_INCIDENCIA: una nueva entidad, once campos y dos FK.

Las otras 25 entidades se conservan íntegramente respecto del modelo inmediatamente anterior. Las 52 relaciones previas se mantienen conceptualmente, con el renombre del historial y la opcionalidad nueva de su estado_nuevo; se agregan tres relaciones, no se eliminan vínculos de negocio. Cada tabla tiene PK; cada FK apunta a una PK int compatible y tiene su relación dibujada. Las unicidades compuestas de documento y alquiler/bicicleta se conservan sin convertir sus componentes en UK individuales.

Se verifican por separado estructura del texto y referencias documentales. Esa revisión no sustituye un renderizado con el motor Mermaid, DDL de MySQL, validación JPA, controles de rol o pruebas de concurrencia. Los tipos SQL, índices, restricciones condicionales, cronología y migración del legado siguen en D06; los códigos/formatos del evento se concretan al implementar sin ampliar permisos.

Las nuevas historias y su estado/datos vigentes se guardarán en la misma transacción local. Si una acción administrativa también exige auditoría, se confirman sus dos evidencias o se revierte el cambio local. La consulta reconstruye la secuencia por fecha e id sin editar/borrar eventos. La idempotencia evita repetir efectos. No se mantienen transacciones esperando correo o Mercado Pago.

## 9. Casos de aceptación para la implementación futura

Estos casos quedan especificados, no ejecutados contra la aplicación:

- CP-TRZ-04-01: crear una incidencia guarda su evento inicial, actor real y fecha de registro; no inventa una decisión o un corte.
- CP-TRZ-04-02: validar/descartar conserva estados anterior/nuevo, decisión y motivo; la operación administrativa tiene su auditoría.
- CP-TRZ-04-03: una corrección permitida conserva los valores previos; no crea una transición de estado ficticia ni borra el reporte original.
- CP-TRZ-04-04: modificar diagnóstico/costo sin transición conserva el evento técnico en la misma orden, sin insertarlo como ADMIN.
- CP-TRZ-04-05: la creación tiene estado anterior nulo y nuevo inicial; un evento de datos tiene ambos nulos; una transición exige ambos y un cambio permitido. Combinaciones incompatibles se rechazan.
- CP-TRZ-04-06: una acción humana sin actor o un origen SISTEMA con administrador ficticio se rechazan; cambiar roles después no altera la autoría histórica.
- CP-TRZ-04-07: una baja/cancelación administrativa sin motivo requerido no se confirma; no se guardan secretos en valores o motivo.
- CP-TRZ-04-08: un detalle no puede referenciar una incidencia inexistente, ajena a ese detalle o sin decisión económica válida.
- CP-TRZ-04-09: una devolución normal permite incidencia_corte_id nulo y se mantienen varios reportes para un mismo detalle, cada uno con su historial.
- CP-TRZ-04-10: un corte anterior validado después de la recepción conserva DEVUELTO y la fecha física; la liquidación espera la revisión y no suma el tiempo de espera.
- CP-TRZ-04-11: dos decisiones concurrentes/repetidas no aplican dos cortes, liquidaciones o cargos; un fallo del historial/auditoría requerida revierte el cambio local.
- CP-TRZ-04-12: consultas autorizadas permiten reconstruir los eventos sin exponer reportes ajenos ni eliminar historia por una baja lógica.

No se declara cerrado todo el DER ni preparada una migración por aprobar este bloque. Continúan los pendientes técnicos de pagos, cotización, prevención, hardware y diseño físico identificados en el documento 22.

## 10. Comprobaciones estructurales ejecutadas

El 2 de noviembre se comparó el texto del modelo anterior con el actualizado y se revisaron los destinos de las FK y las tablas de campos de la documentación. Resultado:

- 29 entidades, 55 columnas FK y 55 relaciones; las 55 FK tienen destino declarado y tipo compatible con la PK referenciada.
- Todas las entidades tienen PK, sin nombres de entidad o campos repetidos.
- Las otras 25 entidades se conservaron íntegramente. No se perdió ni cambió el tipo o las claves de ningún atributo anterior en las tres entidades afectadas; los ocho campos previos del historial de orden se conservan bajo su nuevo nombre.
- Las 52 relaciones previas permanecen conceptualmente, con el renombre y la opcionalidad condicional de estado_nuevo de orden; solo se agregaron tres relaciones.
- HISTORIAL_INCIDENCIA e HISTORIAL_ORDEN_MANTENIMIENTO tienen once campos cada uno y coinciden con sus tablas documentales.
- La referencia del corte es FK/UK opcional y no restringe la cantidad de reportes por detalle ni de eventos por reporte. La auditoría conserva exclusivamente administrador_id, no un actor automático.
- Los enlaces locales de documentación revisados tienen destino existente. Los tres originales conservan sus hashes y no se sobrescribieron.

No se ejecutó un parser/renderizador Mermaid ni se verificaron estas condiciones contra MySQL o JPA. Los casos CP-TRZ-04 siguen pendientes de implementación/ejecución; las comprobaciones anteriores no prueban roles, atomicidad, cronología o concurrencia en la aplicación. El diff de archivos de aplicación permanece sin cambios por esta tarea.
