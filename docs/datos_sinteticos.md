# Datos sintéticos

`generador/generar_datos.py` simula, evento por evento y en orden cronológico, un negocio ficticio de alquiler de
bicicletas, y escribe las sentencias SQL que lo reproducen en la base (`data/seed.sql.gz`). Como pasan por los
mismos triggers que usaría la aplicación, los datos cumplen todas las reglas por construcción.
Solo usa la biblioteca estándar de Python.

Nada es real: los nombres, documentos, teléfonos y correos (dominio reservado `.test`) son inventados.

## Qué simula

- **Flota:** 60 bicicletas al inicio (urbanas, mountain bike, eléctricas, ruta, infantiles y tándem) repartidas
  en tres estaciones y un taller. Con el tiempo se dan de baja las irreparables y se compran reemplazos y
  bicicletas nuevas.
- **Demanda:** por mes (temporada alta de noviembre a marzo), por día de la semana y con un factor aleatorio de
  clima; llegan grupos de 1 a 8 bicicletas, por hora (82 %) o por día (18 %).
- **Reservas** (45 % de los grupos, por web, teléfono o mostrador): con seña del 30 %; las web sin pago vencen a
  los 30 minutos; ~11 % se cancela (con reembolso total o parcial según la anticipación) y ~7 % no se presenta.
  Si el cupo no alcanza, se reserva menos o se pierde la demanda.
- **Retiros y devoluciones:** el mostrador ofrece bicicletas disponibles en la estación (respetando las reservas
  próximas); ~8 % se devuelve en otra estación; algunas bicicletas de un grupo vuelven más tarde; ~4 % se
  devuelve con más de una hora de demora. Un camión reubica cada noche las bicicletas a su estación base.
- **Cobros:** al devolver la última bicicleta, saldo = importe + cargos − seña; una tarjeta rechazada se reintenta;
  ~15 % de los alquileres con cargos por daños los deja sin pagar (deuda); una seña mayor al total se reembolsa.
- **Taller:** cada día a las 7:00 revisa qué tareas del plan están vencidas y abre hasta 6 órdenes preventivas;
  las reparaciones se abren al devolver una bicicleta dañada, esperan turno según la carga del taller y duran
  según la gravedad. Trabaja de lunes a sábado.

## La verdad simulada

La probabilidad de que una bicicleta falle durante un alquiler sale de este proceso:

```
tasa por hora = base[tipo] · exp(0,12 · edad en años) · fragilidad[bicicleta]
                · exp(1,4 · min(atraso, 1,2)) · (1,12 en verano)
P(falla) = 1 − exp(−tasa · horas efectivas)
```

- **atraso** es cuánto se pasó la tarea de mantenimiento más atrasada de su intervalo (0 = al día, 1 = el doble
  del intervalo). Un taller no hace una tarea justo al vencer: deja pasar una fracción del intervalo (55 % de las
  veces menos del 8 %, pero 5 % de las veces entre el 80 % y el 150 %). Esa variación es la señal que un modelo
  debe encontrar.
- **fragilidad** es un factor oculto de cada bicicleta (log-normal): no está en ninguna tabla de la base.
- **El sistema que falla** depende de qué tareas están atrasadas (pesa 1 + 8 × atraso de cada tarea).
- Aparte, hay daños y accidentes **causados por el cliente**, con tasa constante: no dependen del mantenimiento.
- **Horas efectivas:** en un alquiler por día se cuentan como máximo 6 horas por día.

### Archivos de la verdad (carpeta `data/`)

| Archivo | Contenido |
| --- | --- |
| `verdad_bicicletas.csv` | Fragilidad oculta de cada bicicleta. |
| `verdad_exposicion.csv.gz` | Una fila por devolución: `detalle_id`, tasa, atraso, edad, probabilidad real de falla y si hubo falla. |
| `verdad_incidentes.csv` | Cada incidencia con su causa real (falla por desgaste, daño o accidente), sistema y atraso. |

Con `verdad_exposicion` se puede medir qué tan cerca está un modelo del proceso verdadero (por ejemplo, la
correlación entre su probabilidad y `prob_falla`, o la pérdida logarítmica contra `hubo_falla`).

Ejemplo de la señal con los datos incluidos (tasa de falla por alquiler según el atraso del mantenimiento):

| Atraso | Alquileres | Fallas por alquiler |
| --- | --- | --- |
| Al día | 5.733 | 2,4 % |
| 0 a 10 % | 1.939 | 2,8 % |
| 10 a 30 % | 2.142 | 2,7 % |
| 30 a 70 % | 2.036 | 5,0 % |
| más de 70 % | 837 | 9,8 % |

(Se recalcula desde `verdad_exposicion.csv.gz`.)

## Cómo se garantiza la consistencia

`tests/verificar_datos.sql` comprueba 16 invariantes sobre la base cargada, entre ellas: toda bicicleta
*alquilada* tiene un alquiler abierto y viceversa; toda bicicleta *en mantenimiento* tiene una orden abierta; el
último estado del historial coincide con el actual; el costo de cada orden es la suma de sus ítems; ningún
alquiler finalizado queda con saldo negativo ni con más saldo que sus cargos; ningún reembolso supera lo cobrado;
y cada importe coincide con `fn_importe()`.

El generador replica en Python `fn_importe()` y `fn_cupo()`. Si el cupo deja de coincidir con la base, la carga
falla; si el importe no coincide, lo detectan los invariantes de saldo.

## Regenerar y ajustar

```bash
python3 generador/generar_datos.py --hasta 2026-11-04T12:00 --salida data/seed.sql.gz
python3 generador/generar_datos.py --escala 0.5      # la mitad de demanda
python3 generador/generar_datos.py --semilla 7        # otra corrida
```

Las constantes de arriba del archivo (demanda por mes, tasas base, planes de mantenimiento, precios, inflación
mensual del 2,8 % con ajuste trimestral) se pueden cambiar. Un cambio en el generador cambia el archivo entero:
conviene volver a correr las verificaciones.

### La demo envejece

Los datos terminan en la fecha de `--hasta`. Las vistas que miran el presente (`v_alquileres_demorados`,
`v_reservas_por_vencer`, plazos de `v_proximo_servicio`) comparan contra `now()`: si cargás la demo semanas
después, los alquileres que quedaron en curso figuran como muy demorados. Para una demo fresca, regenerá con
`--hasta` igual a la fecha y hora de hoy.
