"""Prueba de punta a punta de la aplicación contra una base con los datos de demostración.

ATENCIÓN: escribe en la base (reservas, alquileres, pagos, órdenes, contraseñas de prueba).
Usar solo sobre una copia de desarrollo:

    createdb bicis_app --template bicis
    DATABASE_URL=postgresql://.../bicis_app SECRET_KEY=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))") \
        python3 tests/prueba_app.py
"""
import re
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import config, db, seguridad  # noqa: E402
from app.main import app  # noqa: E402

CLAVE = "Aa1-" + secrets.token_urlsafe(14)
CLAVE_NUEVA = "Bb2-" + secrets.token_urlsafe(14)
USUARIOS = {
    "admin": "lucia.ferrer@bicis.test",
    "mostrador": "martina.quiroga@bicis.test",
    "tecnico": "ramon.aguilera@bicis.test",
}
fallos = []


def verificar(condicion, texto):
    print(("  ok   " if condicion else "  FALLA ") + texto)
    if not condicion:
        fallos.append(texto)


def csrf_de(html):
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


def sql(consulta, params=None):
    with psycopg.connect(config.DATABASE_URL, row_factory=psycopg.rows.dict_row, autocommit=True) as con:
        cur = con.execute(consulta, params)
        return cur.fetchall() if cur.description else []


def cliente(rol, debe_cambiar=False):
    c = TestClient(app, follow_redirects=False)
    sql("""INSERT INTO credencial_acceso (usuario_id, password_hash, debe_cambiar)
           SELECT id, %s, %s FROM usuario WHERE email = %s
           ON CONFLICT (usuario_id) DO UPDATE SET password_hash = EXCLUDED.password_hash,
                                                  debe_cambiar = EXCLUDED.debe_cambiar""",
        (seguridad.hashear(CLAVE), debe_cambiar, USUARIOS[rol]))
    r = c.post("/login", data={"email": USUARIOS[rol], "clave": CLAVE})
    assert r.status_code == 303, (rol, r.status_code)
    return c


def token(c, ruta):
    return csrf_de(c.get(ruta).text)


def local(dt):
    return dt.strftime("%Y-%m-%dT%H:%M")


DNI = str(secrets.randbelow(9_000_000) + 60_000_000)      # fuera del rango de los datos generados
DNI2 = str(secrets.randbelow(9_000_000) + 70_000_000)

db.abrir()
anonimo = TestClient(app, follow_redirects=False)
if True:
    print("Acceso")
    verificar(anonimo.get("/").status_code == 303 and anonimo.get("/").headers["location"] == "/login",
              "sin sesión, el tablero redirige al login")
    verificar(anonimo.get("/alquileres/1").status_code == 303, "sin sesión, la ficha de un alquiler redirige")
    verificar(anonimo.post("/alquileres/nuevo", data={}).status_code == 303, "sin sesión, no se registra un alquiler")
    anonimo.cookies.set(seguridad.COOKIE, "cookie-falsificada")
    verificar(anonimo.get("/").status_code == 303, "una cookie falsificada no da acceso")
    anonimo.cookies.clear()
    verificar(anonimo.get("/salud").json() == {"estado": "ok"}, "/salud responde sin datos")
    verificar(anonimo.get("/docs").status_code == 404, "no se expone la documentación de la API")
    r = anonimo.post("/login", data={"email": USUARIOS["admin"], "clave": "mala"})
    verificar(r.status_code == 401 and "incorrectos" in r.text, "contraseña incorrecta: 401 con mensaje genérico")
    r2 = anonimo.post("/login", data={"email": "no.existe@x.test", "clave": "mala"})
    verificar(r2.status_code == 401 and "incorrectos" in r2.text, "usuario inexistente: el mismo mensaje")
    for _ in range(6):
        anonimo.post("/login", data={"email": "alguien@x.test", "clave": "mala"})
    verificar(anonimo.post("/login", data={"email": "alguien@x.test", "clave": "mala"}).status_code == 429,
              "demasiados intentos fallidos: bloqueo temporal")

    print("Contraseña inicial")
    nuevo = cliente("mostrador", debe_cambiar=True)
    verificar(nuevo.get("/").headers.get("location") == "/clave", "con contraseña temporal solo se puede ir a /clave")
    t = token(nuevo, "/clave")
    r = nuevo.post("/clave", data={"csrf": t, "actual": CLAVE, "nueva": "corta", "repetida": "corta"})
    verificar(r.status_code == 400, "una contraseña débil se rechaza")
    r = nuevo.post("/clave", data={"csrf": t, "actual": CLAVE, "nueva": CLAVE_NUEVA, "repetida": CLAVE_NUEVA})
    verificar(r.status_code == 303 and nuevo.get("/").status_code == 200, "cambia la contraseña y entra al tablero")

