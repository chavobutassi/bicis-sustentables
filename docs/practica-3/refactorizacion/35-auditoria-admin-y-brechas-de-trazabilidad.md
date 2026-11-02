# Auditoría administrativa y trazabilidad aprobada

Fecha: 2 de noviembre de 2026.

Estado actualizado: el usuario aprobó expresamente las cuatro mejoras de este documento: HISTORIAL_INCIDENCIA; ampliación y renombre a HISTORIAL_ORDEN_MANTENIMIENTO; motivo en AUDITORIA_SISTEMA; e incidencia_corte_id en ALQUILER_DETALLE. Se incorporaron al DER lógico, que pasa de 28/52 a 29 entidades y 55 FK/relaciones. La auditoría sigue siendo exclusivamente de ADMIN. El [documento 36](36-incorporacion-aprobada-trazabilidad-der.md) registra campos, claves, condiciones y comprobaciones. No se modifican Java ni la base de datos.

## 1. Decisión aprobada sobre auditoría

AUDITORIA_SISTEMA registra acciones administrativas críticas ejecutadas con permiso ADMIN, no cualquier modificación de cualquier usuario. Conserva administrador_id como FK obligatoria a USUARIO.id y no tiene origen automático: no acepta un administrador nulo o ficticio. Sus otros campos se conservan: id PK, entidad_afectada, entidad_id, accion, valores_anteriores, valores_nuevos y fecha_operacion. Se incorpora motivo como text con obligatoriedad según la acción.

La FK acredita la existencia del usuario, no garantiza su rol. El backend verifica ADMIN al ejecutar la acción y obtiene su identidad de la autenticación, no de un id enviado libremente por el cliente. Que una cuenta tenga ADMIN y TECNICO no convierte automáticamente sus actuaciones como técnico en acciones administrativas. Perder un rol posteriormente no borra ni reatribuye las actuaciones anteriores.

Ejemplos administrativos: cambios de tarifas, estaciones, roles o estado activo de una cuenta; inactivaciones y bajas permitidas; asignación/reasignación de técnico; cancelaciones administrativas; revisión de incidencias y autorización de habilitación. Se auditan operaciones efectivas y relevantes, no todas las consultas ni cualquier pulsación del panel. Auditar no concede permisos nuevos sobre diagnóstico, trabajo técnico o liquidaciones definitivas.

Los historiales de dominio conservan actor_usuario_id y origen USUARIO/SISTEMA según su acción: esta decisión no los convierte en exclusivos de ADMIN. Una devolución del cliente, un trabajo del técnico, un vencimiento automático y una confirmación financiera externa deben conservar su autor u origen real en su módulo.

El PDF original describe trazabilidad de operaciones administrativas y técnicas. Separarla entre auditoría de ADMIN e historiales de negocio respeta esa finalidad; no exige almacenar todas las actuaciones en la misma tabla. El diccionario original distingue trabajo técnico y administración, y el DER v4 ya nombraba administrador_id en AUDITORIA_SISTEMA. Los originales se consultaron y no se sobrescribieron.

## 2. Cobertura que ya tiene el DER

| Apartado | Representación actual | Qué no debe darse por cubierto |
| --- | --- | --- |
| Estado de bicicleta | HISTORIAL_ESTADO_BICICLETA | No registra automáticamente todos los cambios de ubicación o atributos sin transición |
| Uso de cada unidad | HISTORIAL_ESTADO_DETALLE y fechas/importes congelados de ALQUILER_DETALLE | No autoriza sobrescribir hechos ya cerrados; la liquidación conserva sus propias condiciones |
| Orden de mantenimiento | HISTORIAL_ORDEN_MANTENIMIENTO, ampliado y renombrado | Su implementación debe conservar también cambios permitidos de datos sin transición |
| Pago y reembolso | Sus dos historiales específicos, con origen y referencias externas | No representan nuevos cobros por cada evento ni sustituyen la conciliación con la pasarela |
| Acciones administrativas | AUDITORIA_SISTEMA exclusiva de ADMIN | No cubre actuaciones del cliente, técnico o sistema por el solo hecho de existir |
| Incidencia | INCIDENCIA e HISTORIAL_INCIDENCIA | El historial aprobado debe implementarse y consultarse; su dibujo no registra eventos reales |

Estas son representaciones del modelo, no funciones implementadas ni pruebas superadas. Las transiciones de ADMIN pueden aparecer tanto en su historial de negocio como en auditoría: son dos evidencias de una misma operación, no dos operaciones ni dos cargos.

## 3. Primera mejora aprobada Historial de incidencia

