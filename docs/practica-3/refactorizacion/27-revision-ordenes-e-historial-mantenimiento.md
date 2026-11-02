# Revisión de órdenes e historial de mantenimiento

Fecha: 28 de octubre de 2026.

Estado: el usuario aprobó expresamente el 28 de octubre de 2026 agregar diagnostico a la orden y fijar ARS para costos internos de repuestos. Ambas precisiones se incorporaron al Mermaid; se mantienen RN-MAN-01 a RN-MAN-04 y sus permisos. Se añadió un campo text y se precisaron dos existentes, sin nuevas tablas, PK, FK, unicidades o relaciones en ese paso. No se modificaron Java ni la base de datos. Al consolidar este bloque el modelo conservó 28 entidades y 51 FK/relaciones; el total vigente figura en el [mapa de cambios](22-revision-del-der-y-mapa-de-cambios.md). Los criterios de negocio están documentados, no ejecutados.

Actualización aprobada del 2 de noviembre: RN-TRZ-01 amplía y renombra el historial a HISTORIAL_ORDEN_MANTENIMIENTO, con once campos para transiciones y cambios permitidos de datos. El modelo completo queda en 29 entidades y 55 FK/relaciones por el conjunto de las cuatro mejoras. Se conserva ORDEN_MANTENIMIENTO íntegra. Ver [incorporación y condiciones](36-incorporacion-aprobada-trazabilidad-der.md).

## 1. Base de la revisión

Se releyeron la sección de mantenimiento y los roles del diccionario original, los objetivos y requerimientos del PDF y sus referencias al trabajo técnico, y los campos de la orden e historial del DER v4. Se contrastaron con RN-MAN-01, RN-MAN-02, RN-MAN-03, RN-MAN-04, la baja de bicicleta, las incidencias aprobadas y el modelo v5. Los originales se conservan sin cambios.

El modelo original ya separaba ORDEN_MANTENIMIENTO de su historial y del estado operativo de la bicicleta. El borrador añade el tipo PREVENTIVO/CORRECTIVO, creación, resultado técnico, moneda, motivo de pausa/cancelación y control de concurrencia. Se conserva esa separación: tipo de trabajo, avance de orden y aptitud de la bicicleta no son lo mismo.

Las clases persistentes actuales no implementan este módulo nuevo. Esta revisión no certifica pantallas, endpoints ni pruebas de mantenimiento funcionando.

## 2. TIPO_MANTENIMIENTO y ESTADO_ORDEN_MANTENIMIENTO

TIPO_MANTENIMIENTO conserva id como PK, codigo obligatorio y único y descripcion. Sus códigos iniciales son PREVENTIVO y CORRECTIVO. La descripción pertenece al catálogo y no se copia a cada orden. El catálogo puede tener cero o muchas órdenes; cada orden referencia exactamente un tipo.

ESTADO_ORDEN_MANTENIMIENTO conserva id como PK y codigo obligatorio y único. Sus cinco valores aprobados son CREADA, EN_PROCESO, PAUSADA, FINALIZADA y CANCELADA. Cada orden tiene exactamente un estado actual y el catálogo puede aparecer en muchas órdenes e historiales.

No se agregan una tabla por tipo, combinaciones de tipo/estado ni nuevos estados para representar asignaciones o compras. Tampoco se necesita un ABM público de estos catálogos. Sus PK y las FK correspondientes utilizan el mismo tipo lógico int; las longitudes SQL se concretarán en D06.

## 3. ORDEN_MANTENIMIENTO

