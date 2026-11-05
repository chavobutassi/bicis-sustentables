"""Pruebas de las reglas de la base de datos de Bicis sustentables.

Corre sobre una base VACÍA con db/schema.sql ya cargado (crea sus propios datos
de prueba y no sirve sobre una base con datos reales):

    createdb bicis_prueba && psql -q -v ON_ERROR_STOP=1 -f db/schema.sql bicis_prueba
    DATABASE_URL=postgresql://.../bicis_prueba python3 tests/prueba_reglas.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import psycopg
from psycopg.rows import dict_row

TZ = timezone(timedelta(hours=-3))
fallos = []


def t(*a):
    return datetime(*a, tzinfo=TZ)


def verificar(cond, texto):
    print(("  ok    " if cond else "  FALLA ") + texto)
    if not cond:
        fallos.append(texto)


con = psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row, autocommit=True)
if con.execute("SELECT count(*) AS n FROM bicicleta").fetchone()["n"]:
    sys.exit("La base no está vacía: esta prueba necesita una base nueva con solo el esquema.")


def uno(sql, p=None):
    return con.execute(sql, p).fetchone()


def val(sql, p=None):
    r = uno(sql, p)
    return next(iter(r.values())) if r else None


def rechaza(sql, p, fragmento, texto):
    """La sentencia debe fallar y el mensaje de la base debe contener `fragmento`."""
    try:
        con.execute(sql, p)
    except psycopg.Error as e:
        verificar(fragmento.lower() in str(e).lower(), f"{texto}  [{str(e).splitlines()[0][:70]}]")
        return
    verificar(False, f"{texto}  [no fue rechazado]")


def estado(codigo):
    return uno("""SELECT e.codigo AS estado, b.ubicacion_id, b.horas_uso, b.usos FROM bicicleta b
                    JOIN estado_bicicleta e ON e.id = b.estado_id WHERE b.codigo = %s""", (codigo,))


# ---------------------------------------------------------------- datos de prueba
con.execute("INSERT INTO usuario (nombre, apellido, email) VALUES ('Ana','Mostrador','ana@prueba.test'), ('Tito','Tecnico','tito@prueba.test')")
for nombre, tipo in [("Costanera", "ESTACION"), ("Parque", "ESTACION"), ("Taller", "TALLER")]:
    con.execute("INSERT INTO ubicacion (nombre, tipo) VALUES (%s, %s)", (nombre, tipo))
con.execute("INSERT INTO tipo_bicicleta (codigo, nombre) VALUES ('URBANA','Urbana'), ('MTB','Mountain bike')")
con.execute("""INSERT INTO tarifa (tipo_bicicleta_id, vigente_desde, precio_hora, precio_dia) VALUES
               (1,'2025-01-01',3000,12000),(1,'2026-01-01',3500,14000),(2,'2026-01-01',5000,20000)""")
for i in range(1, 4):
    con.execute("""INSERT INTO bicicleta (codigo, tipo_bicicleta_id, estado_id, ubicacion_base_id, ubicacion_id)
                   VALUES (%s, 1, 1, 1, 1)""", (f"U-{i:02d}",))
con.execute("""INSERT INTO bicicleta (codigo, tipo_bicicleta_id, estado_id, ubicacion_base_id, ubicacion_id)
               VALUES ('M-01', 2, 1, 1, 1), ('P-01', 1, 1, 2, 2)""")
con.execute("""INSERT INTO cliente (nombre, apellido, tipo_documento, numero_documento) VALUES
               ('Luis','Pérez','DNI','12.345.678'), ('Eva','Gómez','PASAPORTE','ab 123 456')""")
OPER, TEC = 1, 2
CLI1, CLI2 = 1, 2


def alquilar(cliente, salida, fin, bicis, estacion=1, reserva=None, modalidad="HORA"):
    with con.transaction():
        aid = val("""INSERT INTO alquiler (cliente_id, reserva_id, ubicacion_retiro_id, operador_id, salida_real, fin_previsto)
                     VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""", (cliente, reserva, estacion, OPER, salida, fin))
        for b in bicis:
            con.execute("""INSERT INTO alquiler_detalle (alquiler_id, bicicleta_id, modalidad)
                           VALUES (%s, (SELECT id FROM bicicleta WHERE codigo=%s), %s)""", (aid, b, modalidad))
    return aid


def devolver(aid, bici, cuando, estacion=1, estado_dev="OK"):
    con.execute("""UPDATE alquiler_detalle SET devuelta_en=%s, ubicacion_devolucion_id=%s, estado_devolucion=%s
                    WHERE alquiler_id=%s AND bicicleta_id=(SELECT id FROM bicicleta WHERE codigo=%s)""",
                (cuando, estacion, estado_dev, aid, bici))


# ---------------------------------------------------------------- clientes
print("Clientes")
rechaza("""INSERT INTO cliente (nombre, apellido, tipo_documento, numero_documento) VALUES ('Otro','Pérez','DNI','12345678')""",
        None, "duplicate key", "el mismo DNI con otro formato (puntos) no se carga dos veces")
verificar(val("SELECT numero_documento FROM cliente WHERE id=2") == "AB123456", "el documento se normaliza (mayúsculas, sin espacios)")

# ---------------------------------------------------------------- alquiler y devolución
print("Alquiler de dos bicicletas")
a1 = alquilar(CLI1, t(2026, 3, 10, 10, 0), t(2026, 3, 10, 13, 0), ["U-01", "M-01"])
verificar(estado("U-01")["estado"] == "ALQUILADA" and estado("U-01")["ubicacion_id"] is None, "al salir, la bicicleta queda ALQUILADA y sin ubicación")
d = uno("SELECT precio_hora, precio_dia, tipo_bicicleta_id FROM alquiler_detalle WHERE alquiler_id=%s ORDER BY id LIMIT 1", (a1,))
verificar(d["precio_hora"] == 3500 and d["precio_dia"] == 14000, "toma la tarifa vigente a la fecha de salida (no la anterior)")
verificar(val("SELECT estado FROM alquiler WHERE id=%s", (a1,)) == "EN_CURSO", "el alquiler está EN_CURSO")
rechaza("INSERT INTO alquiler (cliente_id, ubicacion_retiro_id, operador_id, salida_real, fin_previsto) VALUES (1,1,1,%s,%s)",
        (t(2026, 3, 10, 10, 5), t(2026, 3, 10, 12, 0)), "no tiene ninguna bicicleta", "un alquiler sin bicicletas no se confirma")
a_x = None
try:
    with con.transaction():
        x = val("""INSERT INTO alquiler (cliente_id, ubicacion_retiro_id, operador_id, salida_real, fin_previsto)
                   VALUES (1,1,1,%s,%s) RETURNING id""", (t(2026, 3, 10, 10, 6), t(2026, 3, 10, 12, 0)))
        con.execute("INSERT INTO alquiler_detalle (alquiler_id, bicicleta_id, modalidad) VALUES (%s,(SELECT id FROM bicicleta WHERE codigo='U-01'),'HORA')", (x,))
except psycopg.Error as e:
    verificar("no está disponible" in str(e), "la misma bicicleta no puede estar en dos alquileres")
else:
    verificar(False, "la misma bicicleta no puede estar en dos alquileres")
try:
    alquilar(CLI1, t(2026, 3, 10, 10, 7), t(2026, 3, 10, 12, 0), ["P-01"], estacion=1)
except psycopg.Error as e:
    verificar("no está en la estación de retiro" in str(e), "no se retira una bicicleta que está en otra estación")
else:
    verificar(False, "no se retira una bicicleta que está en otra estación")

print("Importes (tolerancia, tope diario)")
for mod, ph, pd, seg, esperado, txt in [
    ("HORA", 3500, 14000, 60 * 60,        3500,  "1 h exacta = 1 hora"),
    ("HORA", 3500, 14000, 69 * 60,        3500,  "1 h 9 min: dentro de la tolerancia de 10 min"),
    ("HORA", 3500, 14000, 71 * 60,        7000,  "1 h 11 min: se cobra la 2.ª hora"),
    ("HORA", 3500, 14000, 5 * 60,         3500,  "5 minutos: mínimo de una hora"),
    ("HORA", 3500, 14000, 5 * 3600,       14000, "5 horas: el tope diario (14000) gana a 17500"),
    ("DIA",  3500, 14000, 25 * 3600,      14000, "día: 25 h dentro de la tolerancia de 1 h"),
    ("DIA",  3500, 14000, 26 * 3600,      28000, "día: 26 h = 2 días"),
]:
    verificar(val("SELECT fn_importe(%s,%s,%s,%s)", (mod, ph, pd, seg)) == esperado, txt)

print("Devolución")
devolver(a1, "U-01", t(2026, 3, 10, 12, 5))
verificar(estado("U-01")["estado"] == "DISPONIBLE" and estado("U-01")["ubicacion_id"] == 1, "al devolver, vuelve DISPONIBLE a la estación")
verificar(estado("U-01")["horas_uso"] == Decimal("2.08") and estado("U-01")["usos"] == 1, "suma las horas de uso (2,08 h) y un uso")
verificar(val("SELECT importe FROM alquiler_detalle WHERE alquiler_id=%s ORDER BY id LIMIT 1", (a1,)) == 7000, "importe: 2 h 5 min = 2 horas = 7.000")
verificar(val("SELECT retorno_real FROM alquiler WHERE id=%s", (a1,)) is None, "con una bicicleta pendiente el alquiler sigue EN_CURSO")
devolver(a1, "M-01", t(2026, 3, 10, 13, 30), estacion=2, estado_dev="CON_DANIO")
verificar(val("SELECT estado FROM alquiler WHERE id=%s", (a1,)) == "FINALIZADO", "al devolverse la última, el alquiler se FINALIZA solo")
verificar(estado("M-01")["estado"] == "FUERA_DE_SERVICIO" and estado("M-01")["ubicacion_id"] == 2, "devuelta dañada: FUERA_DE_SERVICIO en la estación donde se dejó")
rechaza("UPDATE alquiler_detalle SET devuelta_en=%s WHERE alquiler_id=%s", (t(2026, 3, 10, 14), a1), "ya fue devuelta", "una devolución registrada no se modifica")
rechaza("UPDATE bicicleta SET estado_id = 1 WHERE codigo='M-01'", None, "fn_bici_cambiar_estado", "el estado no se cambia con un UPDATE directo")
rechaza("UPDATE alquiler SET anulada_en=%s, motivo_anulacion='x' WHERE id=%s", (t(2026, 3, 11), a1), "ya se devolvieron", "no se anula un alquiler ya finalizado")

# ---------------------------------------------------------------- mantenimiento
print("Mantenimiento")
con.execute("""INSERT INTO plan_mantenimiento (tipo_bicicleta_id, tarea, sistema, cada_horas, cada_dias)
               VALUES (2,'Revisión de frenos','FRENOS',80,90)""")
ABIERTA, EN_CURSO, CERRADA, CANCELADA = (val("SELECT id FROM estado_orden WHERE codigo=%s", (c,)) for c in ("ABIERTA", "EN_CURSO", "CERRADA", "CANCELADA"))
CORR = val("SELECT id FROM tipo_mantenimiento WHERE codigo='CORRECTIVO'")
PREV = val("SELECT id FROM tipo_mantenimiento WHERE codigo='PREVENTIVO'")
bici_m = val("SELECT id FROM bicicleta WHERE codigo='M-01'")
oid = val("""INSERT INTO orden_mantenimiento (bicicleta_id, tipo_id, estado_id, taller_id, abierta_en, tecnico_id)
             VALUES (%s,%s,%s,3,%s,%s) RETURNING id""", (bici_m, CORR, ABIERTA, t(2026, 3, 10, 15), TEC))
verificar(estado("M-01")["estado"] == "EN_MANTENIMIENTO" and estado("M-01")["ubicacion_id"] == 3, "al abrir la orden, la bicicleta pasa a EN_MANTENIMIENTO (en el taller)")
verificar(val("SELECT horas_uso FROM orden_mantenimiento WHERE id=%s", (oid,)) == Decimal("3.50"), "la orden registra las horas de uso al ingresar (3,5 h de la última salida)")
rechaza("UPDATE orden_mantenimiento SET estado_id=%s, cerrada_en=%s WHERE id=%s", (CERRADA, t(2026, 3, 11), oid), "no puede pasar", "una orden abierta no se cierra sin pasar por EN CURSO")
con.execute("UPDATE orden_mantenimiento SET estado_id=%s, iniciada_en=%s WHERE id=%s", (EN_CURSO, t(2026, 3, 11, 9), oid))
con.execute("INSERT INTO orden_item (orden_id, descripcion, cantidad, costo_unitario) VALUES (%s,'Pastillas de freno',2,4500.50), (%s,'Mano de obra',1,6000)", (oid, oid))
verificar(val("SELECT costo_total FROM orden_mantenimiento WHERE id=%s", (oid,)) == Decimal("15001.00"), "el costo de la orden es la suma de sus ítems (2×4.500,50 + 6.000)")
con.execute("UPDATE orden_mantenimiento SET estado_id=%s, cerrada_en=%s WHERE id=%s", (CERRADA, t(2026, 3, 11, 17), oid))
verificar(estado("M-01")["estado"] == "DISPONIBLE" and estado("M-01")["ubicacion_id"] == 1, "al cerrar la orden, vuelve DISPONIBLE a su estación de origen")
rechaza("INSERT INTO orden_item (orden_id, descripcion, costo_unitario) VALUES (%s,'Tarde',100)", (oid,), "ya está cerrada", "no se agregan ítems a una orden cerrada")
alquilar(CLI1, t(2026, 3, 12, 9), t(2026, 3, 12, 12), ["U-02"])
rechaza("""INSERT INTO orden_mantenimiento (bicicleta_id, tipo_id, estado_id, taller_id, abierta_en)
           VALUES ((SELECT id FROM bicicleta WHERE codigo='U-02'),%s,%s,3,%s)""", (CORR, ABIERTA, t(2026, 3, 12, 10)),
        "alquilada", "una bicicleta alquilada no puede ingresar a taller")
rechaza("""INSERT INTO orden_mantenimiento (bicicleta_id, tipo_id, estado_id, taller_id, abierta_en)
           VALUES (%s,%s,%s,3,%s)""", (bici_m, PREV, ABIERTA, t(2026, 3, 13)), "plan", "una orden preventiva exige plan de mantenimiento")
# dos órdenes abiertas: la bicicleta solo vuelve cuando se cierran las dos
o1 = val("INSERT INTO orden_mantenimiento (bicicleta_id,tipo_id,estado_id,taller_id,abierta_en) VALUES (%s,%s,%s,3,%s) RETURNING id", (bici_m, CORR, ABIERTA, t(2026, 3, 14, 8)))
o2 = val("INSERT INTO orden_mantenimiento (bicicleta_id,tipo_id,estado_id,taller_id,abierta_en) VALUES (%s,%s,%s,3,%s) RETURNING id", (bici_m, CORR, ABIERTA, t(2026, 3, 14, 8, 1)))
con.execute("UPDATE orden_mantenimiento SET estado_id=%s, cerrada_en=%s WHERE id=%s", (CANCELADA, t(2026, 3, 14, 12), o1))
verificar(estado("M-01")["estado"] == "EN_MANTENIMIENTO", "con otra orden abierta, la bicicleta sigue en mantenimiento")
con.execute("UPDATE orden_mantenimiento SET estado_id=%s, cerrada_en=%s WHERE id=%s", (CANCELADA, t(2026, 3, 14, 13), o2))
verificar(estado("M-01")["estado"] == "DISPONIBLE", "al cerrarse la última orden, vuelve a estar DISPONIBLE")

# ---------------------------------------------------------------- reservas y cupo
print("Reservas y cupo")
# URBANA en Costanera: U-01, U-02 (alquilada hasta 12:00 del 12/3 ... ya devuelta abajo), U-03
devolver(val("SELECT id FROM alquiler WHERE cliente_id=1 AND salida_real=%s", (t(2026, 3, 12, 9),)), "U-02", t(2026, 3, 12, 11))
verificar(val("SELECT fn_cupo(1, 1::smallint, %s, %s)", (t(2026, 4, 1, 10), t(2026, 4, 1, 14))) == 3, "cupo inicial: 3 urbanas en Costanera")


def reservar(cliente, ini, fin, tipo, cant, estacion=1, canal="MOSTRADOR", creada=t(2026, 3, 20)):
    with con.transaction():
        rid = val("""INSERT INTO reserva (cliente_id, ubicacion_id, inicio_previsto, fin_previsto, estado, canal, creada_en)
                     VALUES (%s,%s,%s,%s,'CONFIRMADA',%s,%s) RETURNING id""", (cliente, estacion, ini, fin, canal, creada))
        con.execute("INSERT INTO reserva_detalle (reserva_id, tipo_bicicleta_id, cantidad) VALUES (%s,%s,%s)", (rid, tipo, cant))
    return rid


r1 = reservar(CLI1, t(2026, 4, 1, 10), t(2026, 4, 1, 14), 1, 2)
verificar(val("SELECT fn_cupo(1, 1::smallint, %s, %s)", (t(2026, 4, 1, 12), t(2026, 4, 1, 16))) == 1, "con 2 reservadas, queda 1 en horarios que se superponen")
verificar(val("SELECT fn_cupo(1, 1::smallint, %s, %s)", (t(2026, 4, 1, 14), t(2026, 4, 1, 18))) == 3, "pasadas las 14 h el cupo vuelve a ser 3")
try:
    reservar(CLI2, t(2026, 4, 1, 11), t(2026, 4, 1, 13), 1, 2)
except psycopg.Error as e:
    verificar("no hay cupo" in str(e).lower(), "pedir más del cupo restante se rechaza (se piden 2, queda 1)")
else:
    verificar(False, "pedir más del cupo restante se rechaza")
r2 = reservar(CLI2, t(2026, 4, 1, 11), t(2026, 4, 1, 13), 1, 1)
verificar(True, "pedir el último que queda se acepta")
con.execute("UPDATE reserva SET estado='CANCELADA', cerrada_en=%s, motivo_cierre='Cambio de planes' WHERE id=%s", (t(2026, 3, 25), r1))
verificar(val("SELECT fn_cupo(1, 1::smallint, %s, %s)", (t(2026, 4, 1, 11), t(2026, 4, 1, 13))) == 2, "al cancelar una reserva, se libera su cupo")
rechaza("UPDATE reserva SET estado='CONFIRMADA', cerrada_en=NULL WHERE id=%s", (r1,), "no puede pasar", "una reserva cancelada no se reabre")
rechaza("INSERT INTO reserva_detalle (reserva_id, tipo_bicicleta_id, cantidad) VALUES (%s,2,1)", (r1,), "ya no se puede modificar", "no se agregan bicicletas a una reserva cancelada")
rechaza("""INSERT INTO reserva (cliente_id, ubicacion_id, inicio_previsto, fin_previsto, canal, creada_en)
           VALUES (1,1,%s,%s,'WEB',%s)""", (t(2026, 4, 1, 10), t(2026, 4, 1, 12), t(2026, 4, 2)), "check", "una reserva no puede empezar antes de crearse")
# retiro con reserva
a2 = alquilar(CLI2, t(2026, 4, 1, 11, 5), t(2026, 4, 1, 13), ["U-03"], reserva=r2)
verificar(val("SELECT estado FROM reserva WHERE id=%s", (r2,)) == "CONVERTIDA", "al retirar, la reserva pasa a CONVERTIDA")
r3 = reservar(CLI1, t(2026, 4, 5, 10), t(2026, 4, 5, 12), 1, 1)
try:
    alquilar(CLI2, t(2026, 4, 5, 10), t(2026, 4, 5, 12), ["U-01"], reserva=r3)
except psycopg.Error as e:
    verificar("no coincide" in str(e), "no se retira con la reserva de otro cliente")
else:
    verificar(False, "no se retira con la reserva de otro cliente")

# ---------------------------------------------------------------- pagos
print("Pagos")
con.execute("""INSERT INTO pago (reserva_id, tipo, monto, medio, creado_en) VALUES (%s,'SENIA',3000,'TARJETA',%s)""", (r2, t(2026, 3, 20)))
senia = val("SELECT id FROM pago WHERE reserva_id=%s AND tipo='SENIA'", (r2,))
rechaza("INSERT INTO pago (reserva_id, tipo, monto, medio, pago_origen_id) VALUES (%s,'REEMBOLSO',3500,'TARJETA',%s)", (r2, senia), "no se puede reembolsar", "no se devuelve más de lo cobrado")
con.execute("INSERT INTO pago (reserva_id, tipo, monto, medio, pago_origen_id) VALUES (%s,'REEMBOLSO',1000,'TARJETA',%s)", (r2, senia))
rechaza("INSERT INTO pago (reserva_id, tipo, monto, medio, pago_origen_id) VALUES (%s,'REEMBOLSO',2500,'TARJETA',%s)", (r2, senia), "no se puede reembolsar", "tampoco entre varios reembolsos (quedan 2.000)")
rechaza("INSERT INTO pago (alquiler_id, tipo, monto, medio) VALUES (%s,'SENIA',100,'EFECTIVO')", (a2,), "check", "una seña se asocia a una reserva")
devolver(a2, "U-03", t(2026, 4, 1, 12, 50))
con.execute("INSERT INTO pago (alquiler_id, tipo, monto, medio) VALUES (%s,'COBRO',1500,'EFECTIVO')", (a2,))
s = uno("SELECT * FROM v_saldo_alquiler WHERE alquiler_id=%s", (a2,))
verificar(s["total"] == 7000 and s["pagado"] == 3500 and s["saldo"] == 3500,
          f"saldo: total 7.000 (1 h 45 min = 2 horas), pagado 3.500 = seña 3.000 − reembolso 1.000 + cobro 1.500 (total {s['total']}, pagado {s['pagado']}, saldo {s['saldo']})")
con.execute("INSERT INTO cargo_extra (alquiler_id, detalle_id, concepto, monto) VALUES (%s,(SELECT id FROM alquiler_detalle WHERE alquiler_id=%s),'DANIO',2000)", (a2, a2))
verificar(uno("SELECT saldo FROM v_saldo_alquiler WHERE alquiler_id=%s", (a2,))["saldo"] == 5500, "un cargo por daños de 2.000 aumenta el saldo a 5.500")
rechaza("INSERT INTO cargo_extra (alquiler_id, detalle_id, concepto, monto) VALUES (%s,(SELECT id FROM alquiler_detalle WHERE alquiler_id=%s LIMIT 1),'OTRO',50)", (a1, a2), "no pertenece", "un cargo no puede apuntar a la bicicleta de otro alquiler")

# ---------------------------------------------------------------- anulación y límites
print("Anulación y límites")
a3 = alquilar(CLI1, t(2026, 5, 1, 9), t(2026, 5, 1, 12), ["U-01", "U-02"])
con.execute("UPDATE alquiler SET anulada_en=%s, motivo_anulacion='Cargado por error' WHERE id=%s", (t(2026, 5, 1, 9, 10), a3))
verificar(estado("U-01")["estado"] == "DISPONIBLE" and estado("U-02")["estado"] == "DISPONIBLE", "al anular, las bicicletas vuelven a DISPONIBLE")
verificar(val("SELECT estado FROM alquiler WHERE id=%s", (a3,)) == "ANULADO", "el alquiler queda ANULADO")
a4 = alquilar(CLI1, t(2026, 5, 2, 9), t(2026, 5, 2, 12), ["U-01"])
verificar(True, "una bicicleta de un alquiler anulado se puede volver a alquilar")
a5 = alquilar(CLI2, t(2026, 5, 2, 9, 5), t(2026, 5, 2, 12), ["U-02"])
devolver(a5, "U-02", t(2026, 5, 2, 10), estacion=1)
con.execute("""INSERT INTO bicicleta (codigo, tipo_bicicleta_id, estado_id, ubicacion_base_id, ubicacion_id)
               SELECT 'X-' || g, 1, 1, 1, 1 FROM generate_series(1, 11) g""")
try:
    alquilar(CLI1, t(2026, 6, 1, 9), t(2026, 6, 1, 12), [f"X-{i}" for i in range(1, 12)])
except psycopg.Error as e:
    verificar("hasta 10" in str(e), "un alquiler admite como máximo 10 bicicletas")
else:
    verificar(False, "un alquiler admite como máximo 10 bicicletas")
rechaza("UPDATE bicicleta SET fecha_baja = '2000-01-01' WHERE codigo='U-03'", None, "check", "la fecha de baja no puede ser anterior al alta")
con.execute("SELECT fn_bici_cambiar_estado((SELECT id FROM bicicleta WHERE codigo='U-03'),'BAJA',NULL,%s,'Robo',1)", (t(2027, 1, 1),))
rechaza("SELECT fn_bici_cambiar_estado((SELECT id FROM bicicleta WHERE codigo='U-03'),'DISPONIBLE',1,%s,'x')", (t(2027, 1, 2),), "baja", "una bicicleta dada de baja no vuelve al servicio")
verificar(val("SELECT origen FROM historial_estado_bicicleta h JOIN bicicleta b ON b.id=h.bicicleta_id WHERE b.codigo='U-03' ORDER BY h.id DESC LIMIT 1") == "USUARIO", "el historial distingue cambios hechos por una persona de los del sistema")

print()
print("TODO OK" if not fallos else f"{len(fallos)} FALLAS:\n  - " + "\n  - ".join(fallos))
sys.exit(1 if fallos else 0)
