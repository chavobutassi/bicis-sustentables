"""Aplicación web de Bicis sustentables: tablero, reservas, alquileres, taller y clientes.

Las reglas del negocio viven en la base de datos (triggers y restricciones):
la aplicación muestra los datos, valida el formato y traduce los rechazos de la
base a mensajes comprensibles.
"""
import logging
import re
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from psycopg import errors as pgerr

from . import config, db, seguridad

log = logging.getLogger("bicis")
BASE = Path(__file__).parent
TZ = ZoneInfo(config.ZONA_HORARIA)
limite = seguridad.LimiteIntentos()

# Qué roles pueden hacer cada operación (ver docs/diseno.md).
ROLES_MOSTRADOR = {"ADMIN", "MOSTRADOR"}
ROLES_TALLER = {"ADMIN", "TECNICO"}
ROLES_LECTURA = {"ADMIN", "MOSTRADOR", "TECNICO"}

MENSAJES_OK = {
    "alquiler": "Alquiler registrado.",
    "devolucion": "Devolución registrada.",
    "cobro": "Cobro registrado.",
    "cargo": "Cargo registrado.",
    "anulado": "Alquiler anulado.",
    "reserva": "Reserva registrada.",
    "sena": "Seña registrada: la reserva quedó confirmada.",
    "cancelada": "Reserva cancelada.",
    "orden": "Orden de mantenimiento abierta.",
    "iniciada": "Orden iniciada.",
    "cerrada": "Orden cerrada: la bicicleta vuelve a su estación.",
    "cliente": "Cliente guardado.",
    "clave": "Contraseña actualizada.",
}


@asynccontextmanager
async def ciclo_de_vida(_):
    db.abrir()
    yield
    db.cerrar()


