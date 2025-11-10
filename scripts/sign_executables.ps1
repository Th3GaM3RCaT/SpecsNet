# Script para firmar ejecutables de Specs Python
# Ejecutar después de compilar con PyInstaller

param(
    [Parameter(Mandatory=$false)]
    [string]$CertPath = ".\certs\SpecsPython.pfx",
    
    [Parameter(Mandatory=$false)]
    [string]$Password = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"

# Colores
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error-Custom { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Cyan }
function Write-Warning-Custom { Write-Host "⚠️  $args" -ForegroundColor Yellow }

Write-Host "`n🔏 FIRMADOR DE EJECUTABLES - SPECS PYTHON" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Buscar signtool.exe
$possiblePaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x64\signtool.exe",
    "C:\Program Files (x86)\Microsoft SDKs\Windows\v10.0A\bin\NETFX 4.8 Tools\signtool.exe"
)

$signtool = $null
foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $signtool = $path
        break
    }
}

if (-not $signtool) {
    # Buscar en cualquier ubicación
    Write-Info "Buscando signtool.exe en Windows Kits..."
    $found = Get-ChildItem "C:\Program Files (x86)\Windows Kits" -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $signtool = $found.FullName
    } else {
        Write-Error-Custom "signtool.exe no encontrado"
        Write-Warning-Custom "Instalar Windows SDK desde:"
        Write-Host "  https://developer.microsoft.com/windows/downloads/windows-sdk/`n" -ForegroundColor Yellow
        Throw
    }
}

Write-Success "signtool.exe encontrado: $signtool"

# Verificar certificado
if (-not (Test-Path $CertPath)) {
    Write-Error-Custom "Certificado no encontrado: $CertPath"
    Write-Warning-Custom "Opciones:"
    Write-Host "  1. Crear certificado auto-firmado con: .\create_self_signed_cert.ps1" -ForegroundColor Yellow
    Write-Host "  2. Usar certificado comercial: -CertPath 'ruta\al\certificado.pfx'`n" -ForegroundColor Yellow
    Throw
}

Write-Success "Certificado encontrado: $CertPath"

# Solicitar contraseña si no se proporcionó
if ([string]::IsNullOrEmpty($Password)) {
    $securePassword = Read-Host "Contraseña del certificado" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

# Buscar ejecutables en dist/
Write-Info "`nBuscando ejecutables en dist/...`n"

$executables = Get-ChildItem "dist" -Recurse -Filter "*.exe" | Where-Object { 
    $_.Name -notlike "*_signed.exe" 
}

if ($executables.Count -eq 0) {
    Write-Error-Custom "No se encontraron ejecutables en dist/"
    Write-Warning-Custom "Compilar primero con PyInstaller:`n"
    Write-Host "  pyinstaller --onedir --noconsole servidor.py" -ForegroundColor Yellow
    Throw
}

Write-Info "Ejecutables encontrados: $($executables.Count)`n"

$signedCount = 0
$failedCount = 0

foreach ($exe in $executables) {
    Write-Host "📝 Firmando: " -NoNewline -ForegroundColor Cyan
    Write-Host $exe.Name -ForegroundColor White
    Write-Host "   Ruta: $($exe.FullName)" -ForegroundColor DarkGray
    
    try {
        # Firmar ejecutable
        & $signtool sign `
            /f $CertPath `
            /p $Password `
            /fd SHA256 `
            /tr http://timestamp.digicert.com `
            /td SHA256 `
            /d "Specs Python - Sistema de Inventario" `
            /du "https://github.com/Th3GaM3RCaT/specs-python" `
            $exe.FullName 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "   Firmado exitosamente"
            $signedCount++
            
            # Verificar firma
            if (-not $SkipVerify) {
                & $signtool verify /pa $exe.FullName 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "   Firma verificada"
                } else {
                    Write-Warning-Custom "   No se pudo verificar la firma (ejecutable puede funcionar de todos modos)"
                }
            }
        } else {
            Write-Error-Custom "   Error al firmar"
            $failedCount++
        }
    } catch {
        Write-Error-Custom "   Excepción: $($_.Exception.Message)"
        $failedCount++
    }
    
    Write-Host ""
}

# Resumen
Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "RESUMEN DE FIRMA" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan

Write-Host "`nTotal ejecutables: " -NoNewline
Write-Host $executables.Count -ForegroundColor White

Write-Host "Firmados exitosamente: " -NoNewline
Write-Host $signedCount -ForegroundColor Green

if ($failedCount -gt 0) {
    Write-Host "Fallidos: " -NoNewline
    Write-Host $failedCount -ForegroundColor Red
}

if ($signedCount -eq $executables.Count) {
    Write-Host "`n✅ TODOS LOS EJECUTABLES FIRMADOS CORRECTAMENTE`n" -ForegroundColor Green
    Throw
} else {
    Write-Host "`n⚠️  ALGUNOS EJECUTABLES NO SE PUDIERON FIRMAR`n" -ForegroundColor Yellow
    Throw
}
