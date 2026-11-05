-- =====================================================================
-- Bicis sustentables: alquiler de bicicletas con reservas, cobros y
-- mantenimiento predictivo. PostgreSQL 14+ (probado en 16).
--
-- Principio de diseño: la base de datos hace cumplir sus propias reglas.
-- Una bicicleta no puede estar en dos alquileres a la vez, no se vende más
-- cupo del que hay, no se devuelve más de lo cobrado, y cada salida,
-- devolución y orden de taller actualiza solo el estado y el historial.
-- Los estados de una bicicleta cambian únicamente por fn_bici_cambiar_estado().
--
-- Ejecutar sobre una base vacía:  psql -v ON_ERROR_STOP=1 -f db/schema.sql
-- =====================================================================

-- ---------- Personal y acceso (quienes operan el sistema) ----------

CREATE TABLE rol (
    id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo  VARCHAR(20) NOT NULL UNIQUE,
    nombre  VARCHAR(50) NOT NULL
);

CREATE TABLE usuario (
    id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre    VARCHAR(50)  NOT NULL,
    apellido  VARCHAR(50)  NOT NULL,
    email     VARCHAR(254) NOT NULL,
    activo    BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ  NOT NULL DEFAULT now(),
    version   INTEGER      NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX uq_usuario_email ON usuario (lower(email));

CREATE TABLE usuario_rol (
    usuario_id INTEGER  NOT NULL REFERENCES usuario(id),
    rol_id     SMALLINT NOT NULL REFERENCES rol(id),
    PRIMARY KEY (usuario_id, rol_id)
);

-- La contraseña se guarda solo como hash (Argon2) y en una tabla aparte, para
-- que ninguna vista ni consulta de usuarios la exponga.
CREATE TABLE credencial_acceso (
    usuario_id     INTEGER PRIMARY KEY REFERENCES usuario(id),
    password_hash  TEXT        NOT NULL,
    debe_cambiar   BOOLEAN     NOT NULL DEFAULT TRUE,
    actualizada_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------- Clientes ----------

CREATE TABLE cliente (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre           VARCHAR(60)  NOT NULL,
    apellido         VARCHAR(60)  NOT NULL,
    tipo_documento   VARCHAR(10)  NOT NULL CHECK (tipo_documento IN ('DNI','PASAPORTE','OTRO')),
    pais_documento   CHAR(2)      NOT NULL DEFAULT 'AR',
    numero_documento VARCHAR(30)  NOT NULL,        -- normalizado: solo letras y números, en mayúsculas
    email            VARCHAR(254),
    telefono         VARCHAR(30),
    creado_en        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    version          INTEGER      NOT NULL DEFAULT 0,
    UNIQUE (tipo_documento, pais_documento, numero_documento)
);
CREATE INDEX ix_cliente_apellido ON cliente (lower(apellido), lower(nombre));

CREATE FUNCTION fn_cliente_normalizar() RETURNS trigger AS $$
BEGIN
    NEW.numero_documento := upper(regexp_replace(NEW.numero_documento, '[^A-Za-z0-9]', '', 'g'));
    IF NEW.numero_documento = '' THEN
        RAISE EXCEPTION 'El número de documento es obligatorio' USING ERRCODE = 'check_violation';
    END IF;
    NEW.pais_documento := upper(NEW.pais_documento);
    NEW.email := NULLIF(lower(btrim(NEW.email)), '');
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_cliente_normalizar BEFORE INSERT OR UPDATE ON cliente
    FOR EACH ROW EXECUTE FUNCTION fn_cliente_normalizar();

-- ---------- Catálogos ----------

CREATE TABLE ubicacion (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL UNIQUE,
    tipo       VARCHAR(10)  NOT NULL CHECK (tipo IN ('ESTACION','TALLER')),
    direccion  VARCHAR(150),
    capacidad  SMALLINT CHECK (capacidad > 0),     -- bicicletas que entran físicamente
    activa     BOOLEAN NOT NULL DEFAULT TRUE       -- baja lógica, nunca física
);

CREATE TABLE tipo_bicicleta (
    id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo  VARCHAR(20) NOT NULL UNIQUE,
    nombre  VARCHAR(60) NOT NULL
);

-- Historial de precios: una fila por cada vez que se cambia la lista.
-- El alquiler guarda una copia del precio vigente al salir, así que un
-- aumento posterior no altera lo ya contratado.
CREATE TABLE tarifa (
    id                INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_bicicleta_id SMALLINT NOT NULL REFERENCES tipo_bicicleta(id),
    vigente_desde     DATE NOT NULL,
    precio_hora       NUMERIC(10,2) NOT NULL CHECK (precio_hora > 0),
    precio_dia        NUMERIC(10,2) NOT NULL CHECK (precio_dia > 0),
    UNIQUE (tipo_bicicleta_id, vigente_desde),
    CHECK (precio_dia >= precio_hora)
);

CREATE FUNCTION fn_tarifa_vigente(p_tipo SMALLINT, p_fecha DATE)
RETURNS tarifa AS $$
    SELECT t FROM tarifa t
     WHERE t.tipo_bicicleta_id = p_tipo AND t.vigente_desde <= p_fecha
     ORDER BY t.vigente_desde DESC LIMIT 1;
$$ LANGUAGE sql STABLE;

CREATE TABLE estado_bicicleta (
    id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo  VARCHAR(30) NOT NULL UNIQUE,
    nombre  VARCHAR(80) NOT NULL
);

CREATE TABLE tipo_mantenimiento (
    id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo  VARCHAR(20) NOT NULL UNIQUE,           -- PREVENTIVO / CORRECTIVO
    nombre  VARCHAR(50) NOT NULL
);

CREATE TABLE estado_orden (
    id      SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo  VARCHAR(30) NOT NULL UNIQUE,
    nombre  VARCHAR(80) NOT NULL
);

-- ---------- Bicicletas ----------
-- horas_uso es el contador que gobierna el mantenimiento: suma las horas de
-- cada alquiler al devolverse, sin carga manual (a diferencia de un odómetro).

CREATE TABLE bicicleta (
    id                INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo            VARCHAR(20) NOT NULL UNIQUE,            -- el que lleva pintado el cuadro
    tipo_bicicleta_id SMALLINT NOT NULL REFERENCES tipo_bicicleta(id),
    estado_id         SMALLINT NOT NULL REFERENCES estado_bicicleta(id),
    ubicacion_base_id INTEGER  NOT NULL REFERENCES ubicacion(id),  -- estación a la que pertenece
    ubicacion_id      INTEGER  REFERENCES ubicacion(id),           -- dónde está ahora; NULL si está alquilada
    marca             VARCHAR(50),
    modelo            VARCHAR(50),
    talle             VARCHAR(2) NOT NULL DEFAULT 'U' CHECK (talle IN ('XS','S','M','L','XL','U')),
    fecha_alta        DATE NOT NULL DEFAULT current_date,
    fecha_baja        DATE,
    horas_uso         NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (horas_uso >= 0),
    usos              INTEGER NOT NULL DEFAULT 0 CHECK (usos >= 0),
    version           INTEGER NOT NULL DEFAULT 0,
    CHECK (fecha_baja IS NULL OR fecha_baja >= fecha_alta)
);
CREATE INDEX ix_bicicleta_estado ON bicicleta (estado_id);
CREATE INDEX ix_bicicleta_base ON bicicleta (ubicacion_base_id, tipo_bicicleta_id);

CREATE TABLE historial_estado_bicicleta (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bicicleta_id     INTEGER NOT NULL REFERENCES bicicleta(id),
    estado_ant_id    SMALLINT REFERENCES estado_bicicleta(id),
    estado_nuevo_id  SMALLINT NOT NULL REFERENCES estado_bicicleta(id),
    cambiado_en      TIMESTAMPTZ NOT NULL,
    origen           VARCHAR(10) NOT NULL CHECK (origen IN ('SISTEMA','USUARIO')),
    usuario_id       INTEGER REFERENCES usuario(id),
    motivo           VARCHAR(200)
);
CREATE INDEX ix_hist_bici ON historial_estado_bicicleta (bicicleta_id, cambiado_en);

-- Único camino para cambiar el estado de una bicicleta. Deja el historial y
-- mueve la bicicleta de lugar en el mismo paso.
CREATE FUNCTION fn_bici_cambiar_estado(
    p_bici INTEGER, p_codigo VARCHAR, p_ubicacion INTEGER,
    p_cuando TIMESTAMPTZ, p_motivo VARCHAR, p_usuario INTEGER DEFAULT NULL
) RETURNS void AS $$
DECLARE
    v_ant   SMALLINT;
    v_nuevo SMALLINT;
BEGIN
    SELECT estado_id INTO v_ant FROM bicicleta WHERE id = p_bici FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'La bicicleta % no existe', p_bici USING ERRCODE = 'foreign_key_violation';
    END IF;
    SELECT id INTO v_nuevo FROM estado_bicicleta WHERE codigo = p_codigo;
    IF v_nuevo IS NULL THEN
        RAISE EXCEPTION 'Estado de bicicleta inexistente: %', p_codigo USING ERRCODE = 'check_violation';
    END IF;

    PERFORM set_config('bicis.cambio_estado', 'on', true);
    UPDATE bicicleta
       SET estado_id = v_nuevo,
           ubicacion_id = p_ubicacion,
           fecha_baja = CASE WHEN p_codigo = 'BAJA' THEN p_cuando::date ELSE fecha_baja END
     WHERE id = p_bici;
    PERFORM set_config('bicis.cambio_estado', 'off', true);

    IF v_ant IS DISTINCT FROM v_nuevo THEN
        INSERT INTO historial_estado_bicicleta
            (bicicleta_id, estado_ant_id, estado_nuevo_id, cambiado_en, origen, usuario_id, motivo)
        VALUES (p_bici, v_ant, v_nuevo, p_cuando,
                CASE WHEN p_usuario IS NULL THEN 'SISTEMA' ELSE 'USUARIO' END, p_usuario, p_motivo);
    END IF;
END $$ LANGUAGE plpgsql;

CREATE FUNCTION fn_bicicleta_guardia() RETURNS trigger AS $$
DECLARE
    v_baja SMALLINT := (SELECT id FROM estado_bicicleta WHERE codigo = 'BAJA');
BEGIN
    IF NEW.estado_id IS DISTINCT FROM OLD.estado_id
       AND COALESCE(current_setting('bicis.cambio_estado', true), 'off') <> 'on' THEN
        RAISE EXCEPTION 'El estado de una bicicleta solo cambia con fn_bici_cambiar_estado()'
            USING ERRCODE = 'check_violation';
    END IF;
    IF OLD.estado_id = v_baja AND NEW.estado_id <> v_baja THEN
        RAISE EXCEPTION 'Una bicicleta dada de baja no vuelve al servicio' USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_bicicleta_guardia BEFORE UPDATE ON bicicleta
    FOR EACH ROW EXECUTE FUNCTION fn_bicicleta_guardia();

-- ---------- Reservas ----------
-- Se reserva por TIPO de bicicleta y estación, no por unidad: la unidad se
-- asigna al retirar. El cupo se controla en la base (fn_cupo).
--   PENDIENTE  : creada, falta la seña (vence si no se paga)
--   CONFIRMADA : seña acreditada, o reservada sin seña en mostrador
--   CONVERTIDA : el cliente retiró (existe el alquiler)
--   CANCELADA  : cancelada por el cliente o el local, antes del retiro
--   VENCIDA    : no se pagó la seña, o el cliente no se presentó

CREATE TABLE reserva (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id        INTEGER NOT NULL REFERENCES cliente(id),
    ubicacion_id      INTEGER NOT NULL REFERENCES ubicacion(id),     -- estación de retiro
    inicio_previsto   TIMESTAMPTZ NOT NULL,
    fin_previsto      TIMESTAMPTZ NOT NULL,
    estado            VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE'
                      CHECK (estado IN ('PENDIENTE','CONFIRMADA','CONVERTIDA','CANCELADA','VENCIDA')),
    canal             VARCHAR(10) NOT NULL CHECK (canal IN ('WEB','TELEFONO','MOSTRADOR')),
    creada_en         TIMESTAMPTZ NOT NULL DEFAULT now(),
    cerrada_en        TIMESTAMPTZ,                  -- cuando pasó a un estado final
    motivo_cierre     VARCHAR(200),
    creada_por        INTEGER REFERENCES usuario(id),  -- NULL si la hizo el cliente por la web
    CHECK (fin_previsto > inicio_previsto),
    CHECK (inicio_previsto >= creada_en),
    CHECK ((estado IN ('PENDIENTE','CONFIRMADA')) = (cerrada_en IS NULL)),
    CHECK (estado NOT IN ('CANCELADA','VENCIDA') OR motivo_cierre IS NOT NULL)
);
CREATE INDEX ix_reserva_activas ON reserva (ubicacion_id, inicio_previsto)
    WHERE estado IN ('PENDIENTE','CONFIRMADA');
CREATE INDEX ix_reserva_cliente ON reserva (cliente_id);

CREATE TABLE reserva_detalle (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reserva_id        BIGINT NOT NULL REFERENCES reserva(id),
    tipo_bicicleta_id SMALLINT NOT NULL REFERENCES tipo_bicicleta(id),
    cantidad          SMALLINT NOT NULL CHECK (cantidad BETWEEN 1 AND 10),
    UNIQUE (reserva_id, tipo_bicicleta_id)
);

-- ---------- Alquileres ----------
-- Un alquiler (cabecera) incluye de 1 a 10 bicicletas (detalle): un grupo o
-- una familia. Cada bicicleta se devuelve por separado.

CREATE TABLE alquiler (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id         INTEGER NOT NULL REFERENCES cliente(id),
    reserva_id         BIGINT UNIQUE REFERENCES reserva(id),
    ubicacion_retiro_id INTEGER NOT NULL REFERENCES ubicacion(id),
    operador_id        INTEGER NOT NULL REFERENCES usuario(id),
    salida_real        TIMESTAMPTZ NOT NULL DEFAULT now(),
    fin_previsto       TIMESTAMPTZ NOT NULL,
    retorno_real       TIMESTAMPTZ,              -- lo completa la base al devolverse la última bicicleta
    observaciones      VARCHAR(500),
    anulada_en         TIMESTAMPTZ,
    motivo_anulacion   VARCHAR(200),
    version            INTEGER NOT NULL DEFAULT 0,
    estado             VARCHAR(10) GENERATED ALWAYS AS (
                           CASE WHEN anulada_en IS NOT NULL THEN 'ANULADO'
                                WHEN retorno_real IS NOT NULL THEN 'FINALIZADO'
                                ELSE 'EN_CURSO' END) STORED,
    CHECK (fin_previsto > salida_real),
    CHECK (retorno_real IS NULL OR retorno_real >= salida_real),
    CHECK (anulada_en IS NULL OR (retorno_real IS NULL AND motivo_anulacion IS NOT NULL))
);
CREATE INDEX ix_alquiler_cliente ON alquiler (cliente_id);
CREATE INDEX ix_alquiler_salida ON alquiler (salida_real);
CREATE INDEX ix_alquiler_en_curso ON alquiler (fin_previsto) WHERE retorno_real IS NULL AND anulada_en IS NULL;

CREATE TABLE alquiler_detalle (
    id                      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alquiler_id             BIGINT   NOT NULL REFERENCES alquiler(id),
    bicicleta_id            INTEGER  NOT NULL REFERENCES bicicleta(id),
    tipo_bicicleta_id       SMALLINT NOT NULL REFERENCES tipo_bicicleta(id),   -- copia del tipo al salir
    modalidad               VARCHAR(4) NOT NULL CHECK (modalidad IN ('HORA','DIA')),
    precio_hora             NUMERIC(10,2) NOT NULL CHECK (precio_hora > 0),    -- copia de la tarifa al salir
    precio_dia              NUMERIC(10,2) NOT NULL CHECK (precio_dia > 0),
    salida_real             TIMESTAMPTZ NOT NULL,
    devuelta_en             TIMESTAMPTZ,
    ubicacion_devolucion_id INTEGER REFERENCES ubicacion(id),
    estado_devolucion       VARCHAR(10) CHECK (estado_devolucion IN ('OK','CON_DANIO')),
    observaciones_devolucion VARCHAR(300),
    segundos_uso            INTEGER CHECK (segundos_uso >= 0),
    importe                 NUMERIC(12,2) CHECK (importe >= 0),
    anulado_en              TIMESTAMPTZ,
    UNIQUE (alquiler_id, bicicleta_id),
    CHECK (devuelta_en IS NULL OR devuelta_en >= salida_real),
    CHECK ((devuelta_en IS NULL) = (importe IS NULL)),
    CHECK (devuelta_en IS NULL OR (ubicacion_devolucion_id IS NOT NULL AND estado_devolucion IS NOT NULL)),
    CHECK (anulado_en IS NULL OR devuelta_en IS NULL)
);
CREATE INDEX ix_detalle_bici ON alquiler_detalle (bicicleta_id, salida_real);
CREATE INDEX ix_detalle_devuelta ON alquiler_detalle (devuelta_en);

-- Una bicicleta no puede estar en dos alquileres a la vez.
CREATE UNIQUE INDEX uq_detalle_bici_en_uso
    ON alquiler_detalle (bicicleta_id) WHERE devuelta_en IS NULL AND anulado_en IS NULL;

-- ---------- Cobros y cargos ----------
-- Los pagos no se editan: un pago rechazado se reintenta con otra fila, y una
-- devolución de dinero es una fila de tipo REEMBOLSO ligada al pago original.

CREATE TABLE pago (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    reserva_id     BIGINT REFERENCES reserva(id),
    alquiler_id    BIGINT REFERENCES alquiler(id),
    tipo           VARCHAR(10) NOT NULL CHECK (tipo IN ('SENIA','COBRO','REEMBOLSO')),
    monto          NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    medio          VARCHAR(20) NOT NULL CHECK (medio IN ('EFECTIVO','TARJETA','TRANSFERENCIA','BILLETERA_VIRTUAL')),
    estado         VARCHAR(10) NOT NULL DEFAULT 'APROBADO' CHECK (estado IN ('PENDIENTE','APROBADO','RECHAZADO')),
    referencia     VARCHAR(40),
    pago_origen_id BIGINT REFERENCES pago(id),
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    registrado_por INTEGER REFERENCES usuario(id),     -- NULL si fue un pago en línea
    CHECK (reserva_id IS NOT NULL OR alquiler_id IS NOT NULL),
    CHECK (tipo <> 'SENIA' OR reserva_id IS NOT NULL),
    CHECK (tipo <> 'COBRO' OR alquiler_id IS NOT NULL),
    CHECK ((tipo = 'REEMBOLSO') = (pago_origen_id IS NOT NULL))
);
CREATE INDEX ix_pago_alquiler ON pago (alquiler_id);
CREATE INDEX ix_pago_reserva ON pago (reserva_id);

CREATE TABLE cargo_extra (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alquiler_id    BIGINT NOT NULL REFERENCES alquiler(id),
    detalle_id     BIGINT REFERENCES alquiler_detalle(id),
    concepto       VARCHAR(10) NOT NULL CHECK (concepto IN ('DANIO','PERDIDA','LIMPIEZA','OTRO')),
    monto          NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    descripcion    VARCHAR(200),
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    registrado_por INTEGER REFERENCES usuario(id)
);
CREATE INDEX ix_cargo_alquiler ON cargo_extra (alquiler_id);

-- ---------- Incidencias y mantenimiento ----------

CREATE TABLE incidencia (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bicicleta_id   INTEGER NOT NULL REFERENCES bicicleta(id),
    detalle_id     BIGINT REFERENCES alquiler_detalle(id),     -- el alquiler durante el cual ocurrió
    reportada_por  INTEGER REFERENCES usuario(id),
    tipo           VARCHAR(15) NOT NULL CHECK (tipo IN ('FALLA','DANIO','ACCIDENTE','ROBO_PERDIDA')),
    severidad      VARCHAR(10) NOT NULL CHECK (severidad IN ('LEVE','MODERADA','GRAVE')),
    sistema        VARCHAR(15) CHECK (sistema IN ('FRENOS','TRANSMISION','NEUMATICOS','RUEDAS','CUADRO','ELECTRICO','SUSPENSION','OTRO')),
    descripcion    VARCHAR(300) NOT NULL,
    ocurrida_en    TIMESTAMPTZ NOT NULL,
    horas_uso      NUMERIC(10,2) CHECK (horas_uso >= 0),       -- horas acumuladas de la bicicleta en ese momento
    resuelta_en    TIMESTAMPTZ,
    CHECK (resuelta_en IS NULL OR resuelta_en >= ocurrida_en)
);
CREATE INDEX ix_incidencia_bici ON incidencia (bicicleta_id, ocurrida_en DESC);

-- Plan: qué tarea se hace y cada cuánto, por tipo de bicicleta. Vence lo que
-- ocurra primero: horas de uso o días de calendario.
CREATE TABLE plan_mantenimiento (
    id                SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_bicicleta_id SMALLINT NOT NULL REFERENCES tipo_bicicleta(id),
    tarea             VARCHAR(100) NOT NULL,
    sistema           VARCHAR(15) CHECK (sistema IN ('FRENOS','TRANSMISION','NEUMATICOS','RUEDAS','CUADRO','ELECTRICO','SUSPENSION','OTRO')),
    cada_horas        INTEGER CHECK (cada_horas > 0),
    cada_dias         INTEGER CHECK (cada_dias > 0),
    activo            BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (tipo_bicicleta_id, tarea),
    CHECK (cada_horas IS NOT NULL OR cada_dias IS NOT NULL)
);

CREATE TABLE orden_mantenimiento (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bicicleta_id   INTEGER NOT NULL REFERENCES bicicleta(id),
    tipo_id        SMALLINT NOT NULL REFERENCES tipo_mantenimiento(id),
    estado_id      SMALLINT NOT NULL REFERENCES estado_orden(id),
    plan_id        SMALLINT REFERENCES plan_mantenimiento(id),   -- solo preventivas
    incidencia_id  BIGINT REFERENCES incidencia(id),             -- solo correctivas
    tecnico_id     INTEGER REFERENCES usuario(id),
    taller_id      INTEGER NOT NULL REFERENCES ubicacion(id),
    descripcion    VARCHAR(300),
    abierta_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    iniciada_en    TIMESTAMPTZ,
    cerrada_en     TIMESTAMPTZ,
    horas_uso      NUMERIC(10,2) CHECK (horas_uso >= 0),         -- horas de la bicicleta al ingresar
    costo_total    NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (costo_total >= 0),
    version        INTEGER NOT NULL DEFAULT 0,
    CHECK (iniciada_en IS NULL OR iniciada_en >= abierta_en),
    CHECK (cerrada_en IS NULL OR cerrada_en >= abierta_en)
);
CREATE INDEX ix_orden_bici ON orden_mantenimiento (bicicleta_id, abierta_en DESC);
CREATE INDEX ix_orden_estado ON orden_mantenimiento (estado_id);

CREATE TABLE orden_item (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    orden_id        BIGINT NOT NULL REFERENCES orden_mantenimiento(id),
    descripcion     VARCHAR(150) NOT NULL,
    cantidad        NUMERIC(8,2) NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    costo_unitario  NUMERIC(12,2) NOT NULL CHECK (costo_unitario >= 0)
);
CREATE INDEX ix_orden_item_orden ON orden_item (orden_id);

CREATE TABLE historial_orden (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    orden_id         BIGINT NOT NULL REFERENCES orden_mantenimiento(id),
    estado_ant_id    SMALLINT REFERENCES estado_orden(id),
    estado_nuevo_id  SMALLINT NOT NULL REFERENCES estado_orden(id),
    cambiado_en      TIMESTAMPTZ NOT NULL,
    usuario_id       INTEGER REFERENCES usuario(id)
);
CREATE INDEX ix_hist_orden ON historial_orden (orden_id, cambiado_en);

-- Acciones administrativas (anulaciones, cambios de tarifa, bajas de bicicletas).
-- La aplicación escribe aquí; el generador de datos deja algunas filas de ejemplo.
CREATE TABLE auditoria_sistema (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id  INTEGER REFERENCES usuario(id),
    accion      VARCHAR(40) NOT NULL,
    entidad     VARCHAR(40) NOT NULL,
    entidad_id  BIGINT,
    detalle     JSONB,
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fase 2 del proyecto: predicciones de falla que escribirá un modelo.
CREATE TABLE prediccion_mantenimiento (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bicicleta_id     INTEGER NOT NULL REFERENCES bicicleta(id),
    calculada_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    horizonte_dias   SMALLINT NOT NULL CHECK (horizonte_dias > 0),
    sistema          VARCHAR(15),
    probabilidad     NUMERIC(5,4) NOT NULL CHECK (probabilidad BETWEEN 0 AND 1),
    modelo_version   VARCHAR(40) NOT NULL
);

-- =====================================================================
-- Reglas de negocio (funciones y triggers)
-- =====================================================================

CREATE FUNCTION fn_fecha_local(p_ts TIMESTAMPTZ) RETURNS date AS $$
    SELECT (p_ts AT TIME ZONE 'America/Argentina/Buenos_Aires')::date;
$$ LANGUAGE sql IMMUTABLE;

-- Cuánto se cobra por una bicicleta, según el tiempo real de uso.
--   * Tolerancia: 10 minutos sobre la hora, y 1 hora sobre el día.
--   * Modalidad HORA: se cobran horas completas (mínimo una), con tope en el
--     precio de los días que corresponden: nunca sale más caro que alquilar por día.
--   * Modalidad DIA : se cobran días completos (mínimo uno).
-- La demora en devolver se paga sola: se cobra el tiempo real, no el pactado.
CREATE FUNCTION fn_importe(p_modalidad VARCHAR, p_precio_hora NUMERIC, p_precio_dia NUMERIC, p_segundos BIGINT)
RETURNS NUMERIC AS $$
DECLARE
    v_horas INTEGER := GREATEST(1, ceil((p_segundos - 600)  / 3600.0))::int;
    v_dias  INTEGER := GREATEST(1, ceil((p_segundos - 3600) / 86400.0))::int;
BEGIN
    IF p_modalidad = 'DIA' THEN
        RETURN round(v_dias * p_precio_dia, 2);
    END IF;
    RETURN round(LEAST(v_horas * p_precio_hora, v_dias * p_precio_dia), 2);
END $$ LANGUAGE plpgsql IMMUTABLE;

-- Cupo: cuántas bicicletas de un tipo quedan para reservar en una estación y
-- un horario. Flota activa de la estación, menos reservas vigentes que se
-- superponen, menos bicicletas de esa estación que siguen alquiladas y
-- vuelven después del inicio pedido.
CREATE FUNCTION fn_cupo(p_ubicacion INTEGER, p_tipo SMALLINT, p_inicio TIMESTAMPTZ, p_fin TIMESTAMPTZ,
                        p_excluir_reserva BIGINT DEFAULT NULL)
RETURNS INTEGER AS $$
    SELECT (
        (SELECT count(*) FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
          WHERE b.ubicacion_base_id = p_ubicacion AND b.tipo_bicicleta_id = p_tipo
            AND e.codigo NOT IN ('BAJA','FUERA_DE_SERVICIO'))
        - COALESCE((SELECT sum(rd.cantidad)
                      FROM reserva r JOIN reserva_detalle rd ON rd.reserva_id = r.id
                     WHERE r.ubicacion_id = p_ubicacion AND rd.tipo_bicicleta_id = p_tipo
                       AND r.estado IN ('PENDIENTE','CONFIRMADA')
                       AND r.inicio_previsto < p_fin AND r.fin_previsto > p_inicio
                       AND r.id IS DISTINCT FROM p_excluir_reserva), 0)
        - (SELECT count(*)
             FROM alquiler_detalle d
             JOIN alquiler a ON a.id = d.alquiler_id
             JOIN bicicleta b ON b.id = d.bicicleta_id
            WHERE b.ubicacion_base_id = p_ubicacion AND b.tipo_bicicleta_id = p_tipo
              AND d.devuelta_en IS NULL AND d.anulado_en IS NULL AND a.fin_previsto > p_inicio)
    )::integer;
$$ LANGUAGE sql STABLE;

-- 1) Reservas: no se vende más cupo del que hay.
CREATE FUNCTION fn_reserva_detalle_cupo() RETURNS trigger AS $$
DECLARE
    r        reserva%ROWTYPE;
    v_cupo   INTEGER;
BEGIN
    SELECT * INTO r FROM reserva WHERE id = NEW.reserva_id;
    IF r.estado NOT IN ('PENDIENTE','CONFIRMADA') THEN
        RAISE EXCEPTION 'La reserva % está %: ya no se puede modificar', r.id, lower(r.estado)
            USING ERRCODE = 'check_violation';
    END IF;
    PERFORM pg_advisory_xact_lock(hashtext('cupo:' || r.ubicacion_id || ':' || NEW.tipo_bicicleta_id));
    v_cupo := fn_cupo(r.ubicacion_id, NEW.tipo_bicicleta_id, r.inicio_previsto, r.fin_previsto, NEW.reserva_id);
    IF NEW.cantidad > v_cupo THEN
        RAISE EXCEPTION 'No hay cupo: se piden % y quedan % de ese tipo en esa estación para ese horario',
            NEW.cantidad, GREATEST(v_cupo, 0) USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_reserva_detalle_cupo BEFORE INSERT OR UPDATE OF cantidad, tipo_bicicleta_id ON reserva_detalle
    FOR EACH ROW EXECUTE FUNCTION fn_reserva_detalle_cupo();

-- Una reserva solo avanza por transiciones válidas; los estados finales no se reabren.
CREATE FUNCTION fn_reserva_transicion() RETURNS trigger AS $$
BEGIN
    IF NOT (   (OLD.estado = 'PENDIENTE'  AND NEW.estado IN ('CONFIRMADA','CANCELADA','VENCIDA'))
            OR (OLD.estado = 'CONFIRMADA' AND NEW.estado IN ('CONVERTIDA','CANCELADA','VENCIDA'))) THEN
        RAISE EXCEPTION 'Una reserva % no puede pasar a %', lower(OLD.estado), lower(NEW.estado)
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_reserva_transicion BEFORE UPDATE OF estado ON reserva
    FOR EACH ROW WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
    EXECUTE FUNCTION fn_reserva_transicion();

-- 2) Alquileres: al retirar con reserva, esta se marca convertida.
CREATE FUNCTION fn_alquiler_validar() RETURNS trigger AS $$
DECLARE
    r reserva%ROWTYPE;
BEGIN
    IF NEW.reserva_id IS NOT NULL THEN
        SELECT * INTO r FROM reserva WHERE id = NEW.reserva_id FOR UPDATE;
        IF r.estado NOT IN ('PENDIENTE','CONFIRMADA') THEN
            RAISE EXCEPTION 'La reserva % está %: no se puede retirar', r.id, lower(r.estado)
                USING ERRCODE = 'check_violation';
        END IF;
        IF r.cliente_id <> NEW.cliente_id OR r.ubicacion_id <> NEW.ubicacion_retiro_id THEN
            RAISE EXCEPTION 'El alquiler no coincide con el cliente o la estación de la reserva %', r.id
                USING ERRCODE = 'check_violation';
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_alquiler_validar BEFORE INSERT ON alquiler
    FOR EACH ROW EXECUTE FUNCTION fn_alquiler_validar();

CREATE FUNCTION fn_alquiler_reserva_convertida() RETURNS trigger AS $$
BEGIN
    IF NEW.reserva_id IS NOT NULL THEN
        UPDATE reserva
           SET estado = 'CONVERTIDA', cerrada_en = NEW.salida_real,
               motivo_cierre = 'Retiro, alquiler ' || NEW.id
         WHERE id = NEW.reserva_id;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_alquiler_reserva_convertida AFTER INSERT ON alquiler
    FOR EACH ROW EXECUTE FUNCTION fn_alquiler_reserva_convertida();

-- Todo alquiler debe tener al menos una bicicleta; se verifica al confirmar la transacción.
CREATE FUNCTION fn_alquiler_con_detalle() RETURNS trigger AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM alquiler_detalle WHERE alquiler_id = NEW.id) THEN
        RAISE EXCEPTION 'El alquiler % no tiene ninguna bicicleta', NEW.id USING ERRCODE = 'check_violation';
    END IF;
    RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER tg_alquiler_con_detalle AFTER INSERT ON alquiler
    DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION fn_alquiler_con_detalle();

