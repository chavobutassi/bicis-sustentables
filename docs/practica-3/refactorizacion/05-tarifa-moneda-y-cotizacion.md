# RN-ALQ-04: tarifa y cotización congeladas

Fecha de aprobación: 25 de octubre de 2026.

Estado: aprobada para implementar. No implementada todavía en el código de la nueva versión. Los casos de prueba están especificados, no ejecutados.

## 1. Política aprobada

- Las tarifas de referencia se mantienen en USD.
- Los pagos iniciales, pagos adicionales y reembolsos se realizan en pesos argentinos (ARS).
- Al confirmar la contratación, antes de pagar el anticipo, se guardan la tarifa contratada de cada bicicleta y la cotización aplicada al alquiler.
- Esa tarifa y esa cotización quedan congeladas para toda la contratación, incluidos sus retiros y devoluciones individuales.
- El costo final depende del tiempo real de uso. Una variación posterior del dólar no cambia el valor por hora acordado en pesos.
- El ajuste final conjunto utiliza esos mismos valores, tanto si corresponde devolver dinero como si queda un adicional por pagar.

"Congelar" significa guardar los valores utilizados para el contrato, no solamente consultar una cotización al mostrar la pantalla. No se vuelve a consultar una cotización nueva para recalcular ese contrato cuando se devuelve una bicicleta, se procesa un adicional, se solicita un reembolso o se revisa el historial.

## 2. Momento y alcance de la congelación

La confirmación de la contratación inicia la reserva de [RN-ALQ-03](04-reserva-y-vencimiento.md). En ese momento se fijan los valores económicos del contrato. No se espera al pago ni al retiro para fijarlos, porque el anticipo debe mostrarse y cobrarse de forma coherente.

Todas las bicicletas incluidas en ese alquiler utilizan una misma cotización aplicada al conjunto, aunque tengan tarifas USD distintas y se retiren o devuelvan en momentos diferentes.

El tiempo de uso de cada unidad sigue empezando con su retiro efectivo, no con la congelación de valores ni con el pago. Por tanto, el momento de fijar el precio y el comienzo del tiempo facturado son hechos distintos.

Los cambios del catálogo afectan a contrataciones futuras. No modifican una tarifa ya guardada en un detalle contratado. La regla de cotización tampoco crea una excepción al plazo de 15 minutos ni lo reinicia.

### Administración de la tarifa confirmada posteriormente

El 28 de octubre de 2026 el usuario confirmó «Una tarifa por tipo, como en mi DER v4». La tarifa vigente en USD pertenece a TIPO_BICICLETA y no se mantiene un precio independiente por unidad en el modelo nuevo. Las unidades del mismo tipo usan la misma tarifa para nuevas contrataciones. Cada ALQUILER_DETALLE sigue guardando el precio aplicado al confirmar y no se recalcula por un cambio posterior del catálogo.

La implementación deberá adaptar el panel administrativo, que hoy modifica un precio por bicicleta, y preparar la transición de los datos actuales. Si las tarifas existentes por unidad difieren dentro de un mismo tipo, se definirá expresamente el nuevo valor de ese tipo sin promediar ni sobrescribir precios contratados históricos. Esta decisión no modifica el código ni la base actuales por sí sola.

## 3. Datos que deben conservarse

En el diseño revisado deben poder identificarse y persistirse:

- Por detalle: tarifa por hora aplicada en USD y datos necesarios para determinar su valor por hora contratado en ARS.
- Por alquiler: cotización aplicada expresada como cantidad de ARS por 1 USD, momento de aplicación y fuente. Si el proveedor informa su propia fecha de actualización, conservarla separada del momento en que el sistema usa ese dato.
- Por detalle y conjunto: importes estimados y reales claramente separados e identificados por moneda, conservando los importes históricos usados para la liquidación.
- Por pago y reembolso: monto efectivamente solicitado/confirmado, moneda ARS, estado y referencias de la operación original y de la pasarela.

La fuente y las fechas permiten explicar qué valor se aplicó. No basta con almacenar solo un total convertido si luego no puede reconstruirse por qué se calculó de esa manera.

