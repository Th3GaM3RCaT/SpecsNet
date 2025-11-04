# logica_specs.py
from datetime import datetime
from json import dump, dumps
from locale import getpreferredencoding
from os import environ, name, path
from re import IGNORECASE, search
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket, timeout
from subprocess import CREATE_NO_WINDOW, run
import sys

import psutil
from getmac import get_mac_address as gma
from windows_tools.installed_software import get_installed_software
from wmi import WMI

# Constantes globales justificadas
nombre_tarea = "informe_de_dispositivo"  # Usado por configurar_tarea()
new = {}  # Diccionario compartido para datos del sistema (patrón establecido)


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def informe():
    """Recopila especificaciones completas del sistema (hardware/software).
    
    Recolecta información de:
    - Fabricante, modelo, serial, MAC
    - CPU (cores, frecuencias, uso)
    - RAM (módulos individuales, capacidad)
    - Discos (particiones, uso)
    - Red (interfaces, IPs, MACs)
    - Licencia Windows (estado, expiración)
    - Software instalado (nombre, versión, publisher)
    
    Returns:
        dict: Diccionario con todas las especificaciones (almacenado en global `new`)
    
    Note:
        Modifica el diccionario global `new`. UI debe deshabilitar botón antes de llamar.
    """
    my_system = WMI().Win32_ComputerSystem()[0]

    from datos.serialNumber import get_serial
    new["SerialNumber"] = get_serial()
    new["Manufacturer"] = my_system.Manufacturer
    new["Model"] = my_system.Model
    new["Name"] = my_system.Name
    new["NumberOfProcessors"] = my_system.NumberOfProcessors
    new["SystemType"] = my_system.SystemType
    new["SystemFamily"] = my_system.SystemFamily
    new["MAC Address"] = gma()

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    new["Boot Time"] = (
        f" {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
    )

    new["Physical cores"] = psutil.cpu_count(logical=False)
    new["Total cores"] = psutil.cpu_count(logical=True)

    cpufreq = psutil.cpu_freq()
    new[f"Max Frequency"] = f" {cpufreq.max:.2f}Mhz"
    new[f"Min Frequency"] = f"{cpufreq.min:.2f}Mhz"
    new[f"Current Frequency"] = f"{cpufreq.current:.2f}Mhz"

    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        new[f"Core {i}"] = f"{percentage}%"
    new[f"Total CPU Usage"] = f"{psutil.cpu_percent()}%"

    svmem = psutil.virtual_memory()
    new[f"Total virtual memory"] = f"{get_size(svmem.total)}"
    new[f"Available virtual memory"] = f"{get_size(svmem.available)}"
    new[f"Used virtual memory"] = f" {get_size(svmem.used)}"
    new[f"Percentage virtual memory"] = f" {svmem.percent}%"


    from datos.get_ram import get_ram_info

    for i, ram in enumerate(get_ram_info(), 1):
        new[f"--- Módulo RAM {i} ---"] = ""
        for k, v in ram.items():
            new[f"{k}"] = v

    swap = psutil.swap_memory()

    new[f"Total swap memory"] = f" {get_size(swap.total)}"
    new[f"Free swap memory"] = f" {get_size(swap.free)}"
    new[f"Used swap memory"] = f" {get_size(swap.used)}"
    new[f"Percentage swap memory"] = f" {swap.percent}%"

    partitions = psutil.disk_partitions()
    for partition in partitions:
        new["Device"] = f" {partition.device}"
        new["  Mountpoint"] = f" {partition.mountpoint}"
        new["  File system type"] = f" {partition.fstype}"
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        new["  Total Size"] = f" {get_size(partition_usage.total)}"
        new["  Used"] = f" {get_size(partition_usage.used)}"
        new["  Free"] = f" {get_size(partition_usage.free)}"
        new["  Percentage"] = f" {partition_usage.percent}%"

    disk_io = psutil.disk_io_counters()
    new["Total read"] = f"{get_size(disk_io.read_bytes)}"  # type: ignore
    new["Total write"] = f" {get_size(disk_io.write_bytes)}"  # type: ignore

    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            new["Interface"] = f" {interface_name}"
            if str(address.family) == "AddressFamily.AF_INET":
                new["  IP Address"] = f"{address.address}"
                new["  Netmask"] = f" {address.netmask}"
                new["  Broadcast IP"] = f"{address.broadcast}"
            elif str(address.family) == "AddressFamily.AF_PACKET":
                new["  MAC Address"] = f" {address.address}"
                new["  Netmask"] = f" {address.netmask}"
                new["  Broadcast MAC"] = f" {address.broadcast}"

    net_io = psutil.net_io_counters()
    new["Total Bytes Sent"] = f"{get_size(net_io.bytes_sent)}"
    new["Total Bytes Received"] = f" {get_size(net_io.bytes_recv)}"
    new["License status"] = f"{get_license_status()}"
    new["Expiration time"] = f"{get_license_status(1)}"

    for software in get_installed_software():
        new[software["name"]] = (software["version"], software["publisher"])
    return new


