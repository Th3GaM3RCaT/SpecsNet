# Script de instalación para Specs Python
# Ejecutar como Administrador

Write-Host "🚀 Instalador de Specs Python" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Verificar Python
Write-Host "🔍 Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no está instalado" -ForegroundColor Red
    Write-Host "   Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Throw
}
Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green

# Crear entorno virtual
Write-Host "`n📦 Creando entorno virtual..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al crear entorno virtual" -ForegroundColor Red
    Throw
}
Write-Host "✓ Entorno virtual creado" -ForegroundColor Green

# Activar entorno virtual
Write-Host "`n🔌 Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "`n📥 Instalando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
        Throw
    }
    Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt no encontrado, instalando manualmente..." -ForegroundColor Yellow
    pip install PySide6 psutil wmi windows-tools getmac
}

# Configurar security_config.py si no existe
Write-Host "`n🔐 Configurando seguridad..." -ForegroundColor Yellow
if (-not (Test-Path "security_config.py")) {
    Write-Host "⚠️  security_config.py no encontrado" -ForegroundColor Yellow
    Write-Host "   Creando configuración de seguridad..." -ForegroundColor Yellow
    
    # Generar token aleatorio
    $bytes = New-Object Byte[] 32
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $token = [BitConverter]::ToString($bytes).Replace("-", "").ToLower()
    
    @"
# Configuración de seguridad - NO COMPARTIR ESTE ARCHIVO

import hmac
import hashlib
import time
from ipaddress import ip_address, ip_network

# Token secreto compartido (cliente y servidor deben tener el mismo)
SHARED_SECRET = "$token"

# Subnets permitidas (CIDR notation)
ALLOWED_SUBNETS = [
    "10.100.0.0/16",
    "10.101.0.0/16",
    "10.119.0.0/16",
    "127.0.0.1/32",
]

# Límites de seguridad
MAX_BUFFER_SIZE = 10 * 1024 * 1024  # 10 MB
CONNECTION_TIMEOUT = 30  # segundos
MAX_CONNECTIONS_PER_IP = 3
MAX_FIELD_LENGTH = 1024  # caracteres

def generate_auth_token():
    timestamp = str(int(time.time() // 300))
    message = f"specs_auth_{timestamp}"
    token = hmac.new(
        SHARED_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return token

def verify_auth_token(token):
    current_window = str(int(time.time() // 300))
    previous_window = str(int(time.time() // 300) - 1)
    
    for window in [current_window, previous_window]:
        message = f"specs_auth_{window}"
        expected_token = hmac.new(
            SHARED_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(token, expected_token):
            return True
    return False

def is_ip_allowed(ip_str):
    try:
        ip = ip_address(ip_str)
        for subnet_str in ALLOWED_SUBNETS:
            subnet = ip_network(subnet_str)
            if ip in subnet:
                return True
        return False
    except Exception:
        return False

def sanitize_field(value, max_length=MAX_FIELD_LENGTH):
    if not isinstance(value, str):
        value = str(value)
    value = value[:max_length]
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    return value
"@ | Out-File -FilePath "security_config.py" -Encoding UTF8
    
    Write-Host "✓ security_config.py creado con token: $($token.Substring(0, 16))..." -ForegroundColor Green
} else {
    Write-Host "✓ security_config.py ya existe" -ForegroundColor Green
}

# Inicializar base de datos
Write-Host "`n🗄️  Inicializando base de datos..." -ForegroundColor Yellow
if (Test-Path "sql_specs\specs.sql") {
    if (-not (Test-Path "specs.db")) {
        Write-Host "   Creando specs.db desde schema..." -ForegroundColor Yellow
        $schema = Get-Content "sql_specs\specs.sql" -Raw
        # SQLite command line tool required
        # sqlite3 specs.db < sql_specs\specs.sql
        Write-Host "⚠️  Ejecuta manualmente: sqlite3 specs.db < sql_specs\specs.sql" -ForegroundColor Yellow
    } else {
        Write-Host "✓ specs.db ya existe" -ForegroundColor Green
    }
}

Write-Host "`n✅ Instalación completada!" -ForegroundColor Green
Write-Host "`nPara ejecutar el servidor:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python servidor.py`n" -ForegroundColor White

Write-Host "Para ejecutar el cliente:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python specs.py`n" -ForegroundColor White
