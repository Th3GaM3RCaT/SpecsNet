# Script para compilar todos los componentes de Specs Python con PyInstaller
# Genera servidor, cliente e inventario en dist/

param(
    [Parameter(Mandatory=$false)]
    [switch]$Clean,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipServer,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipClient,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipInventory
)

$ErrorActionPreference = "Stop"

Write-Host "`n🔨 COMPILADOR DE SPECS PYTHON" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Verificar que PyInstaller está instalado
try {
    $pyinstallerVersion = pyinstaller --version
    Write-Host "✅ PyInstaller encontrado: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PyInstaller no está instalado" -ForegroundColor Red
    Write-Host "   Instalando PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al instalar PyInstaller" -ForegroundColor Red
        exit 1
    }
}

# Limpiar builds anteriores si se solicita
if ($Clean) {
    Write-Host "`n🧹 Limpiando builds anteriores..." -ForegroundColor Yellow
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
    Get-ChildItem -Filter "*.spec" | Remove-Item -Force
    Write-Host "✅ Limpieza completada`n" -ForegroundColor Green
}

# Icono (opcional)
$iconParam = ""
if (Test-Path "icon.ico") {
    $iconParam = "--icon=icon.ico"
    Write-Host "✅ Icono encontrado: icon.ico`n" -ForegroundColor Green
}

$compiled = @()
$failed = @()

# =============================================================================
# COMPILAR SERVIDOR
# =============================================================================
if (-not $SkipServer) {
    Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
    Write-Host "📦 COMPILANDO SERVIDOR" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    
    Write-Host "`nArchivo: servidor.py" -ForegroundColor White
    Write-Host "Incluye: SQL statements, UI files" -ForegroundColor DarkGray
    Write-Host "Modo: Sin consola (GUI)`n" -ForegroundColor DarkGray
    
    try {
        $cmd = @(
            "pyinstaller",
            "--onedir",
            "--noconsole",
            "servidor.py",
            "--add-data=sql_specs/statement/*.sql;sql_specs/statement",
            "--add-data=ui/*.ui;ui",
            "--name=SpecsServidor",
            $iconParam,
            "--clean"
        ) | Where-Object { $_ -ne "" }
        
        & $cmd[0] $cmd[1..($cmd.Length-1)]
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Servidor compilado exitosamente" -ForegroundColor Green
            $compiled += "SpecsServidor"
        } else {
            Write-Host "`n❌ Error al compilar servidor" -ForegroundColor Red
            $failed += "SpecsServidor"
        }
    } catch {
        Write-Host "`n❌ Excepción al compilar servidor: $($_.Exception.Message)" -ForegroundColor Red
        $failed += "SpecsServidor"
    }
}

# =============================================================================
# COMPILAR CLIENTE
# =============================================================================
if (-not $SkipClient) {
    Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
    Write-Host "📦 COMPILANDO CLIENTE" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    
    Write-Host "`nArchivo: specs.py" -ForegroundColor White
    Write-Host "Incluye: UI files" -ForegroundColor DarkGray
    Write-Host "Modo: Sin consola (GUI)`n" -ForegroundColor DarkGray
    
    try {
        $cmd = @(
            "pyinstaller",
            "--onedir",
            "--noconsole",
            "specs.py",
            "--add-data=ui/*.ui;ui",
            "--name=SpecsCliente",
            $iconParam,
            "--clean"
        ) | Where-Object { $_ -ne "" }
        
        & $cmd[0] $cmd[1..($cmd.Length-1)]
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Cliente compilado exitosamente" -ForegroundColor Green
            $compiled += "SpecsCliente"
        } else {
            Write-Host "`n❌ Error al compilar cliente" -ForegroundColor Red
            $failed += "SpecsCliente"
        }
    } catch {
        Write-Host "`n❌ Excepción al compilar cliente: $($_.Exception.Message)" -ForegroundColor Red
        $failed += "SpecsCliente"
    }
}

# =============================================================================
# COMPILAR INVENTARIO
# =============================================================================
if (-not $SkipInventory) {
    Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
    Write-Host "📦 COMPILANDO INVENTARIO" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    
    Write-Host "`nArchivo: all_specs.py" -ForegroundColor White
    Write-Host "Incluye: UI files, SQL statements" -ForegroundColor DarkGray
    Write-Host "Modo: Sin consola (GUI)`n" -ForegroundColor DarkGray
    
    try {
        $cmd = @(
            "pyinstaller",
            "--onedir",
            "--noconsole",
            "all_specs.py",
            "--add-data=ui/*.ui;ui",
            "--add-data=sql_specs/statement/*.sql;sql_specs/statement",
            "--name=SpecsInventario",
            $iconParam,
            "--clean"
        ) | Where-Object { $_ -ne "" }
        
        & $cmd[0] $cmd[1..($cmd.Length-1)]
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Inventario compilado exitosamente" -ForegroundColor Green
            $compiled += "SpecsInventario"
        } else {
            Write-Host "`n❌ Error al compilar inventario" -ForegroundColor Red
            $failed += "SpecsInventario"
        }
    } catch {
        Write-Host "`n❌ Excepción al compilar inventario: $($_.Exception.Message)" -ForegroundColor Red
        $failed += "SpecsInventario"
    }
}

# =============================================================================
# RESUMEN
# =============================================================================
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "RESUMEN DE COMPILACIÓN" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`nCompilados exitosamente ($($compiled.Count)):" -ForegroundColor Green
foreach ($item in $compiled) {
    Write-Host "  ✅ $item" -ForegroundColor Green
}

if ($failed.Count -gt 0) {
    Write-Host "`nFallidos ($($failed.Count)):" -ForegroundColor Red
    foreach ($item in $failed) {
        Write-Host "  ❌ $item" -ForegroundColor Red
    }
}

# Tamaños de los ejecutables
if (Test-Path "dist") {
    Write-Host "`nTamaños de distribución:" -ForegroundColor Cyan
    Get-ChildItem "dist" -Directory | ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "  📁 $($_.Name): $sizeMB MB" -ForegroundColor White
    }
}

# Siguiente paso
if ($compiled.Count -gt 0) {
    Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
    Write-Host "SIGUIENTE PASO" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
    
    Write-Host "`nPara firmar los ejecutables:" -ForegroundColor Yellow
    Write-Host "  .\sign_executables.ps1`n" -ForegroundColor White
    
    Write-Host "Para probar los ejecutables:" -ForegroundColor Yellow
    foreach ($item in $compiled) {
        $exePath = "dist\$item\$item.exe"
        if (Test-Path $exePath) {
            Write-Host "  .\$exePath" -ForegroundColor White
        }
    }
    Write-Host ""
}

# Exit code
if ($failed.Count -eq 0) {
    Write-Host "✅ COMPILACIÓN COMPLETADA EXITOSAMENTE`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  COMPILACIÓN COMPLETADA CON ERRORES`n" -ForegroundColor Yellow
    exit 1
}
