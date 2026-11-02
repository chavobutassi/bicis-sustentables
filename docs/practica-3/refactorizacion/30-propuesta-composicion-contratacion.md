# Composición de la contratación y cierres pendientes del DER

Fecha: 28 de octubre de 2026.

Estado: RN-ALQ-11 aprobada el 28 de octubre de 2026 e incorporada al DER lógico. El usuario confirmó origen común, traslado de la FK de retiro a la cabecera y selección fija; indicó un máximo acordado con su compañero de diez bicicletas, que sustituye la propuesta inicial de cinco. Se mantiene configurable. Java y la base de datos no se modificaron y los criterios de negocio todavía no se ejecutaron.

El DER lógico de trabajo tiene 28 entidades y 52 FK/relaciones. Su estructura principal está definida, pero todavía hay decisiones capaces de cambiar campos o relaciones. RN-PAG-05 ya excluyó los medios de pago guardados locales de esta versión; las asociaciones históricas y correlaciones de integración pendientes todavía requieren revisión antes de considerar definitivo el modelo.

## 1. Qué falta cerrar

| Bloque | Decisiones pendientes | Efecto sobre el modelo |
| --- | --- | --- |
| Composición del alquiler | Origen único, entre una y diez bicicletas y selección fija ya aprobados; faltan validaciones de duración estimada y no se fijó un límite acumulado por usuario | FK de estación trasladada a ALQUILER; máximo configurable sin tabla nueva; no confundir estos cierres con implementación |
| Dinero e integración | RN-PAG-03 y Checkout Pro externo de RN-PAG-05 ya aprobados; quedan API, correlaciones, confirmaciones y pruebas | No se incorporan entidades de medios guardados; la correspondencia entre checkout, orden y pagos debe comprobarse antes de cerrar el diseño físico |
| Revisión final de trazabilidad e incidencias | Asociaciones entre reportes, incidencias y órdenes; conservación de cambios sin transición de estado; identificación visible histórica | Comprobar si bastan las FK y la auditoría propuestas o hace falta una relación explícita adicional, sin reabrir los estados y reglas de incidencia aprobados |
| Diseño físico y transición | Tipos SQL, longitudes, escalas, nulabilidad, unicidad, índices, normalización de identificadores, bajas lógicas y tratamiento de datos antiguos | Convertir el dibujo lógico en un esquema implementable y preparar una migración reproducible, sin inventar datos históricos |

La fuente y frescura de la cotización, la reacción a su indisponibilidad, los intervalos preventivos iniciales y los detalles de calendario también deben concretarse. No exigen necesariamente rediseñar las entidades ya previstas ni impiden comenzar módulos independientes cuando su modelo esté cerrado. El alcance de QR/candado real o simulado sigue pendiente y puede afectar a su implementación y datos.

Las decisiones se siguen por D01 a D09 en [el mapa central](22-revision-del-der-y-mapa-de-cambios.md). No se promete que la futura integración esté terminada con la aprobación de este documento.

## 2. Contraste con las fuentes

Se revisaron el [PDF de visión](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/TP1/TP1 Prácticas III - Karim Homsi.pdf>), el [diccionario original](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/Diccionario de Estados.docx>) y el [DER v4](<D:/Karim/Downloads/Desarrollo de Software/3er Año/Prácticas 3/TP1 TURI/DER/DERv4.txt>), sin modificarlos.

El PDF contempla retiros y devoluciones en estaciones, desglose por unidad, pagos digitales, vinculación de métodos de pago y auditoría. No fija un máximo de bicicletas ni exige que un carrito abarque varias estaciones de retiro. El diccionario contempla cancelar una bicicleta de una reserva de tres antes del retiro; esa posibilidad ya se conserva en RN-ALQ-05. El DER v4 ubica estacion_retiro_id en ALQUILER_DETALLE, lo que permite representar distintos orígenes, pero por sí solo no obliga a admitirlos como operación del sistema.

La estación única y el límite son decisiones nuevas aprobadas para esta implementación. No se presentan como requisitos originales del profesor. La propuesta inicial de cinco se sustituyó por diez a pedido del usuario.

## 3. Regla aprobada RN-ALQ-11

### Un punto de retiro por alquiler

Todas las bicicletas seleccionadas en una contratación deben estar físicamente en la misma estación activa y ser aptas para reservarse al confirmar. La disponibilidad se vuelve a comprobar en el backend de forma transaccional; lo mostrado anteriormente en el carrito no constituye una reserva.