Se incorporó HISTORIAL_INCIDENCIA como historial de los eventos relevantes del reporte, no como vínculo entre varias órdenes. Una incidencia tiene uno o muchos eventos en el modelo, incluido su registro inicial; cada evento pertenece a una sola incidencia. El nombre amplio permite conservar cambios sin inventar transiciones de estado.

| Campo incorporado | Clave y finalidad |
| --- | --- |
| id | int, PK del evento |
| incidencia_id | int, FK obligatoria a INCIDENCIA.id; no UNIQUE |
| accion | Código controlado del evento: registro, cambio de revisión, corrección permitida, vínculo o recepción |
| estado_anterior | Código de revisión; nulo en la creación y en eventos que no cambien el estado |
| estado_nuevo | Código de revisión; obligatorio en creación/transición y nulo en eventos sin cambio de estado |
| fecha_hora_cambio | Fecha de registro del backend, distinta del momento informado del accidente/falla y del corte validado |
| actor_usuario_id | int, FK a USUARIO.id; obligatorio para actuación humana, nulo solo para origen SISTEMA |
| origen | USUARIO o SISTEMA, determinado por el backend |
| valores_anteriores | Datos permitidos antes del cambio; nulos en la creación |
| valores_nuevos | Datos permitidos registrados o modificados; estructura controlada, no una copia indiscriminada de la entidad |
| observaciones | Contexto y motivo obligatorio cuando la operación lo requiera |

Conserva registro inicial, correcciones permitidas del reporte, revisión económica, decisión de ADMIN, corte validado, recepción/recuperación y cambios autorizados del vínculo con la orden. Un evento sin transición no registra PENDIENTE a PENDIENTE. Los valores estructurados no incluyen secretos; estados y acciones son códigos validados, no texto arbitrario del cliente. No se propone otro catálogo por esta revisión.

La revisión sigue siendo de ADMIN y no se habilita al cliente a editar libremente un reporte ya registrado. Al implementar deben concretarse las correcciones permitidas y sus límites conforme a los permisos aprobados; no se presupone reapertura de una decisión ni reliquidación tras una liquidación definitiva. Las decisiones administrativas se conservarán además en AUDITORIA_SISTEMA.

Esta tabla añade una entidad y dos FK/relaciones: a INCIDENCIA.id y a USUARIO.id. Junto con la FK del corte aprobada en el mismo paso, el modelo queda en 29 entidades y 55 FK/relaciones. No es HISTORIAL_ATENCION_MANTENIMIENTO, que sigue descartado.

## 4. Segunda mejora aprobada Historial de orden

El historial existente conserva transiciones, pero el técnico puede registrar diagnóstico, trabajo, observaciones o costos sin cambiar de EN_PROCESO. Los últimos valores de la orden no conservan esas versiones; AUDITORIA_SISTEMA ya no puede cubrirlas porque son actuaciones técnicas.

Se amplió el historial existente, sin crear otra tabla. Se renombró HISTORIAL_ORDEN_MANTENIMIENTO y se añadieron accion, valores_anteriores y valores_nuevos. Se conservaron sus PK, FK a orden/usuario, fechas, origen y observaciones. Sus dos FK de estados se completan solo para creación y transiciones: anterior nulo al crear, ambos obligatorios en una transición y ambos nulos para un evento exclusivamente de datos. No se inventan cambios de estado para registrar un avance.

Ejemplos: asignación administrativa de técnico anterior/nuevo; corrección técnica autorizada de diagnóstico; avance del trabajo; registro/corrección del costo interno; resultado final. La creación automática sigue conservando origen SISTEMA. Los estados, permisos de asignación y trabajo, diagnóstico obligatorio al finalizar, moneda ARS y máximo de una orden abierta por bicicleta no cambian.

Una única acción puede guardar estado y datos modificados en el mismo evento. Cada guardado efectivo produce su evento, no uno por tecla o por petición sin cambios. El historial conserva la identidad del actor real, no solo el técnico actualmente asignado.

La ampliación y el nuevo nombre están incorporados al Mermaid. No añaden entidades ni FK/relaciones; amplían la nulabilidad condicional de las FK de estados para los eventos de datos. No habilitan edición libre de órdenes finalizadas o canceladas. El nombre antiguo se conserva solo en antecedentes documentales, no como otra entidad.

## 5. Campos aprobados y límites de implementación

### Motivo de la acción administrativa

Se incorporó motivo de tipo text, opcional en cambios rutinarios y obligatorio en operaciones justificadas por las reglas, como una baja o cancelación administrativa. Evita depender de textos no estructurados dentro del nombre de la acción. No cambia la PK ni la FK del administrador. No se registran contraseñas, hashes, tokens, credenciales ni datos de tarjeta en valores o motivos.

