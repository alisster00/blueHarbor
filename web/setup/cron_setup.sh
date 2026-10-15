#!/usr/bin/env bash
set -e

# dirs
mkdir -p /opt/blueharbor
mkdir -p /var/log/blueharbor
mkdir -p /backup

# permisos: omar puede escribir en /var/log/blueharbor
# (necesario para que el ataque de wildcard injection funcione)
chown omar:omar /var/log/blueharbor
chmod 775       /var/log/blueharbor

# solo root puede leer los backups finales
chown root:root /backup
chmod 700       /backup

# script de mantenimiento
cat > /opt/blueharbor/maintenance.sh << 'SCRIPT'
#!/usr/bin/env bash
#
# BlueHarbor Maintenance Script v1.0
# Executed by cron as root.
#
# Function: compress current logs and move them to /backup/
#
# TODO (ticket #302): review handling of filenames with special characters.
# Unassigned - sprint #14.
#

LOG_DIR="/var/log/blueharbor"
BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cd "$LOG_DIR" && tar czf "$BACKUP_DIR/logs_${TIMESTAMP}.tar.gz" *
SCRIPT

chmod 755 /opt/blueharbor/maintenance.sh
chown root:root /opt/blueharbor/maintenance.sh

# directorio solo legible por root y omar (no por www-data)
chown root:omar /opt/blueharbor
chmod 750       /opt/blueharbor

# cron job (corre como root dos veces por minuto: :00 y :30)
cat > /etc/cron.d/blueharbor-maintenance << 'CRON'
# BlueHarbor log rotation - runs as root
* * * * * root /opt/blueharbor/maintenance.sh >> /var/log/blueharbor/cron.log 2>&1
* * * * * root sleep 30 && /opt/blueharbor/maintenance.sh >> /var/log/blueharbor/cron.log 2>&1
CRON

chmod 644 /etc/cron.d/blueharbor-maintenance

echo "[+] Cron job configured: /etc/cron.d/blueharbor-maintenance"
echo "[+] Maintenance script:  /opt/blueharbor/maintenance.sh"