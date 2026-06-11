FROM python:3.11-slim

# ── Dependencias del sistema ──────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server    \
        openssh-client    \
        nginx             \
        sudo              \
        cron              \
        postgresql-client \
        procps            \
        curl              \
    && rm -rf /var/lib/apt/lists/*

# ── Usuarios ──────────────────────────────────────────────────────────────────
RUN useradd -m -s /bin/bash omar && \
    echo 'omar:DevOmar18!' | chpasswd

# ── SSH ───────────────────────────────────────────────────────────────────────
RUN mkdir -p /var/run/sshd                                                  && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/'         \
        /etc/ssh/sshd_config                                                && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/'          \
        /etc/ssh/sshd_config                                                && \
    echo "BlueHarbor Solutions — Authorized access only" > /etc/ssh/sshd_banner && \
    echo "Banner /etc/ssh/sshd_banner" >> /etc/ssh/sshd_config

# ── Python dependencies ───────────────────────────────────────────────────────
WORKDIR /var/www/html
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Librería interna legítima ─────────────────────────────────────────────────
COPY scripts/blueharbor_utils.py /usr/local/lib/python3.11/blueharbor_utils.py

# ── Aplicación Flask ──────────────────────────────────────────────────────────
COPY app/ .
RUN chown -R www-data:www-data /var/www/html

# ── Scripts del sistema ───────────────────────────────────────────────────────
RUN mkdir -p /home/omar/scripts
COPY scripts/backup.py /home/omar/scripts/backup.py
RUN chown -R omar:omar /home/omar/scripts && \
    # 711 en el home: omar tiene control total,
    # otros pueden traversar (x) pero no listar (sin r)
    chmod 711 /home/omar                            && \
    # 755 en scripts: traversable y listable por www-data
    chmod 755 /home/omar/scripts                    && \
    # 644 en el archivo: legible por todos
    chmod 644 /home/omar/scripts/backup.py

# ── Flags ─────────────────────────────────────────────────────────────────────
RUN printf 'BlueHarbor{SSTI_4nd_JWT_4r3_4_d4ng3r0us_c0mb0}\n' \
        > /home/omar/user.txt                          && \
    chown omar:omar /home/omar/user.txt      && \
    chmod 400 /home/omar/user.txt

RUN printf 'BlueHarbor{W1ldc4rd_T4r_1nj3ct10n_0wn3d_r00t}\n' \
        > /root/root.txt                                    && \
    chmod 400 /root/root.txt

# ── Sudoers ───────────────────────────────────────────────────────────────────
# SETENV permite que www-data pase PYTHONPATH al comando - library hijacking.
RUN printf 'www-data ALL=(omar) NOPASSWD: SETENV: /usr/local/bin/python3 /home/omar/scripts/backup.py\n' \
        > /etc/sudoers.d/blueharbor-backup                                     && \
    chmod 440 /etc/sudoers.d/blueharbor-backup                                 && \
    visudo -c -f /etc/sudoers.d/blueharbor-backup

# ── Nginx ─────────────────────────────────────────────────────────────────────
COPY nginx.conf /etc/nginx/nginx.conf

# ── Setup scripts ─────────────────────────────────────────────────────────────
COPY setup/ /setup/
RUN chmod +x /setup/init.sh /setup/cron_setup.sh

EXPOSE 80 22

ENTRYPOINT ["/setup/init.sh"]
