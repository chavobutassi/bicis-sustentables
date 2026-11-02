# Revisión de estaciones tipos y bicicletas

Fecha: 28 de octubre de 2026.

Estado: revisión del segundo bloque del DER lógico. El usuario aprobó expresamente el recorrido de baja de estación de la sección 5, con la condición de que sea exclusivamente lógica, nunca física. Se registra como RN-EST-01 y se aclara borrado_estacion en el Mermaid, sin agregar columnas, claves ni entidades. Los demás campos se contrastan con las reglas y el código existente; no se declara cerrado todo el diseño físico. No se modificaron Java ni la base de datos.

## 1. Base y límites

Se releyeron el diccionario de estados original y los apartados de visión, objetivos y requerimientos del PDF, se contrastó el DER v4 y se revisaron RN-ALQ-03, RN-ALQ-04, RN-BIC-01, RN-BIC-02, RN-MAN-04 y el cierre de incidencias aprobado. La visión exige estaciones, mapa, disponibilidad, mantenimiento y trazabilidad. La separación de estado operativo, presencia física y contrato ya está aprobada; no se vuelve a mezclar en esta revisión.

La aplicación actual conserva tipos y estados como enums, precio por bicicleta, un flag borradoBici y capacidad calculada excluyendo ese flag. El nuevo DER usa catálogos y tarifa por tipo. Por eso la implementación anterior no demuestra que las reglas nuevas estén cubiertas, aunque se reutilicen sus pantallas, fotos y controles de estación.

## 2. ESTACION

| Campo existente en v5 | Clave y condiciones de revisión |
| --- | --- |
| id | PK; identificador estable, no depende del nombre |
| nombre | UNIQUE; obligatorio, sin blanco; normalización y longitud se concretan en D06 |
| direccion | Obligatoria; no se declara única porque no identifica por sí sola una estación |
| capacidad | Entero positivo; nunca puede quedar por debajo de la ocupación física al modificarla |
| borrado_estacion | Indicador de baja lógica; no borra la fila ni sus referencias históricas; recorrido aprobado RN-EST-01 en la sección 5 |
| latitud | Decimal obligatorio; rango de -90 a 90; precisión SQL pendiente |
| longitud | Decimal obligatorio; rango de -180 a 180; precisión SQL pendiente |
| version | Control de concurrencia propuesto; no sustituye coordinar los ingresos y cambios de capacidad |

No se agregan columnas espacios_libres, bicicletas_disponibles ni cantidad_ocupada: se calculan desde las bicicletas físicamente asociadas y las condiciones de disponibilidad. Tampoco se declara única la combinación de coordenadas: no se aprobó prohibir estaciones diferentes por proximidad o por coincidir en un punto.

La ocupación incluye toda bicicleta que siga físicamente allí, incluso RESERVADA, MANTENIMIENTO, INACTIVA o DE_BAJA. Dar de baja una unidad no libera su espacio. Los ingresos, traslados, devoluciones, cambios de capacidad y baja de estación deberán coordinar el acceso a la misma estación dentro de transacciones locales; un contador visual o una FK no garantizan por sí solos que no se exceda capacidad.

Con [RN-ALQ-11](30-propuesta-composicion-contratacion.md) aprobada, el origen común se guarda en ALQUILER.estacion_retiro_id, no en cada detalle. Para impedir la baja de una estación con unidades RESERVADO o PENDIENTE_RETIRO todavía sin retirar, la futura consulta deberá unir esos detalles con su cabecera y comprobar el origen. El traslado de la FK no elimina esa protección ni la comprobación de presencia física. El máximo inicial de diez bicicletas por alquiler no obliga a que una estación tenga diez disponibles ni permite superar su capacidad.

En el código actual se observa un control para no reducir capacidad por debajo del conteo que utiliza borradoBici=false. Al refactorizar deberá adaptarse a la presencia física aprobada, sin excluir DE_BAJA todavía presente. La fórmula del DTO que limita espacios libres a cero no sirve como comprobación de integridad de datos antiguos: las inconsistencias deben detectarse y corregirse con evidencia, no darse por resueltas al ocultar un número negativo.

## 3. TIPO_BICICLETA