admin, mostrador, tecnico = cliente("admin"), cliente("mostrador"), cliente("tecnico")

print("Permisos y pantallas")
r = admin.get("/")
verificar(r.status_code == 200 and "Disponibilidad por estación" in r.text, "el tablero carga")
verificar("Content-Security-Policy" in r.headers and r.headers["X-Frame-Options"] == "DENY", "cabeceras de seguridad")
for ruta in ("/bicicletas", "/bicicletas/1", "/alquileres", "/reservas", "/reservas/nueva", "/alquileres/nuevo",
             "/clientes?q=garcia", "/taller", "/informes"):
    verificar(admin.get(ruta).status_code == 200, f"el administrador abre {ruta}")
verificar(tecnico.get("/alquileres/nuevo").status_code == 403, "el técnico no puede registrar alquileres")
verificar(tecnico.get("/taller").status_code == 200 and tecnico.get("/bicicletas").status_code == 200,
          "el técnico ve taller y bicicletas")
verificar(mostrador.get("/taller").status_code == 403, "el mostrador no entra al taller")
verificar(mostrador.get("/bicicletas/999999").status_code == 404, "una bicicleta inexistente da 404")
verificar(mostrador.get("/bicicletas?q=%27%3B+DROP+TABLE+bicicleta%3B--").status_code == 200,
          "una búsqueda con comillas no rompe nada")
verificar(sql("SELECT count(*) AS n FROM bicicleta")[0]["n"] > 50, "la tabla de bicicletas sigue intacta")
r = mostrador.post("/alquileres/nuevo", data={"est": "1"})
verificar(r.status_code == 403, "un POST sin token CSRF se rechaza")

print("Reserva con seña")
ahora = datetime.now(ZoneInfo(config.ZONA_HORARIA))
inicio, fin = ahora + timedelta(days=1), ahora + timedelta(days=1, hours=3)
est = sql("SELECT id FROM ubicacion WHERE tipo = 'ESTACION' ORDER BY id LIMIT 1")[0]["id"]
tipo_urbana = sql("SELECT id FROM tipo_bicicleta WHERE codigo = 'URBANA'")[0]["id"]
tipo_mtb = sql("SELECT id FROM tipo_bicicleta WHERE codigo = 'MTB'")[0]["id"]
t = token(mostrador, "/reservas/nueva")
base = {"csrf": t, "doc_tipo": "DNI", "doc_pais": "ar", "doc_num": DNI[:2] + "." + DNI[2:], "nombre": "Prueba",
        "apellido": "Automática", "email": "prueba@correo.test", "est": str(est), "canal": "MOSTRADOR",
        "inicio": local(inicio), "fin": local(fin), f"tipo_{tipo_urbana}": "2", f"tipo_{tipo_mtb}": "1",
        "sena": "5000", "medio": "EFECTIVO"}
r = mostrador.post("/reservas/nueva", data={**base, f"tipo_{tipo_mtb}": "10"})
verificar(r.status_code == 400 and "No hay cupo" in r.text, "pedir más de lo que hay: la base rechaza por falta de cupo")
r = mostrador.post("/reservas/nueva", data={**base, "fin": local(inicio - timedelta(hours=1))})
verificar(r.status_code == 400, "una reserva que termina antes de empezar se rechaza")
r = mostrador.post("/reservas/nueva", data=base)
verificar(r.status_code == 303 and "/reservas/" in r.headers["location"], "reserva creada")
rid = int(re.search(r"/reservas/(\d+)", r.headers["location"]).group(1))
fila = sql("SELECT estado, cliente_id FROM reserva WHERE id = %s", (rid,))[0]
verificar(fila["estado"] == "CONFIRMADA", "con seña, la reserva queda confirmada")
cli = sql("SELECT nombre, numero_documento, pais_documento FROM cliente WHERE id = %s", (fila["cliente_id"],))[0]
verificar(cli["numero_documento"] == DNI and cli["pais_documento"] == "AR", "el documento se normaliza al guardar")
verificar(sql("SELECT sum(monto) AS m FROM pago WHERE reserva_id = %s AND tipo = 'SENIA'", (rid,))[0]["m"] == 5000,
          "la seña quedó registrada")