### Incidencia que fundamenta el corte

Se incorporó incidencia_corte_id como int, FK opcional y UK de ALQUILER_DETALLE a INCIDENCIA.id, según D07-A. Un historial explica la evolución de reportes, pero no identifica por sí solo cuál fundamenta el fin de uso aplicado si hubo varios. La incidencia debe pertenecer al mismo detalle y tener una decisión validada que fundamente el corte; no se aplica dos veces un corte ni se reabre una liquidación por cambiar el enlace. La FK y la unicidad no garantizan por sí solas pertenencia, autorización o cronología; sus controles se detallan en el documento 36.

### Enlaces excepcionales a órdenes

HISTORIAL_ATENCION_MANTENIMIENTO permanece descartado. En el historial de incidencia aprobado, un cambio de su orden conserva anterior/nuevo; una reasociación administrativa de un reporte de devolución en ALQUILER_DETALLE conserva anterior/nuevo en la auditoría ADMIN. El enlace inicial automático debe conservarse con la creación del reporte y la orden, no atribuirse a un ADMIN. Si una futura automatización reasociara reportes sin cambiar estados, habría que definir su evento antes de implementarla: no queda autorizada ni trazada mediante esta auditoría administrativa.

### Eventos financieros sin transición

Los historiales de PAGO y REEMBOLSO ya conservan sus transiciones del sistema/pasarela. Una notificación repetida, consulta o reintento sin cambios no debe inventar otra transición ni un nuevo movimiento. Al resolver D03 se definirá el registro técnico necesario, su correlación y conservación, separado de AUDITORIA_SISTEMA; no se propone aquí otra tabla ni se declara que registrar un mensaje de consola alcance para todos los eventos financieros.

### Reglas comunes y consultas

Antes de implementar se deben cerrar las acciones registradas, los campos permitidos, los permisos de corrección y los motivos exigidos por operación. Fechas de registro y autor se obtienen en backend; el momento informado de un hecho puede ser anterior, pero nunca sustituye esa fecha de registro. Las correcciones añaden eventos y no borran los anteriores.

Cada modificación y su historial/auditoría obligatorios se confirman en una transacción local. Si falla el registro requerido, no se confirma aisladamente la modificación. La idempotencia evita repetir efectos y eventos por un reenvío. No se mantienen transacciones abiertas esperando Mercado Pago o correo.

La consulta administrativa debe permitir reconstruir la secuencia por entidad e identificador, fecha y responsable. La vista del técnico o del cliente sigue los permisos aprobados y no expone auditoría administrativa o reportes ajenos por el hecho de consultar un alquiler. La base debe preservar eventos y referencias; baja lógica no equivale a borrar historia. La estrategia de índices, formatos JSON/texto y permisos físicos pertenece a D06.

## 6. Aprobación e incorporación al modelo

El usuario confirmó «apruebo las 4 mejoras/cambios al DER». Las cuatro están incorporadas al modelo lógico y registradas como RN-TRZ-01 en el documento 36. Se conservan las reglas económicas, estados y permisos anteriores; no se incorporó la tabla de atención descartada. Continúan D03, D06 y los demás puntos técnicos expresamente pendientes, no una nueva espera de aprobación de estos cuatro cambios.

No es necesario crear ahora un historial de cabecera de ALQUILER ni una tabla por cada campo, tipo o notificación. Los estados derivados del conjunto pueden reconstruirse de los detalles y sus eventos; no se afirma que ello cubra cualquier futura modificación de cabecera. La matriz anterior y las brechas delimitan el alcance actual.

## 7. Criterios de aceptación pendientes de ejecución

- Un técnico que modifica un diagnóstico sin transición conserva anterior/nuevo en la historia de la orden, sin insertarse como ADMIN.
- Una incidencia conserva registro y revisiones con autor real, fechas separadas y motivo; una corrección no elimina el contenido anterior.
- Una operación administrativa registra un administrador autenticado válido; un proceso automático o una actuación técnica no se atribuye a esta auditoría.
- Una misma operación que requiere historia de negocio y auditoría administrativa conserva ambas o no confirma ninguna modificación local.
- Repetir una petición ya aplicada no duplica un cambio, una recepción ni dinero.
- Las consultas autorizadas reconstruyen la secuencia sin revelar reportes ajenos o secretos.

Estos casos son especificaciones para la implementación futura. No se ejecutaron SQL, pruebas de negocio, arranque de Spring ni llamadas a Mercado Pago. La aprobación de las cuatro mejoras y los demás pendientes técnicos no se confunden con funciones ya operativas.
