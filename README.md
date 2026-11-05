# Bicis sustentables

Sistema para **operar un negocio de alquiler de bicicletas** con varias estaciones y un taller: reservas con seña, retiro y devolución en mostrador, cobros, daños, y mantenimiento planificado según el uso real de cada bicicleta.

Es un proyecto propio de analítica de datos aplicada: la base de datos hace cumplir las reglas del negocio por sí misma (no confía en la aplicación), una aplicación web chica la usa en el mostrador, y un generador produce **dos temporadas de datos sintéticos con una verdad conocida** para poder evaluar después un modelo de mantenimiento predictivo.

> **Estado:** base de datos, generador de datos y aplicación web terminados y probados (58 pruebas de reglas de la base, 82 pruebas de la aplicación, 16 invariantes sobre los datos). La fase 2, el modelo de riesgo de falla, también está terminada ([detalle](docs/modelo_riesgo.md)); falta el tablero (ver [Hoja de ruta](#hoja-de-ruta)).

## Qué tiene de interesante

- **Reglas en la base, no en la aplicación.** 26 tablas, 9 vistas y 20 triggers. Una bicicleta no puede salir si no está disponible en esa estación, no se vende más cupo del que hay, no se reembolsa más de lo cobrado, y el estado de una bicicleta solo cambia por una función que deja el historial.
- **Reservas por tipo y estación, con cupo.** Se reserva "2 urbanas y 1 mountain bike en la Costanera"; la unidad se asigna al retirar. El cupo lo calcula la base con un bloqueo por estación y tipo, así que dos mostradores no pueden vender la misma bicicleta.
- **Alquileres de varias bicicletas, por hora o por día.** Cada bicicleta se devuelve por separado (incluso en otra estación). El precio se copia al alquiler al salir: un aumento posterior no cambia lo contratado. Se cobra el tiempo real con tolerancia, y nunca sale más caro por hora que por día.
- **Mantenimiento por horas de uso y por calendario.** Vistas SQL (`v_proximo_servicio`) dicen qué tarea vence en cada bicicleta, con el ritmo de uso de los últimos 90 días. Es la línea base que un modelo tiene que superar.
- **Datos sintéticos con verdad conocida.** 25 meses, ~6.900 alquileres, ~3.600 reservas y ~550 incidencias, generados por una simulación cronológica. El riesgo de falla depende del atraso del mantenimiento, de la edad y de una fragilidad oculta de cada bicicleta; esos parámetros se guardan aparte ([detalle](docs/datos_sinteticos.md)).

## Inicio rápido

Requisitos: PostgreSQL 14 o superior (probado en 16, y en Supabase).

```bash
createdb bicis
./scripts/cargar_demo.sh "postgresql://usuario@localhost/bicis"
```

Sin `psql` (por ejemplo en Windows): `pip install "psycopg[binary]"`, definir `DATABASE_URL` en el entorno y correr `python scripts/cargar_demo.py` sobre una base que ya tenga `db/schema.sql`. Conserva los usuarios que existan y se niega a correr sobre una base con datos. La carga tarda menos de un minuto en local.

Queda cargado:

| Qué | Cantidad |
| --- | --- |
| Bicicletas (6 tipos, 3 estaciones y un taller) | 72 |
| Clientes | ~5.500 |
| Reservas | ~3.600 |
| Alquileres (con ~12.700 bicicletas sacadas) | ~6.900 |
| Pagos, señas y reembolsos | ~10.800 |
| Incidencias | ~550 |
| Órdenes de taller | ~2.600 |
| Cambios de estado registrados | ~30.800 |

### Consultas para probar

```sql
-- Qué mantenimiento está vencido, por bicicleta
SELECT codigo, tarea, horas_restantes, dias_restantes
FROM v_proximo_servicio
WHERE horas_restantes < 0 OR dias_restantes < 0
ORDER BY LEAST(horas_restantes, dias_restantes * 1.0)
LIMIT 10;

-- Lo que deja cada tipo de bicicleta, descontado el mantenimiento
SELECT tipo, count(*) AS bicis, round(avg(ingresos)) AS ingreso_medio,
       round(avg(costo_mantenimiento)) AS mantenimiento_medio, round(avg(margen)) AS margen_medio
FROM v_rentabilidad_bicicleta GROUP BY tipo ORDER BY margen_medio DESC;

-- Ingresos por mes y tipo
SELECT * FROM v_ingresos_mensuales ORDER BY mes DESC, ingresos DESC LIMIT 12;

-- Alquileres que ya pasaron su hora de devolución
SELECT * FROM v_alquileres_demorados ORDER BY horas_de_demora DESC;
```

## La aplicación web

FastAPI + Jinja2 + psycopg, sin JavaScript propio. Tablero con disponibilidad por estación, reservas, retiro y devolución (con registro de daños y cargos), cobros, clientes, taller (órdenes de mantenimiento) e informes. Roles: `ADMIN`, `MOSTRADOR` y `TECNICO`.

```bash
pip install -r app/requirements.txt
export DATABASE_URL="postgresql://usuario@localhost/bicis"
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
python -m app.crear_usuario lucia.ferrer@bicis.test --rol ADMIN   # pide la contraseña por teclado
uvicorn app.main:app --reload
```

En PowerShell: `$env:DATABASE_URL='...'` y `$env:SECRET_KEY='...'` en lugar de `export`.

La primera vez que alguien ingresa con una contraseña temporal, la aplicación obliga a cambiarla. Los usuarios de los datos de demostración existen **sin contraseña**: no pueden entrar hasta que les asignes una con `app.crear_usuario`.

Seguridad: contraseñas con Argon2, sesión en cookie firmada, token CSRF en cada formulario, política de contenido restrictiva, límite de intentos de acceso y permisos por rol leídos en cada pedido. Detalle en [docs/diseno.md](docs/diseno.md).

### Publicarla en internet

1. **Base:** crear un proyecto gratuito en Supabase, abrir el editor SQL y ejecutar `db/schema.sql` y después `db/supabase_seguridad.sql` (cierra la API pública de Supabase, que esta app no usa). Cargar los datos con `scripts/cargar_demo.py` usando la cadena del **Session pooler**.
2. **Aplicación:** en Render, *New → Blueprint* y elegir este repositorio. Cargar `DATABASE_URL` en el panel de Render (el `render.yaml` ya genera `SECRET_KEY` y marca producción).
3. Crear el primer administrador desde tu máquina con `python -m app.crear_usuario` apuntando a la misma base.

## Pruebas

```bash
# Reglas de la base (sobre una base vacía con solo el esquema)
DATABASE_URL=postgresql://.../bicis_prueba python3 tests/prueba_reglas.py

# Invariantes del conjunto de datos (sobre la base ya cargada)
psql "$DATABASE_URL" -f tests/verificar_datos.sql

# Modelo de riesgo de falla (solo lee; antes correr modelo/riesgo_falla.py --escribir)
DATABASE_URL=postgresql://.../bicis python3 tests/prueba_modelo.py

# Aplicación de punta a punta (escribe en la base: usar una copia)
DATABASE_URL=postgresql://.../bicis_app SECRET_KEY=... python3 tests/prueba_app.py
```

## Regenerar los datos

```bash
python3 generador/generar_datos.py --hasta 2026-11-04T12:00 --salida data/seed.sql.gz
```

Es determinista: la misma semilla y fecha dan exactamente el mismo archivo. `--escala 0.5` reduce a la mitad la demanda. Todos los nombres, documentos, teléfonos y correos son inventados (dominios reservados `.test`).

## Estructura

```
db/           esquema (schema.sql) y cierre de seguridad para Supabase
.github/      job diario que actualiza las predicciones de riesgo
generador/    simulación que produce los datos sintéticos
data/         seed.sql.gz y la verdad simulada (verdad_*.csv)
app/          aplicación web
modelo/       modelo de riesgo de falla (fase 2) y sus resultados
scripts/      cargadores de la demo
tests/        reglas de la base, invariantes de los datos y aplicación
docs/         diseño, diagrama entidad-relación y datos sintéticos
```

## Hoja de ruta

1. **Hecho:** base con reglas, generador, aplicación de mostrador.
2. **Hecho:** modelo de riesgo de falla por bicicleta y sistema (tasa por hora de uso con regresión de Poisson, evaluada contra la regla de vencimiento y contra la verdad simulada). Resultados en `prediccion_mantenimiento`, que se actualiza sola todos los días con un job de GitHub Actions y se usa para ordenar el taller por riesgo. Detalle, límites y cómo activarlo en [docs/modelo_riesgo.md](docs/modelo_riesgo.md).
3. **Tablero en Power BI** sobre las vistas (ocupación, ingresos, rentabilidad por bicicleta, mantenimiento vencido).
4. Reserva en línea para clientes con pago de la seña, y redistribución de bicicletas entre estaciones.

## Licencia

MIT. Ver [LICENSE](LICENSE).
