# RN-ALQ-02: varias bicicletas y liquidación conjunta

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada para implementar. Este documento describe el comportamiento que deberá cumplir el sistema, no una funcionalidad que ya esté programada.

## 1. Regla acordada

Un usuario puede contratar varias bicicletas dentro de un mismo alquiler. La cabecera agrupa la contratación y cada detalle corresponde a una bicicleta concreta.

Cada unidad conserva su tarifa contratada y sus fechas reales de retiro y devolución. Las bicicletas pueden retirarse y devolverse por separado, respetando el plazo de reserva de [RN-ALQ-03](04-reserva-y-vencimiento.md). Las devoluciones pueden ocurrir en estaciones diferentes, siempre que la estación elegida sea válida y tenga espacio.

Al confirmar una devolución:

- Termina el uso de esa bicicleta y deja de acumular costo.
- Se guarda su fecha real de devolución, estación y costo definitivo por el tiempo utilizado.
- Sin falla reportada ni otro impedimento, la bicicleta queda disponible en la estación de devolución, sin esperar a las otras unidades. Con falla reportada, queda fuera de alquiler para revisión técnica, pero su uso igualmente termina, según [RN-ALQ-06](09-devolucion-demora-y-fallas.md). La preventiva vencida también exige MANTENIMIENTO, aun sin falla, según las condiciones aprobadas de [RN-MAN-04](19-propuesta-preventivo-por-calendario.md); no prolonga el cobro al cliente.
- Los detalles que siguen en uso continúan acumulando su propio tiempo.
- El sistema puede mostrar el subtotal definitivo de la unidad devuelta, pero no realiza un ajuste financiero individual en ese momento.

Cuando termina el uso de todas las bicicletas y no quedan detalles pendientes de retiro, se calcula el costo real total y se efectúa una liquidación conjunta frente al anticipo total confirmado. Las unidades no retiradas vencen a los 15 minutos y tienen costo de uso cero, conforme a RN-ALQ-03; su anticipo se incluye en la liquidación del conjunto.

## 2. Liquidación del conjunto

El costo real total es la suma de los costos definitivos de sus detalles. Para el caso normal en que todas las bicicletas se retiraron y devolvieron:

- Si el anticipo total es mayor que el costo real total, corresponde reembolsar la diferencia.
- Si ambos importes son iguales, no corresponde un cobro ni un reembolso adicional.
- Si el anticipo total es menor, la diferencia constituye un saldo deudor y se ofrece su pago adicional.

No se exige un adicional por una devolución intermedia ni se efectúa un reembolso parcial por cada bicicleta devuelta. El ajuste nace al liquidar el conjunto. Esto permite compensar el menor uso de una unidad con el mayor uso de otra dentro del mismo alquiler.

Los pagos y reembolsos son operaciones registradas por separado, vinculadas al alquiler y a sus operaciones de origen. No se modifica el valor del pago inicial para hacerlo coincidir con el costo final.

Una liquidación ya registrada no debe duplicarse si se repite la petición de devolución o se reintenta una llamada a la pasarela. Los cambios posteriores en el estado de sus movimientos financieros tampoco vuelven a iniciar el contador de uso.

RN-INC-01 incorpora CERRADO_POR_INCIDENCIA, con corte validado y sin cerrar otras unidades. Cuenta como terminal para completar el uso. También está aprobada la [sección 8 de RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md): si hay una incidencia previa pendiente que pueda afectar el importe, se conserva la devolución física, se detiene el tiempo y se espera su revisión antes de liquidar el conjunto. Hasta entonces el importe afectado es provisional y la situación financiera permanece SIN_LIQUIDAR, aunque la cabecera ya esté FINALIZADO. No se introduce una segunda liquidación.

## 3. Ejemplo aprobado

Datos ilustrativos: tarifa de ARS 1.000 por hora para cada bicicleta. Se anticipan 2 horas por cada una de las dos unidades.

| Concepto | Importe |
| --- | ---: |
| Anticipo total: dos bicicletas, dos horas cada una | ARS 4.000 |
| Costo real de la primera bicicleta: 45 minutos | ARS 750 |
| Costo real de la segunda bicicleta: 3 horas | ARS 3.000 |
| Costo real del alquiler completo | ARS 3.750 |
| Diferencia a reembolsar al cierre | ARS 250 |

La primera bicicleta se libera al minuto 45. El costo de la segunda sigue aumentando hasta su propia devolución. No se reembolsan ARS 1.250 por la primera para exigir luego ARS 1.000 por la segunda: el ajuste conjunto de este ejemplo es un reembolso de ARS 250.

