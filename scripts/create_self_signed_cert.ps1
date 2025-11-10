# Script para crear certificado auto-firmado para testing
# SOLO para uso en desarrollo/testing interno - NO elimina advertencias de SmartScreen

param(
    [Parameter(Mandatory=$false)]
    [string]$Subject = "CN=Specs Python, O=Testing, C=ES",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\certs\SpecsPython.pfx",
    
    [Parameter(Mandatory=$false)]
    [string]$Password = "SpecsPython2025!"
)

$ErrorActionPreference = "Stop"

Write-Host "`n🔐 GENERADOR DE CERTIFICADO AUTO-FIRMADO" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "⚠️  ADVERTENCIA:" -ForegroundColor Yellow
Write-Host "   Este certificado es SOLO para testing interno" -ForegroundColor Yellow
Write-Host "   NO eliminará las advertencias de Windows SmartScreen" -ForegroundColor Yellow
Write-Host "   Para producción, comprar certificado de Code Signing comercial`n" -ForegroundColor Yellow

# Verificar permisos de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ Este script requiere permisos de Administrador" -ForegroundColor Red
    Write-Host "   Click derecho → Ejecutar como Administrador`n" -ForegroundColor Yellow
    Throw
}

# Crear directorio si no existe
$certDir = Split-Path $OutputPath -Parent
if (-not (Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir -Force | Out-Null
    Write-Host "✅ Directorio creado: $certDir" -ForegroundColor Green
}

Write-Host "📝 Creando certificado..." -ForegroundColor Cyan
Write-Host "   Subject: $Subject" -ForegroundColor DarkGray
Write-Host "   Válido por: 5 años" -ForegroundColor DarkGray

try {
    # Crear certificado
    $cert = New-SelfSignedCertificate `
        -Subject $Subject `
        -Type CodeSigningCert `
        -CertStoreLocation Cert:\CurrentUser\My `
        -NotAfter (Get-Date).AddYears(5) `
        -KeyLength 4096 `
        -KeyAlgorithm RSA `
        -HashAlgorithm SHA256 `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
    
    Write-Host "✅ Certificado creado en store: $($cert.Thumbprint)" -ForegroundColor Green
    
    # Exportar certificado
    Write-Host "`n📦 Exportando certificado a: $OutputPath" -ForegroundColor Cyan
    
    $securePassword = ConvertTo-SecureString -String $Password -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $OutputPath -Password $securePassword | Out-Null
    
    Write-Host "✅ Certificado exportado exitosamente" -ForegroundColor Green
    
    # Mostrar información
    Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
    Write-Host "INFORMACIÓN DEL CERTIFICADO" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Cyan
    
    Write-Host "`nArchivo: " -NoNewline
    Write-Host $OutputPath -ForegroundColor White
    
    Write-Host "Contraseña: " -NoNewline
    Write-Host $Password -ForegroundColor Yellow
    
    Write-Host "Thumbprint: " -NoNewline
    Write-Host $cert.Thumbprint -ForegroundColor White
    
    Write-Host "Válido desde: " -NoNewline
    Write-Host $cert.NotBefore -ForegroundColor White
    
    Write-Host "Válido hasta: " -NoNewline
    Write-Host $cert.NotAfter -ForegroundColor White
    
    Write-Host "`n⚠️  IMPORTANTE: Guardar la contraseña en lugar seguro" -ForegroundColor Yellow
    Write-Host "   Se necesitará para firmar ejecutables`n" -ForegroundColor Yellow
    
    # Instrucciones de uso
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host "SIGUIENTE PASO" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Cyan
    
    Write-Host "`nPara firmar ejecutables, ejecutar:" -ForegroundColor Cyan
    Write-Host "  .\sign_executables.ps1 -CertPath '$OutputPath' -Password '$Password'`n" -ForegroundColor White
    
    # Opcional: Instalar certificado en Trusted Root (permite testing local)
    Write-Host "¿Desea instalar el certificado en Trusted Root para testing local? (s/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq "s" -or $response -eq "S") {
        try {
            # Exportar certificado público (.cer)
            $cerPath = $OutputPath -replace "\.pfx$", ".cer"
            Export-Certificate -Cert $cert -FilePath $cerPath | Out-Null
            
            # Importar a Trusted Root
            Import-Certificate -FilePath $cerPath -CertStoreLocation Cert:\LocalMachine\Root | Out-Null
            
            Write-Host "`n✅ Certificado instalado en Trusted Root" -ForegroundColor Green
            Write-Host "   Ejecutables firmados no mostrarán advertencia de 'Editor desconocido'" -ForegroundColor Green
            Write-Host "   en este equipo específicamente`n" -ForegroundColor Green
            
            # Limpiar archivo .cer
            Remove-Item $cerPath -Force
        } catch {
            Write-Host "`n❌ Error al instalar certificado: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "   Puede instalarlo manualmente desde certmgr.msc`n" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n⚠️  Certificado NO instalado en Trusted Root" -ForegroundColor Yellow
        Write-Host "   Ejecutables firmados seguirán mostrando 'Editor desconocido'`n" -ForegroundColor Yellow
    }
    
    Write-Host "✅ PROCESO COMPLETADO`n" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error al crear certificado: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nPosibles causas:" -ForegroundColor Yellow
    Write-Host "  - Falta de permisos de administrador" -ForegroundColor Yellow
    Write-Host "  - Certificado con mismo Subject ya existe" -ForegroundColor Yellow
    Write-Host "`nSoluciones:" -ForegroundColor Yellow
    Write-Host "  - Ejecutar como Administrador" -ForegroundColor Yellow
    Write-Host "  - Cambiar el parámetro -Subject a otro nombre`n" -ForegroundColor Yellow
    Throw
}