| Campo | Clave y significado | Nulabilidad o condición |
| --- | --- | --- |
| id | PK; identificador de la intervención | Obligatorio, generado por el sistema |
| bicicleta_id | FK a BICICLETA.id | Obligatorio; una orden pertenece a una unidad |
| tipo_mantenimiento_id | FK a TIPO_MANTENIMIENTO.id | Obligatorio; PREVENTIVO o CORRECTIVO |
| estado_orden_mantenimiento_id | FK a ESTADO_ORDEN_MANTENIMIENTO.id | Obligatorio; inicia en CREADA |
| tecnico_id | FK a USUARIO.id; asignación vigente | Puede faltar inicialmente en CREADA; iniciar/reanudar requiere técnico activo, con rol TECNICO y asignado |
| fecha_creacion | Momento de registro de la orden | Obligatorio; backend, no una fecha libre del formulario |
| fecha_inicio | Primer inicio efectivo del trabajo | Nulo antes de iniciar; no se reinicia al reanudar |
| fecha_fin | Momento de cierre de la orden | Nulo mientras esté abierta; se registra al finalizar o cancelar; una cancelación anterior al inicio no inventa fecha_inicio |
| resultado_tecnico | Conclusión de la intervención | Obligatorio al finalizar; representación propuesta mediante APTA o NO_APTA, ya prevista en el borrador; no se inventa una conclusión al cancelar |
| costo_repuestos | Costo interno de los repuestos registrados | Decimal no negativo cuando se conoce; no se confunde pendiente de determinar con cero; una intervención sin repuestos puede registrar cero explícito |
| moneda_repuestos | Moneda de ese costo | ARS, aprobada; explícita cuando se registre un importe, incluso cero; precisión pendiente en D08 |
| descripcion_trabajo | Acciones efectivamente realizadas | Puede faltar antes del trabajo; al finalizar debe explicar la intervención, no solo copiar el reporte del cliente |
| observaciones | Aclaraciones de la orden | Opcionales según el caso; no sustituyen historia de estados o auditoría |
| motivo_pausa_cancelacion | Resumen del motivo aplicable a la última pausa/cancelación | Condicional; motivo no vacío al ejecutar cualquiera de esas acciones; los motivos previos quedan conservados en sus eventos |
| version | Control optimista propuesto | Administrado por persistencia; no habilita cambios libres de estado ni garantiza por sí solo una única orden abierta |
| diagnostico | Campo text incorporado: hallazgo técnico, separado del trabajo | Aprobado; puede faltar en CREADA y durante una evaluación aún no concluida; obligatorio al pasar a FINALIZADA |

### Diagnóstico aprobado e incorporado

Separar diagnostico de descripcion_trabajo permite distinguir «se detectó una falla en el freno» de «se ajustó y comprobó el freno». Un reporte del cliente sigue siendo un reporte: no se copia automáticamente como diagnóstico confirmado. El diagnóstico puede concluir que no se encontró la falla reportada.

Se incorporó un único campo text diagnostico, no una entidad DIAGNOSTICO ni una tabla de repuestos. Puede ser nulo antes de concluir la evaluación, pero finalizar exige un diagnóstico no vacío junto con el trabajo y el resultado técnico. Cancelar no inventa una conclusión ni elimina hallazgos ya registrados. La condición por estado se implementará en las operaciones y sus validaciones: el comentario del DER no es por sí solo una restricción SQL o una prueba superada. No cambia PK, FK, unicidades ni el total de entidades.

### Costos de repuestos aprobados en ARS

Se utilizará ARS para este costo interno y se conserva moneda_repuestos explícita, sin agregar una tabla de monedas o mezclarlo con el importe de alquiler. El valor de referencia del alquiler sigue en USD y sus movimientos en ARS con la cotización contratada: no se reutiliza esa cotización para presentar un costo de taller como cargo al cliente. El backend deberá rechazar otra moneda en ese campo para el alcance aprobado; no alcanza con una etiqueta visual ARS.

Registrar repuestos utilizados no crea PAGO, REEMBOLSO, multa ni deuda del cliente. La imputación de daños o reposición no fue aprobada y sigue fuera del recorrido definido. Cancelar una orden no elimina gastos o trabajos realmente registrados ni los convierte automáticamente en cero. La moneda ya está aprobada; la precisión física continúa pendiente y no modifica los estados aprobados.

## 4. HISTORIAL_ORDEN_MANTENIMIENTO

