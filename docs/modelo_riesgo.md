# Modelo de riesgo de falla (fase 2)

`modelo/riesgo_falla.py` estima, para cada bicicleta, la probabilidad de tener una **falla en los próximos 30 días**,
en total y por sistema (transmisión, frenos, neumáticos, cuadro, suspensión). Escribe el resultado en
`prediccion_mantenimiento`. Las métricas completas quedan en `modelo/resultados.json`.

```bash
pip install -r modelo/requirements.txt
DATABASE_URL=postgresql:///bicis python3 modelo/riesgo_falla.py             # evalúa
DATABASE_URL=postgresql:///bicis python3 modelo/riesgo_falla.py --escribir  # además guarda las predicciones de hoy
DATABASE_URL=postgresql:///bicis python3 tests/prueba_modelo.py             # pruebas
```

Tarda menos de un minuto. Todo es determinista (semilla fija). `--escribir` reemplaza las filas de la misma
versión del modelo, así que se puede repetir.

## Qué se predice y con qué información

Solo se usa lo que el negocio sabe en cada momento: edad, horas acumuladas, ritmo de uso reciente y el **atraso de
cada tarea del plan de mantenimiento** (0 = al día, 1 = el doble del intervalo, calculado con las órdenes cerradas
y las horas de uso). La fragilidad oculta y los archivos `data/verdad_*` **no** se usan para entrenar; se usan
solo para medir qué tan cerca queda el modelo del proceso verdadero. Una prueba comprueba que las variables
reproducen la edad y el atraso del simulador (correlación 0,999 y 0,94) y que no dependen del futuro.

La falla de un alquiler depende de las horas que se usó la bicicleta, así que el modelo principal no predice
"falla sí/no" directamente. Estima una **tasa de falla por hora de uso** (regresión de Poisson con exposición) y
la convierte en probabilidad:

- Para un alquiler: `P = 1 − exp(−tasa × horas efectivas)`.
- Para 30 días: `P = 1 − exp(−tasa × horas pronosticadas)`. Las horas se pronostican con el ritmo de la bicicleta,
  el ritmo de su tipo en la flota y un índice estacional por mes (con los datos anteriores al corte).

Por sistema se ajusta lo mismo sobre la falla de ese sistema, con el atraso de su tarea como variable.

## Cómo se evaluó

Partición temporal: se entrena hasta el 1 de marzo de 2026 y se evalúa después (marzo a octubre, temporada baja).
En el panel de 30 días se deja una separación de 30 días para que las ventanas de entrenamiento y prueba no se
solapen. Las comparaciones son contra tres líneas base (tasa por tipo, regla de mantenimiento vencido) y contra
la **verdad simulada**, que es el techo alcanzable con esta información.

### A nivel de alquiler (2.849 alquileres de prueba, 100 fallas)

| Modelo | AUC | Precisión media | Log-loss |
| --- | --- | --- | --- |
| Tasa global | 0,746 | 0,117 | 0,138 |
| Regla "tarea vencida" | 0,749 | 0,132 | 0,137 |
| **Tasa por hora (Poisson)** | **0,759** | **0,179** | **0,134** |
| Gradiente (Poisson) | 0,742 | 0,126 | 0,139 |
| Verdad simulada (techo) | 0,762 | 0,173 | 0,133 |

El modelo queda prácticamente en el techo y la tasa estimada correlaciona 0,80 con la tasa verdadera. Las líneas
base ya tienen un AUC alto porque las horas de uso explican gran parte de la falla; lo que aporta el modelo está
en la precisión media y en el log-loss. El gradiente rinde peor: con 335 fallas de entrenamiento sobreajusta.

### Por sistema (AUC; fallas de prueba entre paréntesis)

| Sistema | Modelo | Regla vencida |
| --- | --- | --- |
| Transmisión (26) | 0,82 | 0,79 |
| Frenos (19) | 0,87 | 0,86 |
| Neumáticos (24) | 0,71 | 0,71 |
| Cuadro (11) | 0,68 | 0,65 |
| Suspensión (5) | 0,93 | 0,80 |

Hay pocas fallas por sistema, así que estas cifras son orientativas; la ventaja sobre la regla es clara solo en
transmisión y suspensión.

### Bicicleta y semana, a 30 días (lo que se guarda en la base)

1.974 fotos semanales de prueba; fallaron el 15,5 %.

| Modelo | AUC | Precisión media | Log-loss | Media predicha |
| --- | --- | --- | --- | --- |
| Tasa por tipo | 0,476 | 0,149 | 0,463 | 0,250 |
| Regla "tarea vencida" | 0,508 | 0,157 | 0,459 | 0,249 |
| Directo (logística) | 0,548 | 0,186 | 0,450 | 0,207 |
| Tasa por hora, uso por ritmo de 90 días | 0,540 | 0,186 | 0,479 | 0,211 |
| **Tasa por hora, uso pronosticado** | **0,594** | **0,222** | **0,430** | **0,151** |
| Tasa por hora, con el uso real (techo del método) | 0,693 | 0,291 | 0,399 | 0,146 |
| Verdad simulada (techo) | 0,707 | 0,331 | 0,391 | 0,158 |

- Frente a la regla de mantenimiento vencido, la mejora de AUC es de 0,086, con un intervalo del 95 % de
  0,016 a 0,171 (remuestreo de bicicletas). Frente al modelo directo es de 0,046, con un intervalo de −0,001 a
  0,095: **no se puede afirmar** que sea mejor.
- La calibración mejora mucho: la media predicha pasa de 0,211 a 0,151 contra 0,155 observado.
- **El límite no es el modelo de riesgo, es el pronóstico de uso.** Con las horas reales del mes el AUC sube a
  0,693, casi el techo. Pero las horas futuras no se conocen: el ritmo de los últimos 90 días las sobreestimaba un
  53 % (38 contra 25 horas) porque el período de prueba es temporada baja, y su correlación con lo real era 0,29.
  El índice estacional y el ritmo de la flota llevan esa correlación a 0,54 y eliminan el sesgo.

## Limitaciones

- Los datos son sintéticos y el proceso que genera las fallas es la propia verdad conocida; el resultado dice
  qué tan bien se recupera esa señal, no cuánto rendiría en un negocio real.
- Hay un solo corte temporal y pocas fallas (100 en la prueba por alquiler). Los intervalos son anchos.
- El índice estacional sale de menos de dos años de historia. Con una temporada completa más podría mejorar.
- Las ventanas semanales de una misma bicicleta se solapan; por eso los intervalos se calcularon remuestreando
  bicicletas y no filas.
- La falla por causas externas (daños y accidentes del cliente) no se predice: no depende del mantenimiento.

## Próximos pasos

1. Mejorar el pronóstico de uso (es lo que separa 0,59 de 0,69 de AUC): clima, feriados, reservas ya tomadas.
2. Usar `prediccion_mantenimiento` en la aplicación del taller, para ordenar las órdenes preventivas por riesgo
   en lugar de solo por vencimiento.
3. Tablero en Power BI (punto 3 de la hoja de ruta) con las predicciones y las vistas de mantenimiento.