Se conserva el retiro independiente de cada unidad dentro de los 15 minutos originales. Cada una comienza a cobrar solo desde su propio retiro. Las devoluciones siguen siendo independientes y pueden realizarse en distintas estaciones con capacidad, sin obligación de regresar al origen.

Si se necesitan bicicletas de otro punto de retiro, se utiliza otra contratación, sujeta a las reglas vigentes de disponibilidad y deuda. No se aprueba con esto una cantidad ilimitada de contrataciones simultáneas por usuario; ese control de uso no queda resuelto por un límite por carrito.

Se trasladó estacion_retiro_id de ALQUILER_DETALLE a ALQUILER en el DER lógico, como FK obligatoria a ESTACION.id. La estación pertenece al conjunto, no a cada línea. No es UNIQUE, porque una estación conserva muchos alquileres históricos. La devolución real sigue en cada detalle y es opcional hasta la recepción.

El cambio reemplazó la relación de retiro ESTACION–ALQUILER_DETALLE por ESTACION–ALQUILER, sin sumar entidades o FK. RN-EST-01 sigue impidiendo la baja lógica cuando haya unidades pendientes de retiro: la futura consulta deberá obtener la estación a través de la cabecera. La referencia histórica no se modifica cuando luego se administra la estación o la bicicleta. La operación real y el control de esa condición todavía deben implementarse.

### Entre una y diez bicicletas al confirmar

El máximo inicial aprobado es de diez bicicletas por contratación, configurable en el servidor. Es una decisión del proyecto para permitir grupos, no una cifra extraída de los documentos ni una recomendación universal. No obliga a que todas las estaciones dispongan de diez unidades: solo pueden contratarse las bicicletas realmente aptas y disponibles en el origen elegido.

La selección debe contener al menos una unidad y no repetir la misma bicicleta. El máximo se comprueba en el backend, además de informar el límite en la interfaz. Una configuración del servicio basta para este valor; no se crea una tabla solo para almacenarlo.

Un cambio posterior del límite se aplica a nuevas confirmaciones y no invalida contratos aceptados. Tampoco autoriza a omitir la exclusividad entre contrataciones. Un límite por alquiler no sustituye una política de límites acumulados por usuario, si después se requiere.

### Selección fija después de confirmar

Antes de confirmar se pueden agregar o quitar unidades y modificar la estimación. Confirmado el alquiler y congelados sus datos económicos, no se agregan ni sustituyen bicicletas, no se cambia la estación contratada y no se modifica la duración estimada aceptada de sus detalles.

Esto no impide las cancelaciones parciales o totales ya aprobadas de unidades no retiradas, ni el vencimiento, ni la cancelación administrativa por causa operativa. Las unidades retiradas continúan su recorrido. Cancelar una selección no permite reemplazarla dentro del mismo contrato ni reiniciar los 15 minutos.

Para contratar otra selección se crea otra contratación con disponibilidad, tarifa, cotización y plazo propios, sin borrar o reactivar la anterior. Superar la duración estimada durante el uso sigue permitido y se cobra el tiempo real con la tarifa contratada, sin multas ni cierre automático por esa estimación.

La cancelación parcial mientras se procesa un anticipo se aprobó después en RN-PAG-03 del documento 31. No se sobrescriben importes de PAGO ni se presupone que el proveedor canceló o devolvió dinero. D03 conserva las correlaciones y los controles concretos de integración; no vuelve a someter a aprobación ese recorrido de negocio.

## 4. Ejemplo de aplicación

El cliente confirma tres bicicletas de Plaza Cien Años por una duración estimada. Una se retira a las 10:02 y otra a las 10:05. La tercera puede cancelarse antes de retirarla y dentro del plazo original; no se sustituye por otra en ese contrato. Las dos retiradas pueden devolverse en diferentes estaciones y sus tiempos se calculan por separado. El ajuste económico continúa siendo conjunto cuando corresponda liquidar, respetando las revisiones de incidencia pendientes.

## 5. Criterios de aceptación

Estos casos son especificaciones pendientes de implementación y ejecución, no pruebas superadas.

