# Decisiones de diseño

## Las reglas viven en la base

La aplicación puede cambiar, equivocarse o ser reemplazada por otra (un tablero, una API, un script de carga).
Por eso las reglas que protegen los datos están en PostgreSQL, con restricciones y triggers, y la aplicación
solo traduce los rechazos a mensajes en castellano. Las pruebas de las reglas (`tests/prueba_reglas.py`)
corren contra la base sola, sin la aplicación.

Reglas que hace cumplir la base:

- Una bicicleta solo sale si está **disponible y en la estación de retiro**. El estado cambia únicamente por
  `fn_bici_cambiar_estado()`, que además mueve la bicicleta de lugar y escribe el historial; un `UPDATE`
  directo del estado se rechaza.
- **Cupo de reservas.** Se reserva por *tipo* y estación; `fn_cupo()` descuenta la flota activa, las reservas
  vigentes que se superponen y las bicicletas de esa estación que siguen afuera y vuelven después del inicio
  pedido. Un bloqueo asesor por estación y tipo evita que dos transacciones vendan el último lugar a la vez.
- **Máquina de estados** de reservas (pendiente → confirmada → convertida; cancelada o vencida desde cualquiera
  de las dos primeras) y de órdenes de mantenimiento (abierta → en curso → cerrada; cancelable).
- **Tarifas con historial.** El precio vigente se copia a cada fila de `alquiler_detalle` al salir; un aumento
  posterior no altera lo contratado.
- **Importe** (`fn_importe`): se cobra el tiempo real. Por hora: horas completas con 10 minutos de tolerancia,
  mínimo una, con tope en el precio de los días que corresponden (nunca sale más caro que por día). Por día:
  días completos con 1 hora de tolerancia, mínimo uno. La demora en devolver se paga sola.
- **Devolución por bicicleta.** Cada fila se cierra por separado; al cerrarse la última, el alquiler se
  finaliza solo. La bicicleta suma horas y usos y vuelve disponible, o *fuera de servicio* si volvió dañada.
  Una devolución ya registrada no se puede modificar.
- **Pagos.** Un reembolso solo puede salir de un cobro o seña aprobados, del mismo alquiler o reserva, y la
  suma de los reembolsos no puede superar lo cobrado. El saldo de un alquiler incluye la seña de su reserva.
- **Mantenimiento.** Abrir una orden saca la bicicleta de circulación (y se rechaza si está alquilada); cerrarla
  o cancelarla la devuelve a su estación base si no quedan otras órdenes abiertas. El costo de la orden es
  siempre la suma de sus ítems, y los ítems de una orden cerrada no se tocan.
- **Documento de cliente** normalizado (solo letras y números, mayúsculas) y único por tipo y país.

## Horas de uso

`bicicleta.horas_uso` suma el tiempo **alquilado**, no el de pedaleo: una bicicleta que sale dos días suma 48
horas. Es una simplificación a propósito: es lo que el sistema puede medir sin sensores. Los planes de
mantenimiento combinan horas y calendario (lo que ocurra primero) para que un alquiler largo no distorsione.
Con telemetría (GPS o sensor de pedaleo) se agregaría una tabla de lecturas y el contador pasaría a ser real.

## Mantenimiento en dos fases

1. **Reglas** (hecho). `v_proximo_servicio` calcula, por bicicleta y tarea, las horas y días restantes y la
   fecha estimada según el ritmo de uso de los últimos 90 días.
2. **Modelo de riesgo** (pendiente). Estimar la probabilidad de una falla por sistema en los próximos N días y
   escribirla en `prediccion_mantenimiento`. Tiene que superar a la fase 1; la verdad con la que se evalúa está
   en [datos_sinteticos.md](datos_sinteticos.md).

## Permisos

| Operación | ADMIN | MOSTRADOR | TECNICO |
| --- | :-: | :-: | :-: |
| Ver tablero, bicicletas e informes | ✔ | ✔ | ✔ |
| Reservas, alquileres, devoluciones, cobros, clientes | ✔ | ✔ | — |
| Abrir, iniciar y cerrar órdenes de taller | ✔ | — | ✔ |

Los roles se leen de la base en cada pedido: dar de baja a un usuario o quitarle un rol rige al instante.

## Seguridad de la aplicación

- Contraseñas con Argon2; mínimo 12 caracteres con mayúsculas, minúsculas y un número; cambio obligatorio
  del primer ingreso. El tiempo de respuesta del login no revela qué correos existen.
- Sesión en cookie firmada (`HttpOnly`, `SameSite=Lax`, `Secure` en producción) con vencimiento.
- Token CSRF en todos los formularios que escriben.
- Límite de 5 intentos fallidos por IP y correo cada 15 minutos (en memoria: la app corre en un solo proceso).
- Política de contenido restrictiva (`default-src 'self'`), sin JavaScript propio ni recursos externos.
- Consultas siempre parametrizadas; la salida de las plantillas se escapa.
- En Supabase se activa RLS sin políticas y se quitan los permisos de `anon` y `authenticated`
  (`db/supabase_seguridad.sql`): la app usa una conexión directa a Postgres, no la API de Supabase.

## Limitaciones conocidas

- `fn_cupo()` cuenta como flota activa a las bicicletas *en mantenimiento* (solo excluye bajas y fuera de
  servicio). Una reserva puede aceptarse con una bicicleta que sale del taller más tarde de lo previsto; en la
  simulación eso termina, a veces, en una cancelación del local por falta de bicicletas.
- No hay robo ni pérdida de bicicletas en los datos generados: un detalle de alquiler solo se cierra con una
  devolución. El tipo de incidencia `ROBO_PERDIDA` existe, pero su circuito (cerrar un alquiler sin devolución y
  dar de baja) queda para una versión siguiente.
- Los cobros con tarjeta se registran como medio de pago, sin integración con ninguna pasarela.
- Las vistas con ritmo de uso y plazos comparan contra `now()` y `current_date`: la demo envejece. Ver
  [datos_sinteticos.md](datos_sinteticos.md#la-demo-envejece).
