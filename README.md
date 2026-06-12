# BlueHarbor — Vulnerable Lab

```
  ██████╗ ██╗     ██╗   ██╗███████╗██╗  ██╗ █████╗ ██████╗ ██████╗  ██████╗ ██████╗
  ██╔══██╗██║     ██║   ██║██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
  ██████╔╝██║     ██║   ██║█████╗  ███████║███████║██████╔╝██████╔╝██║   ██║██████╔╝
  ██╔══██╗██║     ██║   ██║██╔══╝  ██╔══██║██╔══██║██╔══██╗██╔══██╗██║   ██║██╔══██╗
  ██████╔╝███████╗╚██████╔╝███████╗██║  ██║██║  ██║██║  ██║██████╔╝╚██████╔╝██║  ██║
  ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
```

---

## Descripción

**BlueHarbor Solutions** es una empresa ficticia de logística con un portal interno para gestión de envíos. Un desarrollador construyó la API apresuradamente para cumplir un deadline y el equipo de DevOps olvidó desactivar el modo debug antes del despliegue.

El objetivo es comprometer el sistema encadenando múltiples vulnerabilidades reales, siguiendo un flujo similar al de plataformas como Hack The Box o TryHackMe.

|Atributo|Valor|
|---|---|
|Dificultad|Media|
|Sistema|Linux (Debian slim)|
|Servicios|HTTP (80), SSH (2222)|
|Flags|`user.txt`, `root.txt`|
|Tiempo estimado|2 – 4 horas|

---

## Vulnerabilidades incluidas

### 1. Security Misconfiguration — A05 (OWASP 2021)

**Descripción:** El endpoint `/api/v1/health` expone en producción información sensible del servidor: el flag `debug: true`, la versión exacta del stack y el `sys.path` completo de Python. El Swagger UI está accesible públicamente sin ningún tipo de autenticación.

**Referencia:** CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor)

---

### 2. Broken Access Control — A01 (OWASP 2021)

**Descripción:** El endpoint `/api/v1/auth/debug` fue creado para pruebas de integración y nunca fue desactivado en producción. Cualquier usuario anónimo puede consumirlo y obtener un token JWT firmado con la clave del servidor.

**Referencia:** CWE-284 (Improper Access Control)

---

### 3. Cryptographic Failures — A02 (OWASP 2021)

**Descripción:** El token JWT devuelto por `/auth/debug` está firmado con el algoritmo HS256 usando una clave de baja entropía presente en wordlists comunes. Un atacante puede crackearla offline con `hashcat` y forjar un token con `role: admin`.

**Referencias:**

- CWE-326 (Inadequate Encryption Strength)
- CWE-916 (Use of Password Hash With Insufficient Computational Effort)
- [CVE-2015-9235](https://nvd.nist.gov/vuln/detail/CVE-2015-9235) — JWT `none` algorithm (variante relacionada)

---

### 4. Injection / SSTI — A03 (OWASP 2021)

**Descripción:** El endpoint `/api/v1/admin/report` acepta un campo `template` que es renderizado directamente con `render_template_string()` de Flask/Jinja2 sin ningún tipo de sanitización ni sandboxing. Permite RCE completo como el usuario `www-data`.

**Payload de prueba:**

```
{"template": "{{7*7}}"}  →  {"report": "49"}
```

**Referencias:**

- CWE-94 (Improper Control of Generation of Code)
- CWE-1336 (Improper Neutralization of Special Elements in Template Engines)
- [CVE-2019-8341](https://nvd.nist.gov/vuln/detail/CVE-2019-8341) — Jinja2 SSTI (variante en Ansible)

---

### 5. Software & Data Integrity Failures — A08 (OWASP 2021)

**Descripción:** El script `/home/omar/scripts/backup.py` importa `blueharbor_utils`, un módulo interno no distribuido por PyPI. La regla sudo permite pasar `PYTHONPATH` al intérprete, lo que posibilita plantar un módulo malicioso con el mismo nombre en `/tmp` y que sea cargado con prioridad sobre el legítimo.

**Referencias:**

- CWE-427 (Uncontrolled Search Path Element)
- CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)

---

### 6. Escalada de privilegios — Tar Wildcard Injection

**Descripción:** Un cron job ejecutado como `root` cada minuto comprime los logs con `tar czf /backup/logs.tar.gz *`. Al expandir el wildcard `*`, `tar` interpreta los nombres de archivo como argumentos propios. Un atacante con acceso de escritura al directorio de logs puede crear archivos con nombres como `--checkpoint-action=exec=sh privesc.sh` para ejecutar código como root.

**Referencias:**

- CWE-78 (OS Command Injection)
- [GTFOBins — tar](https://gtfobins.github.io/gtfobins/tar/)

---

## Requisitos

- Docker >= 24.0
- Docker Compose >= 2.0
- Sistema operativo anfitrión: Linux / macOS / WSL2
- ~500 MB de espacio en disco

**Herramientas sugeridas para resolver el lab:**

|Fase|Herramientas|
|---|---|
|Reconocimiento|`nmap`, `curl`|
|Enumeración web|`gobuster`, `ffuf`, navegador|
|JWT|`hashcat`, `jwt_tool`, `PyJWT`|
|Explotación|`Burp Suite`, `curl`|
|Reverse shell|`nc`, `pwncat-cs`|
|Post-explotación|`sudo -l`, línea de comandos estándar|

---

## Despliegue

### 1. Clonar el repositorio

```bash
git clone https://github.com/alisster00/blueHarbor-VulnLab.git
cd blueHarbor-VulnLab
```

### 2. Construir e iniciar los contenedores

```bash
docker compose up --build -d
```

El proceso tarda ~2 minutos la primera vez (descarga de imágenes base e instalación de dependencias).

### 3. Verificar que los servicios están activos

```bash
docker compose ps
```

Salida esperada:

```
NAME               STATUS          PORTS
blueharbor-web     Up              0.0.0.0:80->80/tcp, 0.0.0.0:2222->22/tcp
blueharbor-db      Up (healthy)    5432/tcp
```

### 4. Verificación rápida

```bash
# Web accesible
curl -si http://localhost | grep -E "HTTP|X-Powered"

# API responde
curl -s http://localhost/api/v1/ | python3 -m json.tool

# SSH disponible
ssh -p 2222 omar@localhost 2>&1 | grep "BlueHarbor"
```


---

## Gestión del laboratorio

```bash
# Iniciar
docker compose up -d

# Detener (conserva datos)
docker compose stop

# Reiniciar desde cero (borra DB y flags capturadas)
docker compose down -v && docker compose up --build -d

# Ver logs en tiempo real
docker compose logs -f web

# Acceso de diagnóstico (no usar durante el lab)
docker exec -it blueharbor-web bash
```

---

## Notas de seguridad

> ⚠ Este laboratorio contiene vulnerabilidades **intencionalmente**.

- Desplegarlo **únicamente en entornos locales o aislados**.
- No exponer los puertos a Internet ni a redes no confiables.
- No usar credenciales reales en ningún archivo de configuración.
- Diseñado exclusivamente con fines educativos y de investigación en ciberseguridad.

Laboratorio diseñado con fines educativos. Vulnerabilidades basadas en el [OWASP Top 10 2021](https://owasp.org/Top10/). Referencias adicionales: [GTFOBins](https://gtfobins.github.io/), [CWE/SANS Top 25](https://cwe.mitre.org/top25/).