app = FastAPI(lifespan=ciclo_de_vida, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
plantillas = Jinja2Templates(directory=BASE / "templates")


def fecha(valor, formato="%d/%m/%Y %H:%M"):
    if valor is None:
        return "—"
    if isinstance(valor, datetime):
        valor = valor.astimezone(TZ)
    return valor.strftime(formato)


def numero(valor, decimales=0):
    if valor is None:
        return "—"
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def pesos(valor):
    return "—" if valor is None else "$ " + numero(valor)


def porcentaje(valor):
    return "—" if valor is None else f"{float(valor) * 100:.0f} %"


# Niveles de riesgo de falla a 30 días. Son relativos a la flota (aprox. el 25 % y el 10 % superior de las
# predicciones del modelo, ver docs/modelo_riesgo.md), no una probabilidad "peligrosa" en sí.
UMBRALES_RIESGO = {"total": (0.30, 0.40), "sistema": (0.06, 0.09)}
# Las predicciones se actualizan solas una vez por día (ver docs/modelo_riesgo.md): si pasan más de estos días
# sin una nueva, el taller avisa que algo falló.
DIAS_PREDICCION_VIEJA = 4


def nivel_riesgo(valor, clase="total"):
    if valor is None:
        return ""
    medio, alto = UMBRALES_RIESGO[clase]
    return "mal" if valor >= alto else "aviso" if valor >= medio else "ok"


plantillas.env.filters["fecha"] = fecha
plantillas.env.filters["numero"] = numero
plantillas.env.filters["porcentaje"] = porcentaje
plantillas.env.filters["nivel_riesgo"] = nivel_riesgo
plantillas.env.filters["pesos"] = pesos


# ---------------------------------------------------------------- seguridad HTTP

@app.middleware("http")
async def cabeceras(request: Request, call_next):
    respuesta = await call_next(request)
    respuesta.headers["Content-Security-Policy"] = (
        "default-src 'self'; frame-ancestors 'none'; form-action 'self'; base-uri 'none'")
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "same-origin"
    respuesta.headers["Cache-Control"] = "no-store"
    if config.PRODUCCION:
        respuesta.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return respuesta


class Redirigir(Exception):
    def __init__(self, destino):
        self.destino = destino


@app.exception_handler(Redirigir)
async def _redirigir(_, exc: Redirigir):
    return RedirectResponse(exc.destino, status_code=303)


class Prohibido(Exception):
    pass


@app.exception_handler(Prohibido)
async def _prohibido(request: Request, _):
    return pantalla(request, "error.html", {"titulo": "Sin permiso",
                    "texto": "Tu usuario no tiene permiso para esta operación."}, 403)


class NoExiste(Exception):
    pass


@app.exception_handler(NoExiste)
async def _no_existe(request: Request, _):
    return pantalla(request, "error.html", {"titulo": "No encontrado",
                    "texto": "No existe lo que buscás."}, 404)


# ---------------------------------------------------------------- sesión y permisos

def sesion_actual(request: Request, permitir_cambio_clave=False) -> dict:
    """Usuario autenticado, con sus roles leídos en cada pedido (una baja rige al instante)."""
    ses = seguridad.leer_cookie_sesion(request.cookies.get(seguridad.COOKIE))
    if not ses:
        raise Redirigir("/login")
    fila = db.consultar_uno(
        """SELECT u.id, u.nombre, u.apellido, u.email, c.debe_cambiar,
                  COALESCE(array_agg(r.codigo) FILTER (WHERE r.codigo IS NOT NULL), '{}') AS roles
             FROM usuario u
             JOIN credencial_acceso c ON c.usuario_id = u.id
             LEFT JOIN usuario_rol ur ON ur.usuario_id = u.id
             LEFT JOIN rol r ON r.id = ur.rol_id
            WHERE u.id = %s AND u.activo
            GROUP BY u.id, c.debe_cambiar""", (ses["u"],))
    if not fila:
        raise Redirigir("/login")
    if fila["debe_cambiar"] and not permitir_cambio_clave:
        raise Redirigir("/clave")
    fila["roles"] = set(fila["roles"])
    fila["csrf"] = ses["csrf"]
    return fila


def exigir(usuario: dict, permitidos: set):
    if not (usuario["roles"] & permitidos):
        raise Prohibido()


async def formulario(request: Request, usuario: dict) -> dict:
    datos = dict(await request.form())
    if not seguridad.csrf_valido(usuario, datos.get("csrf")):
        raise Prohibido()
    return datos


async def formulario_multi(request: Request, usuario: dict):
    """Como formulario(), pero conserva los campos repetidos (casillas de selección)."""
    f = await request.form()
    if not seguridad.csrf_valido(usuario, f.get("csrf")):
        raise Prohibido()
    return f


def pantalla(request: Request, nombre: str, contexto: dict, estado: int = 200, usuario=None):
    contexto = {"request": request, "usuario": usuario, **contexto}
    return plantillas.TemplateResponse(request, nombre, contexto, status_code=estado)


# ---------------------------------------------------------------- validación de datos

def a_decimal(texto, campo, obligatorio=True, maximo=Decimal("99999999")):
    texto = (texto or "").strip().replace(",", ".")
    if not texto:
        if obligatorio:
            raise ValueError(f"Falta {campo}.")
        return None
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        raise ValueError(f"{campo.capitalize()} no es un número válido.") from None
    if not valor.is_finite() or valor <= 0 or valor > maximo:
        raise ValueError(f"{campo.capitalize()} fuera de rango.")
    return valor.quantize(Decimal("0.01"))


def a_entero(texto, campo, minimo=1, maximo=10_000_000):
    try:
        v = int((texto or "").strip())
    except ValueError:
        raise ValueError(f"Falta {campo}.") from None
    if not minimo <= v <= maximo:
        raise ValueError(f"{campo.capitalize()} fuera de rango.")
    return v


def a_texto(texto, campo, largo, obligatorio=False):
    texto = (texto or "").strip()
    if not texto and obligatorio:
        raise ValueError(f"Falta {campo}.")
    if len(texto) > largo:
        raise ValueError(f"{campo.capitalize()}: máximo {largo} caracteres.")
    return texto or None


def a_fecha_local(texto, campo):
    texto = (texto or "").strip()
    if not texto:
        raise ValueError(f"Falta {campo}.")
    try:
        return datetime.fromisoformat(texto).replace(tzinfo=TZ)
    except ValueError:
        raise ValueError(f"{campo.capitalize()} no es una fecha válida.") from None


def elegir_de(valor, opciones, campo):
    valor = (valor or "").strip().upper()
    if valor not in opciones:
        raise ValueError(f"{campo.capitalize()} no es válido.")
    return valor


def traducir(exc: Exception) -> str:
    """Convierte un rechazo de la base en un mensaje para el usuario."""
    if isinstance(exc, pgerr.UniqueViolation):
        return "Ese registro ya existe."
    if isinstance(exc, pgerr.CheckViolation):
        if exc.diag.constraint_name:                  # restricción de tabla: mensaje genérico
            return "Algún valor no cumple las reglas de la base (revisá fechas, montos y cantidades)."
        return exc.diag.message_primary               # regla de un trigger: ya está en castellano
    if isinstance(exc, pgerr.ForeignKeyViolation):
        return "Una de las opciones elegidas no es válida."
    log.exception("Error inesperado de base de datos")
    return "No se pudo guardar. Intentá de nuevo."


# ---------------------------------------------------------------- acceso

@app.get("/salud")
async def salud():
    return JSONResponse({"estado": "ok"})


@app.get("/login", response_class=HTMLResponse)
async def login_pantalla(request: Request):
    return pantalla(request, "login.html", {"error": None})


@app.post("/login")
async def login(request: Request):
    datos = dict(await request.form())
    email = (datos.get("email") or "").strip().lower()[:254]
    clave = (datos.get("clave") or "")[:200]
    ip = request.client.host if request.client else "?"
    llave = f"{ip}|{email}"
    if limite.bloqueado(llave):
        return pantalla(request, "login.html",
                        {"error": "Demasiados intentos. Esperá 15 minutos."}, 429)
    fila = db.consultar_uno(
        """SELECT u.id, c.password_hash FROM usuario u
             LEFT JOIN credencial_acceso c ON c.usuario_id = u.id
            WHERE lower(u.email) = %s AND u.activo""", (email,))
    if not seguridad.verificar(clave, fila and fila["password_hash"]) or not fila:
        limite.fallo(llave)
        return pantalla(request, "login.html", {"error": "Correo o contraseña incorrectos."}, 401)
    limite.exito(llave)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(seguridad.COOKIE, seguridad.crear_cookie_sesion(fila["id"]),
                    max_age=config.SESION_HORAS * 3600, httponly=True,
                    secure=config.PRODUCCION, samesite="lax")
    return resp


@app.post("/salir")
async def salir(request: Request):
    usuario = sesion_actual(request, permitir_cambio_clave=True)
    await formulario(request, usuario)
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(seguridad.COOKIE)
    return resp


@app.get("/clave", response_class=HTMLResponse)
async def clave_pantalla(request: Request):
    usuario = sesion_actual(request, permitir_cambio_clave=True)
    return pantalla(request, "clave.html", {"error": None}, usuario=usuario)


@app.post("/clave")
async def clave_guardar(request: Request):
    usuario = sesion_actual(request, permitir_cambio_clave=True)
    datos = await formulario(request, usuario)
    actual, nueva, repetida = (datos.get(k, "") for k in ("actual", "nueva", "repetida"))
    fila = db.consultar_uno("SELECT password_hash FROM credencial_acceso WHERE usuario_id = %s",
                            (usuario["id"],))
    error = None
    if not seguridad.verificar(actual, fila["password_hash"]):
        error = "La contraseña actual no es correcta."
    elif nueva != repetida:
        error = "Las contraseñas nuevas no coinciden."
    elif nueva == actual:
        error = "La contraseña nueva debe ser distinta de la actual."
    else:
        error = seguridad.validar_clave_nueva(nueva)
    if error:
        return pantalla(request, "clave.html", {"error": error}, 400, usuario)
    with db.conexion() as con:
        con.execute("""UPDATE credencial_acceso SET password_hash = %s, debe_cambiar = FALSE,
                              actualizada_en = now() WHERE usuario_id = %s""",
                    (seguridad.hashear(nueva), usuario["id"]))
    return RedirectResponse("/?ok=clave", status_code=303)


# ---------------------------------------------------------------- tablero

@app.get("/", response_class=HTMLResponse)
async def tablero(request: Request, ok: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_LECTURA)
    resumen = db.consultar_uno(
        """SELECT count(*) FILTER (WHERE e.codigo = 'DISPONIBLE') AS disponibles,
                  count(*) FILTER (WHERE e.codigo = 'ALQUILADA') AS alquiladas,
                  count(*) FILTER (WHERE e.codigo IN ('EN_MANTENIMIENTO','FUERA_DE_SERVICIO')) AS en_taller,
                  (SELECT count(*) FROM v_alquileres_demorados) AS demorados,
                  (SELECT count(*) FROM reserva WHERE estado IN ('PENDIENTE','CONFIRMADA')
                      AND fn_fecha_local(inicio_previsto) = fn_fecha_local(now())) AS reservas_hoy,
                  (SELECT COALESCE(sum(importe), 0) FROM alquiler_detalle
                    WHERE devuelta_en IS NOT NULL AND fn_fecha_local(devuelta_en) = fn_fecha_local(now())) AS ingresos_hoy,
                  (SELECT count(DISTINCT bicicleta_id) FROM v_proximo_servicio
                    WHERE horas_restantes < 0 OR dias_restantes < 0) AS con_servicio_vencido
             FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id WHERE e.codigo <> 'BAJA'""")
    disponibilidad = db.consultar(
        "SELECT * FROM v_disponibilidad_estacion WHERE flota > 0 ORDER BY estacion, tipo")
    demorados = db.consultar(
        """SELECT d.*, c.nombre || ' ' || c.apellido AS cliente
             FROM v_alquileres_demorados d JOIN cliente c ON c.id = d.cliente_id
            ORDER BY d.horas_de_demora DESC LIMIT 15""")
    reservas = db.consultar(
        """SELECT r.id, r.inicio_previsto, r.estado, u.nombre AS estacion, c.nombre || ' ' || c.apellido AS cliente,
                  (SELECT string_agg(rd.cantidad || ' ' || tb.nombre, ', ' ORDER BY tb.nombre)
                     FROM reserva_detalle rd JOIN tipo_bicicleta tb ON tb.id = rd.tipo_bicicleta_id
                    WHERE rd.reserva_id = r.id) AS pedido
             FROM reserva r JOIN cliente c ON c.id = r.cliente_id JOIN ubicacion u ON u.id = r.ubicacion_id
            WHERE r.estado IN ('PENDIENTE','CONFIRMADA')
              AND r.inicio_previsto < now() + interval '24 hours'
            ORDER BY r.inicio_previsto LIMIT 20""")
    return pantalla(request, "tablero.html", {
        "resumen": resumen, "disponibilidad": disponibilidad, "demorados": demorados, "reservas": reservas,
        "ok": MENSAJES_OK.get(ok)}, usuario=usuario)


# ---------------------------------------------------------------- bicicletas

@app.get("/bicicletas", response_class=HTMLResponse)
async def bicicletas(request: Request, estado: str = "", q: str = "", vencidas: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_LECTURA)
    q, estado = q.strip()[:50], estado.strip().upper()[:30]
    filas = db.consultar(
        """SELECT b.id, b.codigo, tb.nombre AS tipo, b.marca, b.modelo, e.codigo AS estado_codigo, e.nombre AS estado,
                  COALESCE(u.nombre, 'En la calle') AS ubicacion, ub.nombre AS base, b.horas_uso, b.usos,
                  COALESCE(s.vencidos, 0) AS vencidos
             FROM bicicleta b
             JOIN tipo_bicicleta tb ON tb.id = b.tipo_bicicleta_id
             JOIN estado_bicicleta e ON e.id = b.estado_id
             JOIN ubicacion ub ON ub.id = b.ubicacion_base_id
             LEFT JOIN ubicacion u ON u.id = b.ubicacion_id
             LEFT JOIN (SELECT bicicleta_id, count(*) FILTER (WHERE horas_restantes < 0 OR dias_restantes < 0) AS vencidos
                          FROM v_proximo_servicio GROUP BY bicicleta_id) s ON s.bicicleta_id = b.id
            WHERE (%(estado)s = '' AND e.codigo <> 'BAJA' OR e.codigo = %(estado)s)
              AND (%(q)s = '' OR b.codigo ILIKE '%%' || %(q)s || '%%' OR b.marca ILIKE '%%' || %(q)s || '%%'
                   OR b.modelo ILIKE '%%' || %(q)s || '%%' OR tb.nombre ILIKE '%%' || %(q)s || '%%')
              AND (NOT %(venc)s OR COALESCE(s.vencidos, 0) > 0)
            ORDER BY COALESCE(s.vencidos, 0) DESC, b.codigo""",
        {"estado": estado, "q": q, "venc": vencidas == "1"})
    estados = db.consultar("SELECT codigo, nombre FROM estado_bicicleta ORDER BY id")
    return pantalla(request, "bicicletas.html", {
        "bicis": filas, "estados": estados, "estado": estado, "q": q, "vencidas": vencidas == "1"}, usuario=usuario)


@app.get("/bicicletas/{bici_id}", response_class=HTMLResponse)
async def bicicleta(request: Request, bici_id: int, ok: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_LECTURA)
    return ficha_bicicleta(request, usuario, bici_id, ok=MENSAJES_OK.get(ok))


def ficha_bicicleta(request, usuario, bici_id, error=None, ok=None, estado=200):
    b = db.consultar_uno(
        """SELECT b.*, tb.nombre AS tipo, e.codigo AS estado_codigo, e.nombre AS estado,
                  ub.nombre AS base, u.nombre AS ubicacion
             FROM bicicleta b
             JOIN tipo_bicicleta tb ON tb.id = b.tipo_bicicleta_id
             JOIN estado_bicicleta e ON e.id = b.estado_id
             JOIN ubicacion ub ON ub.id = b.ubicacion_base_id
             LEFT JOIN ubicacion u ON u.id = b.ubicacion_id
            WHERE b.id = %s""", (bici_id,))
    if not b:
        raise NoExiste()
    servicios = db.consultar(
        """SELECT * FROM v_proximo_servicio WHERE bicicleta_id = %s
            ORDER BY LEAST(COALESCE(horas_restantes / NULLIF(horas_por_dia, 0), 9999), COALESCE(dias_restantes, 9999))""",
        (bici_id,))
    alquileres = db.consultar(
        """SELECT d.id, d.alquiler_id, d.salida_real, d.devuelta_en, d.segundos_uso, d.importe, d.estado_devolucion,
                  c.nombre || ' ' || c.apellido AS cliente
             FROM alquiler_detalle d JOIN alquiler a ON a.id = d.alquiler_id JOIN cliente c ON c.id = a.cliente_id
            WHERE d.bicicleta_id = %s AND d.anulado_en IS NULL ORDER BY d.salida_real DESC LIMIT 12""", (bici_id,))
    incidencias = db.consultar(
        """SELECT * FROM incidencia WHERE bicicleta_id = %s ORDER BY ocurrida_en DESC LIMIT 12""", (bici_id,))
    ordenes = db.consultar(
        """SELECT o.id, o.abierta_en, o.cerrada_en, o.costo_total, o.descripcion, e.nombre AS estado,
                  e.codigo AS estado_codigo, t.nombre AS tipo
             FROM orden_mantenimiento o JOIN estado_orden e ON e.id = o.estado_id
             JOIN tipo_mantenimiento t ON t.id = o.tipo_id
            WHERE o.bicicleta_id = %s ORDER BY o.abierta_en DESC LIMIT 12""", (bici_id,))
    historial = db.consultar(
        """SELECT h.cambiado_en, ea.nombre AS antes, en.nombre AS despues, h.motivo
             FROM historial_estado_bicicleta h
             LEFT JOIN estado_bicicleta ea ON ea.id = h.estado_ant_id
             JOIN estado_bicicleta en ON en.id = h.estado_nuevo_id
            WHERE h.bicicleta_id = %s ORDER BY h.cambiado_en DESC, h.id DESC LIMIT 12""", (bici_id,))
    return pantalla(request, "bicicleta.html", {
        "b": b, "servicios": servicios, "alquileres": alquileres, "incidencias": incidencias, "ordenes": ordenes,
        "historial": historial, "error": error, "ok": ok, "puede_taller": bool(usuario["roles"] & ROLES_TALLER)},
        estado, usuario)


# ---------------------------------------------------------------- clientes

@app.get("/clientes", response_class=HTMLResponse)
async def clientes(request: Request, q: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    q = q.strip()[:60]
    filas = []
    if q:
        filas = db.consultar(
            """SELECT c.*, (SELECT count(*) FROM alquiler a WHERE a.cliente_id = c.id AND a.anulada_en IS NULL) AS alquileres
                 FROM cliente c
                WHERE c.numero_documento ILIKE '%%' || upper(regexp_replace(%(q)s, '[^A-Za-z0-9]', '', 'g')) || '%%'
                   OR c.apellido ILIKE '%%' || %(q)s || '%%' OR c.nombre ILIKE '%%' || %(q)s || '%%'
                   OR c.email ILIKE '%%' || %(q)s || '%%'
                ORDER BY lower(c.apellido), lower(c.nombre) LIMIT 50""", {"q": q})
    return pantalla(request, "clientes.html", {"clientes": filas, "q": q}, usuario=usuario)


@app.get("/clientes/{cliente_id}", response_class=HTMLResponse)
async def cliente(request: Request, cliente_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    c = db.consultar_uno("SELECT * FROM cliente WHERE id = %s", (cliente_id,))
    if not c:
        raise NoExiste()
    alquileres = db.consultar(
        """SELECT a.id, a.salida_real, a.retorno_real, a.estado, s.total, s.saldo,
                  (SELECT count(*) FROM alquiler_detalle d WHERE d.alquiler_id = a.id AND d.anulado_en IS NULL) AS bicis
             FROM alquiler a LEFT JOIN v_saldo_alquiler s ON s.alquiler_id = a.id
            WHERE a.cliente_id = %s ORDER BY a.salida_real DESC LIMIT 30""", (cliente_id,))
    reservas = db.consultar(
        """SELECT r.id, r.inicio_previsto, r.estado, u.nombre AS estacion FROM reserva r
             JOIN ubicacion u ON u.id = r.ubicacion_id WHERE r.cliente_id = %s
            ORDER BY r.inicio_previsto DESC LIMIT 15""", (cliente_id,))
    return pantalla(request, "cliente.html", {"c": c, "alquileres": alquileres, "reservas": reservas},
                    usuario=usuario)


def asegurar_cliente(con, datos) -> int:
    """Busca al cliente por documento; si no existe lo da de alta (hacen falta nombre y apellido)."""
    tipo = elegir_de(datos.get("doc_tipo"), {"DNI", "PASAPORTE", "OTRO"}, "el tipo de documento")
    pais = (datos.get("doc_pais") or "AR").strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", pais):
        raise ValueError("El país del documento son dos letras (por ejemplo AR).")
    numero_doc = a_texto(datos.get("doc_num"), "el número de documento", 30, obligatorio=True)
    if not re.search(r"[A-Za-z0-9]", numero_doc):
        raise ValueError("El número de documento no es válido.")
    fila = con.execute(
        """SELECT id FROM cliente WHERE tipo_documento = %s AND pais_documento = %s
              AND numero_documento = upper(regexp_replace(%s, '[^A-Za-z0-9]', '', 'g'))""",
        (tipo, pais, numero_doc)).fetchone()
    if fila:
        return fila["id"]
    nombre = a_texto(datos.get("nombre"), "el nombre", 60, obligatorio=True)
    apellido = a_texto(datos.get("apellido"), "el apellido", 60, obligatorio=True)
    email = a_texto(datos.get("email"), "el correo", 254)
    telefono = a_texto(datos.get("telefono"), "el teléfono", 30)
    return con.execute(
        """INSERT INTO cliente (nombre, apellido, tipo_documento, pais_documento, numero_documento, email, telefono)
           VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
        (nombre, apellido, tipo, pais, numero_doc, email, telefono)).fetchone()["id"]


# ---------------------------------------------------------------- alquileres

def vista_alquiler_nuevo(request, usuario, est=None, reserva_id=None, error=None, valores=None, estado=200):
    estaciones = db.consultar("SELECT id, nombre FROM ubicacion WHERE tipo = 'ESTACION' AND activa ORDER BY id")
    reserva = None
    if reserva_id:
        reserva = db.consultar_uno(
            """SELECT r.*, c.nombre, c.apellido, c.tipo_documento, c.pais_documento, c.numero_documento
                 FROM reserva r JOIN cliente c ON c.id = r.cliente_id WHERE r.id = %s""", (reserva_id,))
        if not reserva or reserva["estado"] not in ("PENDIENTE", "CONFIRMADA"):
            raise NoExiste()
        reserva["pedido"] = db.consultar(
            """SELECT tb.nombre AS tipo, rd.cantidad FROM reserva_detalle rd
                 JOIN tipo_bicicleta tb ON tb.id = rd.tipo_bicicleta_id WHERE rd.reserva_id = %s""", (reserva_id,))
        est = reserva["ubicacion_id"]
    est = est or estaciones[0]["id"]
    disponibles = db.consultar(
        """SELECT b.id, b.codigo, tb.nombre AS tipo, b.marca, b.modelo, b.talle, t.precio_hora, t.precio_dia
             FROM bicicleta b
             JOIN estado_bicicleta e ON e.id = b.estado_id AND e.codigo = 'DISPONIBLE'
             JOIN tipo_bicicleta tb ON tb.id = b.tipo_bicicleta_id
             LEFT JOIN LATERAL fn_tarifa_vigente(b.tipo_bicicleta_id, fn_fecha_local(now())) t ON TRUE
            WHERE b.ubicacion_id = %s ORDER BY tb.nombre, b.codigo""", (est,))
    return pantalla(request, "alquiler_nuevo.html", {
        "estaciones": estaciones, "est": est, "disponibles": disponibles, "reserva": reserva,
        "error": error, "v": valores or {}}, estado, usuario)


@app.get("/alquileres/nuevo", response_class=HTMLResponse)
async def alquiler_nuevo(request: Request, est: int = 0, reserva: int = 0):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    return vista_alquiler_nuevo(request, usuario, est or None, reserva or None)


@app.post("/alquileres/nuevo")
async def alquiler_crear(request: Request):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    f = await formulario_multi(request, usuario)
    datos = {k: f.get(k) for k in f.keys()}
    try:
        est = a_entero(datos.get("est"), "la estación")
        reserva_id = int(datos["reserva_id"]) if (datos.get("reserva_id") or "").isdigit() else None
        modalidad = elegir_de(datos.get("modalidad"), {"HORA", "DIA"}, "la modalidad")
        cantidad = a_entero(datos.get("cantidad"), "la duración", 1, 24 if modalidad == "HORA" else 30)
        bicis = [a_entero(x, "la bicicleta") for x in f.getlist("bicis")]
        if not bicis:
            raise ValueError("Elegí al menos una bicicleta.")
        if len(set(bicis)) != len(bicis):
            raise ValueError("Una bicicleta está repetida.")
        obs = a_texto(datos.get("observaciones"), "las observaciones", 500)
        unidad = "hours" if modalidad == "HORA" else "days"
        with db.conexion() as con:
            cliente_id = asegurar_cliente(con, datos)
            a = con.execute(
                f"""INSERT INTO alquiler (cliente_id, reserva_id, ubicacion_retiro_id, operador_id, salida_real,
                                          fin_previsto, observaciones)
                    VALUES (%s, %s, %s, %s, now(), now() + make_interval({unidad} => %s), %s) RETURNING id""",
                (cliente_id, reserva_id, est, usuario["id"], cantidad, obs)).fetchone()
            for bid in bicis:
                con.execute(
                    """INSERT INTO alquiler_detalle (alquiler_id, bicicleta_id, tipo_bicicleta_id, modalidad,
                                                     precio_hora, precio_dia, salida_real)
                       VALUES (%s, %s, 1, %s, 1, 1, now())""", (a["id"], bid, modalidad))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return vista_alquiler_nuevo(request, usuario, int(datos.get("est") or 0) or None,
                                    int(datos["reserva_id"]) if (datos.get("reserva_id") or "").isdigit() else None,
                                    msg, datos, 400)
    return RedirectResponse(f"/alquileres/{a['id']}?ok=alquiler", status_code=303)


def ficha_alquiler(request, usuario, alquiler_id, error=None, ok=None, estado=200):
    a = db.consultar_uno(
        """SELECT a.*, c.nombre || ' ' || c.apellido AS cliente, c.id AS cliente_id, u.nombre AS estacion,
                  op.nombre || ' ' || op.apellido AS operador
             FROM alquiler a JOIN cliente c ON c.id = a.cliente_id JOIN ubicacion u ON u.id = a.ubicacion_retiro_id
             JOIN usuario op ON op.id = a.operador_id WHERE a.id = %s""", (alquiler_id,))
    if not a:
        raise NoExiste()
    detalles = db.consultar(
        """SELECT d.*, b.codigo, tb.nombre AS tipo, ud.nombre AS estacion_devolucion
             FROM alquiler_detalle d JOIN bicicleta b ON b.id = d.bicicleta_id
             JOIN tipo_bicicleta tb ON tb.id = d.tipo_bicicleta_id
             LEFT JOIN ubicacion ud ON ud.id = d.ubicacion_devolucion_id
            WHERE d.alquiler_id = %s ORDER BY d.id""", (alquiler_id,))
    saldo = db.consultar_uno("SELECT * FROM v_saldo_alquiler WHERE alquiler_id = %s", (alquiler_id,))
    pagos = db.consultar(
        """SELECT p.*, u.nombre AS por FROM pago p LEFT JOIN usuario u ON u.id = p.registrado_por
            WHERE p.alquiler_id = %s OR (p.reserva_id IS NOT NULL AND p.reserva_id = %s) ORDER BY p.creado_en""",
        (alquiler_id, a["reserva_id"]))
    cargos = db.consultar("SELECT * FROM cargo_extra WHERE alquiler_id = %s ORDER BY creado_en", (alquiler_id,))
    estaciones = db.consultar("SELECT id, nombre FROM ubicacion WHERE tipo = 'ESTACION' AND activa ORDER BY id")
    return pantalla(request, "alquiler.html", {
        "a": a, "detalles": detalles, "saldo": saldo, "pagos": pagos, "cargos": cargos, "estaciones": estaciones,
        "error": error, "ok": ok, "puede": bool(usuario["roles"] & ROLES_MOSTRADOR)}, estado, usuario)


@app.get("/alquileres/{alquiler_id}", response_class=HTMLResponse)
async def alquiler(request: Request, alquiler_id: int, ok: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_LECTURA)
    return ficha_alquiler(request, usuario, alquiler_id, ok=MENSAJES_OK.get(ok))


@app.get("/alquileres", response_class=HTMLResponse)
async def alquileres(request: Request, q: str = "", estado: str = "EN_CURSO"):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    estado = estado.upper() if estado.upper() in ("EN_CURSO", "FINALIZADO", "ANULADO", "TODOS") else "EN_CURSO"
    q = q.strip()[:60]
    filas = db.consultar(
        """SELECT a.id, a.salida_real, a.fin_previsto, a.retorno_real, a.estado, c.nombre || ' ' || c.apellido AS cliente,
                  u.nombre AS estacion, s.total, s.saldo,
                  (SELECT count(*) FROM alquiler_detalle d WHERE d.alquiler_id = a.id AND d.anulado_en IS NULL) AS bicis,
                  (a.retorno_real IS NULL AND a.anulada_en IS NULL AND a.fin_previsto < now()) AS demorado
             FROM alquiler a JOIN cliente c ON c.id = a.cliente_id JOIN ubicacion u ON u.id = a.ubicacion_retiro_id
             LEFT JOIN v_saldo_alquiler s ON s.alquiler_id = a.id
            WHERE (%(estado)s = 'TODOS' OR a.estado = %(estado)s)
              AND (%(q)s = '' OR c.apellido ILIKE '%%' || %(q)s || '%%' OR c.nombre ILIKE '%%' || %(q)s || '%%'
                   OR c.numero_documento ILIKE '%%' || upper(regexp_replace(%(q)s, '[^A-Za-z0-9]', '', 'g')) || '%%')
            ORDER BY a.salida_real DESC LIMIT 60""", {"estado": estado, "q": q})
    return pantalla(request, "alquileres.html", {"alquileres": filas, "estado": estado, "q": q}, usuario=usuario)


@app.post("/alquileres/{alquiler_id}/devolver")
async def devolver(request: Request, alquiler_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        detalle_id = a_entero(datos.get("detalle_id"), "la bicicleta")
        destino = a_entero(datos.get("destino"), "la estación de devolución")
        resultado = elegir_de(datos.get("resultado"), {"OK", "CON_DANIO"}, "el estado de devolución")
        obs = a_texto(datos.get("observaciones"), "las observaciones", 300)
        with db.conexion() as con:
            d = con.execute("SELECT bicicleta_id FROM alquiler_detalle WHERE id = %s AND alquiler_id = %s",
                            (detalle_id, alquiler_id)).fetchone()
            if not d:
                raise ValueError("Esa bicicleta no pertenece al alquiler.")
            if resultado == "CON_DANIO":
                tipo = elegir_de(datos.get("tipo"), {"FALLA", "DANIO", "ACCIDENTE"}, "el tipo de incidencia")
                sev = elegir_de(datos.get("severidad"), {"LEVE", "MODERADA", "GRAVE"}, "la severidad")
                sis = (datos.get("sistema") or "").strip().upper() or None
                if sis and sis not in {"FRENOS", "TRANSMISION", "NEUMATICOS", "RUEDAS", "CUADRO", "ELECTRICO",
                                       "SUSPENSION", "OTRO"}:
                    raise ValueError("El sistema afectado no es válido.")
                if not obs:
                    raise ValueError("Describí el daño en las observaciones.")
                monto = a_decimal(datos.get("cargo"), "el cargo", obligatorio=False)
            con.execute(
                """UPDATE alquiler_detalle SET devuelta_en = now(), ubicacion_devolucion_id = %s,
                          estado_devolucion = %s, observaciones_devolucion = %s WHERE id = %s""",
                (destino, resultado, obs, detalle_id))
            if resultado == "CON_DANIO":
                con.execute(
                    """INSERT INTO incidencia (bicicleta_id, detalle_id, reportada_por, tipo, severidad, sistema,
                                               descripcion, ocurrida_en, horas_uso)
                       SELECT b.id, %s, %s, %s, %s, %s, %s, now(), b.horas_uso FROM bicicleta b WHERE b.id = %s""",
                    (detalle_id, usuario["id"], tipo, sev, sis, obs, d["bicicleta_id"]))
                if monto:
                    con.execute(
                        """INSERT INTO cargo_extra (alquiler_id, detalle_id, concepto, monto, descripcion, registrado_por)
                           VALUES (%s, %s, 'DANIO', %s, %s, %s)""",
                        (alquiler_id, detalle_id, monto, obs[:200], usuario["id"]))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return ficha_alquiler(request, usuario, alquiler_id, error=msg, estado=400)
    return RedirectResponse(f"/alquileres/{alquiler_id}?ok=devolucion", status_code=303)


@app.post("/alquileres/{alquiler_id}/cobrar")
async def cobrar(request: Request, alquiler_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        monto = a_decimal(datos.get("monto"), "el monto")
        medio = elegir_de(datos.get("medio"), {"EFECTIVO", "TARJETA", "TRANSFERENCIA", "BILLETERA_VIRTUAL"},
                          "el medio de pago")
        ref = a_texto(datos.get("referencia"), "la referencia", 40)
        with db.conexion() as con:
            s = con.execute("SELECT saldo FROM v_saldo_alquiler WHERE alquiler_id = %s", (alquiler_id,)).fetchone()
            if not s:
                raise ValueError("El alquiler no existe o está anulado.")
            if monto > s["saldo"]:
                raise ValueError(f"El monto supera el saldo pendiente ($ {numero(s['saldo'])}).")
            con.execute(
                """INSERT INTO pago (alquiler_id, tipo, monto, medio, referencia, registrado_por)
                   VALUES (%s, 'COBRO', %s, %s, %s, %s)""", (alquiler_id, monto, medio, ref, usuario["id"]))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return ficha_alquiler(request, usuario, alquiler_id, error=msg, estado=400)
    return RedirectResponse(f"/alquileres/{alquiler_id}?ok=cobro", status_code=303)


@app.post("/alquileres/{alquiler_id}/cargo")
async def cargo(request: Request, alquiler_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        monto = a_decimal(datos.get("monto"), "el monto")
        concepto = elegir_de(datos.get("concepto"), {"DANIO", "PERDIDA", "LIMPIEZA", "OTRO"}, "el concepto")
        desc = a_texto(datos.get("descripcion"), "la descripción", 200)
        with db.conexion() as con:
            con.execute(
                """INSERT INTO cargo_extra (alquiler_id, concepto, monto, descripcion, registrado_por)
                   VALUES (%s, %s, %s, %s, %s)""", (alquiler_id, concepto, monto, desc, usuario["id"]))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return ficha_alquiler(request, usuario, alquiler_id, error=msg, estado=400)
    return RedirectResponse(f"/alquileres/{alquiler_id}?ok=cargo", status_code=303)


@app.post("/alquileres/{alquiler_id}/anular")
async def anular(request: Request, alquiler_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        motivo = a_texto(datos.get("motivo"), "el motivo", 200, obligatorio=True)
        with db.conexion() as con:
            n = con.execute("""UPDATE alquiler SET anulada_en = now(), motivo_anulacion = %s
                                WHERE id = %s AND anulada_en IS NULL AND retorno_real IS NULL""",
                            (motivo, alquiler_id)).rowcount
            if not n:
                raise ValueError("El alquiler ya está cerrado o anulado.")
            con.execute(
                """INSERT INTO auditoria_sistema (usuario_id, accion, entidad, entidad_id, detalle)
                   VALUES (%s, 'ALQUILER_ANULADO', 'alquiler', %s, jsonb_build_object('motivo', %s::text))""",
                (usuario["id"], alquiler_id, motivo))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return ficha_alquiler(request, usuario, alquiler_id, error=msg, estado=400)
    return RedirectResponse(f"/alquileres/{alquiler_id}?ok=anulado", status_code=303)


# ---------------------------------------------------------------- reservas

@app.get("/reservas", response_class=HTMLResponse)
async def reservas(request: Request, ok: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    abiertas = db.consultar(
        """SELECT r.id, r.inicio_previsto, r.fin_previsto, r.estado, r.canal, u.nombre AS estacion,
                  c.nombre || ' ' || c.apellido AS cliente,
                  (r.inicio_previsto + interval '60 minutes' < now()) AS por_vencer,
                  (SELECT string_agg(rd.cantidad || ' ' || tb.nombre, ', ' ORDER BY tb.nombre)
                     FROM reserva_detalle rd JOIN tipo_bicicleta tb ON tb.id = rd.tipo_bicicleta_id
                    WHERE rd.reserva_id = r.id) AS pedido
             FROM reserva r JOIN cliente c ON c.id = r.cliente_id JOIN ubicacion u ON u.id = r.ubicacion_id
            WHERE r.estado IN ('PENDIENTE','CONFIRMADA') ORDER BY r.inicio_previsto LIMIT 80""")
    recientes = db.consultar(
        """SELECT r.id, r.inicio_previsto, r.estado, r.motivo_cierre, c.nombre || ' ' || c.apellido AS cliente
             FROM reserva r JOIN cliente c ON c.id = r.cliente_id
            WHERE r.estado IN ('CONVERTIDA','CANCELADA','VENCIDA') ORDER BY r.cerrada_en DESC LIMIT 15""")
    return pantalla(request, "reservas.html", {"abiertas": abiertas, "recientes": recientes,
                                               "ok": MENSAJES_OK.get(ok)}, usuario=usuario)


def vista_reserva_nueva(request, usuario, error=None, valores=None, estado=200):
    estaciones = db.consultar("SELECT id, nombre FROM ubicacion WHERE tipo = 'ESTACION' AND activa ORDER BY id")
    tipos = db.consultar(
        """SELECT tb.id, tb.nombre, t.precio_hora, t.precio_dia FROM tipo_bicicleta tb
             LEFT JOIN LATERAL fn_tarifa_vigente(tb.id, fn_fecha_local(now())) t ON TRUE ORDER BY tb.nombre""")
    return pantalla(request, "reserva_nueva.html", {
        "estaciones": estaciones, "tipos": tipos, "error": error, "v": valores or {}}, estado, usuario)


@app.get("/reservas/nueva", response_class=HTMLResponse)
async def reserva_nueva(request: Request):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    return vista_reserva_nueva(request, usuario)


@app.post("/reservas/nueva")
async def reserva_crear(request: Request):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        est = a_entero(datos.get("est"), "la estación")
        inicio = a_fecha_local(datos.get("inicio"), "el inicio")
        fin = a_fecha_local(datos.get("fin"), "el fin")
        canal = elegir_de(datos.get("canal"), {"TELEFONO", "MOSTRADOR"}, "el canal")
        pedido = {}
        for k, v in datos.items():
            if k.startswith("tipo_") and (v or "").strip() not in ("", "0"):
                pedido[int(k[5:])] = a_entero(v, "la cantidad", 1, 10)
        if not pedido:
            raise ValueError("Pedí al menos una bicicleta.")
        sena = a_decimal(datos.get("sena"), "la seña", obligatorio=False)
        medio = elegir_de(datos.get("medio") or "EFECTIVO", {"EFECTIVO", "TARJETA", "TRANSFERENCIA", "BILLETERA_VIRTUAL"},
                          "el medio de pago")
        with db.conexion() as con:
            cid = asegurar_cliente(con, datos)
            r = con.execute(
                """INSERT INTO reserva (cliente_id, ubicacion_id, inicio_previsto, fin_previsto, canal, creada_en, creada_por)
                   VALUES (%s, %s, %s, %s, %s, now(), %s) RETURNING id""",
                (cid, est, inicio, fin, canal, usuario["id"])).fetchone()
            for tipo_id, cant in pedido.items():
                con.execute("INSERT INTO reserva_detalle (reserva_id, tipo_bicicleta_id, cantidad) VALUES (%s, %s, %s)",
                            (r["id"], tipo_id, cant))
            if sena:
                con.execute(
                    """INSERT INTO pago (reserva_id, tipo, monto, medio, registrado_por)
                       VALUES (%s, 'SENIA', %s, %s, %s)""", (r["id"], sena, medio, usuario["id"]))
                con.execute("UPDATE reserva SET estado = 'CONFIRMADA' WHERE id = %s", (r["id"],))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return vista_reserva_nueva(request, usuario, msg, datos, 400)
    return RedirectResponse(f"/reservas/{r['id']}?ok=reserva", status_code=303)


def ficha_reserva(request, usuario, reserva_id, error=None, ok=None, estado=200):
    r = db.consultar_uno(
        """SELECT r.*, c.nombre || ' ' || c.apellido AS cliente, c.id AS cliente_id, u.nombre AS estacion
             FROM reserva r JOIN cliente c ON c.id = r.cliente_id JOIN ubicacion u ON u.id = r.ubicacion_id
            WHERE r.id = %s""", (reserva_id,))
    if not r:
        raise NoExiste()
    pedido = db.consultar(
        """SELECT tb.nombre AS tipo, rd.cantidad FROM reserva_detalle rd
             JOIN tipo_bicicleta tb ON tb.id = rd.tipo_bicicleta_id WHERE rd.reserva_id = %s ORDER BY tb.nombre""",
        (reserva_id,))
    pagos = db.consultar("SELECT * FROM pago WHERE reserva_id = %s ORDER BY creado_en", (reserva_id,))
    alq = db.consultar_uno("SELECT id FROM alquiler WHERE reserva_id = %s", (reserva_id,))
    return pantalla(request, "reserva.html", {
        "r": r, "pedido": pedido, "pagos": pagos, "alquiler": alq, "error": error, "ok": ok}, estado, usuario)


@app.get("/reservas/{reserva_id}", response_class=HTMLResponse)
async def reserva(request: Request, reserva_id: int, ok: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    return ficha_reserva(request, usuario, reserva_id, ok=MENSAJES_OK.get(ok))


@app.post("/reservas/{reserva_id}/sena")
async def reserva_sena(request: Request, reserva_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        monto = a_decimal(datos.get("monto"), "la seña")
        medio = elegir_de(datos.get("medio"), {"EFECTIVO", "TARJETA", "TRANSFERENCIA", "BILLETERA_VIRTUAL"},
                          "el medio de pago")
        with db.conexion() as con:
            n = con.execute("SELECT 1 FROM reserva WHERE id = %s AND estado = 'PENDIENTE'", (reserva_id,)).fetchone()
            if not n:
                raise ValueError("Solo se registra la seña de una reserva pendiente.")
            con.execute("""INSERT INTO pago (reserva_id, tipo, monto, medio, registrado_por)
                           VALUES (%s, 'SENIA', %s, %s, %s)""", (reserva_id, monto, medio, usuario["id"]))
            con.execute("UPDATE reserva SET estado = 'CONFIRMADA' WHERE id = %s", (reserva_id,))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return ficha_reserva(request, usuario, reserva_id, error=msg, estado=400)
    return RedirectResponse(f"/reservas/{reserva_id}?ok=sena", status_code=303)


@app.post("/reservas/{reserva_id}/cancelar")
async def reserva_cancelar(request: Request, reserva_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR)
    datos = await formulario(request, usuario)
    try:
        motivo = a_texto(datos.get("motivo"), "el motivo", 180, obligatorio=True)
        devolver_sena = datos.get("devolver") == "1"
        with db.conexion() as con:
            n = con.execute(
                """UPDATE reserva SET estado = 'CANCELADA', cerrada_en = now(), motivo_cierre = %s
                    WHERE id = %s AND estado IN ('PENDIENTE','CONFIRMADA')""", (motivo, reserva_id)).rowcount
            if not n:
                raise ValueError("La reserva ya no se puede cancelar.")
            if devolver_sena:
                s = con.execute("""SELECT id, monto, medio FROM pago WHERE reserva_id = %s AND tipo = 'SENIA'
                                      AND estado = 'APROBADO' ORDER BY id LIMIT 1""", (reserva_id,)).fetchone()
                if s:
                    con.execute(
                        """INSERT INTO pago (reserva_id, tipo, monto, medio, pago_origen_id, registrado_por)
                           VALUES (%s, 'REEMBOLSO', %s, %s, %s, %s)""",
                        (reserva_id, s["monto"], s["medio"], s["id"], usuario["id"]))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return ficha_reserva(request, usuario, reserva_id, error=msg, estado=400)
    return RedirectResponse(f"/reservas/{reserva_id}?ok=cancelada", status_code=303)


# ---------------------------------------------------------------- taller

def vista_taller(request, usuario, error=None, ok=None, estado=200):
    ordenes = db.consultar(
        """SELECT o.id, o.abierta_en, o.iniciada_en, o.descripcion, o.costo_total, e.codigo AS estado_codigo,
                  e.nombre AS estado, t.nombre AS tipo, b.id AS bicicleta_id, b.codigo,
                  tec.nombre || ' ' || tec.apellido AS tecnico
             FROM orden_mantenimiento o JOIN estado_orden e ON e.id = o.estado_id
             JOIN tipo_mantenimiento t ON t.id = o.tipo_id JOIN bicicleta b ON b.id = o.bicicleta_id
             LEFT JOIN usuario tec ON tec.id = o.tecnico_id
            WHERE e.codigo IN ('ABIERTA','EN_CURSO') ORDER BY o.abierta_en""")
    # Última predicción de falla a 30 días del modelo (fase 2), total (sistema NULL) y por sistema.
    pred = """WITH pred AS (
                SELECT DISTINCT ON (bicicleta_id, sistema) bicicleta_id, sistema, probabilidad, calculada_en
                  FROM prediccion_mantenimiento WHERE horizonte_dias = 30
                 ORDER BY bicicleta_id, sistema, calculada_en DESC, id DESC)"""
    pendientes = db.consultar(
        pred + """
           SELECT p.bicicleta_id, p.codigo, p.plan_id, p.tarea, p.horas_restantes, p.dias_restantes, p.fecha_estimada,
                  pm.sistema, ps.probabilidad AS riesgo_sistema, pt.probabilidad AS riesgo_total
             FROM v_proximo_servicio p
             JOIN plan_mantenimiento pm ON pm.id = p.plan_id
             JOIN bicicleta b ON b.id = p.bicicleta_id JOIN estado_bicicleta e ON e.id = b.estado_id
             LEFT JOIN pred ps ON ps.bicicleta_id = p.bicicleta_id AND ps.sistema = pm.sistema
             LEFT JOIN pred pt ON pt.bicicleta_id = p.bicicleta_id AND pt.sistema IS NULL
            WHERE e.codigo = 'DISPONIBLE' AND (p.horas_restantes < 0 OR p.dias_restantes < 0)
              AND NOT EXISTS (SELECT 1 FROM orden_mantenimiento o JOIN estado_orden s ON s.id = o.estado_id
                               WHERE o.bicicleta_id = p.bicicleta_id AND s.codigo IN ('ABIERTA','EN_CURSO'))
            ORDER BY ps.probabilidad DESC NULLS LAST, LEAST(COALESCE(p.horas_restantes, 0), 0), p.dias_restantes NULLS LAST
            LIMIT 40""")
    # Bicicletas de riesgo alto que todavía no tienen ningún servicio vencido (el vencimiento no las muestra).
    riesgo_alto = db.consultar(
        pred + """
           SELECT b.id AS bicicleta_id, b.codigo, pt.probabilidad AS riesgo_total,
                  (SELECT sistema FROM pred x WHERE x.bicicleta_id = b.id AND x.sistema IS NOT NULL
                    ORDER BY x.probabilidad DESC LIMIT 1) AS sistema_mayor_riesgo
             FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
             JOIN pred pt ON pt.bicicleta_id = b.id AND pt.sistema IS NULL
            WHERE e.codigo = 'DISPONIBLE' AND pt.probabilidad >= %s
              AND NOT EXISTS (SELECT 1 FROM v_proximo_servicio v WHERE v.bicicleta_id = b.id
                                 AND (v.horas_restantes < 0 OR v.dias_restantes < 0))
              AND NOT EXISTS (SELECT 1 FROM orden_mantenimiento o JOIN estado_orden s ON s.id = o.estado_id
                               WHERE o.bicicleta_id = b.id AND s.codigo IN ('ABIERTA','EN_CURSO'))
            ORDER BY pt.probabilidad DESC LIMIT 8""", (UMBRALES_RIESGO["total"][1],))
    vigencia = db.consultar("SELECT max(calculada_en) AS calculada_en FROM prediccion_mantenimiento WHERE horizonte_dias = 30")
    calculada = vigencia[0]["calculada_en"] if vigencia else None
    desactualizada = calculada is not None and (datetime.now(calculada.tzinfo) - calculada).days > DIAS_PREDICCION_VIEJA
    return pantalla(request, "taller.html", {"ordenes": ordenes, "pendientes": pendientes, "riesgo_alto": riesgo_alto,
                                             "prediccion_fecha": calculada, "prediccion_vieja": desactualizada, "dias_prediccion_vieja": DIAS_PREDICCION_VIEJA,
                                             "error": error, "ok": ok}, estado, usuario)


@app.get("/taller", response_class=HTMLResponse)
async def taller(request: Request, ok: str = ""):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_TALLER)
    return vista_taller(request, usuario, ok=MENSAJES_OK.get(ok))


@app.post("/taller/abrir")
async def taller_abrir(request: Request):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_TALLER)
    datos = await formulario(request, usuario)
    destino = "/taller"
    try:
        bici_id = a_entero(datos.get("bicicleta_id"), "la bicicleta")
        destino = f"/bicicletas/{bici_id}"
        plan_id = int(datos["plan_id"]) if (datos.get("plan_id") or "").isdigit() else None
        desc = a_texto(datos.get("descripcion"), "la descripción", 300, obligatorio=plan_id is None)
        with db.conexion() as con:
            inc = None
            if plan_id is None:
                i = con.execute("""SELECT id FROM incidencia WHERE bicicleta_id = %s AND resuelta_en IS NULL
                                    ORDER BY ocurrida_en DESC LIMIT 1""", (bici_id,)).fetchone()
                inc = i["id"] if i else None
            if plan_id is not None and not desc:
                desc = con.execute("SELECT tarea FROM plan_mantenimiento WHERE id = %s", (plan_id,)).fetchone()["tarea"]
            con.execute(
                """INSERT INTO orden_mantenimiento (bicicleta_id, tipo_id, estado_id, plan_id, incidencia_id,
                                                    tecnico_id, taller_id, descripcion, abierta_en)
                   VALUES (%s, (SELECT id FROM tipo_mantenimiento WHERE codigo = %s),
                           (SELECT id FROM estado_orden WHERE codigo = 'ABIERTA'), %s, %s, %s,
                           (SELECT id FROM ubicacion WHERE tipo = 'TALLER' AND activa ORDER BY id LIMIT 1), %s, now())""",
                (bici_id, "PREVENTIVO" if plan_id else "CORRECTIVO", plan_id, inc, usuario["id"], desc))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        if destino.startswith("/bicicletas/"):
            return ficha_bicicleta(request, usuario, int(destino.rsplit("/", 1)[1]), error=msg, estado=400)
        return vista_taller(request, usuario, error=msg, estado=400)
    return RedirectResponse(destino + "?ok=orden", status_code=303)


@app.post("/taller/{orden_id}/iniciar")
async def taller_iniciar(request: Request, orden_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_TALLER)
    await formulario(request, usuario)
    try:
        with db.conexion() as con:
            n = con.execute(
                """UPDATE orden_mantenimiento SET estado_id = (SELECT id FROM estado_orden WHERE codigo = 'EN_CURSO'),
                          iniciada_en = now(), tecnico_id = %s
                    WHERE id = %s AND estado_id = (SELECT id FROM estado_orden WHERE codigo = 'ABIERTA')""",
                (usuario["id"], orden_id)).rowcount
            if not n:
                raise ValueError("La orden no está abierta.")
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return vista_taller(request, usuario, error=msg, estado=400)
    return RedirectResponse("/taller?ok=iniciada", status_code=303)


ITEM = re.compile(r"^\s*(?P<d>[^|]{1,150}?)\s*\|\s*(?P<c>[0-9]+(?:[.,][0-9]+)?)\s*\|\s*(?P<m>[0-9]+(?:[.,][0-9]+)?)\s*$")


@app.post("/taller/{orden_id}/cerrar")
async def taller_cerrar(request: Request, orden_id: int):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_TALLER)
    datos = await formulario(request, usuario)
    try:
        items = []
        for linea in (datos.get("items") or "").splitlines():
            if not linea.strip():
                continue
            m = ITEM.match(linea)
            if not m:
                raise ValueError(f"Ítem mal escrito: «{linea.strip()[:40]}». Formato: descripción | cantidad | costo unitario.")
            items.append((m["d"], Decimal(m["c"].replace(",", ".")), Decimal(m["m"].replace(",", "."))))
        if len(items) > 30:
            raise ValueError("Máximo 30 ítems por orden.")
        with db.conexion() as con:
            o = con.execute("""SELECT o.id, o.incidencia_id, o.plan_id FROM orden_mantenimiento o
                                 JOIN estado_orden e ON e.id = o.estado_id WHERE o.id = %s AND e.codigo = 'EN_CURSO'""",
                            (orden_id,)).fetchone()
            if not o:
                raise ValueError("Solo se cierra una orden en curso.")
            for d, c, m in items:
                con.execute("INSERT INTO orden_item (orden_id, descripcion, cantidad, costo_unitario) VALUES (%s, %s, %s, %s)",
                            (orden_id, d, c, m))
            con.execute(
                """UPDATE orden_mantenimiento SET estado_id = (SELECT id FROM estado_orden WHERE codigo = 'CERRADA'),
                          cerrada_en = now() WHERE id = %s""", (orden_id,))
            if o["incidencia_id"]:
                con.execute("UPDATE incidencia SET resuelta_en = now() WHERE id = %s", (o["incidencia_id"],))
    except (ValueError, pgerr.Error) as exc:
        msg = str(exc) if isinstance(exc, ValueError) else traducir(exc)
        return vista_taller(request, usuario, error=msg, estado=400)
    return RedirectResponse("/taller?ok=cerrada", status_code=303)


# ---------------------------------------------------------------- informes

@app.get("/informes", response_class=HTMLResponse)
async def informes(request: Request):
    usuario = sesion_actual(request)
    exigir(usuario, ROLES_MOSTRADOR | ROLES_TALLER)
    meses = db.consultar(
        """SELECT mes, sum(bicicletas_alquiladas) AS bicis, sum(horas) AS horas, sum(ingresos) AS ingresos
             FROM v_ingresos_mensuales GROUP BY mes ORDER BY mes DESC LIMIT 14""")
    rentab = db.consultar("SELECT * FROM v_rentabilidad_bicicleta ORDER BY margen DESC")
    return pantalla(request, "informes.html", {"meses": meses, "mejores": rentab[:8],
                                               "peores": list(reversed(rentab[-8:]))}, usuario=usuario)
