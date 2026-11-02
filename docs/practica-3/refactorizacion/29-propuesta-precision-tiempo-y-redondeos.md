# RN-ALQ-10 Precisión de tiempo y redondeos

Fecha: 28 de octubre de 2026.

Estado: aprobada expresamente el 28 de octubre de 2026 mediante «hagamos esa mejora entonces», después de explicar la comparación con el cálculo actual. Se precisan segundos completos, ausencia de mínimo de uso y bloques, dos decimales independientes por moneda y detalle con HALF_UP y total por suma de líneas. Se reflejó la política en los comentarios del Mermaid sin cambiar campos, claves, estados, entidades o relaciones. Java y la base siguen sin cambios: la implementación corresponde al backend refactorizado. Los ejemplos tienen verificación aritmética independiente, no pruebas de la aplicación ni de Mercado Pago.

## 1. Base de la decisión

Se contrastaron el diccionario y PDF originales, RN-ALQ-01, RN-ALQ-02, RN-ALQ-03, RN-ALQ-04 y la precisión económica aprobada de RN-INC-01. Los originales no fijan una política suficiente de fracciones de segundo, centavos o suma de líneas. Se conservan el inicio al retirar, el corte válido del uso, el anticipo, la cotización congelada y la liquidación conjunta; no se agregan multas ni otra forma de cobrar la demora.

La versión Java anterior usa segundos transcurridos, divide primero la tarifa por 3600 con escala 10, redondea el costo USD a dos decimales y después lo multiplica por la cotización, redondeando ARS a pesos enteros. Además consulta la cotización al devolver: ese comportamiento anterior no implementa la nueva congelación al confirmar. Se revisaron archivos, sin iniciar Spring ni consultar la base.

La decisión mantiene la medición por segundos, evita redondear USD antes de obtener ARS y conserva centavos en pesos. La política es una decisión aprobada del proyecto, no una exigencia atribuida al profesor, a Java o a la pasarela. El método anterior no se presenta como universalmente inválido: utiliza otra política de redondeo. La nueva prioriza la precisión del importe operativo ARS, distinguiéndolo de la referencia USD mostrada.

## 2. Precisión del tiempo aprobada

1. Medir segundos completos transcurridos entre el retiro real y el fin facturable validado. En una devolución ordinaria, ese fin es la recepción real; en el caso excepcional aprobado, el corte autorizado.
2. Descartar únicamente la fracción final de segundo del intervalo: 45 minutos, 23 segundos y una fracción se cobran como 2723 segundos. No redondear hacia arriba al minuto, cuarto de hora u hora.
3. No agregar un mínimo comercial de tiempo de uso. La duración estimada sirve para el anticipo, no es un mínimo de facturación definitiva. Cero segundos completos producen costo cero; el redondeo monetario también puede producir cero sin convertir un retiro real en una cancelación.
4. Usar los instantes registrados por el backend, no el contador del navegador. No truncar primero cada fecha a minutos o segundos y luego restarlas: el descarte se aplica al intervalo. La precisión física y estrategia de zona horaria se fijarán coherentemente en D06.

Se cuenta el tiempo del recorrido, no únicamente el movimiento de las ruedas. Una pausa ordinaria del cliente no detiene el alquiler. La espera posterior a una recepción válida no se cobra; si hay una incidencia previa con efecto económico, se espera su validación sin seguir incrementando el contador, conforme a lo ya aprobado.

Fechas incoherentes no autorizan a fabricar un uso o liquidación definitivos. La validación temporal debe impedir cálculos negativos o cierres basados en datos inventados, sin interpretar la espera administrativa como uso adicional.

## 3. Política monetaria aprobada