| Caso | Entrada o acción | Resultado esperado según RN-ALQ-11 |
| --- | --- | --- |
| CP-ALQ-11-01 | Selección con bicicletas de dos estaciones | Rechazo antes de confirmar, sin reservar parcialmente ni generar un cobro |
| CP-ALQ-11-02 | Selección vacía, repetida o superior al máximo configurado | Rechazo en el backend; no basta con impedirlo en el formulario |
| CP-ALQ-11-03 | Selección válida y disponibilidad suficiente al confirmar | Cabecera y todos sus detalles se registran de forma coherente con una estación de retiro común |
| CP-ALQ-11-04 | Otra operación toma una unidad antes de confirmar | Se rechaza la selección no disponible sin sustituir silenciosamente una bicicleta ni reservar solo parte del conjunto |
| CP-ALQ-11-05 | Intento de agregar, sustituir o cambiar la duración estimada después de confirmar | Rechazo sin cambiar los detalles, snapshots o importes de pagos existentes |
| CP-ALQ-11-06 | Cancelación de una unidad todavía no retirada dentro del plazo original | Se aplica RN-ALQ-05; las demás continúan y no se reinicia el plazo ni se rellena el lugar cancelado |
| CP-ALQ-11-07 | Devoluciones independientes en estaciones con espacio | Se conservan los tiempos y destinos por unidad, sin exigir el origen común como destino |
| CP-ALQ-11-08 | Se reduce el máximo configurado tras una confirmación válida | El contrato aceptado sigue siendo válido; la nueva configuración se aplica a nuevas confirmaciones |
| CP-ALQ-11-09 | Se confirman diez unidades distintas, aptas y disponibles en un mismo origen, con máximo diez | Selección válida si satisface los demás controles; se crea una cabecera con diez detalles, no diez contratos |
| CP-ALQ-11-10 | Se intenta confirmar once bicicletas con máximo diez | Rechazo sin reservar parcialmente ni generar un cobro |
| CP-ALQ-11-11 | El origen solo tiene siete bicicletas aptas disponibles | No se habilitan diez por el mero valor del máximo; una selección de siete puede confirmarse si satisface los demás controles |

## 6. Justificación y alternativa de varios orígenes

Permitir bicicletas de varias estaciones en un alquiler también sería una regla de negocio válida. Puede resultar útil si un grupo organiza retiros desde distintos puntos; no es incorrecto por definición ni lo impide la estructura cabecera/detalle. La elección de un origen común se recomienda para esta entrega porque facilita reunir al grupo, informar dónde retirar y coordinar el plazo original de quince minutos sin recorridos entre estaciones. No se afirma que sea la única solución posible ni que varias estaciones obliguen por sí solas a separar los pagos.

La contrapartida es una menor flexibilidad: un grupo que necesita bicicletas desde otro punto requiere otra contratación, sometida a los controles vigentes. El límite de diez no amplía automáticamente el plazo de retiro, no autoriza a reservar unidades que no estén disponibles y no introduce un límite acumulado por usuario.

Guardar la estación en la cabecera es adecuado bajo el origen único aprobado. Si más adelante se permite un origen diferente por bicicleta, habrá que revisar esa regla y volver a representar la estación en el detalle, adaptar las validaciones, las consultas de baja de estación y la interfaz y preservar los contratos históricos. No bastaría con habilitar otro selector en el frontend. No se añade ahora una segunda FK redundante como preparación especulativa.

## 7. Aprobación e implementación

El usuario aprobó las reglas, incluido trasladar la estación a la cabecera, y señaló que el máximo acordado con su compañero es diez. Se incorporaron la FK y la relación al Mermaid, manteniendo 28 entidades y 52 FK/relaciones. El valor máximo queda documentado como configuración inicial del servicio, no como una columna duplicada o una tabla nueva. Los originales, Java y la base permanecen sin cambios.

No se fijan aquí mínimos o máximos de duración estimada ni si el formulario ofrecerá una estimación común o por unidad. El cálculo temporal individual ya aprobado se mantiene; la validación antigua de una a 24 horas no se adopta silenciosamente como nueva regla.

La revisión de PAGO/REEMBOLSO registra RN-PAG-03 aprobada y RN-PAG-05 con checkout externo, sin medios guardados locales. Sigue revisar asociaciones de trazabilidad y concretar el esquema físico, manteniendo los puntos técnicos de integración pendientes. No hace falta esperar credenciales de la pasarela para comenzar módulos independientes ya definidos, pero tampoco se presenta una simulación como integración real.