t = token(mostrador, f"/reservas/{rid}")
r = mostrador.post("/reservas/nueva", data={**base, "csrf": t, "nombre": "", "apellido": ""})
verificar(r.status_code == 303, "con el mismo documento se reutiliza el cliente sin pedir nombre")
verificar(sql("SELECT count(*) AS n FROM cliente WHERE numero_documento = %s", (DNI,))[0]["n"] == 1,
          "no se duplicó el cliente")

print("Retiro, devolución con daño y cobro")
r = mostrador.get(f"/alquileres/nuevo?reserva={rid}")
verificar(r.status_code == 200 and "Retiro de la reserva" in r.text, "el formulario de retiro muestra la reserva")
libres = sql("""SELECT b.id, b.tipo_bicicleta_id FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
                 WHERE e.codigo = 'DISPONIBLE' AND b.ubicacion_id = %s AND b.tipo_bicicleta_id IN (%s, %s)
                 ORDER BY b.id""", (est, tipo_urbana, tipo_mtb))
urb = [x["id"] for x in libres if x["tipo_bicicleta_id"] == tipo_urbana][:2]
mtb = [x["id"] for x in libres if x["tipo_bicicleta_id"] == tipo_mtb][:1]
verificar(len(urb) == 2 and len(mtb) == 1, "hay bicicletas disponibles para el retiro")
t = token(mostrador, f"/alquileres/nuevo?reserva={rid}")
retiro = {"csrf": t, "est": str(est), "reserva_id": str(rid), "doc_tipo": "DNI", "doc_pais": "AR", "doc_num": DNI,
          "modalidad": "HORA", "cantidad": "3"}
r = mostrador.post("/alquileres/nuevo", data={**retiro, "bicis": []})
verificar(r.status_code == 400 and "al menos una" in r.text, "sin bicicletas elegidas, se rechaza")
r = mostrador.post("/alquileres/nuevo", data={**retiro, "bicis": urb + mtb})
verificar(r.status_code == 303, "retiro registrado")
aid = int(re.search(r"/alquileres/(\d+)", r.headers["location"]).group(1))
verificar(sql("SELECT estado FROM reserva WHERE id = %s", (rid,))[0]["estado"] == "CONVERTIDA", "la reserva queda convertida")
verificar(all(x["e"] == "ALQUILADA" for x in sql(
    """SELECT e.codigo AS e FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id WHERE b.id = ANY(%s)""",
    (urb + mtb,))), "las bicicletas pasan a alquiladas")
r = mostrador.post("/alquileres/nuevo", data={**retiro, "reserva_id": "", "bicis": urb[:1]})
verificar(r.status_code == 400 and "no está disponible" in r.text, "una bicicleta ya alquilada no se puede volver a sacar")
det = sql("SELECT id, bicicleta_id FROM alquiler_detalle WHERE alquiler_id = %s ORDER BY id", (aid,))
verificar(len(det) == 3, "el alquiler tiene las tres bicicletas")

t = token(mostrador, f"/alquileres/{aid}")
dev = {"csrf": t, "destino": str(est), "resultado": "OK", "observaciones": ""}
r = mostrador.post(f"/alquileres/{aid}/devolver", data={**dev, "detalle_id": str(det[0]["id"]), "resultado": "CON_DANIO",
                                                              "tipo": "DANIO", "severidad": "LEVE"})
verificar(r.status_code == 400 and "Describí el daño" in r.text, "un daño exige descripción")
r = mostrador.post(f"/alquileres/{aid}/devolver", data={**dev, "detalle_id": str(det[0]["id"])})
verificar(r.status_code == 303, "primera bicicleta devuelta sin daños")
r = mostrador.post(f"/alquileres/{aid}/devolver", data={**dev, "detalle_id": str(det[0]["id"])})
verificar(r.status_code == 400 and "ya fue devuelta" in r.text, "no se puede devolver dos veces")
dañada = det[1]["bicicleta_id"]
r = mostrador.post(f"/alquileres/{aid}/devolver", data={
    **dev, "detalle_id": str(det[1]["id"]), "resultado": "CON_DANIO", "observaciones": "Frenos sin mordiente",
    "tipo": "DANIO", "severidad": "MODERADA", "sistema": "FRENOS", "cargo": "4500"})