-- 3) Salida de una bicicleta: debe estar disponible y en la estación de retiro.
CREATE FUNCTION fn_detalle_validar() RETURNS trigger AS $$
DECLARE
    a        alquiler%ROWTYPE;
    b        bicicleta%ROWTYPE;
    v_estado VARCHAR;
    t        tarifa%ROWTYPE;
BEGIN
    SELECT * INTO a FROM alquiler WHERE id = NEW.alquiler_id;
    IF a.anulada_en IS NOT NULL OR a.retorno_real IS NOT NULL THEN
        RAISE EXCEPTION 'El alquiler % ya está cerrado', a.id USING ERRCODE = 'check_violation';
    END IF;
    IF (SELECT count(*) FROM alquiler_detalle WHERE alquiler_id = NEW.alquiler_id) >= 10 THEN
        RAISE EXCEPTION 'Un alquiler admite hasta 10 bicicletas' USING ERRCODE = 'check_violation';
    END IF;

    SELECT * INTO b FROM bicicleta WHERE id = NEW.bicicleta_id FOR UPDATE;
    SELECT codigo INTO v_estado FROM estado_bicicleta WHERE id = b.estado_id;
    IF v_estado IS DISTINCT FROM 'DISPONIBLE' THEN
        RAISE EXCEPTION 'La bicicleta % no está disponible (estado: %)', b.codigo, COALESCE(v_estado, 'inexistente')
            USING ERRCODE = 'check_violation';
    END IF;
    IF b.ubicacion_id IS DISTINCT FROM a.ubicacion_retiro_id THEN
        RAISE EXCEPTION 'La bicicleta % no está en la estación de retiro', b.codigo
            USING ERRCODE = 'check_violation';
    END IF;

    SELECT * INTO t FROM fn_tarifa_vigente(b.tipo_bicicleta_id, fn_fecha_local(a.salida_real));
    IF t.id IS NULL THEN
        RAISE EXCEPTION 'No hay tarifa vigente para ese tipo de bicicleta' USING ERRCODE = 'check_violation';
    END IF;

    NEW.tipo_bicicleta_id := b.tipo_bicicleta_id;
    NEW.precio_hora := t.precio_hora;
    NEW.precio_dia  := t.precio_dia;
    NEW.salida_real := a.salida_real;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_detalle_validar BEFORE INSERT ON alquiler_detalle
    FOR EACH ROW EXECUTE FUNCTION fn_detalle_validar();

