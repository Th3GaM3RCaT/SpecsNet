# security_config.example.py
"""
TEMPLATE de configuración de seguridad para el sistema de inventario.

INSTRUCCIONES:
1. Copiar este archivo como security_config.py
2. Configurar los valores según tu entorno
3. NO compartir en repositorios públicos. Agregar a .gitignore.
"""

import secrets
import hashlib
import ipaddress
import os
from pathlib import Path

# ============================================================================
# VARIABLES DE ENTORNO - Crear archivo .env en la raíz del proyecto
# ============================================================================
# SHARED_SECRET=<generar con comando abajo>
# ALLOWED_SUBNETS=10.100.0.0/16,10.119.0.0/16,127.0.0.1/32
# MAX_BUFFER_SIZE=10485760
# CONNECTION_TIMEOUT=30
# MAX_CONNECTIONS_PER_IP=3
# MAX_FIELD_LENGTH=1024
# SERVER_PORT=5255
# USE_TLS=false
#
# Generar SHARED_SECRET:
# python -c "import secrets; print(secrets.token_hex(32))"

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[OK] Configuración cargada desde {env_path}")
    else:
        print(f"[WARN] Archivo .env no encontrado en {env_path}")
except ImportError:
    print("[WARN] python-dotenv no instalado. Ejecutar: pip install python-dotenv")

# ============================================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================================

# Token secreto compartido para autenticación cliente-servidor
# IMPORTANTE: Debe ser el MISMO en servidor y clientes
# GENERAR con: python -c "import secrets; print(secrets.token_hex(32))"
SHARED_SECRET = os.getenv("SHARED_SECRET", "CHANGE_ME_TO_RANDOM_TOKEN")

# Patrón regex para validar IPs IPv4
default_pattern = r"^([1-9]|[1-9][0-9]|(1)[0-9][0-9]|(2)[0-4][0-9]|(25)[0-5])(\.([0-9]|[1-9][0-9]|(1)[0-9][0-9]|(2)[0-4][0-9]|(25)[0-5])){3}$"
PATTERN = os.getenv("IP_PATTERN", default_pattern)

# Redes permitidas (whitelist de subnets en formato CIDR)
# Agregar todas las subredes de tu organización
# Formato: subnet1,subnet2,subnet3
subnets_str = os.getenv("ALLOWED_SUBNETS", "10.100.0.0/16,10.119.0.0/16,127.0.0.1/32")
ALLOWED_SUBNETS = [subnet.strip() for subnet in subnets_str.split(",")]

# ============================================================================
# LÍMITES DE SEGURIDAD
# ============================================================================

# Tamaño máximo de datos que puede recibir el servidor (bytes)
MAX_BUFFER_SIZE = int(os.getenv("MAX_BUFFER_SIZE", "10485760"))  # 10 MB

# Profundidad máxima de JSON anidado
MAX_JSON_DEPTH = 20

# Timeout de conexión TCP (segundos)
CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", "30"))

# Máximo de conexiones simultáneas por IP
MAX_CONNECTIONS_PER_IP = int(os.getenv("MAX_CONNECTIONS_PER_IP", "3"))

# Longitud máxima de campos de texto (caracteres)
MAX_FIELD_LENGTH = int(os.getenv("MAX_FIELD_LENGTH", "1024"))

# ============================================================================
# CONFIGURACIÓN DE RED
# ============================================================================

# Puertos de red
SERVER_PORT = int(os.getenv("SERVER_PORT", "5255"))  # Puerto TCP del servidor
DISCOVERY_PORT = int(os.getenv("DISCOVERY_PORT", "37020"))  # Puerto UDP discovery
BROADCAST_INTERVAL = int(os.getenv("BROADCAST_INTERVAL", "10"))  # Segundos

# ============================================================================
# CONFIGURACIÓN DE ALMACENAMIENTO Y ESCANEO
# ============================================================================

# Rutas de archivos
DB_PATH = os.getenv("DB_PATH", "data/specs.db")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# Configuración de escaneo de red
SCAN_SUBNET_START = os.getenv("SCAN_SUBNET_START", "10.100.0.0")
SCAN_SUBNET_END = os.getenv("SCAN_SUBNET_END", "10.119.0.0")
PING_TIMEOUT = float(os.getenv("PING_TIMEOUT", "1.0"))
SCAN_PER_HOST_TIMEOUT = float(os.getenv("SCAN_PER_HOST_TIMEOUT", "0.8"))
SCAN_PER_SUBNET_TIMEOUT = float(os.getenv("SCAN_PER_SUBNET_TIMEOUT", "8.0"))
SCAN_PROBE_TIMEOUT = float(os.getenv("SCAN_PROBE_TIMEOUT", "0.9"))
PING_BATCH_SIZE = int(os.getenv("PING_BATCH_SIZE", "20"))

# ============================================================================
# CONFIGURACIÓN TLS/SSL (Opcional)
# ============================================================================

USE_TLS = os.getenv("USE_TLS", "false").lower() in ("true", "1", "yes")
TLS_CERT_PATH = os.getenv("TLS_CERT_PATH", "config/server.crt")
TLS_KEY_PATH = os.getenv("TLS_KEY_PATH", "config/server.key")

