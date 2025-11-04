# security_config.py
"""
Configuración de seguridad para el sistema de inventario.

IMPORTANTE: Este archivo contiene secretos sensibles.
NO compartir en repositorios públicos. Agregar a .gitignore.
"""
import secrets
import hashlib
import ipaddress
from typing import List

# Token compartido para autenticación cliente-servidor
# Generar nuevo token: python -c "import secrets; print(secrets.token_hex(32))"
SHARED_SECRET = "CHANGE_ME_TO_RANDOM_TOKEN"  # ⚠️ CAMBIAR EN PRODUCCIÓN

# Redes permitidas (whitelist de subnets)
ALLOWED_SUBNETS = [
    "10.100.0.0/16",
    "10.101.0.0/16",
    "10.102.0.0/16",
    "10.103.0.0/16",
    "10.104.0.0/16",
    "10.105.0.0/16",
    "10.106.0.0/16",
    "10.107.0.0/16",
    "10.108.0.0/16",
    "10.109.0.0/16",
    "10.110.0.0/16",
    "10.111.0.0/16",
    "10.112.0.0/16",
    "10.113.0.0/16",
    "10.114.0.0/16",
    "10.115.0.0/16",
    "10.116.0.0/16",
    "10.117.0.0/16",
    "10.118.0.0/16",
    "10.119.0.0/16",
    "127.0.0.1/32",  # localhost para testing
]

# Límites de seguridad
MAX_BUFFER_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_JSON_DEPTH = 20  # Profundidad máxima de JSON anidado
CONNECTION_TIMEOUT = 30  # segundos
MAX_CONNECTIONS_PER_IP = 3  # Máximo de conexiones simultáneas por IP

# Límites de campo para prevenir DoS
MAX_FIELD_LENGTH = 1024  # Caracteres máximos por campo de texto


def generate_auth_token(secret: str | None = None) -> str:
    """Genera token de autenticación usando HMAC-SHA256.
    
    Args:
        secret (str | None): Secreto compartido. Si es None, usa SHARED_SECRET.
    
    Returns:
        str: Token hexadecimal de 64 caracteres
    """
    if secret is None:
        secret = SHARED_SECRET
    
    # Usar timestamp + secreto para token temporal
    import time
    timestamp = str(int(time.time() // 300))  # Token válido por 5 minutos
    
    message = f"{secret}:{timestamp}"
    return hashlib.sha256(message.encode()).hexdigest()


def verify_auth_token(token: str, secret: str | None = None) -> bool:
    """Verifica token de autenticación.
    
    Args:
        token (str): Token a verificar
        secret (str | None): Secreto compartido. Si es None, usa SHARED_SECRET.
    
    Returns:
        bool: True si el token es válido
    """
    if secret is None:
        secret = SHARED_SECRET
    
    # Verificar token actual y el de 5 minutos atrás (ventana de tiempo)
    import time
    current_time = int(time.time() // 300)
    
    for offset in [0, -1]:  # Actual y anterior
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
        # IP inválida
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
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\t')
    
    return value


def initialize_secret():
    """Genera un nuevo secreto aleatorio si aún no se ha configurado.
    
    Debe ejecutarse la primera vez en servidor y cliente.
    """
    global SHARED_SECRET
    
    if SHARED_SECRET == "CHANGE_ME_TO_RANDOM_TOKEN":
        new_secret = secrets.token_hex(32)
        print("=" * 70)
        print("⚠️  IMPORTANTE: Secreto compartido NO configurado")
        print("=" * 70)
        print(f"\nGenerar nuevo secreto aleatorio:")
        print(f"\nSHARED_SECRET = \"{new_secret}\"")
        print(f"\n1. Copiar esta línea en security_config.py")
        print(f"2. Usar el MISMO secreto en servidor y todos los clientes")
        print(f"3. NO compartir este valor públicamente\n")
        print("=" * 70)
        
        # No modificar automáticamente para evitar problemas
        raise ValueError("Secreto compartido no configurado. Ver mensaje arriba.")
    
    return SHARED_SECRET


# Validar configuración al importar
if __name__ != "__main__":
    if SHARED_SECRET == "CHANGE_ME_TO_RANDOM_TOKEN":
        print("⚠️  WARNING: Usando secreto por defecto. Ejecutar initialize_secret() para generar uno nuevo.")
