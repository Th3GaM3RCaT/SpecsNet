import sys
import sqlite3
from typing import Literal, Optional
from os.path import join, exists

# Inicializar base de datos
def inicializar_db():
    """Crea las tablas de la base de datos si no existen."""
    # Detecta si está corriendo empaquetado con PyInstaller
    if hasattr(sys, "_MEIPASS"):
        base_path = join(sys._MEIPASS, "sql_specs") # type: ignore
    else:
        base_path = "sql_specs"
    
    schema_path = join(base_path, "specs.sql")
    
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        # Conectar y ejecutar schema
        conn = sqlite3.connect("specs.db")
        cur = conn.cursor()
        
        # Verificar si ya existen las tablas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Dispositivos'")
        if not cur.fetchone():
            print("⚙ Inicializando base de datos...")
            cur.executescript(schema_sql)
            conn.commit()
            print("✓ Base de datos creada correctamente")
        
        conn.close()
    except Exception as e:
        print(f"⚠ Error inicializando base de datos: {e}")

# Inicializar DB al importar el módulo
inicializar_db()

connection = sqlite3.connect("specs.db", check_same_thread=False)
cursor = connection.cursor()

def get_thread_safe_connection():
    """
    Crea una nueva conexión SQLite para usar en hilos.
    Cada hilo debe usar su propia conexión.
    """
    return sqlite3.connect("specs.db", check_same_thread=False)

#pasar todas las consultas sql solo con esta funcion
def abrir_consulta(
    consulta_sql: Literal[
        "activo-select.sql",
        "almacenamiento-select.sql",
        "aplicaciones-select.sql",
        "Dispositivos-select.sql",
        "informacion-diagnostico-select.sql",
        "memoria-select.sql",
        "registro-cambios-select.sql",
    ],
    condiciones: Optional[dict] = None
) -> tuple[str, tuple]:
    """
    Devuelve la consulta SQL y los parámetros listos para cursor.execute().
    
    Args:
        consulta_sql: Nombre del archivo .sql
        condiciones: Diccionario de filtros {columna: valor}
    
    Returns:
        (consulta_sql_completa, tuple_de_parametros)
    """
    # Detecta si está corriendo empaquetado con PyInstaller
    if hasattr(sys, "_MEIPASS"):
        base_path = join(sys._MEIPASS, "sql_specs", "statement") # type: ignore
    else:
        base_path = join("sql_specs", "statement")
    
    ruta = join(base_path, consulta_sql)
    with open(ruta, "r", encoding="utf-8") as f:
        statements = f.read().strip()
    
    params = ()
    if condiciones:
        # construir cláusula WHERE con placeholders
        clauses = [f"{col} = ?" for col in condiciones.keys()]
        # quitar ; final si existe
        if statements.endswith(";"):
            statements = statements[:-1]
        statements += "\nWHERE " + " AND ".join(clauses) + ";"
        params = tuple(condiciones.values())

    return statements, params

def setaplication(aplicacion=tuple()):
    """
    Inserta o actualiza una aplicación en la BD.
    
    Args:
        aplicacion: (Dispositivos_serial, name, version, publisher)
    """
    sql, params = abrir_consulta("aplicaciones-select.sql", {"name": aplicacion[1], "publisher": aplicacion[3]})
    cursor.execute(sql, params)
    
    if cursor.fetchone():
        # Actualizar versión si ya existe
        cursor.execute("""UPDATE aplicaciones 
                       SET version = ?
                       WHERE name = ? AND publisher = ?""",
                       (aplicacion[2], aplicacion[1], aplicacion[3]))
    else:
        # Insertar nueva aplicación
        cursor.execute("""INSERT INTO aplicaciones 
                       (Dispositivos_serial, name, version, publisher)
                       VALUES (?,?,?,?)""",
                       (aplicacion[0], aplicacion[1], aplicacion[2], aplicacion[3]))


def setAlmacenamiento(almacenamiento=tuple(), indice=1):
    """
    Inserta información de almacenamiento en la BD.
    
    Args:
        almacenamiento: (Dispositivos_serial, nombre, capacidad, tipo, actual, fecha_instalacion)
        indice: Si es 1, marca otros discos del dispositivo como no actuales
    """
    # Verificar si ya existe
    sql, params = abrir_consulta("almacenamiento-select.sql", {"nombre": almacenamiento[1], "capacidad": almacenamiento[2]})
    cursor.execute(sql, params)
    if cursor.fetchone():
        return  # Ya existe, no duplicar
    
    # Si es el primer disco, marcar otros como no actuales
    if indice <= 1:
        cursor.execute("""UPDATE almacenamiento 
                       SET actual = ?
                       WHERE Dispositivos_serial = ?""",
                       (False, almacenamiento[0]))
    
    # Insertar nuevo almacenamiento
    cursor.execute("""INSERT INTO almacenamiento 
                   (Dispositivos_serial, nombre, capacidad, tipo, actual, fecha_instalacion)
                   VALUES (?,?,?,?,?,?)""",
                   (almacenamiento[0], almacenamiento[1], almacenamiento[2], 
                    almacenamiento[3], almacenamiento[4], almacenamiento[5]))


