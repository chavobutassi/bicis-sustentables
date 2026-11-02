# RN-MAN-02 Permisos de mantenimiento y vuelta al servicio

Fecha de aprobación: 28 de octubre de 2026.

Estado: reparto de permisos y habilitación administrativa posterior aprobados expresamente por el usuario. No implementados en Java ni en una base de datos. Los criterios de aceptación están especificados, no ejecutados.

## 1. Alcance aprobado

ADMIN gestiona las órdenes y sus asignaciones. TECNICO realiza y registra el trabajo de las órdenes que tiene asignadas. El cliente conserva la posibilidad de reportar una falla al devolver, pero no administra órdenes de mantenimiento.

La habilitación posterior por ADMIN es un control adicional aprobado después de revisar el Word y el PDF originales; no se presenta como una exigencia literal de esos documentos. La propuesta de referencia se conserva actualizada en la sección 7 del [diccionario de trabajo](08-diccionario-estados-propuesto.md).

Esta regla completa los tipos y cinco estados de orden aprobados en [RN-MAN-01](12-tipos-y-estados-mantenimiento.md) y los controles operativos de [RN-BIC-01](13-estados-operativos-bicicleta.md). Los originales y el DER v4 permanecen intactos.

## 2. Matriz de permisos aprobada

| Acción | Actor y condiciones |
| --- | --- |
| Crear una orden de tipo PREVENTIVO o CORRECTIVO | ADMIN; la orden comienza en CREADA |
| Asignar o cambiar técnico | ADMIN; la orden debe estar CREADA o PAUSADA y el técnico elegido debe estar activo y tener rol TECNICO |
| Consultar órdenes e historial | ADMIN consulta todas; TECNICO consulta las asignadas a él |
| Iniciar o reanudar el trabajo | TECNICO asignado a la orden |
| Registrar diagnóstico, trabajos y costos | TECNICO asignado, durante el trabajo |
| Pausar el trabajo | TECNICO asignado, indicando un motivo |
| Finalizar la orden | TECNICO asignado, registrando el trabajo y el resultado técnico, incluida la aptitud de la bicicleta |
| Cancelar una orden abierta | ADMIN, indicando un motivo y conservando la orden y su historia |
| Autorizar la vuelta al servicio después del mantenimiento | ADMIN, con revisión técnica favorable y validación de ubicación y restricciones |

Ser ADMIN no sustituye el rol TECNICO ni la asignación para ejecutar trabajo técnico. Si una cuenta tiene ambos roles, cada operación debe satisfacer igualmente sus controles. La asignación, los roles y el estado se verifican en el backend, no solo mediante los botones visibles.

## 3. Transiciones del trabajo manual

| Estado de origen | Acción | Estado de destino | Actor |
| --- | --- | --- | --- |
| CREADA | Iniciar | EN_PROCESO | TECNICO asignado |
| PAUSADA | Reanudar | EN_PROCESO | TECNICO asignado |
| EN_PROCESO | Pausar con motivo | PAUSADA | TECNICO asignado |
| EN_PROCESO | Finalizar con resultado técnico | FINALIZADA | TECNICO asignado |
| CREADA, EN_PROCESO o PAUSADA | Cancelar con motivo | CANCELADA | ADMIN |

Para cambiar de técnico durante EN_PROCESO, primero debe pausarse el trabajo. La reasignación no borra las intervenciones anteriores ni cambia la autoría de los registros existentes.

Las órdenes finalizadas o canceladas no son órdenes abiertas sobre las que se repitan esos cambios del recorrido normal. Su historia debe conservarse. Una eventual corrección excepcional de registros cerrados no se habilita mediante un cambio libre de estado.

## 4. Cierre técnico y habilitación administrativa

El técnico registra si la bicicleta quedó apta o no apta. Finalizar la orden no cambia automáticamente la bicicleta a DISPONIBLE. Cancelar una orden tampoco acredita que se haya reparado o revisado favorablemente.

Después del cierre técnico, ADMIN puede autorizar la transición de MANTENIMIENTO a DISPONIBLE mediante una operación específica. El backend debe comprobar:

- Revisión técnica favorable vigente para las fallas o impedimentos que motivaron la intervención.
- Ausencia de fallas sin resolver y de órdenes abiertas que impidan alquilar la unidad.
- Ubicación física registrada en una estación activa válida.
- Ausencia de otras restricciones incompatibles con la vuelta al servicio.

ADMIN no puede ignorar un resultado desfavorable ni reutilizar una revisión favorable anterior a una falla nueva. Si no está apta, la bicicleta permanece fuera de alquiler.

La habilitación no equivale a un traslado físico ni libera capacidad por sí sola. No permite terminar artificialmente un viaje EN_USO, intervenir una reserva sin su recorrido autorizado o revertir una baja definitiva. Los permisos administrativos de inactivación, reactivación y baja se aprobaron posteriormente en RN-BIC-02; no se deducen de esta habilitación técnica ni resuelven pérdidas o accidentes.

## 5. Trazabilidad y criterios de aceptación

Las acciones conservan responsable real, fecha y evento. Pausa y cancelación conservan además su motivo obligatorio; los trabajos, resultados y asignaciones anteriores no se borran para representar una nueva operación.

Los siguientes casos son especificaciones para pruebas futuras, no evidencia de funcionamiento actual:

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-MAN-02-01 | Un técnico intenta iniciar o finalizar una orden no asignada a él | El backend rechaza la operación |
| CP-MAN-02-02 | Un cliente intenta consultar el listado técnico o cambiar una orden por HTTP | Acceso rechazado; su reporte de falla no concede permisos técnicos |
| CP-MAN-02-03 | ADMIN sin rol técnico ni asignación intenta finalizar técnicamente | No sustituye al técnico asignado |
| CP-MAN-02-04 | ADMIN intenta reasignar una orden EN_PROCESO | Debe pausarse antes de cambiar la asignación |
| CP-MAN-02-05 | Pausa o cancelación sin motivo | Se rechaza sin aplicar parcialmente el cambio |
| CP-MAN-02-06 | El técnico finaliza con resultado no apta | Se conserva el resultado y la bicicleta no queda disponible |
| CP-MAN-02-07 | ADMIN solicita habilitar con otra orden bloqueante, falla pendiente o ubicación inválida | Se rechaza la habilitación |
| CP-MAN-02-08 | ADMIN habilita con revisión favorable vigente y sin impedimentos | La bicicleta pasa de MANTENIMIENTO a DISPONIBLE y se registra la autorización |
| CP-MAN-02-09 | Se cancela una orden | Se conserva la historia y no se habilita automáticamente la bicicleta |
| CP-MAN-02-10 | Se repite una habilitación o aparece una falla nueva | No se duplica la transición ni se ignora la nueva restricción |

## 6. Decisiones que continúan pendientes

- La creación automática desde reportes, el máximo de una orden abierta y la asignación inicial opcional se aprobaron por separado en [RN-MAN-03](18-generacion-y-organizacion-ordenes.md). No se deducen del solo reparto de permisos.
- Detalle de datos y mapeo físico de la orden en el DER, respetando que puede estar CREADA sin técnico y que iniciar o reanudar exige asignación válida.
- Los intervalos numéricos y detalles físicos/técnicos del preventivo por calendario de [RN-MAN-04](19-propuesta-preventivo-por-calendario.md). Sus condiciones de aplicación y la configuración de intervalos solo por ADMIN ya fueron aprobadas, sin otorgar por extensión otros permisos de intervención sobre reservas.
- La cancelación administrativa antes del retiro se aprobó por separado en RN-BIC-02 y el circuito mínimo durante el viaje en [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md). El cierre administrativo no acredita aptitud técnica ni permite al técnico actuar sobre órdenes ajenas. La precisión económica de ese circuito también fue aprobada; queda su diseño físico. No se espera una reparación técnica para fijar un corte ya validado.
- La inactivación, reactivación administrativa ajena al mantenimiento y baja definitiva se aprobaron posteriormente en [RN-BIC-02](20-propuesta-administracion-y-excepciones-bicicletas.md). No se deducen del solo permiso de habilitar después de una revisión técnica.

No se amplían permisos a esas excepciones por aprobar esta matriz. No se modificó código ni base de datos, no se iniciaron aplicaciones ni se ejecutaron pruebas de integración.