| Campo existente en v5 | Clave y condiciones de revisión |
| --- | --- |
| id | PK; referenciado por muchas bicicletas |
| codigo | UNIQUE y obligatorio; conservar inicialmente MONTANA, PASEO y ELECTRICA al migrar el enum |
| precio_por_hora_usd | Tarifa vigente del tipo, no de cada unidad; decimal, nunca un valor negativo; precisión y política sobre tarifa cero se concretan antes de cerrar el diseño físico |
| intervalo_preventivo_meses | Entero positivo; configurado solo por ADMIN; valores numéricos iniciales pendientes, sin convertir los ejemplos en una política definitiva |

No se agrega una tabla cronómetro ni una columna de precio duplicada en BICICLETA. La tarifa aplicada se guarda en ALQUILER_DETALLE y un cambio del tipo no modifica contratos ya confirmados. Los cambios de tarifa e intervalo se auditan con actor, fecha y valores anterior/nuevo, sin guardar solamente la última intervención.

La última preventiva satisfactoria se obtiene de las órdenes; para una bicicleta nueva sin revisiones se utiliza su fecha real de alta. Crear, cancelar o cerrar sin éxito una orden no reinicia el calendario. Un legado sin referencia fiable requiere revisión inicial según RN-MAN-04. No se agrega por ahora otra columna de última preventiva que pueda contradecir el historial.

Los cambios de tarifa e intervalo también necesitan control de concurrencia al implementar. Puede utilizarse bloqueo transaccional o proponerse version para este catálogo mutable; no se afirma que la ausencia/presencia de esa columna implemente por sí sola la consistencia. No se añadió un campo nuevo sin contrastar la estrategia física del conjunto.

## 4. BICICLETA y su catálogo de estados

| Campo existente en v5 | Clave y condiciones de revisión |
| --- | --- |
| id | PK; identidad interna estable de la unidad y sus referencias históricas |
| codigo_bicicleta | UNIQUE y obligatorio; normalización al implementar; la baja no elimina la fila ni permite reutilizar silenciosamente el código para otra bicicleta |
| tipo_bicicleta_id | FK obligatoria a TIPO_BICICLETA.id; no implica guardar otra tarifa en la unidad |
| estado_bicicleta_id | FK obligatoria a ESTADO_BICICLETA.id; no acepta un estado inexistente o una transición libre enviada por el cliente |
| estacion_id | FK opcional a ESTACION.id; representa presencia física actual, no el último lugar conocido |
| fecha_alta | Referencia real de ingreso a flota; obligatoria para altas nuevas; tratamiento del legado sin fecha pendiente en D06 |
| version | Control optimista propuesto; las operaciones deben proteger coherentemente la unidad y su contrato vigente |

ESTADO_BICICLETA conserva id como PK y codigo único, con los siete estados aprobados: DISPONIBLE, RESERVADA, EN_USO, MANTENIMIENTO, INACTIVA, DE_BAJA y EXTRAVIADA. No se agregan estados PREVENTIVA o CORRECTIVA: corresponden al tipo de orden.

Una DISPONIBLE requiere estación activa válida y aptitud técnica sin impedimentos. Una RESERVADA aún no retirada conserva su presencia y ocupación. Al retirar pasa a EN_USO y su estación actual queda vacía. Una MANTENIMIENTO puede estar dentro de una estación o fuera de ella; ese estado no demuestra un traslado. No se toma estacion_id nulo como prueba de pérdida o robo ni se inventa una estación para cerrar un incidente.

El borrador no duplica borradoBici junto con DE_BAJA. Antes de retirar ese flag de la base existente se revisarán conflictos entre flag, estado, ubicación y alquileres. No se borra nada mediante este documento.

Se conservan las relaciones de la unidad con alquileres, órdenes e HISTORIAL_ESTADO_BICICLETA. Los cambios de estado conservan el historial correspondiente. Los traslados o salidas físicas que no cambien el estado también requieren trazabilidad: AUDITORIA_SISTEMA debe registrar sobre la BICICLETA su ubicación anterior/nueva, actor, fecha y motivo; no se genera una transición de estado ficticia para registrar un movimiento. No se necesita agregar otra tabla para el alcance actual si esos eventos se conservan de forma completa y consultable.

