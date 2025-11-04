# Guía de Configuración - Specs Python

## Variables de Entorno (.env)

El sistema utiliza un archivo `.env` para gestionar configuraciones sensibles y personalizables. Este archivo **NO se sube a Git** (protegido por `.gitignore`).

### Configuración Inicial

```bash
# 1. Copiar plantilla
copy .env.example .env

# 2. Generar secreto compartido
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Editar .env y reemplazar SHARED_SECRET con el valor generado
```

---

## Categorías de Configuración

### 🔒 Seguridad

| Variable | Tipo | Valor por Defecto | Descripción |
|----------|------|-------------------|-------------|
| `SHARED_SECRET` | string | ⚠️ REQUERIDO | Token de 64 caracteres hex para autenticación cliente-servidor |
| `ALLOWED_SUBNETS` | lista CSV | `127.0.0.1/32` | Whitelist de subnets permitidas (formato CIDR) |
| `MAX_BUFFER_SIZE` | int | `10485760` (10 MB) | Tamaño máximo de buffer de red |
| `MAX_CONNECTIONS_PER_IP` | int | `3` | Conexiones simultáneas permitidas por IP |
| `CONNECTION_TIMEOUT` | int | `30` | Timeout de conexión en segundos |
| `MAX_FIELD_LENGTH` | int | `1024` | Longitud máxima de campos de texto |

**Ejemplo:**
```env
SHARED_SECRET=e22ab8d62395a094a20ab4b3d2ab1408b1a734ee176dda33bcfbd2c62f8f7c81
ALLOWED_SUBNETS=10.100.0.0/16,10.101.0.0/16,127.0.0.1/32
```

---

### 🌐 Red y Puertos

| Variable | Tipo | Valor por Defecto | Descripción |
|----------|------|-------------------|-------------|
| `SERVER_PORT` | int | `5255` | Puerto TCP del servidor (recepción de datos) |
| `DISCOVERY_PORT` | int | `37020` | Puerto UDP para discovery broadcasts |
| `BROADCAST_INTERVAL` | int | `10` | Intervalo entre broadcasts en segundos |

**Ejemplo:**
```env
SERVER_PORT=5255
DISCOVERY_PORT=37020
BROADCAST_INTERVAL=10
```

---

### 💾 Base de Datos

| Variable | Tipo | Valor por Defecto | Descripción |
|----------|------|-------------------|-------------|
| `DB_PATH` | string | `data/specs.db` | Ruta relativa de la base de datos SQLite |

**Notas:**
- En desarrollo: `data/specs.db` (relativo a raíz del proyecto)
- En producción empaquetada: `specs.db` (junto al ejecutable)

**Ejemplo:**
```env
DB_PATH=data/specs.db
```

---

### 🔍 Escaneo de Red

| Variable | Tipo | Valor por Defecto | Descripción |
|----------|------|-------------------|-------------|
| `SCAN_SUBNET_START` | IP | `10.100.0.0` | IP de inicio del rango a escanear |
| `SCAN_SUBNET_END` | IP | `10.119.0.0` | IP de fin del rango a escanear |
| `PING_TIMEOUT` | float | `1.0` | Timeout de ping en segundos |
| `SCAN_PER_HOST_TIMEOUT` | float | `0.8` | Timeout por host en escaneo |
| `SCAN_PER_SUBNET_TIMEOUT` | float | `8.0` | Timeout por subnet completa |
| `SCAN_PROBE_TIMEOUT` | float | `0.9` | Timeout de probes SSDP/mDNS |
| `PING_BATCH_SIZE` | int | `50` | Tamaño de batch para pings paralelos |

**Ejemplo:**
```env
SCAN_SUBNET_START=10.100.0.0
SCAN_SUBNET_END=10.119.0.0
PING_TIMEOUT=1.0
PING_BATCH_SIZE=50
```

**Cálculo de rango:** `10.100.0.0` a `10.119.0.0` = 20 subnets /16 = 1,310,720 IPs

