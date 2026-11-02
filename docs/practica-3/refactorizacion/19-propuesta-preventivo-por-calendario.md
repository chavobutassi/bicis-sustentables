# RN-MAN-04 Mantenimiento preventivo por calendario

Fecha de consulta: 28 de octubre de 2026.

Fecha de aprobación de la incorporación como requisito: 28 de octubre de 2026.

Fecha de aprobación de las condiciones de aplicación: 28 de octubre de 2026.

Estado: incorporación del preventivo automático por calendario y condiciones de aplicación de la sección 4 aprobadas expresamente por el usuario. No implementado en Java ni en la base de datos. Los valores numéricos de los intervalos, el diseño físico y los detalles técnicos expresamente pendientes todavía deben concretarse. Los intervalos mencionados como ejemplo no son frecuencias definitivas ni recomendaciones técnicas para bicicletas reales.

## 1. Alcance aprobado y encaje

El mantenimiento preventivo por calendario es compatible con la separación ya aprobada entre estado operativo, tipo de trabajo y avance de la orden. No necesita otro estado de bicicleta llamado PREVENTIVA ni una tabla que actúe como cronómetro.

Se incorpora como requisito generar preventivas automáticamente a partir de una periodicidad configurable por tipo de bicicleta. Para una unidad que puede entrar válidamente a revisión, se mantiene el diseño de bicicleta MANTENIMIENTO y orden de tipo PREVENTIVO en estado CREADA, con asignación posterior por ADMIN. La aptitud y la vuelta al servicio mantienen RN-MAN-02.

Se contrastó la idea con el Word de estados, el PDF de visión y el DER v4 antes de presentarla. Las fuentes contemplan prevención, órdenes e historial, pero no determinan estas frecuencias ni sus efectos sobre viajes y reservas. El usuario aprobó primero incorporar la automatización como requisito y después las condiciones de aplicación de la sección 4. Estas decisiones posteriores no se atribuyen a los documentos originales ni aprueban por extensión las excepciones todavía pendientes.

## 2. Diseño inicial para el DER

La dirección de diseño es reutilizar los tipos, bicicletas y órdenes existentes, sin introducir una tabla cronómetro. Los campos, restricciones y cálculos siguientes deben consolidarse en el DER y en sus reglas de datos; no se presentan como columnas ya creadas ni como un esquema físico definitivo.

| Entidad | Cambio o dato a utilizar |
| --- | --- |
| TIPO_BICICLETA | Agregar `intervalo_preventivo_meses`, entero positivo, para configurar la frecuencia por tipo |
| BICICLETA | Agregar una fecha de alta en la flota como referencia inicial cuando no haya una preventiva registrada; la fuente y el tratamiento de datos antiguos requieren una política explícita |
| ORDEN_MANTENIMIENTO | Utilizar bicicleta, tipo de mantenimiento, estado, fecha de finalización y resultado técnico para identificar la última preventiva completada satisfactoriamente |

El DER original ya contiene fecha de finalización de orden y su relación con la bicicleta. El tipo de mantenimiento y el registro de resultado técnico ya forman parte del diseño aprobado, aunque su representación física todavía debe consolidarse.

La fecha de última preventiva puede consultarse desde las órdenes que realmente cumplan esas condiciones. No es necesario duplicarla inicialmente en BICICLETA. Un campo derivado para acelerar consultas podría añadirse si fuese necesario, pero tendría que mantenerse coherente con la historia.

Se propone obtener la fecha de próxima revisión sumando el intervalo del tipo a esa última preventiva válida, o a la referencia inicial cuando todavía no haya una. Crear, pausar o cancelar una orden no reinicia el plazo. Un correctivo tampoco se interpreta automáticamente como una revisión preventiva.

No se inventa una revisión antigua para migrar bicicletas sin historial. Se aplica la política aprobada de la sección 4: fecha real de alta para una unidad nueva sin revisiones; una unidad antigua sin referencia fiable requiere una preventiva inicial antes de alquilarse.

Para esta política única por tipo no hace falta una tabla adicional. Un catálogo independiente de planes solo tendría sentido si luego se requirieran varios planes por modelo, kilometraje u otras reglas; eso no se incorpora mediante esta consulta.

## 3. Ejecución prevista del requisito

Una tarea del backend revisaría periódicamente las fechas persistidas y detectaría qué unidades requieren revisión. No se mantiene un contador en memoria ni se depende del navegador. Si la aplicación estuvo apagada, al volver debe detectar los vencimientos pendientes, sin reiniciar las fechas.

