# RN-ALQ-01: anticipo y costo por tiempo real

Fecha: 25 de octubre de 2026.

Estado: regla de negocio aprobada para implementar. Todavía no implementada en el código ni verificada mediante pruebas de ejecución.

## Decisión confirmada

El cliente paga inicialmente el importe correspondiente al tiempo estimado. El costo definitivo depende del tiempo real de utilización. Si el importe anticipado supera ese costo, se debe reembolsar la diferencia.

El usuario también confirmó el tratamiento del exceso de tiempo: se cobra la diferencia con la misma tarifa contratada, sin penalizaciones adicionales para esta entrega. La devolución confirmada termina el viaje y detiene el cálculo de tiempo, aunque exista una deuda.

Si el pago adicional falla o no se completa, el saldo queda pendiente y el cliente no puede iniciar nuevos alquileres hasta regularizarlo. Debe conservar acceso para ingresar, pagar y devolver otras bicicletas que ya tenga en uso. No se efectuarán débitos adicionales automáticos en esta primera versión.

Para un alquiler de varias bicicletas, el costo de cada unidad se fija cuando se devuelve, pero el ajuste económico se realiza sobre el conjunto al terminar el uso de todas. Se compara la suma de los costos reales con el anticipo total. No se realiza un reembolso ni se exige un adicional por cada devolución intermedia. La regla detallada está en [RN-ALQ-02](03-alquiler-con-varias-bicicletas.md).

Estas son decisiones de negocio confirmadas por el usuario. Los detalles técnicos y las cuestiones identificadas como pendientes todavía necesitan definición; no son funcionalidades ya implementadas.

Los importes se rigen por [RN-ALQ-04](05-tarifa-moneda-y-cotizacion.md): referencia USD, tarifa y cotización congeladas al confirmar la contratación, pagos y reembolsos en ARS con esos mismos valores.

## Ejemplo ilustrativo en pesos

| Concepto | Importe |
| --- | --- |
| Tarifa de ejemplo | ARS 1.000 por hora |
| Anticipo por 2 horas | ARS 2.000 |
| Costo real por 45 minutos | ARS 750 |
| Diferencia a reembolsar | ARS 1.250 |

No se trata de dos cobros separados: el anticipo de ARS 2.000 ya se efectuó. Se conserva el cargo original, se registra un reembolso de ARS 1.250 y el importe neto resulta ARS 750.

Si en cambio utiliza 3 horas, el costo final es ARS 3.000. Se descuentan los ARS 2.000 anticipados y queda un adicional de ARS 1.000. Solo un pago adicional confirmado cancela esa deuda; el cargo inicial no se sobrescribe.

## Comportamiento aprobado para implementar

1. Guardar la tarifa acordada, la duración estimada, el importe anticipado y su moneda.
2. Iniciar la medición del uso al confirmar el retiro de la bicicleta, no al crear la reserva o pagar el anticipo.
3. Al confirmar una devolución válida, registrar el fin real y calcular el costo de esa bicicleta en el backend, con la tarifa contratada. Si quedan otras unidades en uso o pendientes de retiro, todavía no liquidar el conjunto.
4. Cuando todos los detalles hayan terminado su uso y no quede ninguno pendiente de retiro, calcular el costo total real. Las unidades cuya reserva venció sin retiro tienen costo de uso cero según [RN-ALQ-03](04-reserva-y-vencimiento.md); lo mismo ocurre con las canceladas sin retiro según [RN-ALQ-05](06-cancelacion-antes-del-retiro.md). Sus anticipos se incluyen en la liquidación conjunta, sin penalización por cancelación.
5. Comparar el costo total con el anticipo confirmado: si es menor, registrar y solicitar el reembolso de la diferencia; si es igual, no generar movimientos adicionales; si es mayor, registrar la diferencia como saldo pendiente. Cada movimiento debe conservar su identificador y estado real.
6. Mostrar el costo final y el estado de la liquidación. Permitir seguimiento o reintento seguro si el proveedor no responde o rechaza la operación.
7. Si el costo final supera lo anticipado, registrar el saldo deudor y ofrecer su pago por la pasarela. Bloquear únicamente nuevas contrataciones mientras exista una deuda pendiente confirmada por la liquidación, sin impedir devoluciones, acceso a la cuenta o pagos.