verificar(r.status_code == 303, "segunda bicicleta devuelta con daño")
inc = sql("SELECT tipo, severidad, sistema FROM incidencia WHERE bicicleta_id = %s ORDER BY id DESC LIMIT 1", (dañada,))[0]
verificar(inc["sistema"] == "FRENOS" and inc["severidad"] == "MODERADA", "se registró la incidencia")
verificar(sql("SELECT e.codigo AS e FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id WHERE b.id = %s",
              (dañada,))[0]["e"] == "FUERA_DE_SERVICIO", "la bicicleta dañada queda fuera de servicio")
r = mostrador.post(f"/alquileres/{aid}/anular", data={"csrf": t, "motivo": "error"})
verificar(r.status_code == 400 and "ya se devolvieron" in r.text, "no se anula un alquiler con bicicletas devueltas")
r = mostrador.post(f"/alquileres/{aid}/devolver", data={**dev, "detalle_id": str(det[2]["id"])})
verificar(r.status_code == 303, "tercera bicicleta devuelta")
s = sql("SELECT * FROM v_saldo_alquiler WHERE alquiler_id = %s", (aid,))[0]
verificar(s["estado"] == "FINALIZADO" and s["cargos"] == 4500, "el alquiler se finaliza solo y suma el cargo")
verificar(s["pagado"] == 5000 and s["saldo"] == s["total"] - 5000, "la seña de la reserva cuenta como pagada")
t = token(mostrador, f"/alquileres/{aid}")
r = mostrador.post(f"/alquileres/{aid}/cobrar", data={"csrf": t, "monto": str(s["saldo"] + 1), "medio": "EFECTIVO"})
verificar(r.status_code == 400 and "supera el saldo" in r.text, "no se cobra más que el saldo")
r = mostrador.post(f"/alquileres/{aid}/cobrar", data={"csrf": t, "monto": "0", "medio": "EFECTIVO"})
verificar(r.status_code == 400, "un monto de cero se rechaza")
r = mostrador.post(f"/alquileres/{aid}/cobrar", data={"csrf": t, "monto": str(s["saldo"]), "medio": "TARJETA", "referencia": "TJ-TEST"})
verificar(r.status_code == 303, "cobro registrado")
verificar(sql("SELECT saldo FROM v_saldo_alquiler WHERE alquiler_id = %s", (aid,))[0]["saldo"] == 0, "el saldo queda en cero")
verificar("Registrar cobro" not in mostrador.get(f"/alquileres/{aid}").text, "sin saldo, ya no se ofrece cobrar")

print("Alquiler de mostrador y anulación")
libre = sql("""SELECT b.id FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
                WHERE e.codigo = 'DISPONIBLE' AND b.ubicacion_id = %s ORDER BY b.id DESC LIMIT 1""", (est,))[0]["id"]
t = token(mostrador, "/alquileres/nuevo")
r = mostrador.post("/alquileres/nuevo", data={
    "csrf": t, "est": str(est), "doc_tipo": "PASAPORTE", "doc_pais": "br", "doc_num": "X" + DNI2, "nombre": "Turista",
    "apellido": "De Prueba", "modalidad": "DIA", "cantidad": "2", "bicis": [str(libre)]})
verificar(r.status_code == 303, "alquiler por día a un turista extranjero")
aid2 = int(re.search(r"/alquileres/(\d+)", r.headers["location"]).group(1))
d = sql("SELECT modalidad, precio_dia FROM alquiler_detalle WHERE alquiler_id = %s", (aid2,))[0]
verificar(d["modalidad"] == "DIA" and d["precio_dia"] > 0, "el precio vigente se copia al alquiler")
r = mostrador.post(f"/alquileres/{aid2}/anular", data={"csrf": t, "motivo": "Cargado por error"})
verificar(r.status_code == 303, "se anula un alquiler sin devoluciones")
verificar(sql("SELECT e.codigo AS e FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id WHERE b.id = %s",
              (libre,))[0]["e"] == "DISPONIBLE", "la bicicleta vuelve a quedar disponible")
verificar(sql("SELECT count(*) AS n FROM auditoria_sistema WHERE accion = 'ALQUILER_ANULADO' AND entidad_id = %s",
              (aid2,))[0]["n"] == 1, "la anulación queda en la auditoría")

