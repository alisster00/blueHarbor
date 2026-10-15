#!/usr/bin/env bash

set -uo pipefail

log()  { echo "[*] $*"; }
ok()   { echo "[+] $*"; }
fail() { echo "[!] $*" >&2; exit 1; }

log "BlueHarbor Lab - Container starting..."

# ── SSH ───────────────────────────────────────────────────────────────────────
log "Starting SSH..."
mkdir -p /var/run/sshd

if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    ssh-keygen -A -q
fi

/usr/sbin/sshd || fail "SSH failed to start"
ok "SSH ready on port 22"

# ── Cron ──────────────────────────────────────────────────────────────────────
log "Configuring cron..."
/setup/cron_setup.sh || fail "cron_setup failed"

cron || fail "cron failed to start"
ok "Cron ready"

# ── Seed de logs ──────────────────────────────────────────────────────────────
log "Seeding maintenance log..."
echo "[$(date +'%Y-%m-%d %H:%M:%S')] BlueHarbor maintenance subsystem initialized" \
    > /var/log/blueharbor/system.log
chown omar:omar /var/log/blueharbor/system.log
ok "Maintenance log seeded"

# ── PostgreSQL ────────────────────────────────────────────────────────────────
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

# ── Seed de base de datos ─────────────────────────────────────────────────────
log "Seeding database..."
python3 /setup/setup_db.py || fail "Database seed failed"
ok "Database ready"

# ── .env ──────────────────────────────────────────────────────────────────────
log "Generating application .env..."
cat > /var/www/html/.env << 'EOF'
# BlueHarbor Internal API - Environment Configuration
# Last updated: 2024-01-15
# TODO: move to Docker secrets before final release

DB_HOST=db
DB_PORT=5432
DB_NAME=blueharbor
DB_USER=blueharbor
DB_PASSWORD=Str0ng_DB_P4ss!
JWT_SECRET=secret
EOF
chown www-data:www-data /var/www/html/.env
chmod 640                /var/www/html/.env
ok ".env generated"

# ── Verificaciones de permisos ────────────────────────────────────────────────
log "Verifying permissions..."
[ "$(stat -c '%U:%a' /home/omar/user.txt)" = "omar:400" ] \
    || fail "user.txt permissions wrong: $(stat -c '%U:%a' /home/omar/user.txt)"
[ "$(stat -c '%U:%a' /root/root.txt)" = "root:400" ] \
    || fail "root.txt permissions wrong: $(stat -c '%U:%a' /root/root.txt)"
[ "$(stat -c '%U:%a' /var/log/blueharbor)" = "omar:775" ] \
    || fail "/var/log/blueharbor permissions wrong: $(stat -c '%U:%a' /var/log/blueharbor)"
[ "$(stat -c '%U:%a' /var/www/html/.env)" = "www-data:640" ] \
    || fail ".env permissions wrong: $(stat -c '%U:%a' /var/www/html/.env)"
ok "Permissions verified"

# ── Nginx ─────────────────────────────────────────────────────────────────────
log "Starting nginx..."

nginx -t 2>&1 || fail "nginx config invalid"
nginx || fail "nginx failed to start"
ok "nginx ready on port 80"

# ── Gunicorn ──────────────────────────────────────────────────────────────────
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