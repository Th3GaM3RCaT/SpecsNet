# 🚀 Guía Rápida de Distribución

## Resumen Ejecutivo

Para distribuir tu aplicación **sin advertencias de Windows**, tienes 3 opciones principales:

### ✅ OPCIÓN 1: Certificado EV Code Signing (RECOMENDADA PARA PRODUCCIÓN)

**Costo**: ~$400-600/año  
**Ventaja**: ❌ **CERO advertencias desde día 1**  
**Tiempo**: Reputación inmediata

```
1. Comprar certificado EV en DigiCert/Sectigo/SSL.com
2. Firmar ejecutable con signtool.exe
3. Distribuir - Windows confía automáticamente
```

**Proveedores**:
- DigiCert: https://www.digicert.com/signing/code-signing-certificates (~$474/año)
- Sectigo: https://sectigo.com (~$415/año)
- SSL.com: https://www.ssl.com (~$399/año)

---

### ⚡ OPCIÓN 2: Certificado Standard Code Signing

**Costo**: ~$150-300/año  
**Ventaja**: Menos caro, pero requiere "construir reputación"  
**Tiempo**: Semanas/meses hasta que Windows confíe

```
1. Comprar certificado standard
2. Firmar ejecutable
3. Esperar a que usuarios descarguen y ejecuten (construir reputación)
4. Eventualmente Windows deja de mostrar advertencias
```

⚠️ **Problema**: Durante las primeras semanas/meses, seguirá apareciendo la advertencia.

---

### 🆓 OPCIÓN 3: Distribuir Código Fuente

**Costo**: $0  
**Ventaja**: Sin advertencias, transparente, gratis  
**Limitación**: Usuarios deben tener Python instalado

```
1. Distribuir carpeta del proyecto + install.ps1
2. Usuarios ejecutan: .\install.ps1
3. Script instala dependencias y configura automáticamente
```

✅ **Ideal para**: Código abierto, entornos corporativos internos, LANs cerradas

---

## 🎯 Flujo de Trabajo Recomendado

### Para Testing (AHORA)

```powershell
# 1. Crear certificado auto-firmado
.\create_self_signed_cert.ps1

# 2. Compilar con PyInstaller
pyinstaller --onedir --noconsole servidor.py `
    --add-data "sql_specs/statement/*.sql;sql_specs/statement"

# 3. Firmar ejecutables
.\sign_executables.ps1

# 4. Probar en tu máquina
.\dist\servidor\servidor.exe
```

⚠️ **Nota**: Esto NO elimina advertencias en otras máquinas, solo en la tuya.

---

### Para Producción (DESPUÉS)

#### Opción A: Con Presupuesto ($400-600/año)

```powershell
# 1. Comprar certificado EV Code Signing
#    (DigiCert, Sectigo, SSL.com)

# 2. Compilar con PyInstaller
.\build_all.ps1  # O manualmente

# 3. Firmar con certificado EV
.\sign_executables.ps1 -CertPath "C:\certs\mi_cert_EV.pfx" -Password "..."

# 4. Crear instalador con Inno Setup
iscc specs_installer.iss

# 5. Firmar instalador también
signtool sign /f cert.pfx /p pass /tr http://timestamp.digicert.com installers\SpecsPython_Setup.exe

# 6. Distribuir - SIN ADVERTENCIAS ✅
```

#### Opción B: Sin Presupuesto (Gratis)

```powershell
# 1. Comprimir proyecto
Compress-Archive -Path .\* -DestinationPath SpecsPython_v1.0_Source.zip

# 2. Documentar instalación
#    (ya está en install.ps1)

# 3. Distribuir ZIP + instrucciones
#    Los usuarios ejecutan: .\install.ps1
```

---

## 📋 Checklist Antes de Distribuir

### Testing
- [ ] Compilado con PyInstaller sin errores
- [ ] Probado en máquina limpia (sin Python instalado)
- [ ] Probado en Windows 10 y Windows 11
- [ ] Verificado que `security_config.py` NO está incluido
- [ ] Firewall rules documentadas (puertos 5255, 37020)

### Seguridad
- [ ] Ejecutables firmados (si aplica)
- [ ] Checksums SHA256 generados
- [ ] `security_config.py` se genera durante instalación
- [ ] Documentación de seguridad incluida

### Documentación
- [ ] README con instrucciones de instalación
- [ ] Licencia de software incluida
- [ ] Manual de usuario (si aplica)
- [ ] Troubleshooting guide

---

## 🔧 Scripts Incluidos

| Script | Propósito |
|--------|-----------|
| `install.ps1` | Instalación desde código fuente |
| `create_self_signed_cert.ps1` | Crear certificado para testing |
| `sign_executables.ps1` | Firmar ejecutables compilados |
| `build_all.ps1` | Compilar todos los componentes |

---

## 🆘 Troubleshooting Rápido

### "Windows protegió su PC"

**Causa**: Ejecutable no firmado o sin reputación  
**Solución**: 
1. Corto plazo: Click "Más información" → "Ejecutar de todos modos"
2. Largo plazo: Comprar certificado EV Code Signing

### "El antivirus bloquea el ejecutable"

**Causa**: Falso positivo (común con PyInstaller)  
**Solución**:
1. Firmar con certificado confiable (reduce falsos positivos)
2. Reportar falso positivo a proveedor de antivirus
3. O distribuir código fuente en lugar de compilado

### "El instalador es muy grande (>100MB)"

**Causa**: PyInstaller incluye Python runtime completo  
**Solución**:
1. Usar `--onedir` en lugar de `--onefile`
2. Excluir módulos innecesarios: `--exclude-module tkinter`
3. Distribuir solo componentes necesarios (servidor O cliente)

---

## 💡 Recomendación Final

Para tu caso específico (sistema corporativo interno):

### Si tienes presupuesto IT:
→ **Certificado EV Code Signing** ($400/año)  
→ Elimina advertencias permanentemente  
→ Apariencia profesional

### Si NO tienes presupuesto:
→ **Distribuir código fuente + install.ps1**  
→ Gratis, sin advertencias  
→ Usuarios ven el código (transparencia)  
→ Ideal para LANs corporativas

### Para testing AHORA:
→ **Certificado auto-firmado**  
→ Usar scripts incluidos  
→ Advertencias seguirán apareciendo (esperado)

---

## 📚 Documentación Completa

Ver `DISTRIBUCION.md` para guía completa con todos los detalles.

---

**¿Preguntas?**  
Revisa la documentación o consulta:
- PyInstaller: https://pyinstaller.org
- Code Signing: https://learn.microsoft.com/windows/win32/seccrypto/cryptography-tools
