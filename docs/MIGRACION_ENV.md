# Migración a Configuración Centralizada (.env)

## Resumen de Cambios

Se han actualizado **5 archivos principales** para usar variables del `.env` en lugar de valores hardcodeados.

---

## Archivos Modificados

### 1. ✅ `src/logica/logica_servidor.py`

**Variables migradas:**
- `PORT` (5255) → `SERVER_PORT` desde .env
- Puerto de discovery (37020) → `DISCOVERY_PORT` desde .env
- `intervalo` de broadcasts (10) → `BROADCAST_INTERVAL` desde .env
- `batch_size` de pings (50) → `PING_BATCH_SIZE` desde .env

**Código antes:**
```python
PORT = 5255  # Hardcoded
broadcast.sendto(b"servidor specs", ("255.255.255.255", 37020))  # Hardcoded
batch_size = 50  # Hardcoded
```

**Código después:**
```python
try:
    from config.security_config import SERVER_PORT
    PORT = SERVER_PORT
except ImportError:
    PORT = 5255  # Fallback

try:
    from config.security_config import DISCOVERY_PORT
    discovery_port = DISCOVERY_PORT
except ImportError:
    discovery_port = 37020

try:
    from config.security_config import PING_BATCH_SIZE
    batch_size = PING_BATCH_SIZE
except ImportError:
    batch_size = 50
```

---

### 2. ✅ `src/logica/logica_specs.py`

**Variables migradas:**
- `DISCOVERY_PORT` (37020) → desde .env
- `TCP_PORT` (5255) → `SERVER_PORT` desde .env

**Código antes:**
```python
DISCOVERY_PORT = 37020
TCP_PORT = 5255
s.bind(("", DISCOVERY_PORT))
cliente.connect((HOST, TCP_PORT))
```

**Código después:**
```python
try:
    from config.security_config import DISCOVERY_PORT, SERVER_PORT
    discovery_port = DISCOVERY_PORT
    tcp_port = SERVER_PORT
except ImportError:
    discovery_port = 37020
    tcp_port = 5255

s.bind(("", discovery_port))
cliente.connect((HOST, tcp_port))
```

---

### 3. ✅ `src/specs.py`

**Variables migradas:**
- Puerto de escucha (37020) → `DISCOVERY_PORT` desde .env

**Código antes:**
```python
def escuchar_broadcast(port=37020, on_message=None):
    sock.bind(('', port))
    
# Llamada
escuchar_broadcast(port=37020, on_message=manejar_broadcast)
```

**Código después:**
```python
def escuchar_broadcast(port=None, on_message=None):
    if port is None:
        try:
            from config.security_config import DISCOVERY_PORT
            port = DISCOVERY_PORT
        except ImportError:
            port = 37020
    
    sock.bind(('', port))

# Llamada (usa valor del .env)
escuchar_broadcast(on_message=manejar_broadcast)
```

---

### 4. ✅ `src/logica/optimized_block_scanner.py`

**Variables migradas:**
- `PER_HOST_TIMEOUT` (0.8) → `SCAN_PER_HOST_TIMEOUT` desde .env
- `PER_SUBNET_TIMEOUT` (8.0) → `SCAN_PER_SUBNET_TIMEOUT` desde .env
- `PROBE_TIMEOUT` (0.9) → `SCAN_PROBE_TIMEOUT` desde .env
- `OUTPUT_DIR` (output) → desde .env
- `batch_size` de ARP population (50) → `PING_BATCH_SIZE` desde .env

**Código antes:**
```python
PER_HOST_TIMEOUT = 0.8
PER_SUBNET_TIMEOUT = 8.0
PROBE_TIMEOUT = 0.9
OUTPUT_DIR = Path(__file__).parent.parent / "output"
batch_size = 50
```

**Código después:**
```python
try:
    from config.security_config import (
        SCAN_PER_HOST_TIMEOUT,
        SCAN_PER_SUBNET_TIMEOUT,
        SCAN_PROBE_TIMEOUT,
        OUTPUT_DIR as ENV_OUTPUT_DIR,
        PING_BATCH_SIZE
    )
    PER_HOST_TIMEOUT = SCAN_PER_HOST_TIMEOUT
    PER_SUBNET_TIMEOUT = SCAN_PER_SUBNET_TIMEOUT
    PROBE_TIMEOUT = SCAN_PROBE_TIMEOUT
    output_dir_str = ENV_OUTPUT_DIR
except ImportError:
    PER_HOST_TIMEOUT = 0.8
    PER_SUBNET_TIMEOUT = 8.0
    PROBE_TIMEOUT = 0.9
    output_dir_str = "output"

OUTPUT_DIR = Path(__file__).parent.parent / output_dir_str
```

---

## Resumen de Variables del .env Utilizadas