## 4. Uso y deuda son estados distintos

El uso del conjunto termina cuando no queda ninguna bicicleta en uso ni pendiente de retiro. La gestión de dinero puede continuar después.

Si queda un saldo deudor, el cliente no puede iniciar nuevos alquileres hasta cancelarlo. Puede ingresar, pagar y devolver bicicletas de otras contrataciones ya iniciadas. Un reembolso pendiente a favor del cliente no es una deuda suya.

Si falla el pago adicional o el reembolso, las unidades ya devueltas no vuelven a estar alquiladas y no se reanuda su facturación por tiempo.

Esta regla complementa [RN-ALQ-01](02-regla-de-cobro.md). Los cinco estados de cabecera se aprobaron en [RN-ALQ-07](10-estados-cabecera-alquiler.md). Los demás catálogos y sus restricciones se consolidarán al corregir el DER y la tabla de transiciones.

## 5. Consecuencias para el modelo

- `ALQUILER` identifica al contratante y agrupa los detalles y la liquidación.
- `ALQUILER_DETALLE` identifica la bicicleta y conserva su tarifa, tiempos reales, estaciones y subtotales.
- Cada detalle necesita poder distinguir sus datos estimados de los reales.
- La cabecera no puede tratarse como terminada si todavía hay unidades en uso o pendientes de retiro.
- Las verificaciones de propiedad del alquiler y capacidad de estación se aplican también a las devoluciones individuales.
- Costo del viaje, anticipo cobrado, deuda y reembolso no son un único campo intercambiable.
- Todas las unidades del conjunto utilizan la cotización congelada del alquiler y sus propias tarifas USD contratadas, con liquidación en ARS según [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md). La precisión de cálculo y los redondeos todavía deben concretarse.

## 6. Criterios de aceptación para las pruebas futuras

Estas pruebas están especificadas, no ejecutadas.

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-02-01 | Se devuelve una de dos bicicletas sin falla reportada ni preventiva vencida u otro impedimento; la otra sigue en uso | Se detiene solo el contador de la unidad devuelta y esa bicicleta queda disponible en su estación de devolución, ocupando un lugar físico. El conjunto sigue abierto, sin liquidación final |
| CP-ALQ-02-02 | Dos unidades se devuelven a estaciones distintas con capacidad | Cada detalle conserva su estación real de devolución |
| CP-ALQ-02-03 | Anticipo ARS 4.000; costos definitivos ARS 750 y ARS 3.000 | Costo total ARS 3.750 y un ajuste de reembolso de ARS 250 |
| CP-ALQ-02-04 | Anticipo ARS 4.000; costos definitivos ARS 3.000 y ARS 2.000 | Costo total ARS 5.000 y saldo deudor ARS 1.000 |
| CP-ALQ-02-05 | Anticipo ARS 4.000 y costo definitivo total ARS 4.000 | Sin movimiento adicional por diferencia |
| CP-ALQ-02-06 | Se repite la petición de la última devolución | No se duplica la liquidación ni su obligación de pago o reembolso |
| CP-ALQ-02-07 | El reembolso o pago adicional no se completa | Las bicicletas devueltas permanecen liberadas y sus costos no aumentan |
| CP-ALQ-02-08 | Se intenta devolver una unidad de otro cliente o a una estación llena | Se rechaza la operación sin registrar una devolución exitosa ni liberar la bicicleta como si hubiera sido recibida |

## 7. Límites todavía pendientes

La duración de reserva y el abandono que llega al vencimiento están aprobados en RN-ALQ-03. La cancelación voluntaria antes de vencer se aprobó en [RN-ALQ-05](06-cancelacion-antes-del-retiro.md): solo las unidades no retiradas, liberación inmediata, costo cero y tratamiento del anticipo en el ajuste conjunto. Mercado Pago ya fue elegido como pasarela, pero su modalidad e integración y el alcance del candado físico o simulado siguen pendientes. [RN-ALQ-11](30-propuesta-composicion-contratacion.md) ya aprobó origen común, máximo inicial de diez configurable y selección fija tras confirmar, conservando las cancelaciones vigentes. La estación de retiro se trasladó a la cabecera del DER. Los límites acumulados por usuario y las validaciones de duración estimada siguen pendientes; no se presentan como aprobados o implementados.

Una unidad reservada sin retiro vencida o cancelada deja de impedir el cierre del conjunto. Las excepciones operativas adicionales deben completarse sin contradecir esas reglas.

No se modificó código ni base de datos.
