# 📦 Guía de Distribución - Specs Python

## Tabla de Contenidos
1. [Compilación con PyInstaller](#compilación-con-pyinstaller)
2. [Evitar advertencias de Windows](#evitar-advertencias-de-windows)
3. [Firma Digital](#firma-digital)
4. [Empaquetado Profesional](#empaquetado-profesional)
5. [Distribución Corporativa](#distribución-corporativa)

---

## 🔨 Compilación con PyInstaller

### Compilar Servidor

```powershell
pyinstaller --onedir --noconsole servidor.py `
    --add-data "sql_specs/statement/*.sql;sql_specs/statement" `
    --add-data "ui/*.ui;ui" `
    --name "SpecsServidor" `
    --icon "icon.ico"
```

### Compilar Cliente

```powershell
pyinstaller --onedir --noconsole specs.py `
    --add-data "ui/*.ui;ui" `
    --name "SpecsCliente" `
    --icon "icon.ico"
```

### Compilar Inventario

```powershell
pyinstaller --onedir --noconsole all_specs.py `
    --add-data "ui/*.ui;ui" `
    --name "SpecsInventario" `
    --icon "icon.ico"
```

### Opciones de PyInstaller

| Opción | Descripción |
|--------|-------------|
| `--onedir` | Crea directorio con ejecutable y dependencias (recomendado) |
| `--onefile` | Crea ejecutable único (más lento al iniciar) |
| `--noconsole` | Sin ventana de consola (solo GUI) |
| `--console` | Con ventana de consola (útil para debugging) |
| `--add-data` | Incluir archivos adicionales (SQL, UI, etc.) |
| `--icon` | Ícono del ejecutable (.ico) |
| `--name` | Nombre del ejecutable |
| `--hidden-import` | Importaciones que PyInstaller no detecta |

---

## 🛡️ Evitar Advertencias de Windows SmartScreen

### ❌ El Problema

Windows Defender SmartScreen muestra esta advertencia para ejecutables no firmados:

```
Windows protegió su PC
Microsoft Defender SmartScreen evitó el inicio de una aplicación no reconocida.
```

### ✅ Soluciones

#### **Opción 1: Firma Digital (RECOMENDADA)**

**Certificado Standard Code Signing** (~$150-500/año):
- Firma tu ejecutable con certificado válido
- Windows acepta el ejecutable después de construir "reputación"
- Proceso puede tomar semanas/meses

**Certificado EV Code Signing** (~$400-600/año):
- ✅ **Reputación inmediata** - NO hay advertencias desde día 1
- Requiere USB hardware token (mayor seguridad)
- Validación extendida de identidad empresarial

**Proveedores recomendados**:
- **DigiCert**: https://www.digicert.com/signing/code-signing-certificates
- **Sectigo**: https://sectigo.com/ssl-certificates-tls/code-signing
- **SSL.com**: https://www.ssl.com/certificates/code-signing/
- **Certum**: https://en.sklep.certum.pl/ (más económico para Europa)

#### **Opción 2: Certificado Auto-firmado (SOLO testing)**

⚠️ **NO elimina advertencias**, pero permite testing interno:

```powershell
# 1. Crear certificado (ejecutar como Administrador)
$cert = New-SelfSignedCertificate `
    -Subject "CN=Tu Empresa, O=Tu Empresa, C=ES" `
    -Type CodeSigningCert `
    -CertStoreLocation Cert:\CurrentUser\My `
    -NotAfter (Get-Date).AddYears(5)

# 2. Exportar certificado
$password = ConvertTo-SecureString -String "TuPassword123" -Force -AsPlainText
$certPath = "C:\certs\MiCertificado.pfx"
Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $password

# 3. Instalar Windows SDK (contiene signtool.exe)
# Descargar de: https://developer.microsoft.com/windows/downloads/windows-sdk/

# 4. Firmar ejecutable
$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"
& $signtool sign `
    /f $certPath `
    /p "TuPassword123" `
    /fd SHA256 `
    /tr http://timestamp.digicert.com `
    /td SHA256 `
    "dist\SpecsServidor\SpecsServidor.exe"
```

**Verificar firma**:
```powershell
& $signtool verify /pa "dist\SpecsServidor\SpecsServidor.exe"
```

#### **Opción 3: Script de Firma Automatizado**

Crear `sign_exe.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$ExePath,
    
    [Parameter(Mandatory=$true)]
    [string]$CertPath,
    
    [Parameter(Mandatory=$true)]
    [string]$Password
)

$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"

if (-not (Test-Path $signtool)) {
    Write-Error "signtool.exe no encontrado. Instalar Windows SDK."
    exit 1
}

if (-not (Test-Path $ExePath)) {
    Write-Error "Ejecutable no encontrado: $ExePath"
    exit 1
}

Write-Host "🔏 Firmando: $ExePath" -ForegroundColor Cyan

& $signtool sign `
    /f $CertPath `
    /p $Password `
    /fd SHA256 `
    /tr http://timestamp.digicert.com `
    /td SHA256 `
    /v `
    $ExePath

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Firma exitosa" -ForegroundColor Green
    
    # Verificar firma
    & $signtool verify /pa $ExePath
} else {
    Write-Error "❌ Error al firmar ejecutable"
    exit 1
}
```

**Uso**:
```powershell
.\sign_exe.ps1 -ExePath "dist\SpecsServidor\SpecsServidor.exe" `
               -CertPath "C:\certs\MiCertificado.pfx" `
               -Password "TuPassword123"
```

---

## 📦 Empaquetado Profesional

### Opción 1: Inno Setup (GRATIS, recomendado)

**Descargar**: https://jrsoftware.org/isinfo.php

**Script `specs_installer.iss`**:

```ini
[Setup]
AppName=Specs Python
AppVersion=1.0
DefaultDirName={autopf}\SpecsPython
DefaultGroupName=Specs Python
OutputDir=installers
OutputBaseFilename=SpecsPython_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\SpecsServidor.exe

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en escritorio"; GroupDescription: "Iconos adicionales:"

[Files]
Source: "dist\SpecsServidor\*"; DestDir: "{app}\Servidor"; Flags: ignoreversion recursesubdirs
Source: "dist\SpecsCliente\*"; DestDir: "{app}\Cliente"; Flags: ignoreversion recursesubdirs
Source: "sql_specs\specs.sql"; DestDir: "{app}\sql_specs"; Flags: ignoreversion
Source: "security_config.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Specs Servidor"; Filename: "{app}\Servidor\SpecsServidor.exe"
Name: "{group}\Specs Cliente"; Filename: "{app}\Cliente\SpecsCliente.exe"
Name: "{commondesktop}\Specs Servidor"; Filename: "{app}\Servidor\SpecsServidor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Servidor\SpecsServidor.exe"; Description: "Ejecutar Specs Servidor"; Flags: nowait postinstall skipifsilent
```

**Compilar instalador**:
```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" specs_installer.iss
```

### Opción 2: NSIS (Nullsoft Scriptable Install System)

**Descargar**: https://nsis.sourceforge.io/

### Opción 3: WiX Toolset (formato MSI)

**Descargar**: https://wixtoolset.org/

---

## 🏢 Distribución Corporativa

### Método 1: Group Policy (Active Directory)

Para despliegue en dominio Windows:

1. **Firmar ejecutable** con certificado corporativo
2. **Crear MSI** con WiX Toolset
3. **Desplegar vía GPO**:
   - Computer Configuration → Software Settings → Software Installation
   - Asignar o publicar aplicación

### Método 2: Microsoft Intune

Para gestión moderna de dispositivos:

1. Empaquetar como `.intunewin`
2. Subir a Intune Portal
3. Asignar a grupos de dispositivos

### Método 3: SCCM/Configuration Manager

Para grandes empresas:

1. Crear paquete SCCM
2. Distribuir a distribution points
3. Desplegar a colecciones de dispositivos

### Método 4: Repositorio Interno

Para distribución manual controlada:

```powershell
# Servidor de archivos SMB
\\server\software\SpecsPython\
    ├── SpecsServidor\
    ├── SpecsCliente\
    ├── install.ps1
    └── README.txt
```

---

## 🔒 Buenas Prácticas de Seguridad

### 1. Proteger security_config.py

**NUNCA** incluir `security_config.py` en el instalador público:

```powershell
# Generar security_config.py en cada instalación
# Ver install.ps1 para script de generación automática
```

### 2. Ofuscar código (opcional)

```powershell
pip install pyarmor

# Ofuscar scripts
pyarmor obfuscate servidor.py
pyarmor obfuscate specs.py

# Compilar versión ofuscada
pyinstaller --onedir dist\servidor.py
```

### 3. Checksum verification

```powershell
# Generar checksums
Get-FileHash dist\SpecsServidor\SpecsServidor.exe -Algorithm SHA256 | `
    Select-Object Hash | `
    Out-File checksums.txt

# Publicar checksums.txt junto al instalador
```

### 4. Actualizaciones automáticas

Implementar mecanismo de auto-update:

```python
import requests
import hashlib

def check_updates():
    """Verifica si hay nueva versión disponible."""
    response = requests.get("https://tu-servidor.com/api/version")
    latest_version = response.json()["version"]
    current_version = "1.0.0"
    
    if latest_version > current_version:
        return True, latest_version
    return False, None
```

---

## 📝 Checklist de Distribución

- [ ] Código compilado con PyInstaller
- [ ] Ejecutables firmados digitalmente (si aplica)
- [ ] Instalador creado (Inno Setup/NSIS)
- [ ] Instalador firmado digitalmente (si aplica)
- [ ] `security_config.py` NO incluido (generado en instalación)
- [ ] Checksums SHA256 generados
- [ ] Documentación de usuario incluida
- [ ] Licencia de software incluida
- [ ] README con instrucciones de instalación
- [ ] Tested en máquina limpia (sin Python instalado)
- [ ] Tested en Windows 10 y Windows 11
- [ ] Tested con diferentes niveles de permisos (admin/user)
- [ ] Firewall rules documentadas (puertos 5255, 37020)

---

## 🎯 Recomendación Final

**Para distribución profesional corporativa**:

1. ✅ **Obtener certificado EV Code Signing** (~$500/año)
   - Elimina advertencias de SmartScreen inmediatamente
   - Genera confianza en usuarios finales
   - Requerido por muchas políticas corporativas

2. ✅ **Crear instalador con Inno Setup**
   - Apariencia profesional
   - Fácil instalación para usuarios
   - Desinstalación limpia

3. ✅ **Distribuir vía Group Policy o SCCM**
   - Despliegue automatizado
   - Control centralizado
   - Rollback fácil si hay problemas

**Para testing interno o código abierto**:

1. ⚡ **Distribuir código fuente + install.ps1**
   - Sin advertencias de SmartScreen
   - Usuarios ven el código (transparencia)
   - Más fácil de mantener

2. ⚡ **O certificado auto-firmado + instalación manual**
   - Bajo costo
   - Adecuado para LANs corporativas cerradas

---

## 📞 Recursos Adicionales

- **PyInstaller Docs**: https://pyinstaller.org/en/stable/
- **Windows Code Signing**: https://learn.microsoft.com/windows/win32/seccrypto/cryptography-tools
- **Inno Setup**: https://jrsoftware.org/isinfo.php
- **Certificate Providers Comparison**: https://comodosslstore.com/code-signing

---

## 🐛 Troubleshooting

### "El ejecutable no se puede ejecutar"

- Verificar que todas las dependencias están incluidas con `--add-data`
- Revisar `build/specs/warn-specs.txt` para imports faltantes
- Agregar imports ocultos: `--hidden-import nombre_modulo`

### "No se puede verificar el editor"

- Firmar con certificado válido (ver sección Firma Digital)
- O distribuir código fuente en lugar de ejecutable

### "Antivirus bloquea el ejecutable"

- Firmar con certificado confiable
- Reportar falso positivo a proveedor de antivirus
- Solicitar whitelisting si es distribución corporativa interna

### "El ejecutable es muy grande (>100MB)"

- Usar `--onedir` en lugar de `--onefile`
- Excluir módulos innecesarios con `--exclude-module`
- Considerar UPX compression (puede causar falsos positivos en antivirus)
