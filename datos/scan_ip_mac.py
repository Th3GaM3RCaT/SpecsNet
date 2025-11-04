"""
Módulo unificado para escaneo de red y resolución MAC.
Combina funcionalidades de ping sweep, parseo de tabla ARP y actualización de CSVs.
"""

import asyncio
import ipaddress
import platform
import socket
import subprocess
import re
import os
import csv
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

ASSUME_CIDR = "/16"   # ajusta si tu red no es /24
CONCURRENCY = 300
def get_local_network():
    """Detecta la red local basándose en la IP del equipo."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ipaddress.ip_network(ip + ASSUME_CIDR, strict=False)


async def ping_one(host):
    """Ejecuta ping asíncrono a un host. Retorna True si responde."""
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", "-n", "1", "-w", "1000", host]
    elif system == "Darwin":
        cmd = ["ping", "-c", "1", "-t", "1", host]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", host]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        ret = await proc.wait()
        return ret == 0
    except Exception:
        return False

async def ping_sweep(network, concurrency=200):
    """Escanea toda una red con pings asíncronos concurrentes."""
    sem = asyncio.Semaphore(concurrency)
    alive = []
    
    async def worker(ip):
        async with sem:
            ok = await ping_one(str(ip))
            if ok:
                alive.append(str(ip))
    
    tasks = [asyncio.create_task(worker(ip)) for ip in network.hosts()]
    await asyncio.gather(*tasks)
    return alive


def _ping_ip_sync(ip, timeout=1):
    """
    Ping síncrono para uso en ThreadPoolExecutor.
    Retorna True si el host responde.
    """
    system = platform.system()
    if system == "Windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip]
    elif system == "Darwin":
        cmd = ["ping", "-c", "1", "-t", "1", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(int(max(1, timeout))), ip]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return proc.returncode == 0
    except Exception:
        return False


def parse_arp_table_raw():
    """
    Parsea la tabla ARP del sistema operativo.
    Retorna lista de tuplas: [(ip, mac), ...]
    """
    try:
        proc = subprocess.run(["arp", "-a"], capture_output=True, text=True, check=False)
        out = proc.stdout + proc.stderr
    except Exception:
        out = ""
    
    lines = out.splitlines()
    entries = []
    
    for line in lines:
        # Formato Unix/macOS: (192.168.1.1) at aa:bb:cc:dd:ee:ff
        m = re.search(r'\((?P<ip>\d{1,3}(?:\.\d{1,3}){3})\)\s+at\s+(?P<mac>[0-9a-fA-F:]{11,17})', line)
        if m:
            entries.append((m.group("ip"), m.group("mac").lower()))
            continue
        
        # Formato Windows: 192.168.1.1  aa-bb-cc-dd-ee-ff
        m2 = re.search(r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+(?P<mac>[0-9a-fA-F:-]{11,17})', line.strip())
        if m2:
            mac = m2.group("mac").replace('-', ':').lower()
            entries.append((m2.group("ip"), mac))
            continue
        
        # Formato genérico con MAC
        m3 = re.search(r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3}).*(?P<mac>[0-9a-fA-F:]{11,17})', line)
        if m3:
            entries.append((m3.group("ip"), m3.group("mac").replace('-', ':').lower()))
            continue
        
        # Solo IP sin MAC
        m4 = re.search(r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3})', line)
        if m4:
            entries.append((m4.group("ip"), None))
    
    return entries
def is_broadcast_ip(ip_obj, network):
    """Verifica si una IP es broadcast (255.255.255.255 o broadcast de la red)."""
    if str(ip_obj) == "255.255.255.255":
        return True
    try:
        return ip_obj == network.broadcast_address
    except Exception:
        return False


def is_broadcast_mac(mac):
    """Verifica si una MAC es broadcast (ff:ff:ff:ff:ff:ff)."""
    if not mac:
        return False
    return mac.lower() == "ff:ff:ff:ff:ff:ff"


def filter_entries(entries, network):
    """
    Filtra entradas ARP descartando broadcasts, multicast, IPs fuera de red, etc.
    Retorna (kept_dict, discarded_list).
    """
    kept = {}
    discarded = []
    
    for ip_str, mac in entries:
        reason = None
        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except Exception:
            reason = "IP inválida"
            discarded.append((ip_str, mac, reason))
            continue
        
        if is_broadcast_ip(ip_obj, network):
            reason = "broadcast IP"
            discarded.append((ip_str, mac, reason))
            continue
        
        if ip_obj.is_multicast or ip_obj.is_unspecified or ip_obj.is_loopback:
            reason = "multicast/unspecified/loopback"
            discarded.append((ip_str, mac, reason))
            continue
        
        if ip_obj not in network:
            reason = f"fuera de subred {network}"
            discarded.append((ip_str, mac, reason))
            continue
        
        if mac and is_broadcast_mac(mac):
            reason = "MAC broadcast"
            discarded.append((ip_str, mac, reason))
            continue
        
        mac_norm = mac.lower() if mac else None
        
        if ip_str not in kept:
            kept[ip_str] = mac_norm
        else:
            # Si ya existe pero sin MAC, actualizar
            if kept[ip_str] is None and mac_norm:
                kept[ip_str] = mac_norm
    
    print(kept)
    print(discarded)
    return kept, discarded
def print_report(kept, discarded):
    """Imprime reporte de IPs encontradas y descartadas."""
    print("\n---- RESULTADOS FILTRADOS ----")
    if not kept:
        print("No se encontró ninguna IP válida con MAC dentro de la subred.")
    else:
        for ip in sorted(kept.keys(), key=lambda s: tuple(int(x) for x in s.split("."))):
            mac = kept[ip] or "(sin MAC)"
            print(f"{ip} -> {mac}")
    
    print(f"\nTotal válidas: {len(kept)}")
    print("\n---- ENTRADAS DESCARTADAS (ejemplos) ----")
    for ip, mac, reason in discarded[:40]:
        print(f"{ip} -> {mac or '(no mac)'}  : {reason}")
    print(f"\nTotal descartadas: {len(discarded)}")


# =============================================================================
# FUNCIONALIDAD DE ACTUALIZACIÓN DE CSV CON MACs (antes en get_mac.py)
# =============================================================================

def update_csv_with_macs(
    input_csv_path,
    output_csv_path=None,
    ping_missing=True,
    ping_timeout=0.8,
    workers=50,
    overwrite=True
):
    """
    Lee CSV de entrada con IPs, intenta poblar MACs usando tabla ARP.
    Opcionalmente hace ping a IPs sin MAC para poblar la tabla ARP.
    
    Args:
        input_csv_path (str): Path al CSV de entrada.
        output_csv_path (str|None): Path de salida. Si None, crea "<input>_with_macs.csv" 
                                     o sobrescribe si overwrite=True.
        ping_missing (bool): Si True, hace ping a IPs sin MAC antes de leer ARP.
        ping_timeout (float): Timeout por ping en segundos.
        workers (int): Concurrencia para pings.
        overwrite (bool): Si True y output_csv_path es None, sobrescribe input file.
    
    Returns:
        dict: {'input': path, 'output': path, 'total_rows': n, 'mac_found': m, 'mac_missing': k}
    """
    if not os.path.isfile(input_csv_path):
        raise FileNotFoundError(f"Input CSV not found: {input_csv_path}")
    
    # 1) Leer CSV y detectar columnas
    rows = []
    with open(input_csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        lower_fields = [h.lower() for h in fields]
        
        for r in reader:
            row = {k: (v.strip() if v is not None else "") for k, v in r.items()}
            
            # Buscar columna IP
            ip = None
            for candidate in ("ip", "address", "host"):
                if candidate in lower_fields:
                    ip = row[fields[lower_fields.index(candidate)]]
                    break
            if ip is None and len(fields) >= 2:
                ip = row[fields[1]]
            
            # Buscar columna MAC
            mac = None
            for candidate in ("mac", "ether", "hwaddr"):
                if candidate in lower_fields:
                    mac = row[fields[lower_fields.index(candidate)]]
                    break
            if mac is None and len(fields) >= 3:
                mac = row[fields[2]]
            
            rows.append({"raw": row, "ip": ip, "mac": (mac or "").strip()})
    
    total = len(rows)
    
    # 2) Identificar IPs sin MAC
    missing_ips = [r["ip"] for r in rows if r["ip"] and (not r["mac"])]
    missing_ips = list(dict.fromkeys(missing_ips))  # Dedupe preserve order
    print(f"CSV rows: {total}, IPs missing MAC: {len(missing_ips)}")
    
    # 3) Opcional: ping masivo concurrente para poblar ARP
    if ping_missing and missing_ips:
        print(f"Pinging {len(missing_ips)} IPs (timeout={ping_timeout}s, workers={workers}) to populate ARP...")
        with ThreadPoolExecutor(max_workers=min(workers, len(missing_ips))) as ex:
            futures = {ex.submit(_ping_ip_sync, ip, ping_timeout): ip for ip in missing_ips} # type: ignore
            for fut in as_completed(futures):
                ip = futures[fut]
                try:
                    ok = fut.result()
                except Exception:
                    ok = False
        # Pequeña espera para que la tabla ARP se actualice
        time.sleep(0.5)
    
    # 4) Re-parsear tabla ARP
    try:
        arp_entries = parse_arp_table_raw()
    except Exception as e:
        print(f"Warning: parse_arp_table_raw() falló: {e}")
        arp_entries = []
    
    arp_map = {ip: mac.lower() for ip, mac in arp_entries if mac}
    
    # 5) Actualizar filas con MACs si están ahora en arp_map
    updated = 0
    still_missing = 0
    for r in rows:
        ip = r["ip"]
        if not ip:
            continue
        if r["mac"]:
            continue  # Ya tenía MAC
        mac = arp_map.get(ip)
        if mac:
            r["mac"] = mac
            updated += 1
        else:
            still_missing += 1
    
    print(f"MACs found by ARP: {updated}, still missing: {still_missing}")
    
    # 6) Escribir CSV de salida
    if output_csv_path is None:
        if overwrite:
            output_csv_path = input_csv_path
        else:
            base, ext = os.path.splitext(input_csv_path)
            output_csv_path = f"{base}_with_macs{ext}"
    
    # Construir header: conservar campos originales, asegurar columna 'mac'
    orig_fieldnames = fields[:] if fields else ["ip", "mac"]
    low = [h.lower() for h in orig_fieldnames]
    if "mac" not in low:
        orig_fieldnames.append("mac") # type: ignore
    
    with open(output_csv_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=orig_fieldnames)
        writer.writeheader()
        for r in rows:
            outrow = {}
            # Llenar valores originales
            for h in orig_fieldnames:
                if h in r["raw"]:
                    outrow[h] = r["raw"].get(h, "")
                else:
                    # Match case-insensitive
                    for k in r["raw"]:
                        if k.lower() == h.lower():
                            outrow[h] = r["raw"].get(k, "")
                            break
                    else:
                        outrow[h] = ""
            
            # Asegurar campo 'mac' actualizado
            for idx, name in enumerate(orig_fieldnames):
                if name.lower() == "mac":
                    outrow[name] = r.get("mac") or ""
                    break
            
            writer.writerow(outrow)
    
    return {
        "input": input_csv_path,
        "output": output_csv_path,
        "total_rows": total,
        "mac_found": updated,
        "mac_missing": still_missing
    }


# =============================================================================
# FUNCIÓN MAIN - ESCANEO DE RED
# =============================================================================

def main():
    """Función principal para escaneo de red local."""
    network = get_local_network()
    
    try:
        alive = asyncio.run(ping_sweep(network, concurrency=CONCURRENCY))
    except Exception as e:
        pass
    
    raw = parse_arp_table_raw()
    kept, discarded = filter_entries(raw, network)
    
    csv_name = f"scan_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(csv_name, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ip", "mac"])
            for ip in sorted(kept.keys(), key=lambda s: tuple(int(x) for x in s.split("."))):
                w.writerow([ip, kept[ip] or ""])
    except Exception as e:
        pass
    
if __name__ == "__main__":
    main()
