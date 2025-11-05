# Sistema de Inventario de Hardware en Red# Sistema de Inventario de Hardware en Red



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)



Sistema cliente-servidor para Windows que recopila especificaciones de hardware/software de equipos en red. **Filosofía: "Ejecutar y olvidarse"** - interfaz simple con 2 botones y modo tarea automático.Sistema cliente-servidor para Windows que recopila especificaciones de hardware/software de equipos en red. **Filosofía: "Ejecutar y olvidarse"** - interfaz simple con 2 botones y modo tarea automático.



------



## Inicio Rápido## Inicio Rápido



### Instalación### Instalación

```bash```bash

pip install -r requirements.txtpip install -r requirements.txt

``````



### Ejecución### Ejecución



**Cliente:****Cliente:**

```bash```bash

python run_cliente.py              # Modo GUI (2 botones: Enviar/Cancelar)python run_cliente.py              # Modo GUI (2 botones: Enviar/Cancelar)

python src/specs.py --tarea        # Modo tarea silencioso (auto-envío)python src/specs.py --tarea        # Modo tarea silencioso (auto-envío)

``````



**Servidor:****Servidor:**

```bash```bash

python run_servidor.py             # Servidor TCP + UI gestiónpython run_servidor.py             # Servidor TCP + UI gestión

``````



**Inventario:****Inventario:**

```bash```bash

python src/all_specs.py            # Ver todos los dispositivospython src/all_specs.py            # Ver todos los dispositivos

``````



------



## Arquitectura## Estructura del Proyecto



### 1. Cliente (`src/specs.py`)```

- **Modo GUI**: Ventana simple con 2 botones (Enviar/Cancelar)specs-python/

- **Modo Tarea**: `--tarea` flag para ejecución silenciosa automática│

- **Discovery**: Escucha broadcasts UDP del servidor (puerto 37020)├── run_cliente.py                   # Ejecutar cliente

- **Recolección**: Usa WMI, psutil, dxdiag para obtener specs completas├── run_servidor.py                  # Ejecutar servidor

- **Envío**: JSON vía TCP (puerto 5255) al servidor├── requirements.txt                 # Dependencias

├── specs.db                         # Base de datos SQLite

### 2. Servidor (`src/servidor.py`)│

- **TCP Server**: Puerto 5255 - recibe datos de clientes├── src/

- **UDP Broadcast**: Anuncia IP en 255.255.255.255:37020│   ├── specs.py                     # Cliente (entry point)

- **Almacenamiento**: SQLite (`specs.db`)│   ├── servidor.py                  # Servidor (entry point)

- **UI Gestión**: `mainServidor.py` - visualiza dispositivos con estado en tiempo real│   ├── all_specs.py                 # Inventario (entry point)

│   ├── mainServidor.py              # UI servidor

### 3. Monitoreo Inteligente│   │

- **Monitor de Tendencias**: Alertas basadas en 3 consultas consecutivas│   ├── logica/                      # Lógica de negocio

  - RAM > 74%, CPU > 74%, Disco > 85%│   │   ├── logica_specs.py          # Recolección datos sistema

  - Se resetea automáticamente cuando baja del umbral│   │   ├── logica_servidor.py       # Servidor TCP

  - Ver `src/logica/INTEGRACION_MONITOR_TENDENCIAS.py` para integrar│   │   ├── monitor_tendencias.py    # Alertas inteligentes

- **Detector de Spoofing**: Query SQL para detectar MACs duplicadas│   │   ├── detector_spoofing_simple.py

- **Agente de Verificación**: Escaneo ARP local sin pings activos│   │   └── agente_verificacion.py

│   │

### 4. Escaneo de Red│   ├── datos/                       # Módulos recolección

- **Segmentos**: 10.100.0.0/16 a 10.119.0.0/16│   │   ├── serialNumber.py          # Serial BIOS

- **Métodos**: SSDP/mDNS probes + ping-sweep asíncrono│   │   ├── get_ram.py               # Info RAM

- **Batch Size**: 50 dispositivos paralelos (evita saturación)│   │   ├── informeDirectX.py        # Info GPU (dxdiag)

- **Output**: CSV con formato `optimized_scan_YYYYMMDD_HHMMSS.csv`│   │   └── scan_ip_mac.py           # Escaneo red

