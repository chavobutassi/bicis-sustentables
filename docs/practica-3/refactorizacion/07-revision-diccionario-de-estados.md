# Revisión del diccionario de estados original

Fecha: 25 de octubre de 2026.

Estado: revisión de una propuesta aportada por el usuario. No es una nueva regla aprobada ni un diccionario definitivo para implementar. Las correcciones obligatorias derivadas de RN-ALQ-01 a RN-ALQ-05 se distinguen de las simplificaciones y excepciones todavía pendientes.

## Fuente y alcance

Se revisó completo [Diccionario de Estados.docx](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>), de tres páginas en la revisión con Word. El original se abrió en modo de solo lectura y no se modificó.

El documento organiza estados de BICICLETA, ALQUILER_DETALLE, ALQUILER, ORDEN_MANTENIMIENTO y PAGO. También enumera géneros y los roles CLIENTE, ADMIN y TECNICO. Es una base pertinente para construir la tabla de estados y transiciones que acompañará al DER revisado.

Las definiciones del documento son propuestas de diseño. Su recepción no aprueba automáticamente multas, débitos, cierres forzosos, control físico del candado ni funcionalidades de incidencias que no se hayan acordado.

## Cambios necesarios por reglas ya aprobadas

| Definición original | Diferencia con lo acordado | Corrección necesaria |
| --- | --- | --- |
| DEVUELTA_CON_RETRASO genera multa | RN-ALQ-01 establece tiempo real a la misma tarifa, sin multa | Eliminar la multa. Determinar si el retraso necesita un estado propio o basta con las fechas |
| RESERVADO supone una tarjeta preaprobada | Se acordó un anticipo efectivamente pagado antes del retiro y una reserva desde la confirmación | Separar reserva, resultado del pago y retiro; no describir el anticipo como simple preaprobación |
| PENDIENTE_RETIRO supone que el usuario ya pagó | La exclusividad empieza antes de pagar y también necesita una representación válida | Definir explícitamente la fase reservada pendiente de pago y el paso a retiro autorizado |
| EN_CURSO depende de haber escaneado un QR | El inicio del uso requiere retiro válido confirmado por el backend | Un escaneo aislado no debe activar el viaje sin validar propiedad, pago, reserva y plazo |
| FINALIZADO exige que se haya cobrado todo y no exista deuda | El uso termina con las devoluciones y el cierre de pendientes, aunque continúe la gestión de dinero | Separar el estado del uso del estado financiero y de los movimientos pendientes |
| CON_DEUDA solo aparece al rechazarse el débito de una diferencia o multa | No hay débito adicional automático ni multa. La diferencia puede existir antes de un intento de pago | La deuda corresponde al saldo determinado al liquidar, y se cancela con pagos adicionales confirmados |
| REEMBOLSADO reúne devolución total y parcial del dinero | Se acordó conservar pago original, importes y estado de cada reembolso, incluso cuando está pendiente o falla | Representar el reembolso con sus propios datos/estado y distinguir lo solicitado de lo confirmado |

En la bicicleta debe expresarse cómo se aplica la exclusividad de la reserva: mediante un estado reservado o una relación/regla de reserva equivalente. No es correcto ofrecer una unidad a otros solo porque está físicamente en la estación. La decisión de representación se tomará al preparar la tabla, sin imponer ahora otro catálogo o tabla.

La cancelación voluntaria y el vencimiento de 15 minutos del documento son compatibles con lo aprobado. Deben conservar sus causas distintas y respetar que solo se liberan unidades no retiradas. Si CANCELADO es un estado genérico y las causas se guardan aparte, o si se mantienen códigos separados, debe decidirse explícitamente.

## Propuestas adicionales que todavía no se aprueban

### Falta de devolución durante 24 horas

RETENIDO_SISTEMA introduce un cierre forzoso después de 24 horas y no está aprobado. La revisión inicial dejó pendientes la pérdida y su cierre económico. Posteriormente [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md) incorporó reporte, validación de ADMIN, corte de uso y cierre excepcional sin devolución ficticia, EXTRAVIADA y recuperación. No convierte una demora en pérdida ni genera indemnizaciones automáticas. La precisión económica adicional de su sección 8 fue confirmada posteriormente: se devuelve sin seguir contando tiempo y el ajuste espera la revisión del importe.

Una bicicleta no devuelta no puede liberarse como si se hubiera recibido físicamente. Tampoco debe declararse extraviada automáticamente solo por superar el tiempo estimado sin una regla expresa.

### Devolución con falla