La reserva y las operaciones que habilitan una bicicleta también deben comprobar la vigencia de la revisión; no basta con esperar a la siguiente ejecución periódica para impedir una nueva contratación incompatible.

La frecuencia de ejecución y las fechas de revisión son conceptos distintos. Comprobar diariamente no significa que cada bicicleta deba revisarse diariamente. Los intervalos se expresan en meses calendario según la condición aprobada. La frecuencia de la tarea, la zona horaria y el comportamiento de fin de mes se concretarán con las reglas y pruebas de la implementación.

## 4. Condiciones de aplicación aprobadas

Estado del bloque siguiente: condiciones aprobadas expresamente el 28 de octubre de 2026 mediante «apruebo esas condiciones». Antes de formularlas se releyeron el Word y el PDF originales y se contrastaron RN-ALQ-03, RN-BIC-01, RN-MAN-02 y RN-MAN-03. La aprobación abarca los comportamientos, las referencias iniciales y la configuración administrativa indicados a continuación; no equivale a implementación ni fija los intervalos numéricos.

### Tratamiento aprobado según la situación de la bicicleta

| Situación al vencer la preventiva | Comportamiento aprobado |
| --- | --- |
| DISPONIBLE y sin orden abierta | Pasar a MANTENIMIENTO y crear una orden PREVENTIVO en CREADA, sin asignación inicial obligatoria |
| EN_USO | No cerrar ni modificar el viaje por calendario. Mantener la necesidad preventiva pendiente y, al confirmar la devolución válida, dejarla MANTENIMIENTO en vez de ofrecerla a otro cliente |
| RESERVADA antes del vencimiento de la preventiva | Respetar la contratación ya aceptada hasta su límite original de 15 minutos, con sus controles de pago y retiro. Si se retira a tiempo, aplicar la preventiva al devolver; si se cancela o vence sin retiro, pasar a mantenimiento al liberarse la reserva |
| Otra solicitud intenta contratar después del vencimiento preventivo | No crear una nueva reserva incompatible, aunque la tarea periódica todavía no haya actualizado el estado visible |
| Tiene un PREVENTIVO abierto | Conservarlo; no crear otra orden por repetir la comprobación |
| Tiene un CORRECTIVO abierto y además vence la preventiva | Conservar el correctivo y la necesidad preventiva, sin abrir una segunda orden ni cambiar su tipo. Al cerrarse el correctivo, generar la preventiva si sigue pendiente y antes de habilitar el alquiler |
| INACTIVA | Conservar la inactivación. Una futura habilitación debe verificar la preventiva y derivar a mantenimiento si corresponde, sin ofrecerla entre ambas operaciones |
| DE_BAJA | No generar una revisión de retorno ni reactivar la bicicleta por calendario |

La deferencia a un viaje o reserva existente solo trata el vencimiento del calendario. No constituye una política para ignorar averías, pérdidas o accidentes. Los reportes de falla conservan el bloqueo correctivo y los controles aprobados. La intervención operativa antes del retiro se regula en RN-BIC-02 y el circuito mínimo durante el viaje en RN-INC-01, sin deducirlos de la regla de calendario.

Si la devolución informa una falla y la preventiva también está pendiente, se atiende primero el correctivo conforme a RN-MAN-03, conservando la necesidad de preventiva. Si ya existe una orden, se aplica la regla de no duplicarla ni cambiar automáticamente su tipo. ADMIN resuelve una clasificación que no corresponda mediante el recorrido autorizado, sin borrar los reportes.

No se autoriza la vuelta al servicio mientras exista una revisión obligatoria pendiente. El cierre de un correctivo no equivale a completar una preventiva. Cerrar o cancelar cualquier orden tampoco devuelve automáticamente la bicicleta a DISPONIBLE: se conserva la habilitación posterior por ADMIN de RN-MAN-02.

### Referencia inicial y configuración aprobadas

El próximo vencimiento se calcula desde la última preventiva finalizada satisfactoriamente. Para una bicicleta nueva sin esa historia, se utiliza su fecha real de alta en la flota. Una unidad antigua sin historial ni fecha fiable requiere una revisión preventiva inicial antes de volver a alquilarse; no se inventa una fecha de revisión para habilitarla.

