#!/usr/bin/env bash
# Carga el esquema y los datos de demostración en una base PostgreSQL VACÍA.
#
# Uso:
#   ./scripts/cargar_demo.sh "postgresql://usuario:clave@localhost:5432/bicis"
#   DATABASE_URL="postgresql://..." ./scripts/cargar_demo.sh
#
# La carga de datos corre en una sola transacción y tarda alrededor de un minuto,
# porque cada retiro y devolución dispara los triggers que validan y registran el uso.
set -euo pipefail

DB_URL="${1:-${DATABASE_URL:-}}"
if [ -z "$DB_URL" ]; then
    echo "Uso: $0 <cadena-de-conexión>   (o definir DATABASE_URL)" >&2
    exit 1
fi

cd "$(dirname "$0")/.."

echo "1/2 Creando esquema (tablas, restricciones, triggers y vistas)..."
psql "$DB_URL" -v ON_ERROR_STOP=1 -q -f db/schema.sql

echo "2/2 Cargando datos sintéticos (aprox. 1 minuto)..."
gunzip -c data/seed.sql.gz | psql "$DB_URL" -1 -v ON_ERROR_STOP=1 -q -o /dev/null

echo "Listo. Probá:  psql \"\$DB_URL\" -c 'SELECT * FROM v_proximo_servicio ORDER BY fecha_estimada LIMIT 10;'"