---

### 📁 Rutas de Salida

| Variable | Tipo | Valor por Defecto | Descripción |
|----------|------|-------------------|-------------|
| `OUTPUT_DIR` | string | `output` | Directorio para archivos temporales (CSV, JSON, logs) |
| `DXDIAG_OUTPUT_DIR` | string | `output` | Directorio para archivos de diagnóstico DirectX |

**Ejemplo:**
```env
OUTPUT_DIR=output
DXDIAG_OUTPUT_DIR=output
```

---

## Uso en Código

### Importar configuración

```python
# Opción 1: Importar todo
from config.security_config import *

# Opción 2: Importar variables específicas
from config.security_config import (
    SERVER_PORT,
    DISCOVERY_PORT,
    DB_PATH,
    PING_BATCH_SIZE
)
```

### Ejemplo práctico

```python
import socket
from config.security_config import SERVER_PORT, DISCOVERY_PORT

# Crear socket TCP en puerto configurado
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', SERVER_PORT))

# Enviar broadcast UDP
broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
broadcast_socket.sendto(b"servidor specs", ("255.255.255.255", DISCOVERY_PORT))
```

---

## Validación de Configuración

Para verificar que el `.env` se carga correctamente:

```bash
python -c "from config.security_config import *; print(f'Server: {SERVER_PORT}'); print(f'DB: {DB_PATH}')"
```

**Output esperado:**
```
✓ Configuración cargada desde C:\...\specs-python\.env
Server: 5255
DB: data/specs.db
```

---

## Troubleshooting

### ❌ Error: "python-dotenv no instalado"

**Solución:**
```bash
pip install python-dotenv
```

### ❌ Error: "Archivo .env no encontrado"

**Solución:**
```bash
# Crear desde plantilla
copy .env.example .env
```

### ❌ Error: "Secreto compartido no configurado"

**Solución:**
```bash
# Generar nuevo secreto
python -c "import secrets; print(secrets.token_hex(32))"

# Copiar el output a .env
# SHARED_SECRET=<valor_generado>
```

### ⚠️ Warning: "Usando secreto por defecto (INSEGURO)"

**Causa:** `SHARED_SECRET` aún tiene el valor `CHANGE_ME_TO_RANDOM_TOKEN`

**Solución:** Generar y configurar un secreto real (ver arriba)

---

## Seguridad

### ✅ Buenas Prácticas

1. **NUNCA** subir `.env` a repositorios públicos
2. **SIEMPRE** usar `.env.example` como plantilla (sin secretos)
3. **ROTAR** `SHARED_SECRET` periódicamente
4. **LIMITAR** `ALLOWED_SUBNETS` solo a redes confiables
5. **VERIFICAR** `.gitignore` incluye `.env`

### ❌ NO hacer

```bash
# ❌ Exponer secretos en código
SHARED_SECRET = "hardcoded_secret"  # MAL

# ❌ Compartir .env en Slack/Email
cat .env | email  # MAL

# ❌ Commitear .env a Git
git add .env  # MAL (bloqueado por .gitignore)
```

---

## Deployment

### Servidor

1. Copiar `.env.example` a `.env` en el servidor
2. Configurar `SHARED_SECRET` único
3. Ajustar `ALLOWED_SUBNETS` a las redes del datacenter
4. Configurar `DB_PATH` según ubicación de producción
5. Verificar permisos del archivo `.env` (solo lectura para owner)

### Clientes

1. Usar el **mismo** `SHARED_SECRET` que el servidor
2. Configurar `SERVER_PORT` y `DISCOVERY_PORT` iguales al servidor
3. No necesitan `ALLOWED_SUBNETS` (solo el servidor valida IPs)

---

## Referencias

- **python-dotenv**: https://github.com/theskumar/python-dotenv
- **Security Config**: `config/security_config.py`
- **Plantilla**: `.env.example`
- **Copilot Instructions**: `.github/copilot-instructions.md`

---

**Última actualización:** Noviembre 2025