CREATE FUNCTION fn_detalle_salida() RETURNS trigger AS $$
BEGIN
    PERFORM fn_bici_cambiar_estado(NEW.bicicleta_id, 'ALQUILADA', NULL, NEW.salida_real,
                                   'Salida, alquiler ' || NEW.alquiler_id);
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_detalle_salida AFTER INSERT ON alquiler_detalle
    FOR EACH ROW EXECUTE FUNCTION fn_detalle_salida();

-- 4) Devolución: calcula tiempo e importe; la bicicleta suma horas y vuelve a
--    la estación (disponible, o fuera de servicio si volvió dañada).
CREATE FUNCTION fn_detalle_devolucion_validar() RETURNS trigger AS $$
BEGIN
    IF OLD.devuelta_en IS NOT NULL THEN
        RAISE EXCEPTION 'Esta bicicleta ya fue devuelta: el registro no se modifica' USING ERRCODE = 'check_violation';
    END IF;
    IF OLD.anulado_en IS NOT NULL THEN
        RAISE EXCEPTION 'El alquiler fue anulado' USING ERRCODE = 'check_violation';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM ubicacion WHERE id = NEW.ubicacion_devolucion_id AND tipo = 'ESTACION' AND activa) THEN
        RAISE EXCEPTION 'La estación de devolución no es válida' USING ERRCODE = 'check_violation';
    END IF;
    NEW.segundos_uso := floor(extract(epoch FROM (NEW.devuelta_en - OLD.salida_real)));
    NEW.importe := fn_importe(OLD.modalidad, OLD.precio_hora, OLD.precio_dia, NEW.segundos_uso);
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_detalle_devolucion_validar BEFORE UPDATE ON alquiler_detalle
    FOR EACH ROW WHEN (OLD.devuelta_en IS NOT NULL OR NEW.devuelta_en IS NOT NULL)
    EXECUTE FUNCTION fn_detalle_devolucion_validar();