│   │

---│   ├── ui/                          # Interfaces Qt Designer

│   │   ├── specs_window.ui          # UI cliente

## Estructura del Proyecto│   │   ├── servidor_specs_window.ui # UI servidor

│   │   └── inventario.ui            # UI inventario

```│   │   ├── logica_servidor.py       # Servidor TCP/UDP + procesamiento

specs-python/│   │   ├── logica_Hilo.py           # Threading helpers (Hilo, HiloConProgreso)

││   │   └── mainServidor.py          # UI principal del servidor

├── run_cliente.py                   # Ejecutar cliente│   │

├── run_servidor.py                  # Ejecutar servidor│   ├── 📂 datos/                    # Módulos de recolección de datos

├── requirements.txt                 # Dependencias│   │   ├── scan_ip_mac.py           # Escaneo de red + resolución MAC

├── specs.db                         # Base de datos SQLite│   │   ├── get_ram.py               # Información de módulos RAM

││   │   ├── informeDirectX.py        # Parseo de dxdiag

├── src/│   │   ├── ipAddress.py             # Detección de IP local

│   ├── specs.py                     # Cliente (entry point)│   │   └── serialNumber.py          # Número de serie del equipo

│   ├── servidor.py                  # Servidor (entry point)│   │

│   ├── all_specs.py                 # Inventario (entry point)│   ├── 📂 sql/                      # Capa de base de datos

│   ├── mainServidor.py              # UI servidor│   │   ├── consultas_sql.py         # Funciones de acceso a DB

│   ││   │   ├── specs.sql                # Schema de la base de datos

│   ├── logica/                      # Lógica de negocio│   │   └── 📂 statement/            # Queries SQL parametrizadas

│   │   ├── logica_specs.py          # Recolección datos sistema│   │       ├── Dispositivos-select.sql

│   │   ├── logica_servidor.py       # Servidor TCP│   │       ├── activo-select.sql

│   │   ├── logica_Hilo.py           # Threading helpers│   │       └── ... (otros queries)

│   │   ├── monitor_tendencias.py    # Alertas inteligentes│   │

│   │   ├── detector_spoofing_simple.py│   └── 📂 ui/                       # Interfaces Qt Designer

│   │   ├── agente_verificacion.py│       ├── specs_window.ui          # Diseño cliente

│   │   └── INTEGRACION_MONITOR_TENDENCIAS.py  # Guía integración│       ├── specs_window_ui.py       # Auto-generado por extensión

│   ││       ├── servidor_specs_window.ui

│   ├── datos/                       # Módulos recolección│       ├── servidor_specs_window_ui.py

│   │   ├── serialNumber.py          # Serial BIOS│       ├── inventario.ui

│   │   ├── get_ram.py               # Info RAM│       ├── inventario_ui.py

│   │   ├── informeDirectX.py        # Info GPU (dxdiag)│       ├── all_specs.ui

│   │   ├── ipAddress.py             # IP local│       └── all_specs_ui.py

│   │   └── scan_ip_mac.py           # Escaneo red│

│   │├── 📂 scripts/                      # Scripts de utilidad

│   ├── sql_specs/                   # Capa base de datos│   ├── build_all.ps1                # Compilar con PyInstaller

│   │   ├── consultas_sql.py         # Funciones acceso DB│   ├── sign_executables.ps1         # Firmar ejecutables

│   │   ├── specs.sql                # Schema SQLite│   ├── create_self_signed_cert.ps1  # Crear certificado para testing

│   │   └── statement/               # Queries SQL parametrizadas│   ├── install.ps1                  # Instalador desde código fuente

│   ││   └── optimized_block_scanner.py   # Escáner masivo de red

│   └── ui/                          # Interfaces Qt Designer│

│       ├── specs_window.ui          # UI cliente├── 📂 tests/                        # Tests automatizados

│       ├── servidor_specs_window.ui # UI servidor│   └── test_connectivity.py         # Tests de conectividad cliente-servidor

│       └── inventario.ui            # UI inventario│

│├── 📂 docs/                         # Documentación

├── scripts/                         # Scripts build/deploy│   ├── DISTRIBUCION.md              # Guía completa de distribución

│   ├── build_cliente.ps1            # Compilar cliente│   ├── DISTRIBUCION_RAPIDA.md       # Guía rápida

│   ├── build_servidor.ps1           # Compilar servidor│   ├── NETWORK_FLOW.md              # Arquitectura de red

│   └── install.ps1                  # Instalación dependencias│   ├── SECURITY_README.md           # Configuración de seguridad

││   └── REORGANIZACION.md            # Historial de reorganización

├── config/                          # Configuración│

├── data/                            # Datos temporales├── 📂 config/                       # Configuración

├── output/                          # Archivos salida (CSVs, logs)│   └── security_config.example.py   # Template de configuración de seguridad

└── dist/                            # Ejecutables compilados│

```├── 📂 data/                         # Datos de runtime (ignorado por Git)