def get_license_status(a=0):
    """Obtiene estado o fecha de expiración de licencia Windows via slmgr.vbs.
    
    Args:
        a (int): 0 para estado de licencia, 1 para fecha de expiración
    
    Returns:
        str: Estado o fecha de licencia, o None si no se encuentra
    
    Raises:
        OSError: Si no se ejecuta en Windows NT
        FileNotFoundError: Si no se encuentra slmgr.vbs
    """
    if name != "nt":
        raise OSError("solo en windows nt")
    type = r""
    line = r""
    if a != 0:
        type = "/xpr"
        line = r"\s*[::]\s*(.+)"
    else:
        type = "/dli"
        line = r"Estado de la licencia\s*[::]\s*(.+)"
    system_root = environ.get("SystemRoot", r"C:\Windows")
    slmgr_path = path.join(system_root, "System32", "slmgr.vbs")
    if not path.exists(slmgr_path):
        raise FileNotFoundError("no se encontró slmgr.vbs")
    cmd = ["cscript", "//NoLogo", slmgr_path, type]
    proc = run(cmd, capture_output=True, creationflags=CREATE_NO_WINDOW)
    raw_bytes = proc.stdout + proc.stderr
    enc = getpreferredencoding(False) or "utf-8"
    raw = raw_bytes.decode(enc, errors="replace")
    match = search(line, raw, IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return None

def enviar_a_servidor():
    """Descubre servidor vía UDP broadcast y envía especificaciones vía TCP.
    
    Proceso:
    1. Escucha broadcasts UDP en puerto 5255 (5 sec timeout)
    2. Extrae IP del servidor desde el sender
    3. Guarda info del servidor en servidor.json
    4. Lee dxdiag_output.txt y lo incluye en el JSON
    5. Detecta IP local del cliente
    6. Genera token de autenticación (si security_config disponible)
    7. Envía JSON completo vía TCP al servidor puerto 5255
    
    Returns:
        None
    
    Raises:
        timeout: Si no se encuentra servidor en 5 segundos
    
    Note:
        Modifica el diccionario global `new` agregando dxdiag_output_txt y client_ip.
    
    Security:
        Genera token de autenticación basado en timestamp y secreto compartido.
    """
    # Importar seguridad si está disponible
    try:
        from security_config import generate_auth_token
        security_available = True
    except ImportError:
        security_available = False
        print("⚠️  WARNING: security_config no disponible, enviando sin autenticación")
    
    DISCOVERY_PORT = 37020  # Puerto para escuchar broadcasts del servidor
    TCP_PORT = 5255         # Puerto TCP del servidor para enviar datos
    txt_data = ""
    
    # Escuchar broadcasts en puerto 37020
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(5)
    s.bind(("", DISCOVERY_PORT))
    print(f"🔍 Buscando servidor (escuchando broadcasts en puerto {DISCOVERY_PORT})...")
    

    try:
        # Descubrir servidor vía UDP broadcast
        data, addr = s.recvfrom(1024)
        HOST = addr[0]
        s.close()  # Cerrar socket UDP
        
        print("Servidor encontrado:", HOST)

        # Guardar info del servidor localmente
        with open("servidor.json", "w", encoding="utf-8") as f:
            dump(addr, f, indent=4)

        with open("dxdiag_output.txt", "r", encoding="cp1252") as f:
            txt_data = f.read()
        # Incluir el TXT dentro del JSON
        new["dxdiag_output_txt"] = txt_data
        
        # Agregar IP del cliente
        try:
            # Obtener IP local conectando al servidor
            temp_sock = socket(AF_INET, SOCK_DGRAM)
            temp_sock.connect((HOST, TCP_PORT))
            new["client_ip"] = temp_sock.getsockname()[0]
            temp_sock.close()
        except:
            new["client_ip"] = "unknown"
        
        # SECURITY: Agregar token de autenticación
        if security_available:
            try:
                new["auth_token"] = generate_auth_token() # type: ignore
                print("✓ Token de autenticación agregado")
            except ValueError as e:
                print(f"⚠️  ERROR generando token: {e}")
                print("   Configurar SHARED_SECRET en security_config.py")
                return  # No enviar sin autenticación si está habilitada
        
        # Conectar vía TCP y enviar todo
        print(f"🔌 Conectando al servidor {HOST}:{TCP_PORT}...")
        cliente = socket(AF_INET, SOCK_STREAM)
        cliente.connect((HOST, TCP_PORT))
        cliente.sendall(dumps(new).encode("utf-8"))
        cliente.close()
        print("✓ Datos enviados correctamente al servidor")

    except timeout:
        print("❌ Timeout: No se encontró el servidor (esperó 5 segundos)")
        print("   Verificar que el servidor esté ejecutándose")


def configurar_tarea(valor=1):
    """Configura auto-start de specs.py en registro de Windows.
    
    Args:
        valor (int): 0=agregar tarea, 1=consultar tarea, 2=eliminar tarea
    
    Returns:
        None
    
    Note:
        Usa registro HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
        para ejecutar specs.py --tarea al iniciar Windows.
        
    Security:
        Usa subprocess con lista de argumentos (NO shell=True) para prevenir inyección.
    """
    import re
    from pathlib import Path
    
    # Validar nombre_tarea contra caracteres peligrosos
    if not re.match(r'^[a-zA-Z0-9_-]+$', nombre_tarea):
        raise ValueError(f"Nombre de tarea inválido: {nombre_tarea}. Solo se permiten letras, números, guiones y guiones bajos.")
    
    accion = ["add", "query", "delete"]
    reg_key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    
    # Construir argumentos como lista (NO string)
    cmd_args = ["reg", accion[valor], reg_key, "/v", nombre_tarea]
    
    if valor == 0:  # Agregar tarea
        # Obtener path del script actual
        if getattr(sys, "frozen", False):
            # Ejecutable empaquetado
            script_path = sys.executable
        else:
            # Script Python
            script_path = str(Path(__file__).parent / "specs.py")
        
        # Agregar parámetros de valor
        cmd_args.extend(["/d", f'"{script_path}" --tarea', "/f"])
    elif valor == 2:  # Eliminar tarea
        cmd_args.append("/f")
    # valor == 1 (query) no necesita parámetros adicionales
    
    # Ejecutar sin shell (seguro)
    run(cmd_args, creationflags=CREATE_NO_WINDOW, check=False)