CREATE FUNCTION fn_detalle_devolucion() RETURNS trigger AS $$
BEGIN
    UPDATE bicicleta
       SET horas_uso = horas_uso + round(NEW.segundos_uso / 3600.0, 2),
           usos = usos + 1
     WHERE id = NEW.bicicleta_id;

    PERFORM fn_bici_cambiar_estado(
        NEW.bicicleta_id,
        CASE NEW.estado_devolucion WHEN 'OK' THEN 'DISPONIBLE' ELSE 'FUERA_DE_SERVICIO' END,
        NEW.ubicacion_devolucion_id, NEW.devuelta_en,
        'Devolución, alquiler ' || NEW.alquiler_id);

    IF NOT EXISTS (SELECT 1 FROM alquiler_detalle
                    WHERE alquiler_id = NEW.alquiler_id AND devuelta_en IS NULL AND anulado_en IS NULL) THEN
        UPDATE alquiler
           SET retorno_real = (SELECT max(devuelta_en) FROM alquiler_detalle WHERE alquiler_id = NEW.alquiler_id)
         WHERE id = NEW.alquiler_id;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_detalle_devolucion AFTER UPDATE ON alquiler_detalle
    FOR EACH ROW WHEN (OLD.devuelta_en IS NULL AND NEW.devuelta_en IS NOT NULL)
    EXECUTE FUNCTION fn_detalle_devolucion();