- Obtener cada subtotal con la tarifa USD contratada, los segundos cobrables de esa unidad y la cotización ARS por USD congelada en su alquiler.
- No redondear una tarifa por segundo ni un subtotal USD intermedio antes de obtener ARS. Multiplicar los factores pertinentes y realizar la división final con el redondeo monetario correspondiente.
- Persistir los subtotales monetarios USD de referencia y ARS con dos decimales, calculados por separado a partir de esos factores. El importe ARS no se obtiene multiplicando el subtotal USD ya redondeado.
- Usar HALF_UP: al redondear a centavos, la mitad sube para los importes no negativos del alquiler. Ejemplos: 12,344 pasa a 12,34 y 12,345 pasa a 12,35.
- Redondear una vez el importe de cada bicicleta en cada moneda. Después obtener el total del conjunto sumando esos subtotales ya redondeados, sin recalcularlo desde otra suma de valores sin redondear.
- Aplicar el mismo criterio a estimaciones y costos reales. La precisión de tarifa y cotización de entrada se conserva según el contrato; no se redondean anticipadamente a la escala de un subtotal.

La consecuencia deliberada es que multiplicar el USD mostrado con dos decimales por la cotización puede no reproducir exactamente el ARS. USD es una referencia redondeada y ARS es el importe de la operación de dinero, calculado antes de perder precisión. La pantalla debe identificar ese carácter referencial y utilizar los valores almacenados, no reconvertir uno mostrado para reemplazar al otro.

Ejemplo ficticio que muestra por qué importa: USD 1/h, 1 segundo y cotización ARS 1000/USD. El USD exacto es 1/3600; el importe mostrado es USD 0,00, mientras el importe ARS es 1000/3600 y se redondea a ARS 0,28. Convertir primero USD 0,00 produciría falsamente ARS 0,00. No hay dos cobros ni una nueva tarifa: son redondeos de referencia y de moneda operativa independientes.

## 4. Fórmulas y total del conjunto

Para cada detalle, sean P la tarifa USD/h aplicada, S los segundos completos estimados o reales según el cálculo y C la cotización congelada ARS/USD. R2 significa redondeo a dos decimales con HALF_UP:

```text
Subtotal USD = R2(P × S / 3600)
Subtotal ARS = R2(P × S × C / 3600)

Total USD = suma de subtotales USD de los detalles
Total ARS = suma de subtotales ARS de los detalles
```

No utilizar Subtotal USD ya redondeado como entrada de la segunda fórmula. Una unidad cancelada o vencida sin retiro tiene costo real cero sin inventar timestamps; su estimación original y el anticipo recibido se conservan conforme a las reglas de liquidación.

El dinero neto confirmado se sigue obteniendo de pagos aprobados menos reembolsos confirmados. La diferencia frente al costo final ARS determina saldo o reintegro según RN-ALQ-08. Los intentos pendientes/rechazados no saldan nada y no se vuelve a consultar el dólar. Una diferencia cero no crea otro movimiento ni una solicitud por importe cero a la pasarela.

Una devolución intermedia puede fijar el subtotal definitivo de esa bicicleta sin cobrar/devolver su diferencia individualmente. La liquidación sigue siendo conjunta y espera además las revisiones económicas relevantes pendientes. La política no crea una segunda liquidación ni habilita correcciones libres de importes definitivos.

## 5. Ejemplos y verificación aritmética

Son datos ficticios, no cotizaciones actuales. Se comprobaron de forma independiente el 28 de octubre de 2026 con fracciones exactas y redondeo de unidades monetarias; no se probó código Java, SQL o HTTP del proyecto.

| Caso | Entrada | Resultado verificado |
| --- | --- | --- |
| AR-01 | USD 10/h, 45 minutos, cotización 1000 | USD 7,50 de referencia y ARS 7500,00; frente a anticipo ARS 20000,00, reintegro de ARS 12500,00 |
| AR-02 | Misma tarifa/cotización, uso de 3 horas | ARS 30000,00; frente a anticipo ARS 20000,00, adicional de ARS 10000,00 |
| AR-03 | Importe sin redondear 0,005 | Resultado 0,01 con HALF_UP |
| AR-04 | USD 1/h, 1 segundo, cotización 1000 | USD referencial 0,00; ARS 0,28 calculado directamente antes de redondear USD |
| AR-05 | Dos unidades: USD 2,01/h y USD 4,01/h, ambas 180 segundos, cotización 10 | ARS 1,01 + ARS 2,01 = ARS 3,02; redondear únicamente el conjunto daría 3,01 y no es la política aprobada |
| AR-06 | USD 9/h, 45 minutos y 23 segundos, cotización 1000 | USD referencial 6,81 y ARS 6807,50; no ARS 6810,00 obtenidos del USD ya redondeado |
| AR-07 | Intervalo de 2723,999 segundos; y otro caso de cero segundos | 2723 segundos cobrables en el primero; costo cero en el segundo |

