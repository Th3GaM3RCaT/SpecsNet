# 📁 Estructura Propuesta para Specs Python

## Estructura Actual vs Nueva

### ❌ Actual (Desordenada)
```
specs-python/
├── specs.py
├── servidor.py
├── all_specs.py
├── logica_specs.py
├── logica_servidor.py
├── logica_Hilo.py
├── mainServidor.py
├── optimized_block_scanner.py
├── test_connectivity.py
├── build_all.ps1
├── sign_executables.ps1
├── create_self_signed_cert.ps1
├── install.ps1
├── README.md
├── DISTRIBUCION.md
├── DISTRIBUCION_RAPIDA.md
├── NETWORK_FLOW.md
├── SECURITY_README.md
├── requirements.txt
├── datos/
├── sql_specs/
├── ui/
└── ... (muchos archivos sueltos)
```

### ✅ Nueva (Organizada)
```
specs-python/
│
├── 📂 src/                          # Código fuente principal
│   ├── specs.py                     # Cliente GUI
│   ├── servidor.py                  # Servidor TCP/UDP
│   ├── all_specs.py                 # Inventario completo
│   │
│   ├── 📂 logica/                   # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── logica_specs.py          # Recolección de datos
│   │   ├── logica_servidor.py       # Servidor networking
│   │   ├── logica_Hilo.py           # Threading helpers
│   │   └── mainServidor.py          # UI servidor
│   │
│   ├── 📂 datos/                    # Módulos de recolección de datos
│   │   ├── __init__.py
│   │   ├── scan_ip_mac.py
│   │   ├── get_ram.py
│   │   ├── informeDirectX.py
│   │   ├── ipAddress.py
│   │   └── serialNumber.py
│   │
│   ├── 📂 sql/                      # Database layer
│   │   ├── __init__.py
│   │   ├── consultas_sql.py
│   │   ├── specs.sql                # Schema
│   │   └── 📂 statement/            # SQL queries
│   │       ├── activo-select.sql
│   │       ├── Dispositivos-select.sql
│   │       └── ...
│   │
│   └── 📂 ui/                       # Interfaces Qt (*.ui + *_ui.py juntos)
│       ├── __init__.py
│       ├── specs_window.ui          # Qt Designer file
│       ├── specs_window_ui.py       # Auto-generado por extensión
│       ├── servidor_specs_window.ui
│       ├── servidor_specs_window_ui.py
│       ├── inventario.ui
│       ├── inventario_ui.py
│       ├── all_specs.ui
│       └── all_specs_ui.py
│
├── 📂 scripts/                      # Scripts de utilidad
│   ├── build_all.ps1                # Compilar con PyInstaller
│   ├── sign_executables.ps1         # Firmar ejecutables
│   ├── create_self_signed_cert.ps1  # Crear certificado testing
│   ├── install.ps1                  # Instalador desde fuente
│   └── optimized_block_scanner.py   # Escáner de red
│
├── 📂 tests/                        # Tests automatizados
│   ├── __init__.py
│   ├── test_connectivity.py         # Tests de conectividad
│   ├── test_database.py             # Tests de BD (futuro)
│   └── test_security.py             # Tests de seguridad (futuro)
│
├── 📂 docs/                         # Documentación
│   ├── README.md                    # Doc principal (link)
│   ├── DISTRIBUCION.md
│   ├── DISTRIBUCION_RAPIDA.md
│   ├── NETWORK_FLOW.md
│   ├── SECURITY_README.md
│   └── 📂 images/                   # Imágenes de docs
│       └── ejemplo nmap.png
│
├── 📂 config/                       # Configuración
│   ├── security_config.py           # Config de seguridad
│   └── security_config.example.py   # Template sin secretos
│
├── 📂 data/                         # Datos de runtime
│   ├── specs.db                     # Base de datos SQLite
│   ├── .gitkeep
│   └── (otros archivos .db, .csv, .json ignorados)
│
├── 📂 build/                        # PyInstaller build (ignorado)
├── 📂 dist/                         # Ejecutables (ignorado)
│
├── .gitignore
├── requirements.txt
├── README.md                        # README principal
└── LICENSE                          # Licencia del proyecto
```

## Beneficios de la Nueva Estructura

### 1. **Separación Clara de Responsabilidades**
- `src/`: Código fuente
- `scripts/`: Herramientas auxiliares
- `tests/`: Tests automatizados
- `docs/`: Documentación
- `config/`: Configuración
- `data/`: Datos runtime

### 2. **Imports Más Claros**
```python
# Antes
from logica_specs import LogicaSpecs
from datos.get_ram import get_ram_info

# Después
from src.logica.logica_specs import LogicaSpecs
from src.datos.get_ram import get_ram_info
```

### 3. **Más Fácil de Navegar**
- Archivos relacionados juntos
- Menos archivos en raíz
- Estructura estándar Python

### 4. **Mejor para PyInstaller**
```powershell
# Paths más claros - .ui y _ui.py en misma carpeta
--add-data "src/sql/statement/*.sql;sql/statement"
--add-data "src/ui/*.ui;ui"
```

### 5. **Git Más Limpio**
```gitignore
# Directorios completos
/build/
/dist/
/data/*.db
/data/*.csv
/config/security_config.py
```

## Plan de Migración

### Fase 1: Crear Estructura (Sin Romper Nada)
1. Crear carpetas nuevas
2. Copiar archivos (no mover todavía)
3. Agregar `__init__.py` en paquetes

### Fase 2: Actualizar Imports
1. Actualizar imports en archivos principales
2. Actualizar imports en módulos
3. Probar que todo funciona

### Fase 3: Limpiar
1. Mover archivos a nueva estructura
2. Eliminar duplicados
3. Actualizar PyInstaller specs

### Fase 4: Actualizar Scripts
1. Actualizar `build_all.ps1`
2. Actualizar `install.ps1`
3. Actualizar tests

## ¿Proceder con la Reorganización?

La reorganización tomará varios pasos pero el resultado será:
- ✅ Más profesional
- ✅ Más fácil de mantener
- ✅ Más fácil de contribuir (si es open source)
- ✅ Mejor para distribución

**Nota**: Haré la migración gradualmente para no romper nada.