-- 5) Anulación de un alquiler cargado por error (solo si no se devolvió nada).
CREATE FUNCTION fn_alquiler_anulacion_validar() RETURNS trigger AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM alquiler_detalle WHERE alquiler_id = NEW.id AND devuelta_en IS NOT NULL) THEN
        RAISE EXCEPTION 'No se puede anular: ya se devolvieron bicicletas de este alquiler'
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_alquiler_anulacion_validar BEFORE UPDATE ON alquiler
    FOR EACH ROW WHEN (OLD.anulada_en IS NULL AND NEW.anulada_en IS NOT NULL)
    EXECUTE FUNCTION fn_alquiler_anulacion_validar();

CREATE FUNCTION fn_alquiler_anulacion() RETURNS trigger AS $$
DECLARE
    d record;
BEGIN
    FOR d IN SELECT bicicleta_id FROM alquiler_detalle WHERE alquiler_id = NEW.id AND anulado_en IS NULL LOOP
        PERFORM fn_bici_cambiar_estado(d.bicicleta_id, 'DISPONIBLE', NEW.ubicacion_retiro_id, NEW.anulada_en,
                                       'Anulación, alquiler ' || NEW.id);
    END LOOP;
    UPDATE alquiler_detalle SET anulado_en = NEW.anulada_en WHERE alquiler_id = NEW.id AND anulado_en IS NULL;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_alquiler_anulacion AFTER UPDATE ON alquiler
    FOR EACH ROW WHEN (OLD.anulada_en IS NULL AND NEW.anulada_en IS NOT NULL)
    EXECUTE FUNCTION fn_alquiler_anulacion();

