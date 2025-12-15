"""Utilidades para parseo de tabla ARP - versión consolidada única."""

from subprocess import run, CREATE_NO_WINDOW
from platform import system
from re import search
from platform import system


def parse_arp_table():
    """Parsea tabla ARP del sistema operativo y retorna lista de tuplas (ip, mac).

    Intenta múltiples métodos en orden:
    1. ip neigh (Linux)
    2. arp -a (multiplataforma)
    3. Fallback vacío

    Returns:
        list: Lista de tuplas (ip_string, mac_string_lowercase)
    """
    print("[DEBUG] parse_arp_table: Iniciando parseo de tabla ARP")
    entries = []

    # Método 1: ip neigh (Linux moderno)
    try:
        print("[DEBUG] parse_arp_table: Intentando método ip neigh")
        proc = run(
            ["ip", "neigh"],
            capture_output=True,
            text=True,
            check=False,
            creationflags=CREATE_NO_WINDOW if system() == "Windows" else 0,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if out.strip():
            for line in out.splitlines():
                m = search(
                    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}).*(lladdr|at)\s+(?P<mac>[0-9a-fA-F:]{11,17})",
                    line,
                )
                if m:
                    entries.append((m.group("ip"), m.group("mac").lower()))
            if entries:
                print(
                    f"[DEBUG] parse_arp_table: Método ip neigh encontró {len(entries)} entradas"
                )
                return _deduplicate_entries(entries)
    except FileNotFoundError:
        print("[DEBUG] parse_arp_table: ip neigh no disponible")
        pass
    except Exception as e:
        print(f"[DEBUG] parse_arp_table: Error en ip neigh: {e}")
        pass

    # Método 2: arp -a (Windows, macOS, Linux legacy)
    try:
        print("[DEBUG] parse_arp_table: Intentando método arp -a")
        proc = run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10.0,  # Agregar timeout de 10 segundos
            creationflags=CREATE_NO_WINDOW if system() == "Windows" else 0,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        print(
            f"[DEBUG] parse_arp_table: arp -a retornó {len(out)} caracteres de output"
        )

        for line in out.splitlines():
            # Patrón para formato (192.168.1.1) at aa:bb:cc:dd:ee:ff
            m = search(
                r"\((?P<ip>\d{1,3}(?:\.\d{1,3}){3})\)\s+at\s+(?P<mac>[0-9a-fA-F:]{11,17})",
                line,
            )
            if not m:
                # Patrón alternativo para Windows: IP address ... Physical Address
                m = search(
                    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+(?P<mac>[0-9a-fA-F\-:]{11,17})",
                    line,
                )

            if m:
                mac = m.group("mac").replace("-", ":").lower()
                entries.append((m.group("ip"), mac))
        print(
            f"[DEBUG] parse_arp_table: Método arp -a encontró {len(entries)} entradas"
        )
    except Exception as e:
        print(f"[DEBUG] parse_arp_table: Error en arp -a: {e}")
        pass

    result = _deduplicate_entries(entries)
    print(f"[DEBUG] parse_arp_table: Retornando {len(result)} entradas deduplicadas")
    return result


def _deduplicate_entries(entries):
    """Elimina entradas duplicadas, manteniendo la última MAC para cada IP."""
    seen = {}
    for ip, mac in entries:
        if mac and mac != "00:00:00:00:00:00":
            seen[ip] = mac
    return list(seen.items())


def get_mac_for_ip(ip):
    """Busca MAC address para una IP específica en la tabla ARP.

    Args:
        ip: Dirección IP a buscar

    Returns:
        str|None: MAC address en formato aa:bb:cc:dd:ee:ff o None si no se encuentra
    """
    arp_table = parse_arp_table()
    arp_map = dict(arp_table)
    return arp_map.get(ip)