│   ├── specs.db                     # Base de datos SQLite

---│   └── .gitkeep

│

## Flujo de Datos├── requirements.txt                 # Dependencias Python

├── .gitignore                       # Archivos ignorados por Git

1. **Servidor Broadcast**: Anuncia IP via UDP → `255.255.255.255:37020`└── README.md                        # Este archivo

2. **Cliente Discovery**: Escucha puerto 37020, detecta IP servidor```

3. **Cliente Recolecta**: Ejecuta `informe()` → specs completas (WMI, psutil, dxdiag)

4. **Cliente Envía**: TCP connect `<IP_SERVIDOR>:5255`, envía JSON## 🚀 Inicio Rápido

5. **Servidor Persiste**: Guarda en SQLite `specs.db`

6. **Monitor Verifica**: `monitor_tendencias.py` analiza RAM/CPU/Disco### Instalación

7. **UI Actualiza**: `mainServidor.py` muestra estado con ping paralelo (batches de 50)

```powershell

---# Clonar repositorio

git clone https://github.com/Th3GaM3RCaT/specs-python.git

## Compilación (PyInstaller)cd specs-python



### Cliente# Ejecutar instalador automático

```bash.\scripts\install.ps1

cd scripts```

.\build_cliente.ps1

```### Ejecución

Genera: `dist/SpecsCliente/SpecsCliente.exe`

```powershell

### Servidor# Iniciar servidor

```bashpython src/servidor.py

cd scripts

.\build_servidor.ps1# Iniciar cliente (GUI)

```python src/specs.py

Genera: `dist/SpecsServidor/SpecsServidor.exe`

# Iniciar cliente (modo tarea)

**Importante**: Incluir `--add-data` para archivos SQL:python src/specs.py --tarea

```bash```

pyinstaller --onedir --noconsole servidor.py \

    --add-data "sql_specs/statement/*.sql;sql_specs/statement"## Arquitectura del Sistema

```

### 1. **Cliente (`src/specs.py`)**

---Aplicación que se ejecuta en cada equipo de la red para recopilar y enviar información.



## Configuración de Puertos#### Modos de Ejecución:

- **Modo GUI** (por defecto): `python specs.py`

| Servicio | Puerto | Protocolo | Uso |  - Interfaz gráfica para ejecutar manualmente el informe

|----------|--------|-----------|-----|  - Botón para enviar datos al servidor

| Discovery | 37020 | UDP | Broadcast servidor |  

| Datos | 5255 | TCP | Envío specs cliente → servidor |- **Modo Tarea**: `python specs.py --tarea`

  - Se ejecuta en segundo plano

---  - Escucha broadcasts del servidor en puerto `37020`

  - Responde automáticamente enviando sus datos

## Dependencias Principales

#### Datos Recopilados:

- **PySide6**: UI Qt (ventanas, tablas)- **Hardware**: Serial, Modelo, Procesador, GPU, RAM, Disco

- **WMI**: Info hardware Windows- **Sistema**: Nombre del equipo, Usuario, MAC Address, IP

- **psutil**: Stats sistema (CPU, RAM, disco)- **Software**: Aplicaciones instaladas, Estado de licencia Windows

- **windows-tools**: Software instalado, servicios- **Diagnóstico**: Reporte DirectX completo (dxdiag)

- **getmac**: Dirección MAC

- **pywin32**: Integración Windows (dxdiag, registro)### 2. **Servidor (`servidor.py` + `logica_servidor.py`)**

Aplicación central que recibe datos de clientes y los almacena en la base de datos.

Ver `requirements.txt` para lista completa.

#### Componentes:

---- **Servidor TCP** (puerto `5255`): Recibe JSON de clientes

- **Broadcast UDP** (puerto `37020`): Anuncia presencia en la red

## Base de Datos (SQLite)- **Base de Datos**: SQLite (`specs.db`)

- **Procesamiento**: Parsea JSON y DirectX, guarda en tablas normalizadas

### Tablas Principales

- `Dispositivos`: Info general (serial, nombre, IP, MAC)#### Tablas de la Base de Datos:

- `almacenamiento`: Discos duros- `Dispositivos`: Información principal del equipo

- `aplicaciones`: Software instalado- `activo`: Historial de estados (encendido/apagado)

- `memoria`: Módulos RAM- `memoria`: Módulos RAM individuales

- `activo`: Estado ping (1 registro por dispositivo)- `almacenamiento`: Discos y particiones

- `tendencias_recursos`: Histórico para alertas inteligentes- `aplicaciones`: Software instalado

- `informacion_diagnostico`: Reportes completos (JSON + DirectX)

### Pattern DELETE + INSERT- `registro_cambios`: Historial de modificaciones de hardware

```python

