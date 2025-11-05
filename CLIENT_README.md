# Cliente Specs - Inventario de Hardware

## 📋 Descripción

Cliente para el Sistema de Inventario de Hardware de Specs. Recopila especificaciones de hardware y software del equipo y las envía al servidor central.

## ✅ Características

- ✔️ **Sin permisos de administrador**: Funciona sin privilegios elevados
- ✔️ **Sin configuración de Firewall**: Conexión directa al servidor
- ✔️ **Modo gráfico**: Interfaz amigable con botón de envío
- ✔️ **Modo automático**: Ejecución silenciosa en segundo plano
- ✔️ **Seguro**: Autenticación por tokens, conexión encriptada

---

## 🚀 Instalación Rápida

### 1️⃣ Descomprimir

Extrae todos los archivos en una carpeta (ej: `C:\Specs\`):

```
SpecsCliente/
├── SpecsCliente.exe          ← Ejecutable principal
├── configurar_cliente.bat    ← Script de configuración
├── _internal/                ← Bibliotecas (NO borrar)
└── config/
    └── server_config.json    ← Configuración del servidor
```

### 2️⃣ Configurar

**Opción A - Script Automático (RECOMENDADO)**:

1. Doble clic en `configurar_cliente.bat`
2. Ingresa la IP del servidor cuando te lo pida
3. Presiona Enter

**Opción B - Manual**:

Edita `config/server_config.json` con un editor de texto:

```json
{
  "server_ip": "10.100.2.152",
  "server_port": 5255,
  "use_discovery": false
}
```

Cambia `10.100.2.152` por la IP de tu servidor.

### 3️⃣ Ejecutar

**Modo Gráfico** (con ventana):
- Doble clic en `SpecsCliente.exe`
- Clic en botón **"Enviar Informe"**
- Esperar confirmación

**Modo Automático** (sin ventana):
```cmd
SpecsCliente.exe --tarea
```

---

## 🔧 Uso Detallado

### Modo Gráfico

1. Ejecutar `SpecsCliente.exe` (doble clic)
2. Ver ventana con información del equipo
3. Clic en **"Enviar Informe"**
4. Esperar mensaje: "✓ Datos enviados correctamente al servidor"
5. Cerrar ventana

### Modo Tarea (Automático)

```cmd
cd C:\Specs\SpecsCliente
SpecsCliente.exe --tarea
```

El cliente:
1. Se conecta al servidor configurado
2. Recopila especificaciones del sistema
3. Envía datos al servidor
4. Cierra automáticamente

**Ideal para**:
- Tareas programadas de Windows
- Scripts de inicio de sesión (GPO)
- Automatización con RMM tools

---

## 📊 Información Recopilada

El cliente recopila las siguientes especificaciones:

### Hardware
- ✔️ Fabricante, modelo, número de serie
- ✔️ Procesador (modelo, cores, frecuencia)
- ✔️ Memoria RAM (módulos, capacidad, velocidad)
- ✔️ Discos duros/SSD (capacidad, uso, modelo)
- ✔️ Tarjeta gráfica (GPU, VRAM, driver)
- ✔️ Interfaces de red (MAC, IP, estado)

### Software
- ✔️ Sistema operativo (versión, build, licencia)
- ✔️ Aplicaciones instaladas (nombre, versión, publisher)
- ✔️ Estado de licencia de Windows

### Red
- ✔️ Dirección IP actual
- ✔️ Dirección MAC
- ✔️ Hostname
- ✔️ Estado de conectividad

---

## 🛠️ Configuración Avanzada

### Archivo `config/server_config.json`

```json
{
  "server_ip": "10.100.2.152",      // IP del servidor
  "server_port": 5255,              // Puerto TCP (5255 por defecto)
  "use_discovery": false,           // false = conexión directa
  "discovery_port": 37020,          // Puerto UDP (solo si use_discovery=true)
  "connection_timeout": 10          // Timeout en segundos
}
```

**Campos explicados**:
- `server_ip`: Dirección IP donde corre el servidor Specs
- `server_port`: Puerto TCP del servidor (por defecto 5255)
- `use_discovery`: **Dejar en `false`** para configuración manual
- `connection_timeout`: Segundos máximos para conectar al servidor

---

## 🔍 Troubleshooting

### Error: "No se puede conectar al servidor"

**Síntomas**: Cliente muestra error de conexión, no envía datos

**Solución**:
1. Verificar que `server_ip` en `config/server_config.json` es correcta
2. Verificar que el servidor está corriendo:
   ```
   Test-NetConnection -ComputerName 10.100.2.152 -Port 5255
   ```
3. Si el test falla, contactar al administrador del servidor

### Error: "Archivo de configuración no encontrado"

**Síntomas**: Cliente dice que falta `server_config.json`

**Solución**:
1. Ejecutar `configurar_cliente.bat`
2. O crear manualmente `config/server_config.json`

### Cliente se congela o no responde

**Síntomas**: Ventana se congela, no cierra

**Solución**:
1. Presionar Ctrl+C si está en modo consola
2. Cerrar desde Task Manager si es necesario
3. Verificar conectividad al servidor (puede estar esperando respuesta)

### Modo tarea no ejecuta

**Síntomas**: `SpecsCliente.exe --tarea` no hace nada visible

**Solución**:
- Es comportamiento normal (ejecuta en segundo plano)
- Verificar en el servidor si llegaron los datos
- Revisar logs del servidor para confirmar recepción

---

## 📅 Automatización

### Tarea Programada de Windows

Para ejecutar el cliente automáticamente cada hora:

1. Abrir **Programador de tareas** (`taskschd.msc`)
2. Crear tarea básica:
   - Nombre: `Inventario Specs`
   - Desencadenador: Diariamente, repetir cada 1 hora
   - Acción: `C:\Specs\SpecsCliente\SpecsCliente.exe --tarea`
   - Iniciar en: `C:\Specs\SpecsCliente\`

3. Configuración adicional:
   - ✔️ Ejecutar aunque el usuario no haya iniciado sesión
   - ✔️ Ocultar mientras se ejecuta
   - ✔️ No detener si se ejecuta más de: 1 hora

### Script de Inicio de Sesión (GPO)

Para ejecutar al iniciar sesión de usuario:

1. Crear GPO en Active Directory
2. Configuración de usuario → Configuración de Windows → Scripts
3. Agregar script:
   ```cmd
   \\servidor\compartido\SpecsCliente\SpecsCliente.exe --tarea
   ```

---

## 🔐 Seguridad y Privacidad

### ¿Qué datos se envían?

- ✅ Especificaciones de hardware (pública, no sensible)
- ✅ Lista de aplicaciones instaladas
- ✅ Información de red (IP, MAC)
- ❌ NO se envían archivos personales
- ❌ NO se envía historial de navegación
- ❌ NO se envían contraseñas ni credenciales

### Autenticación

El cliente utiliza tokens de autenticación basados en secreto compartido:
- Token válido por 5 minutos
- Generado con timestamp actual + secreto compartido
- Servidor valida autenticidad antes de aceptar datos

### Conexión

- Conexión TCP directa (puerto 5255)
- Sin exposición de broadcasts en red
- Comunicación en JSON sobre TCP

---

## 📞 Soporte

### Información del Sistema

Para reportar problemas, incluye:
- Versión de Windows
- Mensaje de error completo
- Contenido de `config/server_config.json`

### Contacto

- **Administrador del servidor**: [Insertar contacto]
- **Departamento de IT**: [Insertar contacto]

---

## 📚 Documentación Adicional

- [README Principal del Proyecto](../README.md)
- [Configuración Sin Permisos de Admin](../NO_ADMIN_SETUP.md)

---

## ℹ️ Información Técnica

### Requisitos

- **Sistema Operativo**: Windows 10/11 (64-bit)
- **Permisos**: Usuario estándar (NO requiere admin)
- **Espacio en disco**: ~120 MB
- **Red**: Conectividad TCP al servidor en puerto 5255

### Tecnología

- Lenguaje: Python 3.13 (compilado con PyInstaller)
- Framework UI: PySide6 (Qt6)
- Bibliotecas: WMI, psutil, windows_tools
- Empaquetado: PyInstaller --onedir

### Versión

- **Cliente**: 1.0.0
- **Protocolo**: JSON sobre TCP
- **Autenticación**: Token-based (5 min expiry)

---

## 📝 Licencia

MIT License - Ver [LICENSE](../LICENSE) para detalles.

Copyright © 2025 Th3GaM3RCaT

---

## 🎓 Notas Finales

Este cliente está diseñado para funcionar en entornos corporativos **sin permisos de administrador**.

La configuración manual por IP ofrece:

- ✅ Simplicidad - Solo requiere editar un archivo JSON
- ✅ Funciona entre diferentes subnets
- ✅ Compatible con VPNs y redes corporativas
- ✅ Compatible con políticas de seguridad corporativas
- ✅ Configuración en 2 minutos

**¡Listo para usar en producción!** 🚀
