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
    echo 'omar:katherine' | chpasswd

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

# ── Aplicación Flask ──────────────────────────────────────────────────────────
COPY app/ .
RUN chown -R www-data:www-data /var/www/html

# ── Home de omar ──────────────────────────────────────────────────────────────
RUN chown omar:omar /home/omar && chmod 700 /home/omar

# ── Flags ─────────────────────────────────────────────────────────────────────
RUN printf 'FLAG{SSTI_4nd_JWT_4r3_4_d4ng3r0us_c0mb0}\n' \
        > /home/omar/user.txt                          && \
    chown omar:omar /home/omar/user.txt      && \
    chmod 400 /home/omar/user.txt

RUN printf 'FLAG{W1ldc4rd_T4r_1nj3ct10n_0wn3d_r00t}\n' \
        > /root/root.txt                                    && \
    chmod 400 /root/root.txt

# ── Nginx ─────────────────────────────────────────────────────────────────────
COPY nginx.conf /etc/nginx/nginx.conf

# ── Setup scripts ─────────────────────────────────────────────────────────────
COPY setup/ /setup/
RUN chmod +x /setup/init.sh /setup/cron_setup.sh

EXPOSE 80 22

ENTRYPOINT ["/setup/init.sh"]
