-- Seguridad para publicar la base en Supabase (o cualquier Postgres con la
-- API de datos de PostgREST expuesta).
--
-- Supabase expone por API REST todas las tablas del esquema `public` a los roles
-- `anon` y `authenticated`. Sin este script, cualquiera que tenga la clave pública
-- (anon key) podría leer y escribir las bicicletas, los clientes y los pagos, y leer los hashes de contraseñas.
--
-- Este proyecto NO usa esa API: la aplicación se conecta directamente a Postgres
-- con credenciales guardadas en el servidor. Entonces se cierra por completo:
--   1) se activa RLS en todas las tablas, sin políticas (deniega todo),
--   2) se quitan los permisos de `anon` y `authenticated`,
--   3) lo mismo para los objetos que se creen más adelante.
--
-- Ejecutar DESPUÉS de db/schema.sql, con el usuario dueño de las tablas (postgres).
-- Si más adelante se quiere usar la API de Supabase desde un navegador, hay que
-- escribir políticas por rol (hoja de ruta, fase 6) antes de abrir nada.

DO $$
DECLARE
    t record;
BEGIN
    FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t.tablename);
    END LOOP;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon;
        REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
        REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM anon;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM anon;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM authenticated;
        REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM authenticated;
        REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM authenticated;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM authenticated;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM authenticated;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM authenticated;
    END IF;
END $$;
