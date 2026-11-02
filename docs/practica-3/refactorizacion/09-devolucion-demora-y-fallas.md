# RN-ALQ-06: devolución, demora y fallas reportadas

Fecha de aprobación: 25 de octubre de 2026.

Estado: regla aprobada para implementar. No implementada todavía en la nueva versión. Los criterios de aceptación están especificados, no ejecutados.

## 1. Regla aprobada

Se conserva DEVUELTO como estado de uso del detalle cuando se confirma una devolución válida. Además se distinguen dos condiciones independientes:

- Tiempo de devolución: dentro del tiempo estimado o con demora.
- Condición informada: sin falla reportada o con falla reportada.

Una devolución puede presentar ambas condiciones a la vez: demora y falla reportada. El historial debe permitir reconocerlas, no mostrar solamente un estado genérico que oculte esa información.

## 2. Tiempo y costo

La demora se determina comparando las fechas estimada y real de devolución del detalle. Si la fecha real supera la estimada, existe demora; si es igual o anterior, la devolución está dentro del tiempo estimado.

Ambas fechas deben conservarse separadas. La demora no genera una multa ni cambia la tarifa o cotización contratadas: se cobra el uso real conforme a RN-ALQ-01 y RN-ALQ-04.

Al confirmar la devolución válida termina el contador de uso de esa bicicleta, incluso cuando se reporta una falla. No permanece alquilada ni sigue acumulando costo mientras espera al técnico.

## 3. Falla reportada y disponibilidad

Cuando se informa una falla al devolver:

- Se registra el reporte asociado a la devolución y a la bicicleta, conservando su descripción, autor y fecha según los datos disponibles y las validaciones que se definan.
- El detalle queda DEVUELTO y conserva su costo real de uso.
- La bicicleta queda fuera de alquiler, pendiente de revisión técnica, en lugar de ofrecerse como disponible.
- La bicicleta está físicamente en la estación de devolución y sigue ocupando un lugar de su capacidad.
- El reporte no acredita por sí solo la existencia técnica de la avería ni la responsabilidad del cliente.
- No se genera un cargo por daños de forma automática.

SIN_FALLA_REPORTADA significa que no se informó una falla en ese recorrido. No es una certificación técnica de que la bicicleta esté libre de cualquier defecto.

La reincorporación al alquiler requiere que la revisión determine su aptitud y se cumplan los controles del módulo de mantenimiento. Recibir o cerrar un reporte no demuestra por sí solo que la bicicleta está lista para volver a ofrecerse.

## 4. Presentación del historial

| Tiempo | Condición informada | Presentación prevista |
| --- | --- | --- |
| Dentro del estimado | Sin falla reportada | Devuelta normalmente |
| Con demora | Sin falla reportada | Devuelta con demora |
| Dentro del estimado | Falla reportada | Devuelta con falla reportada |
| Con demora | Falla reportada | Devuelta con demora y falla reportada |

Estas presentaciones acompañan al estado de uso DEVUELTO. No son cuatro estados mutuamente excluyentes del ciclo del alquiler.

## 5. Relación con las otras reglas

Esta regla completa la devolución normal de [RN-ALQ-02](03-alquiler-con-varias-bicicletas.md): sin reporte de falla ni otro impedimento, la unidad devuelta queda disponible; con reporte, termina el uso pero permanece fuera de alquiler para revisión. La ampliación aprobada en [RN-MAN-04](19-propuesta-preventivo-por-calendario.md) también exige MANTENIMIENTO si venció la preventiva, aun sin falla reportada. Si coinciden falla y preventiva pendiente, se conserva la prioridad correctiva y una sola orden abierta; la necesidad preventiva no se pierde.

La liquidación sigue siendo conjunta al cerrar el uso de todas las unidades y resolver las pendientes de retiro. La revisión técnica no mantiene abierto el uso de una bicicleta ya devuelta ni obliga a esperar su reparación para calcular ese uso real.

El reporte tampoco aprueba descuentos, compensaciones por avería, responsabilidad o cobros por daños. Esas situaciones requerirían reglas y permisos específicos, sin sobrescribir los movimientos financieros originales.

## 6. Consecuencias para el DER y las operaciones

- Conservar fecha estimada y fecha real para obtener la demora, sin depender de un estado combinado.
- Registrar por separado el reporte de falla y el estado de uso del detalle. Su representación física definitiva se decidirá en el DER.
- Diferenciar el detalle DEVUELTO del estado operativo de la bicicleta que espera revisión. El nombre concreto de ese estado operativo forma parte de la validación del diccionario.
- Asociar correctamente el reporte a su bicicleta y devolución. Una petición repetida no debe borrar una falla ya registrada ni crear operaciones duplicadas.
- Cambiar ubicación, terminar el uso, fijar el costo y bloquear la disponibilidad cuando corresponda debe hacerse de forma coherente en el backend, con historial y controles de concurrencia.
- Mantener la autorización de propietario o administrador habilitado y la validación de capacidad antes de dar por exitosa la devolución.

La aprobación del uso de DEVUELTO y de estas condiciones no implica aprobar por completo los demás nombres y transiciones del documento 08, que se revisan por bloques.

## 7. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-06-01 | Devolución válida dentro del tiempo estimado y sin falla reportada | Detalle DEVUELTO, presentación normal y bicicleta disponible en su estación |
| CP-ALQ-06-02 | Devolución válida posterior al estimado y sin falla reportada | Detalle DEVUELTO, indicador de demora y costo por uso real sin multa |
| CP-ALQ-06-03 | Devolución válida dentro del estimado y con falla reportada | Se termina el uso y la bicicleta queda fuera de alquiler para revisión |
| CP-ALQ-06-04 | Devolución válida con demora y falla reportada | Se identifican ambas condiciones, sin perder ninguna ni cobrar una multa automática |
| CP-ALQ-06-05 | La bicicleta devuelta espera revisión o reparación | Su costo de uso no sigue aumentando y continúa ocupando el lugar físico de devolución |
| CP-ALQ-06-06 | Se registra un reporte del cliente | No se genera automáticamente un cargo por daños ni una atribución de responsabilidad |
| CP-ALQ-06-07 | Se repite una petición de devolución con reporte | No se reinicia el uso, no se duplica la liquidación y no se elimina el reporte previo por los valores de un reintento |
| CP-ALQ-06-08 | La estación está llena o el actor no está autorizado | No se registra una devolución exitosa ni se aplican sus efectos como si la bicicleta hubiera sido recibida |

## 8. Pendientes que no se consideran aprobados

La asignación manual, los permisos, el resultado técnico y la habilitación posterior se aprobaron en [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md). RN-MAN-03 aprueba el correctivo desde devolución, una orden abierta y CREADA sin técnico. RN-MAN-04 incorpora el preventivo por calendario, con intervalos numéricos y detalles técnicos pendientes. [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md) incorpora después el reporte y cierre excepcional durante el viaje; su sección 8 también está aprobada: conserva la devolución real y el fin del tiempo, pero la liquidación espera las revisiones pendientes que puedan cambiar el importe. La precisión temporal y los redondeos se cerrarán con la política general de cálculo.

No se modificó código, base de datos ni el diccionario Word original. No se realizaron pagos ni reembolsos reales.