## 6. Implementación prevista y límites

La implementación prevista utilizará BigDecimal con entradas decimales exactas, multiplicando antes de dividir y eligiendo escala y HALF_UP para cada subtotal final. No utilizar double para los cálculos monetarios ni confiar en que guardar un DECIMAL sin política reproduzca el criterio. La escala monetaria de subtotales/totales y operaciones ARS ya está fijada en dos decimales. La precisión total SQL, los límites, precisión de tarifa/cotización de entrada y timestamps se concretarán en D06; este registro no genera migraciones ni modifica el servicio antiguo.

Se consultaron las referencias oficiales de [BigDecimal de Java 11](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/BigDecimal.html) y [RoundingMode](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/math/RoundingMode.html) para contrastar precisión decimal y significado del redondeo. Son herramientas para implementar la decisión, no una imposición del criterio de negocio.

También se verificó que la [referencia de creación de órdenes de Checkout Pro](https://www.mercadopago.com.ar/developers/es/reference/online-payments/checkout-pro/create-order/post) admite total con dos decimales o ninguno, exige concordancia con sus ítems y rechaza cero. Esto solo verifica el formato de esa referencia: no selecciona Checkout Pro ni prueba que todo medio de pago/reembolso admita cualquier importe. Producto, mínimos operativos y tratamiento de diferencias demasiado pequeñas para un medio concreto siguen en D03. No se inventa un recargo o redondeo a un mínimo de pasarela para solventarlo.

Fuentes externas comprobadas el 28 de octubre de 2026. No se enviaron pagos ni se consultaron cuentas o credenciales. La composición enviada a la pasarela deberá corresponder al movimiento solicitado, no repetir el costo final como si fuera siempre otro cobro completo.

## 7. Criterios de aceptación de la regla aprobada

Los casos de aplicación siguientes no se ejecutaron:

- CP-ALQ-10-01: el contador comienza en el retiro y una fracción final de segundo no redondea el intervalo al minuto u hora siguiente.
- CP-ALQ-10-02: los importes reproducen las fórmulas por detalle, con tarifa/cotización congeladas y sin redondear USD antes de obtener ARS.
- CP-ALQ-10-03: la suma de subtotales almacenados coincide con los totales en cada moneda, incluidos los empates de medio centavo.
- CP-ALQ-10-04: anticipos, adicionales y reintegros se expresan en ARS con dos decimales; costo o diferencia cero no crea una operación externa de importe cero.
- CP-ALQ-10-05: devolución con incidencia previa pendiente detiene el tiempo, mantiene costo provisional y espera la validación del corte antes de liquidar.
- CP-ALQ-10-06: backend, historial y comprobantes utilizan los mismos importes persistidos; el frontend no reconstruye el importe operativo desde un USD mostrado y redondeado.

## 8. Aprobación e incorporación al modelo

El usuario autorizó adoptar la mejora después de contrastarla con el cálculo existente. Quedan aprobados segundos completos con descarte de fracción final, sin mínimo comercial de uso ni bloques, subtotales USD/ARS independientes a dos decimales con HALF_UP y totales por suma de líneas. La referencia USD redondeada no se usa para reconstruir el ARS operativo.

Se añadieron comentarios de política global y se aclararon los importes y duración del modelo. No se añadieron o eliminaron atributos ni cambiaron tipos, claves o cardinalidades: permanecen 28 entidades y 52 FK/relaciones. El código actual aún usa el cálculo anterior; esta aprobación fija lo que debe implementar el backend nuevo, no acredita un parche de Java ni una migración.

Siguen pendientes la fuente/tipo de cotización, frescura, fallos del proveedor y otros puntos de D02/D03, además de composición de contratación y D06. El siguiente bloque concreto es cerrar selección de bicicletas, estación de retiro y límites de contratación, sin reabrir los estados, cobro real ni redondeos ya aprobados.
