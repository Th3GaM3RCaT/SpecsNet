#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de conexión manual al servidor (sin broadcasts UDP).
Simula el flujo del cliente usando config/server_config.json
"""

import sys
from pathlib import Path
from json import load, dumps
from socket import socket, AF_INET, SOCK_STREAM

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_manual_connection():
    """Prueba la conexión manual al servidor sin usar broadcasts."""
    
    print("=" * 60)
    print("TEST DE CONEXIÓN MANUAL (SIN FIREWALL)")
    print("=" * 60)
    print()
    
    # 1. Leer configuración
    config_path = Path(__file__).parent / "config" / "server_config.json"
    
    if not config_path.exists():
        print("❌ ERROR: No existe config/server_config.json")
        print(f"   Ruta esperada: {config_path}")
        return False
    
    print(f"📁 Leyendo configuración desde: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = load(f)
    
    server_ip = config.get("server_ip")
    server_port = config.get("server_port", 5255)
    use_discovery = config.get("use_discovery", True)
    
    print(f"   ├─ IP del servidor: {server_ip}")
    print(f"   ├─ Puerto: {server_port}")
    print(f"   └─ Modo discovery UDP: {'Habilitado' if use_discovery else 'Deshabilitado'}")
    print()
    
    if use_discovery:
        print("⚠️  ADVERTENCIA: use_discovery está en true")
        print("   Para evitar broadcasts UDP, cambiar a false en config/server_config.json")
        print()
    
    # 2. Probar conexión TCP
    print(f"🔌 Probando conexión TCP a {server_ip}:{server_port}...")
    
    try:
        # Crear datos de prueba mínimos
        test_data = {
            "SerialNumber": "TEST-12345",
            "Name": "TEST-CLIENT",
            "MAC Address": "00:11:22:33:44:55",
            "test_mode": True,
            "message": "Conexión de prueba sin broadcasts UDP"
        }
        
        # Conectar al servidor
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.settimeout(10)
        
        print(f"   ├─ Conectando...")
        client_socket.connect((server_ip, server_port))
        print(f"   ├─ ✅ Conexión TCP establecida")
        
        # Enviar datos
        print(f"   ├─ Enviando datos de prueba...")
        json_data = dumps(test_data).encode("utf-8")
        client_socket.sendall(json_data)
        print(f"   ├─ ✅ {len(json_data)} bytes enviados")
        
        # Cerrar
        client_socket.close()
        print(f"   └─ ✅ Conexión cerrada correctamente")
        print()
        
        print("=" * 60)
        print("✅ TEST EXITOSO")
        print("=" * 60)
        print()
        print("La conexión funciona correctamente SIN necesidad de broadcasts UDP.")
        print("El cliente puede conectarse directamente al servidor usando la IP configurada.")
        print()
        print("Próximo paso: Ejecutar el cliente compilado en modo tarea:")
        print(f"   .\\dist\\SpecsCliente\\SpecsCliente.exe --tarea")
        print()
        
        return True
        
    except ConnectionRefusedError:
        print(f"   └─ ❌ ERROR: Conexión rechazada")
        print()
        print("Causas posibles:")
        print("  1. El servidor no está corriendo")
        print("  2. El puerto 5255 está bloqueado")
        print("  3. La IP del servidor es incorrecta")
        print()
        print("Verificar:")
        print(f"  Get-Process python")
        print(f"  Test-NetConnection -ComputerName {server_ip} -Port {server_port}")
        return False
        
    except TimeoutError:
        print(f"   └─ ❌ ERROR: Timeout (no responde en 10 segundos)")
        print()
        print("Causas posibles:")
        print("  1. IP incorrecta en server_config.json")
        print("  2. Servidor en otra subnet sin conectividad")
        print("  3. Firewall bloqueando conexiones TCP salientes (raro)")
        return False
        
    except Exception as e:
        print(f"   └─ ❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = test_manual_connection()
    sys.exit(0 if success else 1)