# Tabla activo: mantener 1 registro por dispositivo### 3. **Interfaz de Gestión (`mainServidor.py`)**

cursor.execute("DELETE FROM activo WHERE Dispositivos_serial = ?", (serial,))UI para visualizar y administrar el inventario de dispositivos.

cursor.execute("INSERT INTO activo (Dispositivos_serial, powerOn, date) VALUES (?, ?, ?)", ...)

```#### Características:

- **Tabla de Dispositivos**: Muestra todos los equipos registrados

---  - Estado (Encendido/Apagado/Inactivo)

  - DTI, Serial, Usuario, Modelo

## Seguridad (Opcional)  - Procesador, GPU, RAM, Disco

  - Estado de licencia, IP

Si existe `security_config.py`:  

- **Autenticación**: Token compartido válido por 5 minutos- **Filtros y Búsqueda**:

- **Whitelist IP**: Subnets `10.100.0.0/16` - `10.119.0.0/16`  - Buscar por cualquier campo

- **Rate Limiting**: Max 3 conexiones por IP  - Filtrar por: Activos, Inactivos, Encendidos, Apagados, Sin Licencia

- **Buffer Limit**: 10 MB por mensaje  

- **Detalles por Dispositivo**:

---  - Diagnóstico completo

  - Aplicaciones instaladas

## Threading Pattern  - Detalles de almacenamiento

  - Módulos de memoria RAM

```python  - Historial de cambios

from logica.logica_Hilo import Hilo, HiloConProgreso

### 4. **Escaneo de Red (`optimized_block_scanner.py`)**

# Operaciones simples bloqueantes:Descubre dispositivos en la red para consultar su información.

hilo = Hilo(funcion_pesada, arg1, arg2)

hilo.terminado.connect(callback_exito)#### Funcionalidad:

hilo.error.connect(callback_error)- Escanea rangos `10.100.0.0/16` a `10.119.0.0/16`

hilo.start()- Usa probes SSDP/mDNS + ping-sweep asíncrono

- Parsea tabla ARP para asociar IP ↔ MAC

# Operaciones con progreso en tiempo real:- Genera CSV: `optimized_scan_YYYYMMDD_HHMMSS.csv`

hilo = HiloConProgreso(funcion_con_callback, arg1)

hilo.progreso.connect(callback_progreso)  # Actualizaciones en vivo## Flujo de Trabajo Completo

hilo.terminado.connect(callback_exito)

hilo.start()### Instalación Inicial

```

1. **Servidor**:

**Razón**: Evita freeze de UI. `HiloConProgreso` permite emisión de progreso durante ejecución (ej: ping masivo de 386 dispositivos).   ```bash

   # Crear base de datos

---   sqlite3 specs.db < sql_specs/specs.sql

   

## Troubleshooting   # Ejecutar servidor

   python servidor.py

### Cliente no encuentra servidor   ```