| Campo actual | Clave y condición |
| --- | --- |
| id | PK de cada evento; conservada del historial anterior |
| orden_mantenimiento_id | FK obligatoria a ORDEN_MANTENIMIENTO.id |
| accion | Campo string nuevo; código obligatorio de la operación validado por backend |
| estado_anterior_id | FK a ESTADO_ORDEN_MANTENIMIENTO.id; nulo al crear o en un evento solo de datos; obligatorio en transición |
| estado_nuevo_id | FK al mismo catálogo; obligatorio al crear/transicionar; nulo en un evento solo de datos |
| fecha_hora_cambio | Momento de registro del evento en el backend |
| actor_usuario_id | FK a USUARIO.id; obligatorio para una acción humana y nulo únicamente para origen SISTEMA |
| origen | USUARIO o SISTEMA, determinado por el backend |
| observaciones | Conserva el motivo y contexto pertinentes a esa transición; obligatorio el motivo de pausa/cancelación |
| valores_anteriores | Campo text nuevo; datos permitidos previos, nulo al crear; no almacena secretos |
| valores_nuevos | Campo text nuevo; datos permitidos registrados/modificados, con estructura validada |

Cada orden tiene uno o muchos registros, incluido CREADA. Cada evento pertenece a exactamente una orden. Los estados anterior y nuevo son dos relaciones independientes al mismo catálogo; un estado puede no aparecer o aparecer muchas veces. El usuario puede intervenir en muchos eventos y el actor de un evento no debe confundirse con el técnico actualmente asignado.

El historial se añade, no se reemplaza ni se edita desde el ABM normal. El estado/datos vigentes y su evento se registran juntos. La secuencia conserva inicios, pausas, reanudaciones, cierre y modificaciones permitidas de datos; las fechas de la orden son resúmenes de primer inicio y cierre, no sustitutos de esos eventos. El nombre anterior HISTORIAL_ESTADO_ORDEN_MANTENIMIENTO se conserva en antecedentes, no como una segunda entidad del modelo.

## 5. Asignaciones cambios de trabajo y auditoría

Cambiar de técnico en CREADA no cambia necesariamente el estado. Tampoco lo hace completar un avance de trabajo o registrar un costo. No corresponde inventar una transición CREADA a CREADA para que esas acciones entren en un historial de estados.

Con RN-TRZ-01, HISTORIAL_ORDEN_MANTENIMIENTO conserva esos eventos con acción, valores anteriores/nuevos, autor, fecha y contexto. La asignación registra técnico anterior/nuevo y ADMIN real; los cambios técnicos autorizados conservan al técnico que efectivamente actuó. Las actuaciones administrativas tienen además AUDITORIA_SISTEMA, exclusiva de ADMIN. La modificación y todos los eventos obligatorios se confirman en la misma transacción local. El último tecnico_id o el último texto de la orden no bastan para afirmar que se conservó toda la intervención.

La creación manual registra al ADMIN real. Una creación automática desde reporte o calendario tiene origen SISTEMA y no inventa un administrador humano; la autoría del reporte del cliente permanece en el detalle/incidencia correspondiente. La habilitación de la bicicleta registra a ADMIN y su transición en HISTORIAL_ESTADO_BICICLETA, sin convertir la orden finalizada en una autorización automática.

Esta ampliación reutiliza el historial de orden; no agrega una tabla de asignaciones o intervenciones. Requiere eventos completos, consultables y sin edición/borrado en el flujo normal, permisos de consulta y protección contra cambios parciales. La existencia del diagrama no prueba que ya se cumpla ese comportamiento.

Las FK operativas de ALQUILER_DETALLE e INCIDENCIA permiten varios reportes para una orden, y cada reporte puede apuntar a su orden de atención vigente. Si una orden se cancela y se crea otra por reclasificación, conservar ambas órdenes y auditar los enlaces anterior/nuevo es la propuesta compacta ya prevista. No se afirma que una sola FK mutable sea por sí sola la historia completa. La necesidad de consultar múltiples asociaciones históricas mediante FK directas continúa identificada en D07 para cerrar su representación física, sin agregar una tabla nueva en esta revisión.

La revisión de [D07 en el documento 33](33-revision-trazabilidad-incidencias-y-ordenes.md) propuso HISTORIAL_ATENCION_MANTENIMIENTO, pero el usuario lo descartó. El [documento 36](36-incorporacion-aprobada-trazabilidad-der.md) incorpora HISTORIAL_INCIDENCIA para los eventos y cambios autorizados de su vínculo; los reemplazos administrativos de enlaces de devolución conservan auditoría ADMIN. No se necesitan varias órdenes por un cambio de técnico o un avance de trabajo. La ampliación aprobada modifica el modelo lógico, no Java ni SQL.

