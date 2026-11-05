# Modelo de datos

Relaciones principales del esquema (`db/schema.sql`). Las claves foráneas son todas reales; los
historiales y la auditoría no se dibujan con todos sus vínculos para que el diagrama se pueda leer.

```mermaid
erDiagram
    usuario ||--o{ usuario_rol : tiene
    usuario ||--o| credencial_acceso : "ingresa con"
    rol ||--o{ usuario_rol : "se asigna en"

    tipo_bicicleta ||--o{ bicicleta : clasifica
    estado_bicicleta ||--o{ bicicleta : "estado actual"
    ubicacion ||--o{ bicicleta : "estación base"
    ubicacion |o--o{ bicicleta : "dónde está ahora"
    bicicleta ||--o{ historial_estado_bicicleta : registra
    tipo_bicicleta ||--o{ tarifa : "precio en el tiempo"

    cliente ||--o{ reserva : hace
    ubicacion ||--o{ reserva : "estación de retiro"
    reserva ||--|{ reserva_detalle : "pide por tipo"
    tipo_bicicleta ||--o{ reserva_detalle : "tipo pedido"

    cliente ||--o{ alquiler : contrata
    reserva |o--o| alquiler : "se convierte en"
    usuario ||--o{ alquiler : "atiende"
    alquiler ||--|{ alquiler_detalle : "una fila por bicicleta"
    bicicleta ||--o{ alquiler_detalle : "sale en"

    reserva ||--o{ pago : "seña"
    alquiler ||--o{ pago : cobro
    pago |o--o{ pago : "reembolsa"
    alquiler ||--o{ cargo_extra : suma
    alquiler_detalle |o--o{ cargo_extra : "por bicicleta"

    bicicleta ||--o{ incidencia : sufre
    alquiler_detalle |o--o{ incidencia : "ocurrió en"

    tipo_bicicleta ||--o{ plan_mantenimiento : define
    bicicleta ||--o{ orden_mantenimiento : recibe
    plan_mantenimiento |o--o{ orden_mantenimiento : "origina (preventivo)"
    incidencia |o--o{ orden_mantenimiento : "origina (correctivo)"
    tipo_mantenimiento ||--o{ orden_mantenimiento : clasifica
    estado_orden ||--o{ orden_mantenimiento : estado
    ubicacion ||--o{ orden_mantenimiento : "taller"
    orden_mantenimiento ||--o{ orden_item : detalla
    orden_mantenimiento ||--o{ historial_orden : registra

    bicicleta ||--o{ prediccion_mantenimiento : "riesgo estimado (fase 2)"
```

## Vistas

| Vista | Para qué sirve |
| --- | --- |
| `v_disponibilidad_estacion` | Flota, disponibles, alquiladas y en taller por estación y tipo. |
| `v_alquileres_demorados` | Alquileres en curso que ya pasaron su hora de devolución. |
| `v_reservas_por_vencer` | Reservas vigentes cuyo cliente no se presentó pasada la tolerancia. |
| `v_saldo_alquiler` | Lo devengado, lo cobrado (la seña de la reserva cuenta) y el saldo. |
| `v_ingresos_mensuales` | Ingresos, horas y bicicletas alquiladas por mes y tipo. |
| `v_rentabilidad_bicicleta` | Ingresos y cargos menos mantenimiento, por bicicleta. |
| `v_ritmo_uso` | Horas de uso por día de cada bicicleta en los últimos 90 días. |
| `v_ultimo_servicio` | Último servicio preventivo cerrado de cada tarea del plan. |
| `v_proximo_servicio` | Horas y días que faltan para cada tarea, y fecha estimada según el ritmo de uso. |