Los intervalos son configurados únicamente por ADMIN, como enteros positivos en meses calendario para cada tipo. Los valores de uno, dos y tres meses del ejemplo no quedan fijados como política definitiva. Antes de operar deben definirse los valores iniciales; eso puede resolverse con los datos del DER y las pruebas sin agregar estados nuevos.

Crear, pausar, cancelar o terminar sin éxito una orden no reinicia el calendario. Los cambios de intervalo no borran inspecciones históricas, no cancelan automáticamente órdenes abiertas ni alteran los viajes o reservas ya aceptados.

### Detalles técnicos para concretar al implementar

Se propone calcular el vencimiento por fecha, usando la zona horaria configurada del sistema. Al sumar meses, si el día no existe en el mes de destino, se propone usar el último día de ese mes. La zona, el límite temporal exacto y sus pruebas deben documentarse antes de implementar; no se presentan como decisiones técnicas ya verificadas.

Como diseño técnico se propone registrar el cambio de intervalo con actor, fecha y valor anterior/nuevo y calcular el próximo vencimiento desde la referencia válida de cada unidad. Si el nuevo cálculo indica una revisión vencida, se debe respetar la tabla aprobada. Ampliar un intervalo no libera por sí solo una bicicleta: sus restricciones y órdenes siguen sujetas al recorrido autorizado. La representación de estos datos se consolida en el DER.

### Criterios de aceptación de las condiciones aprobadas

Estos escenarios documentan cómo comprobar las condiciones aprobadas. Son pruebas especificadas, no ejecutadas:

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-MAN-04-01 | Vence una preventiva para una unidad disponible | Bicicleta MANTENIMIENTO y una sola orden PREVENTIVO en CREADA |
| CP-MAN-04-02 | Vence durante un viaje | El viaje conserva sus fechas y propietario; la preventiva se atiende al devolver sin seguir cobrando por esperar al técnico |
| CP-MAN-04-03 | Vence durante una reserva ya aceptada | Se conserva el plazo original; devolución, cancelación o vencimiento derivan a mantenimiento cuando corresponde |
| CP-MAN-04-04 | Nueva contratación después del vencimiento preventivo, antes de la tarea periódica | El backend impide crearla y no depende solo del estado mostrado por el frontend |
| CP-MAN-04-05 | Hay un correctivo abierto y vence la preventiva | No hay dos órdenes abiertas; la necesidad preventiva no desaparece y se atiende antes de habilitar |
| CP-MAN-04-06 | Unidad antigua sin historial ni referencia fiable | No se crea historia ficticia; requiere revisión inicial para alquilarse |
| CP-MAN-04-07 | Cliente o técnico intenta cambiar intervalos | El backend rechaza la operación por falta de permiso administrativo |
| CP-MAN-04-08 | Se repite la tarea o se reinicia la aplicación | No se reinician fechas ni se duplican órdenes; se detectan los vencimientos pendientes |
| CP-MAN-04-09 | Se cambia un intervalo con una orden abierta | Se conserva la orden, su historia y los controles de habilitación |
| CP-MAN-04-10 | La unidad está INACTIVA o DE_BAJA | La tarea no elimina la restricción administrativa ni la vuelve disponible |

La aplicación de esta regla a devoluciones sin falla o a liberaciones de reservas es una excepción ahora aprobada expresamente al retorno normal a DISPONIBLE de RN-ALQ-02, RN-ALQ-03 y RN-BIC-01. También completa RN-ALQ-05 y RN-ALQ-09: se libera la exclusividad o termina el uso según corresponda, pero una preventiva vencida impide ofrecer la bicicleta nuevamente. No se agrega costo al cliente por la espera de mantenimiento.

## 5. Decisiones abiertas

La incorporación del automatismo y las condiciones de aplicación de la sección 4 ya están aprobadas. Siguen pendientes los valores numéricos iniciales por tipo, el diseño físico y los detalles técnicos de cálculo y ejecución identificados en este documento. No impiden preparar el DER, pero deben concretarse antes de operar el requisito. No se asumen como definitivos los ejemplos del usuario.

La cancelación operativa antes del retiro se aprobó en RN-BIC-02 y las incidencias durante el viaje en [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md), incluida su precisión económica adicional, ya aprobada. Diferir una revisión por calendario no aprueba ignorar una avería ni otorga permisos nuevos por extensión.

No se modificaron código, base de datos ni el DER original. No se ejecutaron pruebas del requisito. Esta definición no certifica la seguridad mecánica de una unidad ni sustituye las indicaciones de revisión que correspondan a bicicletas reales.