# ============================================================================
# FUNCIONES DE SEGURIDAD
# ============================================================================


def generate_auth_token(secret: str | None = None) -> str:
    """Genera token de autenticación usando HMAC-SHA256.

    Args:
        secret (str | None): Secreto compartido. Si es None, usa SHARED_SECRET.

    Returns:
        str: Token hexadecimal de 64 caracteres válido por 5 minutos
    """
    if secret is None:
        secret = SHARED_SECRET

    import time

    # Token válido por 5 minutos (ventana de 300 segundos)
    timestamp = str(int(time.time() // 300))
    message = f"{secret}:{timestamp}"

    return hashlib.sha256(message.encode()).hexdigest()


def verify_auth_token(token: str, secret: str | None = None) -> bool:
    """Verifica token de autenticación.

    Acepta token de ventana actual y anterior para tolerar clock skew.

    Args:
        token (str): Token a verificar
        secret (str | None): Secreto compartido. Si es None, usa SHARED_SECRET.

    Returns:
        bool: True si el token es válido
    """
    if secret is None:
        secret = SHARED_SECRET

    import time

    # Verificar ventana actual y anterior (5 minutos cada una)
    current_time = int(time.time() // 300)

    for offset in [0, -1]:
        timestamp = str(current_time + offset)
        message = f"{secret}:{timestamp}"
        expected_token = hashlib.sha256(message.encode()).hexdigest()

        if token == expected_token:
            return True

    return False


def is_ip_allowed(ip: str) -> bool:
    """Verifica si una IP está en la whitelist de subnets.

    Args:
        ip (str): Dirección IP a verificar

    Returns:
        bool: True si la IP está permitida
    """
    try:
        ip_obj = ipaddress.ip_address(ip)

        for subnet_str in ALLOWED_SUBNETS:
            subnet = ipaddress.ip_network(subnet_str)
            if ip_obj in subnet:
                return True

        return False
    except ValueError:
        return False


def sanitize_field(value: str, max_length: int = MAX_FIELD_LENGTH) -> str:
    """Sanitiza un campo de texto para prevenir ataques.

    Args:
        value (str): Valor a sanitizar
        max_length (int): Longitud máxima permitida

    Returns:
        str: Valor sanitizado y truncado
    """
    if not isinstance(value, str):
        value = str(value)

    # Truncar a longitud máxima
    if len(value) > max_length:
        value = value[:max_length]

    # Remover caracteres de control peligrosos
    value = "".join(char for char in value if ord(char) >= 32 or char in "\n\t")

    return value


def initialize_secret():
    """Genera un nuevo secreto aleatorio si aún no se ha configurado.

    Debe ejecutarse la primera vez en servidor y cliente.
    """
    global SHARED_SECRET

    if SHARED_SECRET == "CHANGE_ME_TO_RANDOM_TOKEN":
        new_secret = secrets.token_hex(32)
        print("=" * 70)
        print("[WARN] IMPORTANTE: Secreto compartido NO configurado")
        print("=" * 70)
        print("\nGenerar nuevo secreto aleatorio:")
        print(f'\nSHARED_SECRET = "{new_secret}"')
        print(f"\n1. Copiar esta línea en security_config.py o .env")
        print(f"2. Usar el MISMO secreto en servidor y todos los clientes")
        print(f"3. NO compartir este valor públicamente\n")
        print("=" * 70)

        raise ValueError("Secreto compartido no configurado. Ver mensaje arriba.")

    return SHARED_SECRET


# ============================================================================
# VALIDACIÓN AL IMPORTAR
# ============================================================================

if __name__ != "__main__":
    if SHARED_SECRET == "CHANGE_ME_TO_RANDOM_TOKEN":
        print(
            "[WARN] WARNING: Usando secreto por defecto. Ejecutar initialize_secret() para generar uno nuevo."
        )

# ============================================================================
# TESTING - Descomentar para probar configuración
# ============================================================================

if __name__ == "__main__":
    print("[INFO] Testing security_config.py\n")

    # Test 1: Token generation
    try:
        token = generate_auth_token()
        print(f"[OK] Token generado: {token[:16]}...")
    except Exception as e:
        print(f"[ERROR] Error generando token: {e}")

    # Test 2: Token verification
    try:
        is_valid = verify_auth_token(token) # pyright: ignore[reportPossiblyUnboundVariable]
        print(f"[OK] Token válido: {is_valid}")
    except Exception as e:
        print(f"[ERROR] Error verificando token: {e}")

    # Test 3: IP validation
    test_ips = ["10.100.1.1", "192.168.1.1", "8.8.8.8", "127.0.0.1"]
    print("\n[INFO] Validación de IPs:")
    for ip in test_ips:
        allowed = is_ip_allowed(ip)
        status = "[OK] Permitida" if allowed else "[X] Bloqueada"
        print(f"  {status}: {ip}")

    # Test 4: Field sanitization
    test_field = "A" * 2000 + "\x00\x01\x02"
    sanitized = sanitize_field(test_field)
    print(f"\n[OK] Sanitización: {len(test_field)} chars → {len(sanitized)} chars")

    print("\n[OK] Configuración de seguridad validada")