- Verificar que servidor esté ejecutándose

- Verificar firewall permite UDP puerto 370202. **Clientes**:

- Verificar ambos en misma LAN/subnet   ```bash

   # Modo manual

### Error encoding (UnicodeEncodeError)   python specs.py

- **NUNCA usar emojis en código Python** (Windows usa cp1252)   

- Usar solo ASCII estándar: `[OK]`, `[ERROR]`, `*`, `+`, `-`   # Modo automático (tarea programada)

   python specs.py --tarea

### Tabla `activo` con duplicados   ```

- Verificar pattern DELETE + INSERT se usa correctamente

- Solo 1 registro por dispositivo (serial como key)### Proceso de Recopilación de Datos



### Ping masivo lento```

- Aumentar `batch_size` en `consultar_dispositivos_desde_csv()`1. SERVIDOR anuncia su presencia

- Usar `asyncio` con batches de 50 (default correcto)   └─> Broadcast UDP: "servidor specs" → 255.255.255.255:37020



---2. CLIENTE detecta servidor

   └─> Escucha puerto 37020, extrae IP del sender

## Licencia

3. CLIENTE recopila información

MIT License - Ver `LICENSE` para detalles   ├─> WMI: Serial, Modelo, Procesador, RAM

   ├─> psutil: CPU, Memoria, Disco, Red

---   ├─> dxdiag: GPU y diagnóstico completo

   ├─> windows_tools: Aplicaciones instaladas

## Notas   └─> slmgr: Estado de licencia Windows



- **Status Migración**: SQLite es única fuente de verdad (JSON deprecados)4. CLIENTE envía datos al servidor

- **Grupo de Usuarios**: ~300 clientes, 2-3 administradores servidor   └─> TCP connect a SERVIDOR:5255, envía JSON completo

- **Filosofía**: Simple, ejecutar y olvidarse

- **Código Auto-documentado**: Comentarios inline suficientes5. SERVIDOR procesa y almacena

- **Sin Auditorías Extensas**: App pequeña, uso interno   ├─> Parsea JSON + DirectX

   ├─> Extrae datos según esquema de DB
   ├─> Inserta/actualiza en tablas:
   │   ├─ Dispositivos (info principal)
   │   ├─ activo (estado encendido/apagado)
   │   ├─ memoria (módulos RAM)
   │   ├─ almacenamiento (discos)
   │   ├─ aplicaciones (software)
   │   └─ informacion_diagnostico (reportes completos)
   └─> Commit a SQLite

6. INTERFAZ muestra datos actualizados
   └─> Consulta DB y presenta en tabla con colores
```

### Escaneo y Descubrimiento Masivo

```
1. EJECUTAR ESCANEO
   └─> python optimized_block_scanner.py --start 100 --end 119

2. GENERAR CSV
   └─> optimized_scan_20251030_HHMMSS.csv
       ├─ IP,MAC
       ├─ 10.100.2.101,bc:ee:7b:74:d5:b0
       └─ ...

3. SERVIDOR CARGA CSV
   └─> ls.cargar_ips_desde_csv()

4. SERVIDOR CONSULTA CADA IP
   ├─> Ping para verificar si está activo
   ├─> Anuncia presencia (broadcast)
   ├─> Espera que cliente se conecte
   └─> Actualiza estado en DB

5. MONITOREO PERIÓDICO
   └─> ls.monitorear_dispositivos_periodicamente(intervalo_minutos=15)
       ├─ Ping a todos los dispositivos
       ├─ Actualiza campo "activo" en DB
       └─ Repite cada N minutos
