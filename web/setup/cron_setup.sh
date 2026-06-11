#!/usr/bin/env bash
set -e

# dirs
mkdir -p /opt/blueharbor
mkdir -p /var/log/blueharbor
mkdir -p /backup

# permisos: omar puede escribir en /var/log/blueharbor
# (necesario para que el ataque de wildcard injection funcione)
chown omar:omar /var/log/blueharbor
chmod 775               /var/log/blueharbor

# solo root puede leer los backups finales
chown root:root /backup
chmod 700       /backup

# script de mantenimiento
cat > /opt/blueharbor/maintenance.sh << 'SCRIPT'
#!/usr/bin/env bash
#
# BlueHarbor Maintenance Script v1.0
# Executed by cron as root every minute.
#
# Function: compress daily logs and move them to /backup/
#
# INTERNAL WARNING: This script uses an unquoted wildcard.
# Ticket #302 opened to fix it - pending assignment.
#

LOG_DIR="/var/log/blueharbor"
BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# VULNERABILITY - Tar Wildcard Injection:
#
# 'tar' expands the wildcard '*' before execution, meaning that
# filenames act as arguments to the tar command.
#
# An attacker with access to /var/log/blueharbor can create:
#   --checkpoint=1
#   --checkpoint-action=exec=sh privesc.sh
#   privesc.sh  (with the desired payload)
#
# When cron executes this script as root, tar will interpret
# those filenames as flags and execute privesc.sh as root.
#
cd "$LOG_DIR" && tar czf "$BACKUP_DIR/logs_${TIMESTAMP}.tar.gz" *
SCRIPT

chmod +x /opt/blueharbor/maintenance.sh

# cron job (corre como root cada minuto)
cat > /etc/cron.d/blueharbor-maintenance << 'CRON'
# BlueHarbor log rotation - runs as root
* * * * * root /opt/blueharbor/maintenance.sh >> /var/log/blueharbor/cron.log 2>&1
CRON

chmod 644 /etc/cron.d/blueharbor-maintenance

echo "[+] Cron job configured: /etc/cron.d/blueharbor-maintenance"
echo "[+] Maintenance script:  /opt/blueharbor/maintenance.sh"
