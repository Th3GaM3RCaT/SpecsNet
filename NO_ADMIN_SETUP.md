# 🔓 Configuración Sin Permisos de Administrador

## 🎯 Problema Original

El sistema requería broadcasts UDP para que los clientes descubrieran automáticamente el servidor, pero esto presentaba varios problemas:
- Requería configuración de Windows Firewall
- Necesitaba permisos de administrador
- Incompatible con Firewall gestionado remotamente (Bitdefender, políticas corporativas)

## ✅ Solución Implementada: Configuración Manual por IP

El sistema ahora soporta **configuración manual** de la IP del servidor mediante un archivo JSON, eliminando completamente la dependencia de broadcasts UDP y configuración de Firewall.

---

## 📋 Configuración Paso a Paso

### 1️⃣ Obtener la IP del Servidor

En el equipo donde **corre el servidor**, ejecuta:

```powershell
# PowerShell
ipconfig | Select-String "IPv4"
```

O en Python:
```powershell
python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()"
```

Deberías obtener algo como: `192.168.1.100` o `10.100.5.25`

### 2️⃣ Crear Archivo de Configuración

**En el equipo cliente** (donde ejecutas `SpecsCliente.exe`), edita el archivo:

📁 **`config/server_config.json`**

```json
{
  "server_ip": "192.168.1.100",
  "server_port": 5255,
  "use_discovery": false,
  "connection_timeout": 10
}
```

**Campos explicados:**
- `server_ip`: IP del servidor obtenida en el paso 1
- `server_port`: Puerto TCP del servidor (por defecto 5255)
- `use_discovery`: **`false`** = Usar IP manual (modo recomendado)
- `connection_timeout`: Segundos para timeout de conexión TCP

### 3️⃣ Probar Conexión

```powershell
# Probar conectividad TCP al servidor (puerto 5255)
Test-NetConnection -ComputerName 192.168.1.100 -Port 5255
```

Deberías ver:
```
TcpTestSucceeded : True
```

Si dice `False`, verifica:
- ✅ IP correcta
- ✅ Servidor corriendo (`python servidor.py`)
- ✅ Puerto correcto (5255)
- ✅ Ambos equipos en la misma red

---

## 🚀 Uso del Cliente

### Modo GUI (Interfaz Gráfica)

```powershell
.\dist\SpecsCliente\SpecsCliente.exe
```

1. Clic en **"Enviar Informe"**
2. Verás:
   ```
   [CONFIG] Configuracion manual: Servidor en 192.168.1.100:5255
   [INFO] Modo discovery UDP deshabilitado (util sin permisos de Firewall)
   [CONNECT] Conectando al servidor 192.168.1.100:5255...
   [OK] Datos enviados correctamente al servidor
   ```

### Modo Tarea (Background - Sin GUI)

```powershell
.\dist\SpecsCliente\SpecsCliente.exe --tarea
```

El cliente:
1. Lee `config/server_config.json`
2. Se conecta directamente a la IP configurada
3. Envía especificaciones al servidor
4. Cierra automáticamente

---

## 🔄 Ventajas de la Configuración Manual

| Característica | Ventaja |
|----------------|---------|
| **Firewall** | ❌ NO requiere configuración |
| **Permisos Admin** | ❌ NO necesarios |
| **Configuración** | Simple archivo JSON |
| **Multi-subnet** | ✅ Funciona entre diferentes redes |
| **Seguridad** | Conexión directa punto a punto |
| **Compatibilidad** | ✅ Compatible con políticas corporativas |

---

## 🛠️ Distribución a Múltiples Clientes

### Opción A: Archivo Config Incluido

1. Edita `config/server_config.json` con la IP del servidor
2. Crea ZIP con:
   ```
   SpecsCliente/
   ├── SpecsCliente.exe
   ├── _internal/
   └── config/
       └── server_config.json  ← Con IP pre-configurada
   ```
3. Distribuye este ZIP a todos los clientes

### Opción B: Script de Configuración

Crea un archivo `configurar_cliente.bat` junto al ejecutable:

```batch
@echo off
echo ====================================
echo Configuracion de Cliente Specs
echo ====================================
echo.

set /p SERVER_IP="Ingresa la IP del servidor: "

if not exist config mkdir config

echo { > config\server_config.json
echo   "server_ip": "%SERVER_IP%", >> config\server_config.json
echo   "server_port": 5255, >> config\server_config.json
echo   "use_discovery": false, >> config\server_config.json
echo   "connection_timeout": 10 >> config\server_config.json
echo } >> config\server_config.json

echo.
echo [OK] Configuracion guardada en config\server_config.json
echo.
echo Ahora puedes ejecutar SpecsCliente.exe
pause
```

Los usuarios solo ejecutan `configurar_cliente.bat` y escriben la IP.

---

## 🔍 Troubleshooting

### "[ERROR] Error al enviar datos: [Errno 10061] No connection could be made"

**Causa**: No se puede conectar al servidor en TCP puerto 5255

**Soluciones**:
1. Verificar que el servidor esté corriendo:
   ```powershell
   # En el servidor
   Get-Process python
   ```

2. Verificar conectividad de red:
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.100 -Port 5255
   ```

3. Verificar que la IP sea correcta en `config/server_config.json`

4. Si el servidor está en otra subnet, verificar que los routers permitan tráfico TCP

### "[SOLUCION] Crea config/server_config.json con IP del servidor"

**Causa**: No existe `config/server_config.json`

**Solución**: Crear el archivo según el paso 2 de configuración

### Cliente no envía datos

**Causa**: IP incorrecta o servidor no accesible

**Solución**: 
1. Verificar IP en `config/server_config.json`
2. Probar conectividad con `Test-NetConnection`
3. Verificar que `use_discovery` esté en `false`

---

## 📊 Verificación de Funcionamiento

### En el Servidor

Cuando un cliente se conecta, deberías ver:

```
[OK] Servidor TCP escuchando en 0.0.0.0:5255
conectado por: ('192.168.1.50', 54321)
Informacion recibida de: ('192.168.1.50', 54321)
[OK] Dispositivo guardado: LAPTOP-ABC123 (00:11:22:33:44:55)
[OK] Conexion TCP procesada en 2.34 segundos
desconectado: ('192.168.1.50', 54321)
```

### En el Cliente

```
[CONFIG] Configuracion manual: Servidor en 192.168.1.100:5255
[INFO] Modo discovery UDP deshabilitado (util sin permisos de Firewall)
[CONNECT] Conectando al servidor 192.168.1.100:5255...
[OK] Datos enviados correctamente al servidor
```

---

## 🔐 Seguridad

El modo manual es **más seguro** porque:

✅ **Conexión directa** cliente → servidor (sin intermediarios)
✅ **Soporta autenticación** por tokens (si `security_config.py` existe)
✅ **Funciona con VPN** y múltiples subnets
✅ **Sin exposición de red** - no anuncia presencia del servidor

---

## 🎓 Notas Técnicas

### Flujo de Conexión

```
Modo Manual (Recomendado):
Cliente → lee config/server_config.json → conecta directamente TCP 5255

Modo Manual (Recomendado):
Cliente → lee config/server_config.json → conecta directamente TCP 5255
```

### Compatibilidad

- ✅ **Windows 10/11** (sin permisos admin)
- ✅ **Redes corporativas** (Firewall gestionado)
- ✅ **Antivirus/EDR** (Bitdefender, Kaspersky, etc.)
- ✅ **Multi-subnet** (diferentes VLANs)
- ✅ **VPN** (cliente y servidor en VPN)

---

## 📚 Referencias

- [README Principal](README.md)
- [Arquitectura del Sistema](README.md#arquitectura)

---

## 💡 Resumen Rápido

**Para usuarios SIN permisos de administrador:**

1. Obtener IP del servidor: `ipconfig | Select-String "IPv4"`
2. Crear `config/server_config.json`:
   ```json
   {"server_ip": "TU_IP_AQUI", "server_port": 5255, "use_discovery": false}
   ```
3. Ejecutar cliente: `SpecsCliente.exe` o `SpecsCliente.exe --tarea`
4. ✅ Funciona sin configuración adicional

**Ventajas:**
- ✅ No requiere permisos de administrador
- ✅ Compatible con Firewall corporativo
- ✅ Configuración en 2 minutos
- ✅ Funciona con Firewall corporativo
- ✅ Compatible con Bitdefender/antivirus gestionados
- ✅ Configuración en 2 minutos