```

## Mapeo de Datos JSON → Base de Datos

### Tabla `Dispositivos`

| Campo DB | Fuente | Ubicación en JSON/DirectX |
|----------|--------|---------------------------|
| `serial` | JSON | `SerialNumber` |
| `DTI` | Manual | - (se asigna manualmente) |
| `user` | JSON | `Name` |
| `MAC` | JSON | `MAC Address` |
| `model` | JSON | `Model` |
| `processor` | DirectX | `Processor:` |
| `GPU` | DirectX | `Card name:` |
| `RAM` | JSON | Suma de `Capacidad_GB` de módulos |
| `disk` | DirectX | `Drive:`, `Model:`, `Total Space:` |
| `license_status` | JSON | `License status` |
| `ip` | JSON | `client_ip` |
| `activo` | Calculado | `True` si envía datos |

### Tabla `memoria`

Extrae módulos RAM del JSON donde hay claves como:
```json
"--- Módulo RAM 1 ---": "",
"Fabricante": "Micron",
"Número_de_Serie": "18573571",
"Capacidad_GB": 4.0,
"Velocidad_MHz": 2400,
"Etiqueta": "Physical Memory 1"
```

### Tabla `aplicaciones`

Extrae del JSON donde:
```json
"Microsoft Office Standard 2016": ["16.0.4266.1001", "Microsoft Corporation"]
```
- `name`: Clave (nombre de la app)
- `version`: Primer elemento del array
- `publisher`: Segundo elemento del array

## Funciones Principales

### `logica_servidor.py`

| Función | Descripción |
|---------|-------------|
| `parsear_datos_dispositivo(json_data)` | Extrae campos de JSON/DirectX para tabla Dispositivos |
| `parsear_modulos_ram(json_data)` | Extrae módulos RAM para tabla memoria |
| `parsear_almacenamiento(json_data)` | Extrae discos para tabla almacenamiento |
| `parsear_aplicaciones(json_data)` | Extrae apps para tabla aplicaciones |
| `consultar_informacion(conn, addr)` | Recibe datos del cliente y guarda en DB |
| `cargar_ips_desde_csv(archivo_csv)` | Lee CSV de escaneo y retorna lista de IPs |
| `solicitar_datos_a_cliente(ip)` | Hace ping y solicita datos a un cliente |
| `consultar_dispositivos_desde_csv()` | Consulta todos los dispositivos del CSV |
| `monitorear_dispositivos_periodicamente()` | Monitorea estados cada N minutos |
| `main()` | Inicia servidor TCP y acepta conexiones |

### `logica_specs.py` (Cliente)

| Función | Descripción |
|---------|-------------|
| `informe()` | Recopila todas las specs del equipo |
| `enviar_a_servidor()` | Descubre servidor y envía JSON |
| `get_license_status()` | Consulta licencia Windows vía slmgr.vbs |
| `configurar_tarea(valor)` | Registra/desregistra tarea en Registry |

### `mainServidor.py` (UI)

| Función | Descripción |
|---------|-------------|
| `iniciar_servidor()` | Inicia servidor TCP en segundo plano |
| `cargar_dispositivos()` | Consulta DB y llena tabla |
| `escanear_red()` | Ejecuta optimized_block_scanner.py |
| `consultar_dispositivos_csv()` | Consulta dispositivos del CSV |
| `on_dispositivo_seleccionado()` | Carga detalles al seleccionar fila |

## Compilación (PyInstaller)

### Opción 1: Usando Scripts Automatizados (Recomendado)

```powershell
# Compilar Cliente
.\scripts\build_cliente.ps1