En la revisión inicial, DEVUELTA_CON_FALLA y su cambio automático a REPARACION_PENDIENTE incorporaban un recorrido de incidencias no acordado. Posteriormente el usuario aprobó [RN-ALQ-06](09-devolucion-demora-y-fallas.md): DEVUELTO acompañado de condiciones independientes de demora y falla reportada, y bicicleta fuera de alquiler para revisión sin mantener activo su uso.

El nombre general MANTENIMIENTO se aprobó para la bicicleta en RN-BIC-01. La asignación manual, los permisos técnicos, el resultado y la habilitación posterior se aprobaron en [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md). La generación correctiva desde devolución, una sola orden abierta y CREADA sin técnico se aprobaron en [RN-MAN-03](18-generacion-y-organizacion-ordenes.md). El preventivo periódico se aprobó por separado en [RN-MAN-04](19-propuesta-preventivo-por-calendario.md) y el circuito mínimo durante el viaje, en RN-INC-01. Esto no aprueba automáticamente el mecanismo completo del Word original.

### Pago y reembolso

El 28 de octubre de 2026 se aprobaron los cinco estados de pago y los cuatro de reembolso en [RN-PAG-01](14-estados-pago-y-reembolso.md). El pago conserva su importe e historia, y cada devolución de dinero se registra por separado y vinculada. Esto reemplaza el uso ambiguo de REEMBOLSADO del Word, que reunía una devolución parcial y una total sin distinguir su gestión.

Se releyeron el Word completo y el PDF de visión antes de registrar la aprobación. El flujo 11a del PDF y la descripción de CANCELADO en el Word vinculaban el rechazo inicial con la cancelación. Posteriormente el usuario aprobó [RN-PAG-02](15-reintentos-pago-durante-reserva.md): el rechazo no cancela la reserva ni modifica el estado de las bicicletas; permite nuevos intentos dentro del plazo original de 15 minutos, sin reiniciarlo. Esta decisión posterior sustituye expresamente ese comportamiento de los originales.

### Estados de bicicleta y trabajo de mantenimiento

Los estados de la orden CREADA, EN_PROCESO, PAUSADA, FINALIZADA y CANCELADA se aprobaron en [RN-MAN-01](12-tipos-y-estados-mantenimiento.md). El reparto de permisos, las transiciones manuales y la habilitación posterior se completaron mediante RN-MAN-02; el correctivo desde reporte, el máximo de una orden abierta y la asignación inicial opcional, mediante RN-MAN-03. RN-MAN-04 incorpora el preventivo por calendario y sus condiciones aprobadas. Continúan pendientes los intervalos numéricos y el detalle físico/técnico de datos, fechas y ejecución.

Los estados originales de la bicicleta MANTENIMIENTO_PREVENTIVO, MANTENIMIENTO_ACTIVO, REPARACION_PENDIENTE y REPARACION_ACTIVA mezclaban motivo del trabajo y avance de la orden. En RN-MAN-01 se aprobó preservar PREVENTIVO/CORRECTIVO en el catálogo TIPO_MANTENIMIENTO y referenciarlo desde la orden. El catálogo de seis estados operativos de bicicleta se aprobó posteriormente en [RN-BIC-01](13-estados-operativos-bicicleta.md), con MANTENIMIENTO como estado general de revisión/reparación.

Finalizar o cancelar una orden no demuestra por sí solo que la unidad está apta para alquilar: debe definirse el resultado técnico y cómo se autoriza su vuelta al servicio.

## Qué debe aportar el diccionario revisado

Para cada entidad/estado se documentarán significado, condiciones de entrada, estado de origen, evento que provoca el cambio, actor autorizado, estados de destino y efectos sobre disponibilidad, tiempos, costo e historial.

Además, habrá reglas comunes para las transiciones del conjunto:

- El primer retiro cambia la situación de la cabecera, pero no inicia el contador de las otras unidades.
- Una devolución parcial cierra únicamente el uso de su detalle.
- Cancelar o vencer el último detalle pendiente puede permitir la liquidación si todas las unidades usadas ya volvieron.
- Cada liquidación usa las tarifas y cotización congeladas y no se repite por una petición duplicada.
- El pago adicional o reembolso pendiente no reactiva un uso terminado ni libera una unidad no devuelta.

Los roles y géneros son catálogos, no estados del ciclo de un alquiler. El rol TECNICO debe reflejarse luego en la matriz de permisos y en la asignación de órdenes.

## Próximo paso

La propuesta unificada se preparó en el documento 08 y se aprobó por bloques, incluido el reparto de permisos de RN-MAN-02. El [índice de estado](00-indice-y-estado.md) identifica las decisiones confirmadas y los pendientes vigentes. Las excepciones de incidencias/hardware siguen distinguiéndose de lo aprobado, sin llevarlas silenciosamente al código.

Esta revisión no modificó el documento original, código, base de datos ni las reglas ya aprobadas.