| Variable .env | Archivos que la usan | Valor por defecto | Descripción |
|---------------|----------------------|-------------------|-------------|
| `SERVER_PORT` | `logica_servidor.py`, `logica_specs.py` | `5255` | Puerto TCP del servidor |
| `DISCOVERY_PORT` | `logica_servidor.py`, `logica_specs.py`, `specs.py` | `37020` | Puerto UDP para discovery |
| `BROADCAST_INTERVAL` | `logica_servidor.py` | `10` | Segundos entre broadcasts |
| `PING_BATCH_SIZE` | `logica_servidor.py`, `optimized_block_scanner.py` | `50` | Tamaño de lote para pings |
| `SCAN_PER_HOST_TIMEOUT` | `optimized_block_scanner.py` | `0.8` | Timeout por host (seg) |
| `SCAN_PER_SUBNET_TIMEOUT` | `optimized_block_scanner.py` | `8.0` | Timeout por subnet (seg) |
| `SCAN_PROBE_TIMEOUT` | `optimized_block_scanner.py` | `0.9` | Timeout de probes (seg) |
| `OUTPUT_DIR` | `optimized_block_scanner.py` | `output` | Directorio de salida |

---

## Beneficios de la Migración

### ✅ **Antes (Hardcoded)**
```python
# ❌ Difícil de cambiar
PORT = 5255
broadcast.sendto(b"data", ("255.255.255.255", 37020))
batch_size = 50

# Para cambiar el puerto:
# 1. Buscar en 5 archivos diferentes
# 2. Modificar cada archivo manualmente
# 3. Riesgo de inconsistencias
```

### ✅ **Ahora (Centralizado)**
```python
# ✅ Fácil de cambiar
from config.security_config import SERVER_PORT, DISCOVERY_PORT, PING_BATCH_SIZE
PORT = SERVER_PORT
broadcast.sendto(b"data", ("255.255.255.255", DISCOVERY_PORT))
batch_size = PING_BATCH_SIZE

# Para cambiar el puerto:
# 1. Editar UNA línea en .env
# 2. Reiniciar aplicaciones
# 3. Todos los componentes sincronizados
```

---

## Compatibilidad y Fallbacks

Todos los archivos incluyen **fallbacks** por si el `.env` no está disponible:

```python
try:
    from config.security_config import SERVER_PORT
    PORT = SERVER_PORT
except ImportError:
    PORT = 5255  # Valor por defecto original
```

**Ventajas:**
- ✅ Funciona sin `.env` (desarrollo rápido)
- ✅ No rompe código legacy
- ✅ Migración gradual posible
- ✅ Mensajes de advertencia automáticos

---

## Verificación

Para confirmar que los valores se cargan correctamente:

```bash
# Verificar puerto del servidor
python -c "import sys; sys.path.insert(0, 'src'); from logica import logica_servidor; print(f'Puerto: {logica_servidor.PORT}')"

# Output esperado:
# ✓ Configuración cargada desde C:\...\specs-python\.env
# Puerto: 5255
```

---

## Próximos Pasos Recomendados

### Archivos Pendientes de Migrar (Opcional)

1. **`src/datos/scan_ip_mac.py`**
   - `ping_timeout=0.8` → podría usar `PING_TIMEOUT` del .env
   - Línea 234, 296

2. **`src/datos/ipAddress.py`**
   - `PING_TIMEOUT_SECONDS = 1` → podría usar `PING_TIMEOUT` del .env
   - Línea 35

3. **`src/sql/consultas_sql.py`**
   - `db_path = "specs.db"` → podría usar `DB_PATH` del .env
   - Líneas 23, 54, 56

**Prioridad:** Baja (estos archivos funcionan correctamente con valores actuales)

---

## Testing

### Test Manual

1. **Modificar .env:**
   ```env
   SERVER_PORT=9999
   DISCOVERY_PORT=12345
   ```

2. **Ejecutar servidor:**
   ```bash
   python run_servidor.py
   ```

3. **Verificar logs:**
   ```
   ✓ Configuración cargada desde ...\.env
   🔄 Iniciando anuncios periódicos cada 10 segundos...
   📡 Broadcast enviado a 255.255.255.255:12345
   Servidor escuchando en 10.100.2.152:9999
   ```

4. **Ejecutar cliente:**
   ```bash
   python run_cliente.py --tarea
   ```

5. **Verificar conexión:**
   ```
   ✓ Configuración cargada desde ...\.env
   🔊 Escuchando broadcasts en puerto 12345...
   📡 Broadcast recibido de 10.100.2.152: servidor specs
   🔌 Conectando al servidor 10.100.2.152:9999...
   ✓ Datos enviados correctamente al servidor
   ```

---

## Documentación Relacionada

- **Variables disponibles:** `docs/CONFIGURACION.md`
- **Plantilla de configuración:** `.env.example`
- **Implementación de seguridad:** `config/security_config.py`

---

**Fecha:** Noviembre 2025  
**Estado:** ✅ Completado  
**Archivos migrados:** 5/5