print("Cancelación de reserva con reembolso")
inicio3 = ahora + timedelta(days=3)
t = token(mostrador, "/reservas/nueva")
r = mostrador.post("/reservas/nueva", data={**base, "csrf": t, "inicio": local(inicio3), "fin": local(inicio3 + timedelta(hours=2)),
                                           f"tipo_{tipo_urbana}": "1", f"tipo_{tipo_mtb}": "0", "sena": "3000"})
rid3 = int(re.search(r"/reservas/(\d+)", r.headers["location"]).group(1))
r = mostrador.post(f"/reservas/{rid3}/cancelar", data={"csrf": t, "motivo": "El cliente avisó", "devolver": "1"})
verificar(r.status_code == 303 and sql("SELECT estado FROM reserva WHERE id = %s", (rid3,))[0]["estado"] == "CANCELADA",
          "reserva cancelada")
verificar(sql("SELECT sum(monto) AS m FROM pago WHERE reserva_id = %s AND tipo = 'REEMBOLSO'", (rid3,))[0]["m"] == 3000,
          "se devolvió la seña")
r = mostrador.post(f"/reservas/{rid3}/cancelar", data={"csrf": t, "motivo": "otra vez"})
verificar(r.status_code == 400, "una reserva cancelada no se cancela de nuevo")

print("Taller")
t = token(tecnico, "/taller")
r = tecnico.post("/taller/abrir", data={"csrf": t, "bicicleta_id": str(dañada), "descripcion": "Frenos sin mordiente"})
verificar(r.status_code == 303, "el técnico abre la orden correctiva")
o = sql("""SELECT o.id, o.incidencia_id, e.codigo AS estado FROM orden_mantenimiento o JOIN estado_orden e ON e.id = o.estado_id
            WHERE o.bicicleta_id = %s ORDER BY o.id DESC LIMIT 1""", (dañada,))[0]
verificar(o["estado"] == "ABIERTA" and o["incidencia_id"] is not None, "la orden toma la incidencia sin resolver")
verificar(sql("SELECT e.codigo AS e, ubicacion_id FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id WHERE b.id = %s",
              (dañada,))[0]["e"] == "EN_MANTENIMIENTO", "la bicicleta pasa a mantenimiento")
r = tecnico.post(f"/taller/{o['id']}/cerrar", data={"csrf": t, "items": "Mano de obra | 1 | 6000"})
verificar(r.status_code == 400 and "en curso" in r.text, "no se cierra una orden que no empezó")
r = tecnico.post(f"/taller/{o['id']}/iniciar", data={"csrf": t})
verificar(r.status_code == 303, "la orden se inicia")
r = tecnico.post(f"/taller/{o['id']}/cerrar", data={"csrf": t, "items": "esto no tiene el formato"})
verificar(r.status_code == 400 and "mal escrito" in r.text, "un ítem mal escrito se rechaza")
r = tecnico.post(f"/taller/{o['id']}/cerrar", data={"csrf": t, "items": "Mano de obra | 1,5 | 6000\nPastillas de freno | 2 | 4500"})
verificar(r.status_code == 303, "la orden se cierra con sus ítems")
f = sql("SELECT costo_total FROM orden_mantenimiento WHERE id = %s", (o["id"],))[0]
verificar(f["costo_total"] == 18000, "el costo es la suma de los ítems (9.000 + 9.000)")
b = sql("""SELECT e.codigo AS e, b.ubicacion_id, b.ubicacion_base_id FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
            WHERE b.id = %s""", (dañada,))[0]
verificar(b["e"] == "DISPONIBLE" and b["ubicacion_id"] == b["ubicacion_base_id"], "la bicicleta vuelve disponible a su estación")
verificar(sql("SELECT resuelta_en FROM incidencia WHERE id = %s", (o["incidencia_id"],))[0]["resuelta_en"] is not None,
          "la incidencia queda resuelta")
r = admin.get(f"/bicicletas/{dañada}")
verificar("Frenos sin mordiente" in r.text and "Fin de la orden" in r.text, "la ficha muestra incidencias e historial")

