# BlueHarbor — Vulnerable Lab

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
|Tiempo estimado|30 min - 1 hora|

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
git clone https://github.com/alisster00/blueHarbor.git
cd blueHarbor
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