El mapeo físico, los nombres finales de las columnas y su precisión decimal se fijarán al corregir el DER. Esta regla no exige crear una tabla de monedas o de cotizaciones por sí sola.

## 4. Ejemplo ilustrativo

Los valores siguientes son ficticios y no representan una cotización actual.

| Concepto | Valor |
| --- | ---: |
| Tarifa contratada | USD 10 por hora |
| Cotización congelada al confirmar | ARS 1.000 por USD 1 |
| Valor por hora contratado en pesos | ARS 10.000 |
| Anticipo por 2 horas | ARS 20.000 |
| Costo real por 45 minutos | USD 7,50, equivalentes a ARS 7.500 |
| Diferencia a reembolsar | ARS 12.500 |

Aunque al devolver el proveedor informe otra cotización, el costo de ese contrato sigue convirtiéndose con ARS 1.000 por USD 1.

Si en cambio la bicicleta se usa 3 horas, el costo real es USD 30, equivalentes a ARS 30.000 con la cotización contratada. Frente a ARS 20.000 anticipados, queda un saldo deudor de ARS 10.000. No se convierte el adicional con la cotización del día en que se paga.

En un alquiler de varias bicicletas, se calculan los costos de los detalles con sus respectivas tarifas contratadas y la misma cotización del conjunto. La liquidación conjunta sigue [RN-ALQ-02](03-alquiler-con-varias-bicicletas.md).

## 5. Criterios de aceptación

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| CP-ALQ-04-01 | Cambia el dólar entre la confirmación, el pago y el retiro | El anticipo y el valor por hora contratado en ARS no cambian |
| CP-ALQ-04-02 | Cambia la tarifa del catálogo durante una reserva o un viaje | El detalle conserva su tarifa USD original |
| CP-ALQ-04-03 | Tarifa USD 10/h, cotización ARS 1.000/USD, anticipo por 2 horas y uso real de 45 minutos | Costo real ARS 7.500 y reembolso correspondiente ARS 12.500 |
| CP-ALQ-04-04 | Mismo contrato, pero con uso real de 3 horas y otra cotización al pagar el adicional | Costo real ARS 30.000 y adicional ARS 10.000, sin aplicar la cotización nueva |
| CP-ALQ-04-05 | Dos bicicletas del mismo alquiler se devuelven en días o momentos con cotizaciones distintas | Se usa la cotización congelada del alquiler para ambas |
| CP-ALQ-04-06 | Se consulta el historial luego de un cambio de tarifa o dólar | Los importes guardados permanecen iguales y no se reconvierten con valores actuales |
| CP-ALQ-04-07 | Se procesa un reembolso tiempo después de terminar el uso | Se devuelve el importe ARS determinado por la liquidación, sin reconvertirlo a la cotización del día |
| CP-ALQ-04-08 | Se inspecciona la contratación | Se identifican tarifa aplicada, cotización, moneda, momento de aplicación y fuente |

## 6. Decisiones todavía pendientes

- Proveedor y tipo de cotización que se usarán para las nuevas contrataciones. La existencia de una API en la versión anterior no sustituye esta definición.
- Antigüedad admisible de la cotización y comportamiento si el proveedor falla, no responde o devuelve un dato inválido. No se aprueba aquí inventar una tasa de respaldo.
- Mapeo físico de la precisión: [RN-ALQ-10](29-propuesta-precision-tiempo-y-redondeos.md) ya aprobó segundos completos, sin mínimo comercial ni bloques, dos decimales HALF_UP por detalle/moneda y total por suma; siguen pendientes precisión SQL de entradas y límites, no el criterio de cálculo.
- Modalidad de integración de Mercado Pago, medios compatibles y pruebas concretas. El usuario eligió esa pasarela para más adelante y planteó usar sus herramientas de prueba, sin autorizar cobros reales ni implementar todavía un sustituto local; ver [decisión de pasarela](23-pasarela-mercadopago-y-pruebas.md).

No se consultó una cotización actual, no se modificó código ni base de datos y no se realizaron pagos ni reembolsos.