print("Taller: riesgo de falla (modelo de la fase 2)")
# Una bicicleta disponible sin servicio vencido ni orden abierta, con un riesgo alto inventado, para ejercitar la
# tabla "Riesgo alto sin servicio vencido" (en los datos reales todas las de riesgo alto ya tienen algo vencido).
sin_vencer = sql("""SELECT b.id, b.codigo FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
                     WHERE e.codigo = 'DISPONIBLE'
                       AND NOT EXISTS (SELECT 1 FROM v_proximo_servicio v WHERE v.bicicleta_id = b.id
                                          AND (v.horas_restantes < 0 OR v.dias_restantes < 0))
                       AND NOT EXISTS (SELECT 1 FROM orden_mantenimiento o JOIN estado_orden s ON s.id = o.estado_id
                                        WHERE o.bicicleta_id = b.id AND s.codigo IN ('ABIERTA','EN_CURSO'))
                     ORDER BY b.id LIMIT 1""")
if sin_vencer:
    sql("""INSERT INTO prediccion_mantenimiento (bicicleta_id, horizonte_dias, sistema, probabilidad, modelo_version)
           VALUES (%s, 30, NULL, 0.95, 'prueba-app'), (%s, 30, 'FRENOS', 0.20, 'prueba-app')""",
        (sin_vencer[0]["id"], sin_vencer[0]["id"]))
html = tecnico.get("/taller").text
verificar("Riesgo del sistema" in html and "modelo del" in html, "el taller muestra el riesgo y la fecha del modelo")
tramo = html.split("Servicios vencidos")[1].split("Riesgo alto sin servicio vencido")[0]
filas = re.findall(r'<tr><td><a href="/bicicletas/(\d+)">([^<]+)</a></td><td>[^<]*</td>\s*<td class="num">(.*?)</td>', tramo)
riesgos = [int(m.group(1)) if (m := re.search(r"(\d+) %", celda)) else -1 for _, _, celda in filas]
verificar(len(filas) > 0 and riesgos == sorted(riesgos, reverse=True),
          "los servicios vencidos salen ordenados por riesgo del sistema (sin dato, al final)")
codigos_vencidos = {codigo for _, codigo, _ in filas}
if "Riesgo alto sin servicio vencido" in html:
    alto = html.split("Riesgo alto sin servicio vencido")[1]
    cods = re.findall(r'<a href="/bicicletas/\d+">([^<]+)</a>', alto)
    verificar(cods and not (set(cods) & codigos_vencidos), "el riesgo alto sin vencimiento no repite bicicletas ya listadas")
    umbral = round(100 * __import__("app.main", fromlist=["UMBRALES_RIESGO"]).UMBRALES_RIESGO["total"][1])
    pcts = [int(x) for x in re.findall(r"(\d+) %", alto)]
    verificar(all(x >= umbral for x in pcts), f"todas las de esa tabla superan el {umbral} % de riesgo")
    if sin_vencer:
        verificar(sin_vencer[0]["codigo"] in alto and "95 %" in alto and "FRENOS" in alto,
                  "una bicicleta de riesgo alto sin vencimiento aparece, con su sistema de mayor riesgo")
else:
    verificar(not sin_vencer, "la tabla de riesgo alto aparece cuando corresponde")
sql("DELETE FROM prediccion_mantenimiento WHERE modelo_version = 'prueba-app'")
verificar("Riesgo alto sin servicio vencido" not in tecnico.get("/taller").text or not sin_vencer,
          "al sacar esa predicción, la bicicleta deja de figurar")
sql("UPDATE prediccion_mantenimiento SET calculada_en = calculada_en - interval '20 days'")
verificar("actualización automática no está funcionando" in tecnico.get("/taller").text,
          "avisa si las predicciones tienen más de 4 días")
sql("UPDATE prediccion_mantenimiento SET calculada_en = calculada_en + interval '20 days'")
verificar("actualización automática no está funcionando" not in tecnico.get("/taller").text,
          "no avisa con predicciones recientes")
sql("DELETE FROM prediccion_mantenimiento")   # (base de prueba: es una copia)
r = tecnico.get("/taller")
verificar(r.status_code == 200 and "Sin predicciones de riesgo" in r.text,
          "sin predicciones, el taller funciona y ordena por vencimiento")

print("Clientes")
r = mostrador.get(f"/clientes?q={DNI}")
verificar("Automática" in r.text, "se busca un cliente por documento")
cid = sql("SELECT id FROM cliente WHERE numero_documento = %s", (DNI,))[0]["id"]
verificar("Alquileres" in mostrador.get(f"/clientes/{cid}").text, "ficha del cliente")

db.cerrar()
print()
if fallos:
    print(f"{len(fallos)} FALLAS:")
    for f_ in fallos:
        print("  -", f_)
    sys.exit(1)
print("Todo en orden.")
