-- Invariantes que deben cumplirse sobre el conjunto de datos generado. Cada fila debe dar 0.
\pset tuples_only on
\pset format unaligned
\pset fieldsep ' | '
WITH chk(nombre, malos) AS (
 VALUES
 ('bici ALQUILADA sin detalle abierto', (SELECT count(*) FROM bicicleta b JOIN estado_bicicleta e ON e.id=b.estado_id
    WHERE e.codigo='ALQUILADA' AND NOT EXISTS (SELECT 1 FROM alquiler_detalle d WHERE d.bicicleta_id=b.id AND d.devuelta_en IS NULL AND d.anulado_en IS NULL))),
 ('detalle abierto con bici no ALQUILADA', (SELECT count(*) FROM alquiler_detalle d JOIN bicicleta b ON b.id=d.bicicleta_id JOIN estado_bicicleta e ON e.id=b.estado_id
    WHERE d.devuelta_en IS NULL AND d.anulado_en IS NULL AND e.codigo<>'ALQUILADA')),
 ('bici EN_MANTENIMIENTO sin orden abierta', (SELECT count(*) FROM bicicleta b JOIN estado_bicicleta e ON e.id=b.estado_id
    WHERE e.codigo='EN_MANTENIMIENTO' AND NOT EXISTS (SELECT 1 FROM orden_mantenimiento o JOIN estado_orden s ON s.id=o.estado_id WHERE o.bicicleta_id=b.id AND s.codigo IN ('ABIERTA','EN_CURSO')))),
 ('orden abierta con bici disponible/alquilada', (SELECT count(*) FROM orden_mantenimiento o JOIN estado_orden s ON s.id=o.estado_id JOIN bicicleta b ON b.id=o.bicicleta_id JOIN estado_bicicleta e ON e.id=b.estado_id
    WHERE s.codigo IN ('ABIERTA','EN_CURSO') AND e.codigo IN ('DISPONIBLE','ALQUILADA'))),
 ('ultimo historial distinto del estado actual', (SELECT count(*) FROM bicicleta b WHERE b.estado_id IS DISTINCT FROM
    (SELECT h.estado_nuevo_id FROM historial_estado_bicicleta h WHERE h.bicicleta_id=b.id ORDER BY h.cambiado_en DESC, h.id DESC LIMIT 1))),
 ('horas_uso menor que lo alquilado', (SELECT count(*) FROM bicicleta b WHERE b.horas_uso < COALESCE((SELECT sum(round(d.segundos_uso/3600.0,2)) FROM alquiler_detalle d WHERE d.bicicleta_id=b.id),0))),
 ('costo de orden distinto de suma de items', (SELECT count(*) FROM orden_mantenimiento o WHERE o.costo_total <> COALESCE((SELECT sum(round(cantidad*costo_unitario,2)) FROM orden_item i WHERE i.orden_id=o.id),0))),
 ('alquiler finalizado con saldo <> total no debido', (SELECT count(*) FROM v_saldo_alquiler s WHERE s.estado='FINALIZADO' AND s.saldo < 0)),
 ('alquiler finalizado con saldo > cargos', (SELECT count(*) FROM v_saldo_alquiler s WHERE s.estado='FINALIZADO' AND s.saldo > s.cargos)),
 ('retorno_real distinto del max devuelta', (SELECT count(*) FROM alquiler a WHERE a.retorno_real IS NOT NULL AND a.retorno_real <> (SELECT max(devuelta_en) FROM alquiler_detalle d WHERE d.alquiler_id=a.id))),
 ('reserva abierta con cerrada_en', (SELECT count(*) FROM reserva WHERE estado IN ('PENDIENTE','CONFIRMADA') AND cerrada_en IS NOT NULL)),
 ('reserva convertida sin alquiler', (SELECT count(*) FROM reserva r WHERE estado='CONVERTIDA' AND NOT EXISTS (SELECT 1 FROM alquiler a WHERE a.reserva_id=r.id))),
 ('reembolsos > pago original', (SELECT count(*) FROM pago p WHERE p.tipo<>'REEMBOLSO' AND p.estado='APROBADO' AND
    (SELECT COALESCE(sum(monto),0) FROM pago r WHERE r.pago_origen_id=p.id AND r.estado='APROBADO') > p.monto)),
 ('incidencia sin resolver con orden cerrada', (SELECT count(*) FROM incidencia i WHERE resuelta_en IS NULL AND EXISTS
    (SELECT 1 FROM orden_mantenimiento o JOIN estado_orden s ON s.id=o.estado_id WHERE o.incidencia_id=i.id AND s.codigo='CERRADA'))),
 ('mas de 1 estado de ubicacion inconsistente', (SELECT count(*) FROM bicicleta b JOIN estado_bicicleta e ON e.id=b.estado_id
    WHERE (e.codigo='ALQUILADA') <> (b.ubicacion_id IS NULL))),
 ('detalle con importe <> fn_importe', (SELECT count(*) FROM alquiler_detalle d WHERE d.devuelta_en IS NOT NULL AND d.importe <> fn_importe(d.modalidad,d.precio_hora,d.precio_dia,d.segundos_uso)))
)
SELECT nombre, malos, CASE WHEN malos=0 THEN 'ok' ELSE 'FALLA' END FROM chk;
