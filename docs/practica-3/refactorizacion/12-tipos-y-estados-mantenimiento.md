# RN-MAN-01: tipos y estados de la orden de mantenimiento

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada la incorporación del catálogo TIPO_MANTENIMIENTO y de los cinco estados de ORDEN_MANTENIMIENTO. No implementados todavía en Java ni en una base de datos. Los permisos y las transiciones manuales se aprobaron posteriormente en RN-MAN-02; las decisiones expresamente pendientes siguen separadas.

## 1. Separación aprobada

Cada orden debe identificar por separado el tipo de trabajo y su estado de avance. No se elimina la distinción entre mantenimiento preventivo y correctivo.

- El tipo expresa por qué se realiza la intervención.
- El estado expresa en qué punto está el trabajo.
- La condición operativa de la bicicleta expresa si puede ofrecerse para alquiler, de acuerdo con las reglas de disponibilidad y revisión.

El mantenimiento correctivo puede estar creado, en proceso o pausado sin dejar de ser correctivo. No se representa cada combinación de tipo y avance mediante un estado diferente de la bicicleta.

## 2. Catálogo TIPO_MANTENIMIENTO aprobado

| Campo | Función |
| --- | --- |
| id | Clave primaria del tipo |
| codigo | Código obligatorio y único |
| descripcion | Descripción del tipo de trabajo, sin repetirla en cada orden |

Registros iniciales:

| Código | Significado |
| --- | --- |
| PREVENTIVO | Revisión o intervención de rutina para prevenir fallas |
| CORRECTIVO | Atención o reparación de una falla reportada o detectada, con el diagnóstico técnico que corresponda |

Una orden correctiva por reporte no supone que se haya comprobado la avería ni atribuido su responsabilidad a un cliente. La revisión conserva esa distinción conforme a RN-ALQ-06.

La incorporación del catálogo no exige desarrollar una pantalla de ABM para esta entrega: se prevé cargar los dos registros iniciales y seleccionarlos al crear una orden. No se aprueba con ello la creación libre de nuevos tipos desde un formulario público.

## 3. Relación incorporada al modelo de trabajo

TIPO_MANTENIMIENTO tiene una relación de uno a muchos con ORDEN_MANTENIMIENTO. Cada nueva orden identifica un tipo válido mediante `tipo_mantenimiento_id`.

ESTADO_ORDEN_MANTENIMIENTO conserva una relación independiente de uno a muchos con ORDEN_MANTENIMIENTO, mediante `estado_orden_mantenimiento_id`.

Se incorporó el [fragmento del modelo de mantenimiento](modelo-mantenimiento-catalogos.mmd) con esas relaciones. Es un fragmento, no el DER completo ni una migración ejecutada. No elimina de la orden sus relaciones con bicicleta/técnico ni los demás atributos del DER original.

Agregar este catálogo al DER v4 original supone una entidad adicional. La cantidad definitiva del modelo completo se determinará con los demás ajustes, no forzando el número 21.

## 4. Estados de orden aprobados

| Estado | Significado |
| --- | --- |
| CREADA | Orden registrada; el trabajo técnico todavía no comenzó |
| EN_PROCESO | Trabajo técnico iniciado y en ejecución |
| PAUSADA | Trabajo interrumpido temporalmente, sin que la orden esté cerrada |
| FINALIZADA | Trabajo terminado, con su resultado registrado |
| CANCELADA | Orden invalidada, conservando su motivo y trazabilidad |

Ejemplos: una revisión de rutina puede tener tipo PREVENTIVO y estado EN_PROCESO; una reparación puede tener tipo CORRECTIVO y estado PAUSADA mientras espera repuestos.

Los nombres y significados están aprobados. La recepción de esta aprobación no habilita automáticamente todas las combinaciones de transición ni todos los roles para ejecutarlas.

## 5. Coherencia con la bicicleta

Las bicicletas con fallas reportadas siguen fuera de alquiler para revisión según [RN-ALQ-06](09-devolucion-demora-y-fallas.md). La creación o cancelación de una orden no debe ignorar esa restricción.

Finalizar o cancelar una orden no demuestra por sí solo que una bicicleta está apta y disponible. La vuelta al servicio debe respetar la revisión, el resultado técnico, la ubicación física y los controles de disponibilidad.

Esta aprobación fija el tipo y los estados de la orden. Los seis nombres del catálogo operativo de BICICLETA se aprobaron posteriormente, de forma explícita, en [RN-BIC-01](13-estados-operativos-bicicleta.md).

## 6. Controles y criterios de aceptación

Estos criterios no se ejecutaron todavía:

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-MAN-01-01 | Carga de los tipos iniciales | PREVENTIVO y CORRECTIVO existen con códigos únicos |
| CP-MAN-01-02 | Nueva orden con tipo seleccionado | La orden referencia un tipo válido mediante su FK y no duplica la descripción del catálogo |
| CP-MAN-01-03 | Cambia el avance de una orden correctiva | Conserva su tipo CORRECTIVO y registra el nuevo estado de avance |
| CP-MAN-01-04 | Consulta de una orden | Se identifican por separado el tipo y el estado |
| CP-MAN-01-05 | Orden cancelada | Se conserva la orden y su historia; no se utiliza un borrado para representar la cancelación |
| CP-MAN-01-06 | Termina o se cancela una orden para una bicicleta todavía no habilitada | No se ofrece automáticamente por el solo hecho de cerrar esa orden |

## 7. Pendientes para completar el flujo

El 28 de octubre de 2026 el usuario aprobó el reparto de permisos manuales y las condiciones de vuelta al servicio, registrados en [RN-MAN-02](17-permisos-y-transiciones-mantenimiento.md) y en la sección 7 del [diccionario de trabajo](08-diccionario-estados-propuesto.md). Esa decisión completa quién crea, asigna, inicia, pausa, finaliza y cancela, además de reservar la habilitación posterior a ADMIN con revisión técnica favorable. No constituye una implementación.

La generación correctiva desde una devolución con falla, el máximo de una orden abierta y la asignación inicial opcional se aprobaron después en [RN-MAN-03](18-generacion-y-organizacion-ordenes.md).

- Valores numéricos iniciales y detalles físicos/técnicos del preventivo por calendario de [RN-MAN-04](19-propuesta-preventivo-por-calendario.md). La referencia inicial y los casos de reservas, viajes y otras órdenes abiertas ya fueron aprobados expresamente.
- La cancelación administrativa antes del retiro se aprobó en [RN-BIC-02](20-propuesta-administracion-y-excepciones-bicicletas.md) y el circuito mínimo de pérdida/accidente en [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md). Se conservan revisión técnica, historia y controles de una sola orden abierta; falta su consolidación física; la precisión económica de RN-INC-01 ya fue aprobada.
- Definición física y validaciones de datos/fechas, respetando CREADA sin técnico y las condiciones de permisos y aptitud ya aprobadas.

No se modificó la base de datos, código Java ni el DER o Word originales. La consolidación posterior de estos tipos y estados ya figura en el [DER v5 de trabajo](der-v5-propuesto.mmd); el fragmento conserva su carácter ilustrativo, no es un segundo esquema completo. La revisión detallada de campos e historia está en el [documento 27](27-revision-ordenes-e-historial-mantenimiento.md), que separa las reglas aprobadas de sus nuevas propuestas.
