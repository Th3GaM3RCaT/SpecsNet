@echo off
REM =====================================================
REM Configurador de Cliente Specs
REM Para usuarios SIN permisos de administrador
REM =====================================================

echo.
echo ====================================================
echo   Configuracion de Cliente Specs
echo   (Modo Manual - Sin Firewall)
echo ====================================================
echo.

REM Verificar que estamos en la carpeta correcta
if not exist SpecsCliente.exe (
    echo [ERROR] No se encontro SpecsCliente.exe
    echo.
    echo Este script debe estar en la misma carpeta que SpecsCliente.exe
    pause
    exit /b 1
)

REM Solicitar IP del servidor
echo Necesitas conocer la IP del servidor donde corre el
echo Sistema de Inventario de Specs.
echo.
set /p SERVER_IP="Ingresa la IP del servidor (ej: 10.100.2.152): "

REM Validar que no este vacio
if "%SERVER_IP%"=="" (
    echo.
    echo [ERROR] Debes ingresar una IP valida
    pause
    exit /b 1
)

REM Crear directorio config si no existe
if not exist config mkdir config

REM Crear archivo de configuracion
echo { > config\server_config.json
echo   "server_ip": "%SERVER_IP%", >> config\server_config.json
echo   "server_port": 5255, >> config\server_config.json
echo   "use_discovery": false, >> config\server_config.json
echo   "discovery_port": 37020, >> config\server_config.json
echo   "connection_timeout": 10 >> config\server_config.json
echo } >> config\server_config.json

echo.
echo ====================================================
echo   CONFIGURACION COMPLETADA
echo ====================================================
echo.
echo [OK] Archivo creado: config\server_config.json
echo.
echo Configuracion guardada:
echo   - IP del servidor: %SERVER_IP%
echo   - Puerto: 5255
echo   - Modo: Conexion directa (sin broadcasts UDP)
echo.
echo ====================================================
echo   COMO USAR EL CLIENTE
echo ====================================================
echo.
echo OPCION 1: Modo Grafico (ventana)
echo   - Doble clic en SpecsCliente.exe
echo   - Clic en boton "Enviar Informe"
echo.
echo OPCION 2: Modo Tarea (automatico)
echo   - Ejecutar: SpecsCliente.exe --tarea
echo   - Se ejecuta en segundo plano
echo   - Ideal para programar tareas automaticas
echo.
echo NOTA: Este modo NO requiere permisos de administrador
echo       ni configuracion del Firewall.
echo.
echo ====================================================
echo   VERIFICAR CONECTIVIDAD (Opcional)
echo ====================================================
echo.
echo Para verificar que puedes conectarte al servidor:
echo   Test-NetConnection -ComputerName %SERVER_IP% -Port 5255
echo.

pause