def setMemoria(memoria=tuple(), indice=1):
    """
    Inserta información de módulo RAM en la BD.
    
    Args:
        memoria: (Dispositivos_serial, modulo, fabricante, capacidad, velocidad, numero_serie, actual, fecha_instalacion)
        indice: Si es 1, marca otros módulos del dispositivo como no actuales
    """
    # Verificar si ya existe por número de serie
    sql, params = abrir_consulta("memoria-select.sql", {"numero_serie": memoria[5]})
    cursor.execute(sql, params)
    if cursor.fetchone():
        return  # Ya existe, no duplicar
    
    # Si es el primer módulo, marcar otros como no actuales
    if indice <= 1:
        cursor.execute("""UPDATE memoria 
                       SET actual = ?
                       WHERE Dispositivos_serial = ?""",
                       (False, memoria[0]))
    
    # Insertar nuevo módulo de memoria
    cursor.execute("""INSERT INTO memoria 
                   (Dispositivos_serial, modulo, fabricante, capacidad, velocidad, numero_serie, actual, fecha_instalacion)
                   VALUES (?,?,?,?,?,?,?,?)""",
                   (memoria[0], memoria[1], memoria[2], memoria[3], 
                    memoria[4], memoria[5], memoria[6], memoria[7]))
    







def setInformeDiagnostico(informes = tuple()):
    """Inserta información de diagnóstico de dispositivo en la base de datos.
    
    Args:
        informes (tuple): Tupla con (serial_dispositivo, json_diagnostico, reporteDirectX, fecha)
                         Schema: Dispositivos_serial, json_diagnostico, reporteDirectX, fecha, id (AUTOINCREMENT)
    
    Returns:
        None
    """
    cursor.execute("""INSERT INTO informacion_diagnostico 
                   (Dispositivos_serial, json_diagnostico, reporteDirectX, fecha)
                   VALUES (?,?,?,?)""",
                   (informes[0], informes[1], informes[2], informes[3]))
    
def setResgistro_cambios(registro = tuple()):
    """Registra cambios de especificaciones de hardware/software de un dispositivo.
    
    Args:
        registro (tuple): Tupla con (serial_dispositivo, user, processor, GPU, RAM, disk, 
                         license_status, ip, date)
                         Schema: Dispositivos_serial, user, processor, GPU, RAM, disk, 
                         license_status, ip, date, id (AUTOINCREMENT)
    
    Returns:
        None
    """
    cursor.execute("""INSERT INTO registro_cambios 
                   (Dispositivos_serial, user, processor, GPU, RAM, disk, license_status, ip, date)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                   (registro[0], registro[1], registro[2], registro[3], registro[4], 
                    registro[5], registro[6], registro[7], registro[8]))

def setDevice(info_dispositivo = tuple()):
    """Inserta o actualiza información completa de un dispositivo usando UPSERT.
    
    Args:
        info_dispositivo (tuple): Tupla con (serial, DTI, user, MAC, model, processor, 
                                  GPU, RAM, disk, license_status, ip, activo)
                                  Schema completo de tabla Dispositivos (12 campos)
    
    Returns:
        None
    
    Note:
        Usa ON CONFLICT para actualizar si el serial ya existe. Este es el único caso
        donde UPSERT está justificado por la complejidad de los 12 campos a actualizar.
    """
    cursor.execute("""INSERT INTO Dispositivos 
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(serial) DO UPDATE SET
                       DTI = excluded.DTI,
                       user = excluded.user,
                       MAC = excluded.MAC,
                       model = excluded.model,
                       processor = excluded.processor,
                       GPU = excluded.GPU,
                       RAM = excluded.RAM,
                       disk = excluded.disk,
                       license_status = excluded.license_status,
                       ip = excluded.ip,
                       activo = excluded.activo""",(
            info_dispositivo[0], info_dispositivo[1], info_dispositivo[2], info_dispositivo[3],
            info_dispositivo[4], info_dispositivo[5], info_dispositivo[6], info_dispositivo[7],
            info_dispositivo[8], info_dispositivo[9], info_dispositivo[10], info_dispositivo[11]
    ))

def setActive(dispositivoEstado = tuple()):
    """Inserta estado de actividad de un dispositivo (encendido/apagado).
    
    Args:
        dispositivoEstado (tuple): Tupla con (serial_dispositivo, powerOn, date)
                                  Schema: Dispositivos_serial, powerOn, date 
                                  (sin id porque no tiene PRIMARY KEY AUTOINCREMENT)
    
    Returns:
        None
    
    Warning:
        SIEMPRE usar DELETE antes de INSERT para evitar duplicados (1 registro por dispositivo).
        Ver logica_servidor.py para implementación correcta.
    """
    cursor.execute("""INSERT INTO activo 
                   VALUES (?,?,?)""", (
                       dispositivoEstado[0], dispositivoEstado[1], dispositivoEstado[2]
                       ))


def set_dispositivo_inicial(ip, mac):
    """
    Inserta o actualiza un dispositivo con información básica (IP y MAC).
    Si la MAC ya existe, actualiza la IP.
    Si no existe, crea un nuevo registro con valores por defecto.
    """
    # Usar la MAC como clave temporal para el serial si no existe
    serial_provisional = mac 
    
    cursor.execute("""
        INSERT INTO Dispositivos (serial, MAC, ip, activo) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(MAC) DO UPDATE SET
            ip = excluded.ip;
    """, (serial_provisional, mac, ip, False))
    connection.commit()


#ejemplo de uso
#abrir_consulta("Dispositivos-select.sql","serial","=","'12345'")