El viaje y el dinero tienen ciclos distintos. La bicicleta no debe permanecer alquilada porque el proveedor no terminó de procesar el reembolso. Un reintento no debe devolver dos veces el mismo dinero.

Según [RN-ALQ-06](09-devolucion-demora-y-fallas.md), una devolución válida con falla reportada también termina el uso y fija su costo. La unidad queda fuera de alquiler para revisión, sin seguir facturando al cliente durante esa espera y sin un cargo automático por daños.

Posteriormente se aprobó [RN-INC-01](21-propuesta-minima-incidencias-en-viaje.md): ADMIN puede autorizar un cierre excepcional con corte validado, manteniendo tarifa/cotización y ajuste conjunto. También se aprobó su sección 8: una devolución con incidencia previa pendiente se registra de inmediato y detiene el tiempo; el costo queda provisional si la incidencia puede cambiarlo y la liquidación del conjunto espera la revisión. La recuperación posterior no reinicia el uso y el anticipo confirmado no se altera.

La liquidación debe persistirse antes de depender de servicios externos. La llamada al proveedor no debe mantener un bloqueo de base de datos durante toda su espera. El mecanismo concreto de persistencia y recuperación se resolverá al diseñar el módulo de pagos.

Las cuatro situaciones financieras que expresan el resultado de ese recorrido están aprobadas en [RN-ALQ-08](11-situacion-financiera-alquiler.md): SIN_LIQUIDAR, SALDO_PENDIENTE, REEMBOLSO_PENDIENTE y SALDADO. No sustituyen el estado de la cabecera ni el de cada intento de pago.

## Consecuencias para el DER

- Separar costo estimado, costo final, pagos confirmados y reembolsos. No sobrescribir el pago original con el importe neto.
- Un reembolso debe referenciar el pago al que corresponde y guardar monto, moneda, estado y referencia externa. La elección entre una entidad propia o movimientos financieros tipados queda pendiente del DER revisado.
- Los importes pendientes de reembolso y los importes efectivamente reembolsados son conceptos diferentes.
- La deuda se reduce con pagos adicionales confirmados, no con intentos pendientes o rechazados. Los reintentos deben evitar cargos duplicados.
- El control de deuda debe ejecutarse en el backend antes de permitir un nuevo alquiler. No basta con deshabilitar el botón del frontend.
- Con varios detalles, guardar sus costos individualmente y liquidar el conjunto al terminar el uso de todas las unidades. Una devolución intermedia no crea una deuda ni un reembolso definitivos por sí sola.
- Conservar tarifa USD por detalle y una cotización congelada por alquiler conforme a RN-ALQ-04. Anticipo, costo final, adicional y reembolso se expresan en ARS sin aplicar una cotización nueva al mismo contrato.

## Decisiones todavía pendientes

- Mapeo físico de las precisiones: [RN-ALQ-10](29-propuesta-precision-tiempo-y-redondeos.md) ya aprobó segundos completos, sin mínimo de uso ni bloques, y dos decimales HALF_UP por detalle/moneda. Faltan precisión SQL de entradas, límites y timestamps, no volver a elegir esa política.
- Proveedor y tipo de cotización, antigüedad admisible y tratamiento de sus fallos; la política de moneda y congelación ya está aprobada en RN-ALQ-04.
- Modalidad de integración de Mercado Pago, medios compatibles y pruebas: el proveedor ya fue elegido posteriormente en el documento 23, no se vuelve a tratar como una elección abierta.

## Referencia de viabilidad anterior a la elección de proveedor

La referencia siguiente se incluyó antes de elegir pasarela para mostrar la viabilidad de reembolsos parciales y reintentos sin duplicados, sin generalizar condiciones a todos los medios. Después el usuario eligió Mercado Pago, como registra el [documento 23](23-pasarela-mercadopago-y-pruebas.md); siguen pendientes producto e integración, no esa elección.

- [API oficial de creación de reembolsos](https://www.mercadopago.com.ar/developers/es/reference/online-payments/checkout-pro-preferences/create-refund/post).
- [Condiciones de reembolsos y cancelaciones](https://www.mercadopago.com.ar/developers/en/docs/checkout-pro-preferences/additional-settings/refunds-and-cancellations).

No se modificó código ni base de datos. No se realizaron pagos ni reembolsos reales.