-- 6) Pagos: no se devuelve más de lo que se cobró.
CREATE FUNCTION fn_pago_validar() RETURNS trigger AS $$
DECLARE
    o            pago%ROWTYPE;
    v_devuelto   NUMERIC;
BEGIN
    IF NEW.tipo = 'REEMBOLSO' THEN
        SELECT * INTO o FROM pago WHERE id = NEW.pago_origen_id FOR UPDATE;
        IF o.tipo = 'REEMBOLSO' OR o.estado <> 'APROBADO' THEN
            RAISE EXCEPTION 'Solo se reembolsa un cobro o seña aprobados' USING ERRCODE = 'check_violation';
        END IF;
        IF o.reserva_id IS DISTINCT FROM NEW.reserva_id OR o.alquiler_id IS DISTINCT FROM NEW.alquiler_id THEN
            RAISE EXCEPTION 'El reembolso debe corresponder a la misma reserva o alquiler del pago original'
                USING ERRCODE = 'check_violation';
        END IF;
        SELECT COALESCE(sum(monto), 0) INTO v_devuelto
          FROM pago WHERE pago_origen_id = o.id AND tipo = 'REEMBOLSO' AND estado = 'APROBADO';
        IF NEW.estado = 'APROBADO' AND NEW.monto > o.monto - v_devuelto THEN
            RAISE EXCEPTION 'No se puede reembolsar % : del pago original quedan % por devolver',
                NEW.monto, o.monto - v_devuelto USING ERRCODE = 'check_violation';
        END IF;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_pago_validar BEFORE INSERT ON pago
    FOR EACH ROW EXECUTE FUNCTION fn_pago_validar();

CREATE FUNCTION fn_cargo_validar() RETURNS trigger AS $$
BEGIN
    IF NEW.detalle_id IS NOT NULL AND NOT EXISTS
        (SELECT 1 FROM alquiler_detalle WHERE id = NEW.detalle_id AND alquiler_id = NEW.alquiler_id) THEN
        RAISE EXCEPTION 'La bicicleta del cargo no pertenece a ese alquiler' USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_cargo_validar BEFORE INSERT ON cargo_extra
    FOR EACH ROW EXECUTE FUNCTION fn_cargo_validar();

-- 7) Órdenes de mantenimiento: al abrirse sacan la bicicleta de circulación;
--    al cerrarse o cancelarse la devuelven a su estación si no quedan otras abiertas.
CREATE FUNCTION fn_orden_validar_alta() RETURNS trigger AS $$
DECLARE
    v_estado   VARCHAR;
    v_tipo_bic SMALLINT;
    v_horas    NUMERIC;
    v_tipo     VARCHAR := (SELECT codigo FROM tipo_mantenimiento WHERE id = NEW.tipo_id);
BEGIN
    SELECT e.codigo, b.tipo_bicicleta_id, b.horas_uso INTO v_estado, v_tipo_bic, v_horas
      FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
     WHERE b.id = NEW.bicicleta_id FOR UPDATE OF b;
    IF v_estado = 'ALQUILADA' THEN
        RAISE EXCEPTION 'La bicicleta está alquilada: no puede ingresar a taller' USING ERRCODE = 'check_violation';
    END IF;
    IF v_estado = 'BAJA' THEN
        RAISE EXCEPTION 'La bicicleta está dada de baja' USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.estado_id <> (SELECT id FROM estado_orden WHERE codigo = 'ABIERTA') THEN
        RAISE EXCEPTION 'Una orden se crea abierta' USING ERRCODE = 'check_violation';
    END IF;
    IF (v_tipo = 'PREVENTIVO') <> (NEW.plan_id IS NOT NULL) THEN
        RAISE EXCEPTION 'Una orden preventiva lleva plan de mantenimiento; una correctiva no' USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.plan_id IS NOT NULL AND NOT EXISTS
        (SELECT 1 FROM plan_mantenimiento WHERE id = NEW.plan_id AND tipo_bicicleta_id = v_tipo_bic) THEN
        RAISE EXCEPTION 'El plan no corresponde al tipo de esta bicicleta' USING ERRCODE = 'check_violation';
    END IF;
    IF NEW.horas_uso IS NULL THEN
        NEW.horas_uso := v_horas;
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_orden_validar_alta BEFORE INSERT ON orden_mantenimiento
    FOR EACH ROW EXECUTE FUNCTION fn_orden_validar_alta();

CREATE FUNCTION fn_orden_alta() RETURNS trigger AS $$
BEGIN
    PERFORM fn_bici_cambiar_estado(NEW.bicicleta_id, 'EN_MANTENIMIENTO', NEW.taller_id, NEW.abierta_en,
                                   'Orden de mantenimiento ' || NEW.id);
    INSERT INTO historial_orden (orden_id, estado_ant_id, estado_nuevo_id, cambiado_en, usuario_id)
    VALUES (NEW.id, NULL, NEW.estado_id, NEW.abierta_en, NEW.tecnico_id);
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_orden_alta AFTER INSERT ON orden_mantenimiento
    FOR EACH ROW EXECUTE FUNCTION fn_orden_alta();

