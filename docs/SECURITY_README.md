# 🔒 Configuración de Seguridad - Specs Python

## ⚠️ IMPORTANTE: Primera Configuración

El sistema ahora incluye **autenticación por token** y **validación de IPs**. Debes configurar el archivo `security_config.py` antes del primer uso.

## 🚀 Pasos de Configuración

### 1. Generar Secreto Compartido

Ejecuta este comando en Python para generar un token aleatorio seguro:

```bash
python -c "import secrets; print('SHARED_SECRET = \"' + secrets.token_hex(32) + '\"')"
```

**Ejemplo de salida:**
```
SHARED_SECRET = "a1b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef0123456789"
```

### 2. Editar `security_config.py`

Abre el archivo `security_config.py` y **reemplaza** la línea:

```python
SHARED_SECRET = "CHANGE_ME_TO_RANDOM_TOKEN"  # ⚠️ CAMBIAR
```

Por el secreto generado:

```python
SHARED_SECRET = "a1b2c3d4e5f6789abcdef0123456789abcdef0123456789abcdef0123456789"
```

### 3. Configurar Subnets Permitidas

Edita la lista `ALLOWED_SUBNETS` con las redes de tu organización:

```python
ALLOWED_SUBNETS = [
    "10.100.0.0/16",  # Red sede principal
    "10.119.0.0/16",  # Red sucursal
    "192.168.1.0/24", # Red oficina local
    "127.0.0.1/32",   # localhost (para testing)
]
```

### 4. Copiar a Todos los Dispositivos

**CRÍTICO**: El archivo `security_config.py` con el **MISMO `SHARED_SECRET`** debe estar presente en:

- ✅ **Servidor** (donde corre `servidor.py`)
- ✅ **Todos los clientes** (donde corre `specs.py`)

**NO** cambiar el `SHARED_SECRET` después de distribuirlo. Si necesitas rotarlo, actualiza todos los dispositivos simultáneamente.

---

## 🛡️ Características de Seguridad Implementadas

### 1. Autenticación por Token
- Token generado con HMAC-SHA256
- Validez de 5 minutos (ventana de tiempo configurable)
- Previene conexiones no autorizadas

### 2. Whitelist de IPs
- Solo IPs en `ALLOWED_SUBNETS` pueden conectarse
- Bloqueo automático de IPs fuera de rango
- Configurable por subnet CIDR

### 3. Rate Limiting
- Máximo 3 conexiones simultáneas por IP
- Previene ataques de Denial of Service (DoS)
- Configurable con `MAX_CONNECTIONS_PER_IP`

### 4. Buffer Overflow Protection
- Límite de 10 MB por mensaje JSON
- Timeout de 30 segundos por conexión
- Previene Memory Exhaustion attacks

### 5. Input Sanitization
- Todos los campos de texto son sanitizados
- Longitud máxima de 1024 caracteres por campo
- Remoción de caracteres de control peligrosos

### 6. Command Injection Prevention
- Subprocess ejecutado con lista de argumentos (NO `shell=True`)
- Validación de entrada con regex
- Previene ejecución de comandos arbitrarios

---

## 🔧 Parámetros Configurables

En `security_config.py`:

```python
# Límites de seguridad
MAX_BUFFER_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_JSON_DEPTH = 20  # Profundidad máxima de JSON
CONNECTION_TIMEOUT = 30  # segundos
MAX_CONNECTIONS_PER_IP = 3
MAX_FIELD_LENGTH = 1024  # caracteres por campo
```

---

## 🧪 Testing de Configuración

### Verificar Autenticación

**Cliente:**
```python
python specs.py
# Debe mostrar: "✓ Token de autenticación agregado"
```

**Servidor:**
```python
python servidor.py
# Al recibir cliente debe mostrar: "✓ Token válido desde <IP>"
```

### Verificar Whitelist de IPs

Intenta conectar desde una IP NO permitida. El servidor debe rechazar con:
```
⚠️  SECURITY: IP bloqueada (no está en whitelist): <IP>
```

---

## ⚙️ Modo Fallback (Sin Seguridad)

Si `security_config.py` NO existe o está mal configurado:

```
⚠️  WARNING: security_config.py no encontrado. Seguridad DESHABILITADA.
```

El sistema funcionará **SIN autenticación** (modo legacy para testing).

**NO usar en producción sin security_config.py configurado.**

---

## 🔐 Mejores Prácticas

### ✅ DO:
- Generar secreto aleatorio con `secrets.token_hex(32)`
- Rotar secreto cada 90 días
- Usar HTTPS/VPN para comunicación en redes públicas
- Auditar logs de conexiones rechazadas
- Mantener `security_config.py` en `.gitignore`

### ❌ DON'T:
- Compartir `security_config.py` en repositorios públicos
- Usar secretos débiles o predecibles
- Dejar `SHARED_SECRET = "CHANGE_ME_TO_RANDOM_TOKEN"`
- Permitir toda la internet en `ALLOWED_SUBNETS` (`0.0.0.0/0`)
- Deshabilitar validación de tokens en producción

---

## 🆘 Troubleshooting

### "Token de autenticación inválido"
- ✅ Verificar que `SHARED_SECRET` sea idéntico en cliente y servidor
- ✅ Verificar sincronización de reloj (diferencia < 5 minutos)
- ✅ Reiniciar cliente y servidor después de cambiar secreto

### "IP bloqueada"
- ✅ Agregar subnet del cliente a `ALLOWED_SUBNETS`
- ✅ Usar formato CIDR correcto (ej: `10.100.0.0/16`)
- ✅ Verificar IP real del cliente con `ipconfig` (Windows)

### "Demasiadas conexiones"
- ✅ Esperar a que conexiones anteriores se cierren
- ✅ Aumentar `MAX_CONNECTIONS_PER_IP` si es legítimo
- ✅ Investigar posible ataque DoS si conexiones son sospechosas

---

## 📞 Soporte

Para problemas de seguridad críticos, contactar al administrador del sistema.

**NO** compartir logs que contengan tokens o secretos.