## 6. Integridad y permisos que deben implementarse

Una bicicleta puede tener muchas órdenes históricas, pero como máximo una abierta entre CREADA, EN_PROCESO y PAUSADA. Por eso no corresponde declarar bicicleta_id UNIQUE de forma global: impediría crear nuevas intervenciones después de cerrar las anteriores. El límite condicional requiere proteger la bicicleta y comprobar/crear la orden en una operación transaccional coherente, con la estrategia de índices y bloqueo que se concrete para la base elegida.

Asignar exige ADMIN y una orden CREADA o PAUSADA. Iniciar, registrar trabajo, pausar o finalizar exige el técnico autorizado y asignado según RN-MAN-02; ser ADMIN no lo sustituye. Cancelar se conserva como acción administrativa con motivo. No se amplían permisos para salvar una operación que sus condiciones no permiten.

Un nuevo reporte se conserva aunque ya haya una orden abierta. No crea otra por repetición o concurrencia ni cambia automáticamente PREVENTIVO por CORRECTIVO. Reclasificar mantiene el recorrido autorizado de cancelación con motivo y creación de la correspondiente. Una preventiva pendiente no desaparece por cerrar un correctivo y no produce dos órdenes abiertas simultáneas.

FINALIZADA y CANCELADA conservan la orden y su historia, sin borrado físico ni reapertura normal. FINALIZADA significa intervención concluida con resultado: no necesariamente bicicleta apta. Ni finalizar ni cancelar permiten alquilar automáticamente. La aptitud, revisión preventiva pendiente, ausencia de restricciones, estación válida y autorización posterior de ADMIN se conservan según RN-MAN-02/RN-MAN-04.

Las fechas no se reescriben para simular otro inicio ni para forzar el calendario. La última preventiva válida corresponde a una intervención preventiva finalizada satisfactoriamente, no a una cancelación o a cualquier cierre. Los intervalos numéricos iniciales siguen pendientes; los ejemplos de meses no se presentan como recomendaciones mecánicas reales.

## 7. Criterios de comprobación del diseño

Son criterios especificados, no ejecutados:

- CP-DER-MAN-01: las FK de tipo, estado, bicicleta, técnico e historial apuntan a sus entidades; las dos referencias de estado del historial son independientes.
- CP-DER-MAN-02: CREADA sin técnico se conserva, pero no permite iniciar; dos peticiones no crean órdenes abiertas duplicadas.
- CP-DER-MAN-03: varias órdenes cerradas de una bicicleta se conservan sin chocar con una restricción única global indebida.
- CP-DER-MAN-04: pausa y reanudación conservan todos sus eventos y motivos; fecha_inicio mantiene el primer inicio real.
- CP-DER-MAN-05: reasignar o actualizar trabajo/costos conserva valores anteriores/nuevos y actor sin inventar un cambio de estado.
- CP-DER-MAN-06: una cancelación conserva trabajos y costos reales ya registrados; no crea un cargo al cliente ni acredita aptitud.
- CP-DER-MAN-07: reporte, hallazgo técnico y trabajo realizado se consultan separados; se exige diagnóstico al finalizar, no al crear.
- CP-DER-MAN-08: los costos internos identifican moneda ARS y no modifican la liquidación del alquiler; otra moneda se rechaza en el alcance aprobado.

## 8. Incorporación y siguiente bloque

El usuario confirmó ambas precisiones mediante «apruebo ambas cosas». Se incorporaron al DER en ORDEN_MANTENIMIENTO: diagnostico como text, obligatorio al finalizar, y costos internos expresados en ARS mediante los campos existentes. Se conservaron todos los demás campos, entidades, claves y relaciones. La validación realizada es estructural del modelo, no ejecución de mantenimiento o persistencia.

Los estados, tipos, roles y autorización posterior de ADMIN ya estaban aprobados y no se reabren. Siguen pendientes precisión SQL, intervalos preventivos iniciales y representación histórica de enlaces identificada en D07. Continúa la revisión de ALQUILER y ALQUILER_DETALLE con las reglas de reserva, tiempo real, precios y cotización congelados ya aprobadas. El cambio del modelo no equivale a implementación en Java ni a migración de datos.