CREATE FUNCTION fn_orden_transicion() RETURNS trigger AS $$
DECLARE
    v_ant  VARCHAR := (SELECT codigo FROM estado_orden WHERE id = OLD.estado_id);
    v_nvo  VARCHAR := (SELECT codigo FROM estado_orden WHERE id = NEW.estado_id);
BEGIN
    IF NOT (   (v_ant = 'ABIERTA'  AND v_nvo IN ('EN_CURSO','CANCELADA'))
            OR (v_ant = 'EN_CURSO' AND v_nvo IN ('CERRADA','CANCELADA'))) THEN
        RAISE EXCEPTION 'Una orden % no puede pasar a %', lower(v_ant), lower(v_nvo) USING ERRCODE = 'check_violation';
    END IF;
    IF v_nvo = 'EN_CURSO' AND NEW.iniciada_en IS NULL THEN
        RAISE EXCEPTION 'Falta la fecha de inicio' USING ERRCODE = 'check_violation';
    END IF;
    IF v_nvo IN ('CERRADA','CANCELADA') AND NEW.cerrada_en IS NULL THEN
        RAISE EXCEPTION 'Falta la fecha de cierre' USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_orden_transicion BEFORE UPDATE OF estado_id ON orden_mantenimiento
    FOR EACH ROW WHEN (OLD.estado_id IS DISTINCT FROM NEW.estado_id)
    EXECUTE FUNCTION fn_orden_transicion();

CREATE FUNCTION fn_orden_estado_cambiado() RETURNS trigger AS $$
DECLARE
    v_nvo    VARCHAR := (SELECT codigo FROM estado_orden WHERE id = NEW.estado_id);
    v_cuando TIMESTAMPTZ := COALESCE(NEW.cerrada_en, NEW.iniciada_en);
    v_base   INTEGER;
BEGIN
    INSERT INTO historial_orden (orden_id, estado_ant_id, estado_nuevo_id, cambiado_en, usuario_id)
    VALUES (NEW.id, OLD.estado_id, NEW.estado_id, v_cuando, NEW.tecnico_id);

    IF v_nvo IN ('CERRADA','CANCELADA')
       AND NOT EXISTS (SELECT 1 FROM orden_mantenimiento o JOIN estado_orden e ON e.id = o.estado_id
                        WHERE o.bicicleta_id = NEW.bicicleta_id AND o.id <> NEW.id
                          AND e.codigo IN ('ABIERTA','EN_CURSO'))
       AND (SELECT e.codigo FROM bicicleta b JOIN estado_bicicleta e ON e.id = b.estado_id
             WHERE b.id = NEW.bicicleta_id) = 'EN_MANTENIMIENTO' THEN
        SELECT ubicacion_base_id INTO v_base FROM bicicleta WHERE id = NEW.bicicleta_id;
        PERFORM fn_bici_cambiar_estado(NEW.bicicleta_id, 'DISPONIBLE', v_base, v_cuando,
                                       'Fin de la orden de mantenimiento ' || NEW.id);
    END IF;
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_orden_estado_cambiado AFTER UPDATE OF estado_id ON orden_mantenimiento
    FOR EACH ROW WHEN (OLD.estado_id IS DISTINCT FROM NEW.estado_id)
    EXECUTE FUNCTION fn_orden_estado_cambiado();

-- El costo de la orden es siempre la suma de sus ítems; los ítems no se tocan con la orden cerrada.
CREATE FUNCTION fn_orden_item_costo() RETURNS trigger AS $$
DECLARE
    v_orden BIGINT := COALESCE(NEW.orden_id, OLD.orden_id);
BEGIN
    IF (SELECT e.codigo FROM orden_mantenimiento o JOIN estado_orden e ON e.id = o.estado_id
         WHERE o.id = v_orden) IN ('CERRADA','CANCELADA') THEN
        RAISE EXCEPTION 'La orden % ya está cerrada: no se modifican sus ítems', v_orden USING ERRCODE = 'check_violation';
    END IF;
    UPDATE orden_mantenimiento
       SET costo_total = COALESCE((SELECT sum(round(cantidad * costo_unitario, 2))
                                     FROM orden_item WHERE orden_id = v_orden), 0)
     WHERE id = v_orden;
    RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tg_orden_item_costo AFTER INSERT OR UPDATE OR DELETE ON orden_item
    FOR EACH ROW EXECUTE FUNCTION fn_orden_item_costo();

-- =====================================================================
-- Vistas
-- =====================================================================

-- Horas de uso por día de cada bicicleta en los últimos 90 días.
CREATE VIEW v_ritmo_uso AS
SELECT b.id AS bicicleta_id,
       round(COALESCE(sum(d.segundos_uso) FILTER (WHERE d.devuelta_en >= now() - interval '90 days'), 0) / 3600.0
             / GREATEST(LEAST(90, current_date - b.fecha_alta), 1), 3) AS horas_por_dia
FROM bicicleta b
LEFT JOIN alquiler_detalle d ON d.bicicleta_id = b.id
GROUP BY b.id, b.fecha_alta;

-- Último servicio cerrado de cada tarea del plan, por bicicleta.
CREATE VIEW v_ultimo_servicio AS
SELECT DISTINCT ON (o.bicicleta_id, o.plan_id)
       o.bicicleta_id, o.plan_id, o.cerrada_en, o.horas_uso
FROM orden_mantenimiento o
JOIN estado_orden e ON e.id = o.estado_id
WHERE e.codigo = 'CERRADA' AND o.plan_id IS NOT NULL
ORDER BY o.bicicleta_id, o.plan_id, o.cerrada_en DESC;

-- Fase 1 del mantenimiento predictivo: reglas con el ritmo real de uso.
-- Negativo = vencido. La fecha estimada es lo que ocurra primero entre el plazo
-- por calendario y el que resulta de gastar las horas restantes al ritmo actual.
CREATE VIEW v_proximo_servicio AS
SELECT
    b.id        AS bicicleta_id,
    b.codigo,
    p.id        AS plan_id,
    p.tarea,
    p.sistema,
    b.horas_uso AS horas_actuales,
    CASE WHEN p.cada_horas IS NOT NULL
         THEN COALESCE(u.horas_uso, 0) + p.cada_horas - b.horas_uso END AS horas_restantes,
    CASE WHEN p.cada_dias IS NOT NULL
         THEN (COALESCE(u.cerrada_en::date, b.fecha_alta) + p.cada_dias) - current_date END AS dias_restantes,
    r.horas_por_dia,
    LEAST(
        CASE WHEN p.cada_dias IS NOT NULL
             THEN COALESCE(u.cerrada_en::date, b.fecha_alta) + p.cada_dias END,
        CASE WHEN p.cada_horas IS NOT NULL AND COALESCE(r.horas_por_dia, 0) > 0
             THEN current_date + CEIL(
                    GREATEST(COALESCE(u.horas_uso, 0) + p.cada_horas - b.horas_uso, 0)
                    / r.horas_por_dia)::int END
    ) AS fecha_estimada
FROM bicicleta b
JOIN estado_bicicleta eb ON eb.id = b.estado_id AND eb.codigo <> 'BAJA'
JOIN plan_mantenimiento p ON p.tipo_bicicleta_id = b.tipo_bicicleta_id AND p.activo
LEFT JOIN v_ultimo_servicio u ON u.bicicleta_id = b.id AND u.plan_id = p.id
LEFT JOIN v_ritmo_uso r ON r.bicicleta_id = b.id;

