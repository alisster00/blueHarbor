#!/usr/bin/env bash

set -uo pipefail

log()  { echo "[*] $*"; }
ok()   { echo "[+] $*"; }
fail() { echo "[!] $*" >&2; exit 1; }

log "BlueHarbor Lab - Container starting..."

usermod -s /bin/bash www-data 2>/dev/null || true

log "Starting SSH..."
mkdir -p /var/run/sshd

# regenerar host keys si no existen (primera ejecución)
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    ssh-keygen -A -q
fi

/usr/sbin/sshd || fail "SSH failed to start"
ok "SSH ready on port 22"

# cron
log "Configuring cron..."
/setup/cron_setup.sh

# en imágenes slim no existe 'service'. Llamar al binario directamente.
cron || fail "cron failed to start"
ok "Cron ready"

# esperar a PostgreSQL
log "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."
max_attempts=30
attempt=0

until pg_isready \
        -h "${DB_HOST:-db}" \
        -p "${DB_PORT:-5432}" \
        -U "${DB_USER:-blueharbor}" \
        -q 2>/dev/null
do
    attempt=$((attempt + 1))
    [ "$attempt" -ge "$max_attempts" ] && fail "PostgreSQL not available after ${max_attempts} attempts"
    echo "    Waiting... ($attempt/$max_attempts)"
    sleep 3
done
ok "PostgreSQL ready"

# iniciar base de datos
log "Seeding database..."

python3 /setup/setup_db.py || fail "Database seed failed"
ok "Database ready"

# nginx
log "Starting nginx..."

# validar configuración antes de arrancar
nginx -t 2>&1 || fail "nginx config invalid"

# arrancar en segundo plano (sin daemon off - gunicorn será el proceso principal)
nginx || fail "nginx failed to start"
ok "nginx ready on port 80"

# gunicorn / flask
log "Starting Flask/Gunicorn as www-data..."
cd /var/www/html

exec gunicorn \
    --bind          0.0.0.0:5000  \
    --workers       2             \
    --timeout       60            \
    --user          www-data      \
    --group         www-data      \
    --access-logfile -            \
    --error-logfile  -            \
    "app:create_app()"