# Compilar Servidor
.\scripts\build_servidor.ps1
```

**Nota**: Si PowerShell bloquea la ejecución de scripts, ejecuta una vez:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Opción 2: Comando Manual

#### Cliente:
```powershell
pyinstaller --onedir --noconsole --name "SpecsCliente" --add-data "src/ui/*.ui;ui" --hidden-import=wmi --hidden-import=psutil --hidden-import=getmac --hidden-import=windows_tools.installed_software --paths=src src/specs.py
```

#### Servidor:
```powershell
pyinstaller --onedir --noconsole --name "SpecsServidor" --add-data "src/sql/statement/*.sql;sql/statement" --add-data "src/ui/*.ui;ui" --hidden-import=wmi --hidden-import=psutil --paths=src src/servidor.py
```

### Resultado

Los ejecutables se generan en:
- **Cliente**: `dist/SpecsCliente/SpecsCliente.exe`
- **Servidor**: `dist/SpecsServidor/SpecsServidor.exe`

Para distribuir, comprime las carpetas completas:
- `dist/SpecsCliente/` → `SpecsCliente.zip`
- `dist/SpecsServidor/` → `SpecsServidor.zip`

### Notas de Compilación

- **`--paths=src`**: ⚠️ **CRÍTICO** - Agrega directorio `src/` al Python path para resolver imports (`from logica.xxx`). Sin esto, PyInstaller no puede encontrar los módulos.
- **`--add-data`**: Incluye archivos no-Python necesarios en runtime (archivos `.ui`, `.sql`)
- **`--onedir`**: Genera un directorio con el .exe y todas las dependencias (inicio rápido, ~5-10x más rápido que `--onefile`)
- **`--noconsole`**: No muestra ventana de consola (solo GUI)
- **`--hidden-import`**: Fuerza la inclusión de módulos que PyInstaller no detecta automáticamente

### ¿Por qué `--onedir` en lugar de `--onefile`?

| Característica | `--onefile` | `--onedir` |
|----------------|-------------|------------|
| Velocidad de inicio | ❌ Lento (5-15 seg) | ✅ Rápido (<1 seg) |
| Distribución | ✅ Un solo .exe | ❌ Carpeta completa |
| Tamaño | ~47 MB | ~60 MB (carpeta) |
| Debugging | ❌ Difícil | ✅ Fácil (archivos visibles) |

**Recomendación**: Usar `--onedir` para aplicaciones que se ejecutan frecuentemente (como este cliente/servidor).

### Debugging

Si el ejecutable falla al iniciar, usa `--console` para ver errores:

```powershell
pyinstaller --onedir --console --name "SpecsCliente_Debug" --paths=src src/specs.py
```

Esto mostrará la ventana de consola con los errores de Python.

## Configuración de Puertos

| Puerto | Protocolo | Uso |
|--------|-----------|-----|
| `5255` | TCP | Recepción de datos de clientes |
| `37020` | UDP | Broadcast de descubrimiento |

**Importante**: Firewall debe permitir estos puertos.

## Dependencias

```
PySide6         # UI Qt
wmi             # Windows Management Instrumentation
psutil          # System info cross-platform
getmac          # Obtener MAC address
windows_tools   # Aplicaciones instaladas
sqlite3         # Base de datos (incluido en Python)
```

## Notas de Implementación

### Encoding
- **DirectX output** (`dxdiag_output.txt`): `cp1252` (Windows-1252)
- **JSON**: `utf-8`
- **CSV**: `utf-8`

### Threading
- Usar `logica_Hilo.Hilo` para operaciones bloqueantes
- Evita freeze de UI en operaciones de red/DB/WMI

### Broadcast Limitations
- Solo funciona en misma LAN/subnet
- Routers pueden bloquear broadcasts a `255.255.255.255`
- Considerar multicast o discovery protocol más robusto

## Mejoras Futuras

1. **Autenticación**: Tokens o certificados para clientes
2. **Encriptación**: TLS/SSL para comunicación TCP
3. **Discovery Robusto**: mDNS/Zeroconf en lugar de broadcasts
4. **API REST**: Para integración con otros sistemas
5. **Mapa de Red**: Visualización con NetworkX/Graphviz
6. **Alertas**: Notificaciones cuando dispositivos caen
7. **Reportes**: Exportar a Excel, PDF
8. **Multi-servidor**: Replicación y alta disponibilidad

## Troubleshooting

### Cliente no encuentra servidor
- Verificar firewall (puerto 37020 UDP)
- Confirmar que están en la misma subnet
- Ejecutar cliente en modo `--tarea` para escuchar broadcasts

### Servidor no recibe datos
- Verificar puerto 5255 TCP abierto
- Ver logs en consola del servidor
- Confirmar que `specs.db` existe y tiene permisos de escritura

### Errores de encoding en DirectX
- Asegurar que `dxdiag_output.txt` se lee con `encoding='cp1252'`

### DB locked error
- Solo una instancia del servidor debe acceder a `specs.db`
- Cerrar conexiones después de commits
- Usar `connection.commit()` después de escrituras

## Contacto y Soporte

Para reportar bugs o solicitar features, crear issue en el repositorio.

---

## 📄 Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).

**En resumen:**
- ✅ Uso comercial permitido
- ✅ Modificación permitida
- ✅ Distribución permitida
- ✅ Uso privado permitido
- ℹ️ Requiere incluir el aviso de copyright y licencia

Para más detalles, consulta el archivo [LICENSE](LICENSE).