## 5. RN-EST-01 Baja lógica de estaciones aprobada

El 28 de octubre de 2026 el usuario aprobó este recorrido y remarcó «siempre y cuando sea una baja lógica, nada de borrado físico». Queda aprobada la política de baja de estación, sin extender esa aprobación a otras decisiones pendientes del inventario:

1. Solo ADMIN puede dar de baja lógicamente una estación, conservando motivo, actor y fecha en auditoría.
2. No se permite mientras tenga bicicletas físicamente asociadas, cualquiera sea su estado. Primero deben resolverse las reservas incompatibles y registrarse los movimientos físicos autorizados; no se trasladan unidades ficticiamente por dar de baja la estación.
3. Tampoco se permite mientras exista un detalle RESERVADO o PENDIENTE_RETIRO vigente cuyo retiro esté previsto allí. Se verifican los detalles persistidos y su vencimiento, no solamente el conteo de bicicletas, y no se cancela ni reembolsa automáticamente al intentar dar de baja.
4. Las referencias históricas no impiden la baja cuando ya no hay stock ni retiros pendientes: se conserva la fila para no romper alquileres y trazabilidad. No se exige borrar o terminar viajes que ya salieron solo por haber partido de esa estación.
5. Una estación de baja no admite nuevas reservas de retiro ni ingresos de bicicletas. La operación se coordina con reserva, retiro e ingreso para que solicitudes simultáneas no eludan las comprobaciones.

La baja conserva la fila de ESTACION y cambia borrado_estacion de false a true, junto con la auditoría de la operación. No ejecuta borrado físico ni cascadas de eliminación, ni borra bicicletas, contratos, pagos, historiales o autorías. Los valores anteriores/nuevos, el responsable ADMIN, la fecha y el motivo se registran mediante AUDITORIA_SISTEMA, sin agregar una tabla o guardar solamente la última modificación.

Las consultas históricas deben poder resolver la estación referenciada aunque esté de baja; el filtro de estaciones habilitadas se aplica al uso operativo, no como una eliminación de su historia. La baja tampoco vacía ubicaciones ni modifica datos anteriores para aparentar que nunca existió.

El formulario de edición no sustituye ese recorrido transaccional. No se agregan una entidad ESTADO_ESTACION, reactivación automática ni cierres temporales automáticos. La aprobación se documenta y se refleja en el modelo, pero no acredita que el servicio nuevo esté implementado o probado.

## 6. Criterios para implementar y probar

Estos casos están especificados, no ejecutados:

- CP-INV-01: modificar capacidad por debajo de la ocupación física se rechaza, incluida una bicicleta DE_BAJA que aún esté dentro.
- CP-INV-02: dos ingresos compiten por el último espacio y solo uno se confirma; el otro no deja efectos parciales.
- CP-INV-03: retirar una reservada elimina su ubicación actual; cancelar antes del retiro termina la exclusividad pero no libera espacio físico.
- CP-INV-04: modificar la tarifa del tipo cambia nuevas contrataciones, no los precios ya aplicados de sus detalles.
- CP-INV-05: vencimiento preventivo y una orden abierta se gestionan conforme a RN-MAN-04 sin crear duplicados ni poner una unidad restringida a disposición.
- CP-INV-06: estado y ubicación son comprobables por separado; un traslado sin cambio de estado conserva su evento de inventario.
- CP-INV-07: intentar dar de baja una estación con stock o retiro pendiente se rechaza sin cancelaciones automáticas.
- CP-INV-08: estación vacía con solo referencias históricas puede darse de baja lógicamente, conservando sus relaciones y auditoría.
- CP-INV-09: la baja cambia el indicador y registra actor, fecha y motivo; no elimina físicamente filas ni ejecuta cascadas. Las consultas históricas autorizadas siguen identificando la estación original.

Las longitudes, precisión decimal, índices, estrategia de bloqueo y datos iniciales se concretarán junto con D02, D05 y D06. La identificación y RN-EST-01 no aprueban automáticamente todos los campos físicos del inventario. Sigue revisar ORDEN_MANTENIMIENTO, TIPO_MANTENIMIENTO y sus estados e historial, respetando las reglas de mantenimiento ya aprobadas y conservando los parámetros numéricos todavía pendientes.