-- Lo que rinde y lo que cuesta cada bicicleta.
CREATE VIEW v_rentabilidad_bicicleta AS
WITH ing AS (
    SELECT bicicleta_id, count(*) AS alquileres, sum(importe) AS ingresos,
           round(sum(segundos_uso) / 3600.0, 1) AS horas_alquiladas
    FROM alquiler_detalle WHERE devuelta_en IS NOT NULL GROUP BY bicicleta_id
), car AS (
    SELECT d.bicicleta_id, sum(c.monto) AS cargos
    FROM cargo_extra c JOIN alquiler_detalle d ON d.id = c.detalle_id GROUP BY d.bicicleta_id
), man AS (
    SELECT o.bicicleta_id,
           count(*) FILTER (WHERE t.codigo = 'CORRECTIVO') AS ordenes_correctivas,
           count(*) FILTER (WHERE t.codigo = 'PREVENTIVO') AS ordenes_preventivas,
           sum(o.costo_total) AS costo_mantenimiento
    FROM orden_mantenimiento o
    JOIN tipo_mantenimiento t ON t.id = o.tipo_id
    JOIN estado_orden e ON e.id = o.estado_id AND e.codigo = 'CERRADA'
    GROUP BY o.bicicleta_id
)
SELECT b.id AS bicicleta_id, b.codigo, tb.nombre AS tipo,
       COALESCE(ing.alquileres, 0)            AS alquileres,
       COALESCE(ing.horas_alquiladas, 0)      AS horas_alquiladas,
       COALESCE(ing.ingresos, 0)              AS ingresos,
       COALESCE(car.cargos, 0)                AS cargos_por_danios,
       COALESCE(man.ordenes_preventivas, 0)   AS ordenes_preventivas,
       COALESCE(man.ordenes_correctivas, 0)   AS ordenes_correctivas,
       COALESCE(man.costo_mantenimiento, 0)   AS costo_mantenimiento,
       COALESCE(ing.ingresos, 0) + COALESCE(car.cargos, 0) - COALESCE(man.costo_mantenimiento, 0) AS margen
FROM bicicleta b
JOIN tipo_bicicleta tb ON tb.id = b.tipo_bicicleta_id
LEFT JOIN ing ON ing.bicicleta_id = b.id
LEFT JOIN car ON car.bicicleta_id = b.id
LEFT JOIN man ON man.bicicleta_id = b.id;

CREATE VIEW v_ingresos_mensuales AS
SELECT date_trunc('month', d.devuelta_en AT TIME ZONE 'America/Argentina/Buenos_Aires')::date AS mes,
       tb.nombre AS tipo,
       count(*) AS bicicletas_alquiladas,
       round(sum(d.segundos_uso) / 3600.0, 1) AS horas,
       sum(d.importe) AS ingresos
FROM alquiler_detalle d
JOIN tipo_bicicleta tb ON tb.id = d.tipo_bicicleta_id
WHERE d.devuelta_en IS NOT NULL
GROUP BY 1, 2;

-- Cuántas bicicletas hay, ahora, por estación y tipo.
CREATE VIEW v_disponibilidad_estacion AS
SELECT u.id AS ubicacion_id, u.nombre AS estacion, tb.nombre AS tipo,
       count(*) FILTER (WHERE e.codigo <> 'BAJA')                                   AS flota,
       count(*) FILTER (WHERE e.codigo = 'DISPONIBLE')                              AS disponibles,
       count(*) FILTER (WHERE e.codigo = 'ALQUILADA')                               AS alquiladas,
       count(*) FILTER (WHERE e.codigo IN ('EN_MANTENIMIENTO','FUERA_DE_SERVICIO')) AS en_taller
FROM bicicleta b
JOIN ubicacion u ON u.id = b.ubicacion_base_id
JOIN tipo_bicicleta tb ON tb.id = b.tipo_bicicleta_id
JOIN estado_bicicleta e ON e.id = b.estado_id
GROUP BY u.id, u.nombre, tb.nombre;

-- Alquileres en curso que ya pasaron su hora de devolución.
CREATE VIEW v_alquileres_demorados AS
SELECT a.id AS alquiler_id, a.cliente_id, a.salida_real, a.fin_previsto,
       round(extract(epoch FROM (now() - a.fin_previsto)) / 3600.0, 1) AS horas_de_demora,
       (SELECT count(*) FROM alquiler_detalle d
         WHERE d.alquiler_id = a.id AND d.devuelta_en IS NULL AND d.anulado_en IS NULL) AS bicicletas_pendientes
FROM alquiler a
WHERE a.retorno_real IS NULL AND a.anulada_en IS NULL AND a.fin_previsto < now();

-- Reservas vigentes cuyo cliente no se presentó pasada la hora de tolerancia (60 minutos).
CREATE VIEW v_reservas_por_vencer AS
SELECT r.id AS reserva_id, r.cliente_id, r.ubicacion_id, r.inicio_previsto, r.estado,
       round(extract(epoch FROM (now() - r.inicio_previsto)) / 60.0) AS minutos_de_atraso
FROM reserva r
WHERE r.estado IN ('PENDIENTE','CONFIRMADA') AND r.inicio_previsto + interval '60 minutes' < now();

-- Situación de cobro de cada alquiler: lo devengado, lo cobrado y el saldo.
CREATE VIEW v_saldo_alquiler AS
SELECT a.id AS alquiler_id, a.estado,
       COALESCE(d.importe, 0)                                   AS importe_bicicletas,
       COALESCE(c.cargos, 0)                                    AS cargos,
       COALESCE(d.importe, 0) + COALESCE(c.cargos, 0)           AS total,
       COALESCE(p.neto, 0)                                      AS pagado,
       COALESCE(d.importe, 0) + COALESCE(c.cargos, 0) - COALESCE(p.neto, 0) AS saldo
FROM alquiler a
LEFT JOIN (SELECT alquiler_id, sum(importe) AS importe
             FROM alquiler_detalle WHERE devuelta_en IS NOT NULL GROUP BY alquiler_id) d ON d.alquiler_id = a.id
LEFT JOIN (SELECT alquiler_id, sum(monto) AS cargos FROM cargo_extra GROUP BY alquiler_id) c ON c.alquiler_id = a.id
LEFT JOIN LATERAL (
    SELECT sum(CASE WHEN pg.tipo = 'REEMBOLSO' THEN -pg.monto ELSE pg.monto END) AS neto
      FROM pago pg
     WHERE pg.estado = 'APROBADO'
       AND (pg.alquiler_id = a.id OR (a.reserva_id IS NOT NULL AND pg.reserva_id = a.reserva_id))
) p ON TRUE
WHERE a.anulada_en IS NULL;

-- =====================================================================
-- Datos iniciales de catálogos
-- =====================================================================

INSERT INTO rol (codigo, nombre) VALUES
    ('ADMIN',    'Administrador'),
    ('MOSTRADOR','Atención en estación'),
    ('TECNICO',  'Técnico de taller');

INSERT INTO estado_bicicleta (codigo, nombre) VALUES
    ('DISPONIBLE',        'Disponible'),
    ('ALQUILADA',         'Alquilada'),
    ('EN_MANTENIMIENTO',  'En mantenimiento'),
    ('FUERA_DE_SERVICIO', 'Fuera de servicio (a revisar)'),
    ('BAJA',              'Dada de baja');

INSERT INTO estado_orden (codigo, nombre) VALUES
    ('ABIERTA',  'Abierta'),
    ('EN_CURSO', 'En curso'),
    ('CERRADA',  'Cerrada'),
    ('CANCELADA','Cancelada');

INSERT INTO tipo_mantenimiento (codigo, nombre) VALUES
    ('PREVENTIVO', 'Preventivo'),
    ('CORRECTIVO', 'Correctivo');
