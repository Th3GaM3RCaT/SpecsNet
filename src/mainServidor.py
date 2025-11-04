from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QMainWindow
import sys
import asyncio
from ui.inventario_ui import Ui_MainWindow  # Importar el .ui convertido
from sql.consultas_sql import cursor, abrir_consulta  # Funciones de DB
from logica import logica_servidor as ls  # Importar lógica del servidor
from logica.logica_Hilo import Hilo, HiloConProgreso  # Para operaciones en background

class InventarioWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Hilos para operaciones de red
        self.hilo_servidor = None
        self.hilo_escaneo = None
        self.hilo_consulta = None
        
        # Mapa de IP a fila de tabla para actualización en tiempo real
        self.ip_to_row = {}
        
        # Agregar emojis a los botones después de cargar la UI
        #self.agregar_iconos_texto()
        
        # Conectar señales
        self.ui.tableDispositivos.itemSelectionChanged.connect(self.on_dispositivo_seleccionado)
        self.ui.lineEditBuscar.textChanged.connect(self.filtrar_dispositivos)
        self.ui.comboBoxFiltro.currentTextChanged.connect(self.aplicar_filtro)
        self.ui.btnActualizar.clicked.connect(self.iniciar_escaneo_completo)  # Cambio: ahora hace escaneo completo
        
        # Botones de acciones
        self.ui.btnVerDiagnostico.clicked.connect(self.ver_diagnostico)
        self.ui.btnVerAplicaciones.clicked.connect(self.ver_aplicaciones)
        self.ui.btnVerAlmacenamiento.clicked.connect(self.ver_almacenamiento)
        self.ui.btnVerMemoria.clicked.connect(self.ver_memoria)
        self.ui.btnVerHistorialCambios.clicked.connect(self.ver_historial)
        
        # Botón de escaneo inicial (opcional)
        btn_escanear = getattr(self.ui, 'btnEscanear', None)
        if btn_escanear:
            btn_escanear.clicked.connect(self.iniciar_escaneo_completo)
        self.configurar_tabla()
        
        # Deshabilitar botones hasta seleccionar dispositivo
        self.deshabilitar_botones_detalle()
        
        # Cargar datos iniciales y verificar si hay datos
        self.cargar_datos_iniciales()
        
        # Iniciar servidor en segundo plano
        self.iniciar_servidor()
    
    def cargar_datos_iniciales(self):
        """Carga datos de la DB. Si no hay datos, inicia actualización automática."""
        try:
            # Verificar si hay dispositivos en la DB
            cursor.execute("SELECT COUNT(*) FROM Dispositivos")
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Hay datos, cargarlos
                print(f">> Cargando {count} dispositivos de la DB...")
                self.cargar_dispositivos()
            else:
                # No hay datos, iniciar actualización automática
                print(">> DB vacía - Iniciando actualización automática...")
                self.ui.statusbar.showMessage(">> DB vacía - Iniciando escaneo automático...", 0)
                # Esperar 1 segundo y luego iniciar escaneo
                QtCore.QTimer.singleShot(1000, self.iniciar_escaneo_completo)
        except Exception as e:
            print(f"Error verificando DB: {e}")
            self.ui.statusbar.showMessage(f"ERROR: No se pudo acceder a la DB", 5000)
    
    
    def iniciar_servidor(self):
        """Inicia el servidor TCP en segundo plano para recibir datos de clientes."""
        def iniciar_tcp():
            ls.main()
        
        self.hilo_servidor = Hilo(iniciar_tcp)
        self.hilo_servidor.start()
        self.ui.statusbar.showMessage(">> Servidor iniciado - Esperando conexiones de clientes", 3000)
        print("Servidor TCP iniciado en puerto 5255")
    
    def configurar_tabla(self):
        """Configura el ancho de columnas y otros ajustes de la tabla"""
        header = self.ui.tableDispositivos.horizontalHeader()
        
        # Ajustar ancho de columnas
        self.ui.tableDispositivos.setColumnWidth(0, 80)   # Estado
        self.ui.tableDispositivos.setColumnWidth(1, 60)   # DTI
        self.ui.tableDispositivos.setColumnWidth(2, 90)  # Serial
        self.ui.tableDispositivos.setColumnWidth(3, 120)  # Usuario
        self.ui.tableDispositivos.setColumnWidth(4, 180)  # Modelo
        self.ui.tableDispositivos.setColumnWidth(5, 200)  # Procesador
        self.ui.tableDispositivos.setColumnWidth(6, 80)   # RAM
        self.ui.tableDispositivos.setColumnWidth(7, 150)  # GPU
        self.ui.tableDispositivos.setColumnWidth(8, 85)   # Licencia
        # IP se estira automáticamente
    
    def cargar_dispositivos(self):
        """Carga los dispositivos desde la base de datos y verifica estado con ping"""
        # Limpiar tabla
        self.ui.tableDispositivos.setRowCount(0)
        
        try:
            # Consultar dispositivos desde la DB
            sql, params = abrir_consulta("Dispositivos-select.sql")
            cursor.execute(sql, params)
            dispositivos = cursor.fetchall()
            
            if not dispositivos:
                self.ui.statusbar.showMessage(">> No hay dispositivos en la DB", 3000)
                return
            
            # Limpiar mapa ip_to_row
            self.ip_to_row.clear()
            
            # Llenar tabla primero con estado "Verificando..."
            for dispositivo in dispositivos:
                row_position = self.ui.tableDispositivos.rowCount()
                self.ui.tableDispositivos.insertRow(row_position)
                
                # Desempaquetar datos
                serial, dti, user, mac, model, processor, gpu, ram, disk, license_status, ip, activo = dispositivo
                
                # Guardar mapeo ip -> row
                if ip:
                    self.ip_to_row[ip] = row_position
                
                # Columna Estado (inicialmente "Verificando...")
                estado_item = QtWidgets.QTableWidgetItem("[...]")
                estado_item.setBackground(QBrush(QColor(255, 255, 200)))
                self.ui.tableDispositivos.setItem(row_position, 0, estado_item)
                
                # Resto de columnas
                self.ui.tableDispositivos.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(dti or '-')))
                self.ui.tableDispositivos.setItem(row_position, 2, QtWidgets.QTableWidgetItem(serial))
                self.ui.tableDispositivos.setItem(row_position, 3, QtWidgets.QTableWidgetItem(user or '-'))
                self.ui.tableDispositivos.setItem(row_position, 4, QtWidgets.QTableWidgetItem(model or '-'))
                self.ui.tableDispositivos.setItem(row_position, 5, QtWidgets.QTableWidgetItem(processor or '-'))
                self.ui.tableDispositivos.setItem(row_position, 6, QtWidgets.QTableWidgetItem(str(ram or '-')))
                self.ui.tableDispositivos.setItem(row_position, 7, QtWidgets.QTableWidgetItem(gpu or '-'))
                
                # Licencia con color
                lic_item = QtWidgets.QTableWidgetItem("[OK] Activa" if license_status else "[X] Inactiva")
                if not license_status:
                    lic_item.setForeground(QBrush(QColor(200, 0, 0)))
                self.ui.tableDispositivos.setItem(row_position, 8, lic_item)
                
                self.ui.tableDispositivos.setItem(row_position, 9, QtWidgets.QTableWidgetItem(ip or '-'))
            
            # Actualizar contador
            self.ui.labelContador.setText(f"Mostrando {len(dispositivos)} dispositivos")
            
            # Verificar estado de conexión en background
            self.verificar_estados_conexion(dispositivos)
            
        except Exception as e:
            print(f"Error consultando base de datos: {e}")
            import traceback
            traceback.print_exc()
            self.ui.statusbar.showMessage(f"ERROR: Error cargando datos: {e}", 5000)
    
    def verificar_estados_conexion(self, dispositivos):
        """Verifica el estado de conexión (ping) de todos los dispositivos en background"""
        
        def verificar_estados():
            async def ping_dispositivo(ip, row):
                """Hace ping a un dispositivo y actualiza la UI"""
                try:
                    if not ip or ip == '-':
                        return (row, False, "sin_ip")
                    
                    # Ping con timeout de 1 segundo
                    proc = await asyncio.create_subprocess_exec(
                        "ping", "-n", "1", "-w", "1000", ip,
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL
                    )
                    returncode = await proc.wait()
                    conectado = (returncode == 0)
                    return (row, conectado, ip)
                except Exception as e:
                    return (row, False, ip)
            
            async def verificar_todos():
                # Crear tareas para todos los dispositivos
                tareas = []
                for idx, dispositivo in enumerate(dispositivos):
                    ip = dispositivo[10]  # IP está en posición 10
                    tareas.append(ping_dispositivo(ip, idx))
                
                # Ejecutar todos los pings en paralelo
                resultados = await asyncio.gather(*tareas, return_exceptions=True)
                return resultados
            
            # Ejecutar verificación asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                resultados = loop.run_until_complete(verificar_todos())
                return resultados
            finally:
                loop.close()
        
        # Ejecutar en hilo separado
        def callback_estados(resultados):
            # Actualizar UI con resultados (estamos en el thread principal ahora)
            for resultado in resultados:
                if isinstance(resultado, tuple):
                    row, conectado, ip = resultado
                    estado_item = self.ui.tableDispositivos.item(row, 0)
                    
                    if estado_item:  # Verificar que existe
                        if ip == "sin_ip":
                            estado_item.setText("[?] Sin IP")
                            estado_item.setBackground(QBrush(QColor(200, 200, 200)))
                        elif conectado:
                            estado_item.setText("Encendido")
                            estado_item.setBackground(QBrush(QColor(150, 255, 150)))
                        else:
                            estado_item.setText("Apagado")
                            estado_item.setBackground(QBrush(QColor(255, 200, 200)))
            
            print(f">> Verificación de estados completada")
        
        self.hilo_verificacion = Hilo(verificar_estados)
        self.hilo_verificacion.terminado.connect(callback_estados)
        self.hilo_verificacion.start()
        print(">> Verificando estado de conexión de dispositivos...")
    
    def on_consulta_progreso(self, datos):
        """Callback para actualizar estado en tiempo real durante consulta de dispositivos"""
        try:
            ip = datos.get('ip')
            activo = datos.get('activo')
            index = datos.get('index')
            total = datos.get('total')
            
            # Actualizar tabla si tenemos el mapeo
            if ip and ip in self.ip_to_row:
                row = self.ip_to_row[ip]
                estado_item = self.ui.tableDispositivos.item(row, 0)
                
                if estado_item:
                    if activo:
                        estado_item.setText("Encendido")
                        estado_item.setBackground(QBrush(QColor(150, 255, 150)))
                    else:
                        estado_item.setText("Apagado")
                        estado_item.setBackground(QBrush(QColor(255, 200, 200)))
            
            # Mostrar progreso en consola
            if index is not None and total is not None:
                print(f">> Consultando dispositivo {index}/{total}: {ip} - {'Encendido' if activo else 'Apagado'}")
        
        except Exception as e:
            print(f"Error en on_consulta_progreso: {e}")
    
    def on_dispositivo_seleccionado(self):
        """Cuando se selecciona un dispositivo en la tabla"""
        selected_items = self.ui.tableDispositivos.selectedItems()
        if not selected_items:
            self.deshabilitar_botones_detalle()
            return
        
        # Obtener serial de la fila seleccionada
        row = selected_items[0].row()
        serial_item = self.ui.tableDispositivos.item(row, 2)
        if not serial_item:
            return
        serial = serial_item.text()
        
        # Cargar detalles
        self.cargar_detalles_dispositivo(serial)
        self.habilitar_botones_detalle()
    
    def cargar_detalles_dispositivo(self, serial):
        """Carga los detalles del dispositivo seleccionado"""
        # DATOS DE PRUEBA - Reemplazar con consulta real
        if serial == "SN001":
            dti, mac, disk = 101, "00:1A:2B:3C:4D:5E", "512GB SSD"
            ultimo_cambio = ("jperez", "Intel Core i7-11700", "Intel UHD 750", 16, 
                           "512GB SSD", True, "192.168.1.50", "2024-10-15 14:30:00")
        elif serial == "SN002":
            dti, mac, disk = 102, "00:1A:2B:3C:4D:5F", "256GB SSD"
            ultimo_cambio = ("mgarcia", "Intel Core i5-10500", "Intel UHD 630", 8, 
                           "256GB SSD", True, "192.168.1.51", "2024-09-20 10:15:00")
        else:
            dti, mac, disk = 103, "00:1A:2B:3C:4D:60", "512GB SSD"
            ultimo_cambio = None
        
        # CONSULTA REAL (descomenta):
        # sql, params = abrir_consulta("Dispositivos-select.sql", {"serial": serial})
        # cursor.execute(sql, params)
        # dispositivo = cursor.fetchone()
        
        # Actualizar labels de información
        self.ui.labelInfoSerialValue.setText(serial)
        self.ui.labelInfoDTIValue.setText(str(dti or '-'))
        self.ui.labelInfoMACValue.setText(mac or '-')
        self.ui.labelInfoDiscoValue.setText(disk or '-')
        
        # Cargar último cambio
        # sql_cambio = """SELECT user, processor, GPU, RAM, disk, license_status, ip, date 
        #                 FROM registro_cambios 
        #                 WHERE Dispositivos_serial = ? 
        #                 ORDER BY date DESC LIMIT 1"""
        # cursor.execute(sql_cambio, (serial,))
        # ultimo_cambio = cursor.fetchone()
        
        if ultimo_cambio:
            user, processor, gpu, ram, disk, lic, ip, fecha = ultimo_cambio
            self.ui.labelUltimoCambioFecha.setText(f"Fecha: {fecha}")
            
            # Formatear cambios con HTML
            texto_cambio = f"""
            <b>Usuario:</b> {user or '-'}<br>
            <b>Procesador:</b> {processor or '-'}<br>
            <b>GPU:</b> {gpu or '-'}<br>
            <b>RAM:</b> {ram or '-'} GB<br>
            <b>Disco:</b> {disk or '-'}<br>
            <b>Licencia:</b> {'Activa' if lic else 'Inactiva'}<br>
            <b>IP:</b> {ip or '-'}
            """
            self.ui.textEditUltimoCambio.setHtml(texto_cambio)
        else:
            self.ui.labelUltimoCambioFecha.setText("Fecha: Sin cambios registrados")
            self.ui.textEditUltimoCambio.setPlainText("No hay cambios registrados para este dispositivo.")
    
    def deshabilitar_botones_detalle(self):
        """Deshabilita botones cuando no hay selección"""
        self.ui.btnVerDiagnostico.setEnabled(False)
        self.ui.btnVerAplicaciones.setEnabled(False)
        self.ui.btnVerAlmacenamiento.setEnabled(False)
        self.ui.btnVerMemoria.setEnabled(False)
        self.ui.btnVerHistorialCambios.setEnabled(False)
        
        # Limpiar info
        self.ui.labelInfoSerialValue.setText('-')
        self.ui.labelInfoDTIValue.setText('-')
        self.ui.labelInfoMACValue.setText('-')
        self.ui.labelInfoDiscoValue.setText('-')
        self.ui.labelUltimoCambioFecha.setText('Fecha: -')
        self.ui.textEditUltimoCambio.setPlainText('Seleccione un dispositivo para ver los cambios...')
    
    def habilitar_botones_detalle(self):
        """Habilita botones cuando hay selección"""
        self.ui.btnVerDiagnostico.setEnabled(True)
        self.ui.btnVerAplicaciones.setEnabled(True)
        self.ui.btnVerAlmacenamiento.setEnabled(True)
        self.ui.btnVerMemoria.setEnabled(True)
        self.ui.btnVerHistorialCambios.setEnabled(True)
    
    def filtrar_dispositivos(self, texto):
        """Filtra dispositivos según texto de búsqueda"""
        for row in range(self.ui.tableDispositivos.rowCount()):
            match = False
            for col in range(self.ui.tableDispositivos.columnCount()):
                item = self.ui.tableDispositivos.item(row, col)
                if item and texto.lower() in item.text().lower():
                    match = True
                    break
            self.ui.tableDispositivos.setRowHidden(row, not match)
        
        # Actualizar contador
        visible_count = sum(1 for row in range(self.ui.tableDispositivos.rowCount()) 
                          if not self.ui.tableDispositivos.isRowHidden(row))
        self.ui.labelContador.setText(f"Mostrando {visible_count} dispositivos")
    
    def aplicar_filtro(self, filtro):
        """Aplica filtro según combo seleccionado"""
        for row in range(self.ui.tableDispositivos.rowCount()):
            estado_item = self.ui.tableDispositivos.item(row, 0)
            lic_item = self.ui.tableDispositivos.item(row, 8)
            
            mostrar = True
            if filtro == "Activos" and estado_item:
                mostrar = "Inactivo" not in estado_item.text()
            elif filtro == "Inactivos" and estado_item:
                mostrar = "Inactivo" in estado_item.text()
            elif filtro == "Encendidos" and estado_item:
                mostrar = "Encendido" in estado_item.text()
            elif filtro == "Apagados" and estado_item:
                mostrar = "Apagado" in estado_item.text()
            elif filtro == "Sin Licencia" and lic_item:
                mostrar = "Inactiva" in lic_item.text()
            
            self.ui.tableDispositivos.setRowHidden(row, not mostrar)
        
        # Actualizar contador
        visible_count = sum(1 for row in range(self.ui.tableDispositivos.rowCount()) 
                          if not self.ui.tableDispositivos.isRowHidden(row))
        self.ui.labelContador.setText(f"Mostrando {visible_count} dispositivos")
    
    def ver_diagnostico(self):
        """Abre ventana de diagnóstico completo"""
        selected = self.ui.tableDispositivos.selectedItems()
        if selected:
            serial_item = self.ui.tableDispositivos.item(selected[0].row(), 2)
            if serial_item:
                serial = serial_item.text()
                QtWidgets.QMessageBox.information(self, "Diagnóstico", 
                                                f"Abriendo diagnóstico completo de {serial}")
    
    def ver_aplicaciones(self):
        """Abre ventana de aplicaciones instaladas"""
        selected = self.ui.tableDispositivos.selectedItems()
        if selected:
            serial_item = self.ui.tableDispositivos.item(selected[0].row(), 2)
            if serial_item:
                serial = serial_item.text()
                QtWidgets.QMessageBox.information(self, "Aplicaciones", 
                                                f"Mostrando aplicaciones instaladas en {serial}")
    
    def ver_almacenamiento(self):
        """Abre ventana de detalles de almacenamiento"""
        selected = self.ui.tableDispositivos.selectedItems()
        if selected:
            serial_item = self.ui.tableDispositivos.item(selected[0].row(), 2)
            if serial_item:
                serial = serial_item.text()
                QtWidgets.QMessageBox.information(self, "Almacenamiento", 
                                                f"Detalles de almacenamiento de {serial}")
    
    def ver_memoria(self):
        """Abre ventana de detalles de memoria"""
        selected = self.ui.tableDispositivos.selectedItems()
        if selected:
            serial_item = self.ui.tableDispositivos.item(selected[0].row(), 2)
            if serial_item:
                serial = serial_item.text()
                QtWidgets.QMessageBox.information(self, "Memoria RAM", 
                                                f"Detalles de memoria RAM de {serial}")
    
    def ver_historial(self):
        """Abre ventana de historial completo de cambios"""
        selected = self.ui.tableDispositivos.selectedItems()
        if selected:
            serial_item = self.ui.tableDispositivos.item(selected[0].row(), 2)
            if serial_item:
                serial = serial_item.text()
                QtWidgets.QMessageBox.information(self, "Historial", 
                                                f"Historial completo de cambios de {serial}")
    
    def iniciar_escaneo_completo(self):
        """
        Flujo completo:
        1. Escanear red con optimized_block_scanner.py
        2. Poblar DB inicial con IPs/MACs del CSV
        3. Solicitar datos completos a cada cliente
        4. Actualizar tabla
        """
        self.ui.statusbar.showMessage("Paso 1/4: Iniciando escaneo de red...", 0)
        self.ui.btnActualizar.setEnabled(False)
        
        # Paso 1: Escanear red
        self.ejecutar_escaneo_red()
    
    def ejecutar_escaneo_red(self):
        """Paso 1: Ejecuta optimized_block_scanner.py"""
        def callback_escaneo():
            import subprocess
            try:
                print("\n=== Ejecutando escaneo de red ===")
                # Ya no se necesitan argumentos - configuracion esta en el archivo
                result = subprocess.run(
                    ['python', 'optimized_block_scanner.py'],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                print(result.stdout)
                if result.stderr:
                    print("Errores:", result.stderr)
                
                if result.returncode == 0:
                    print(">> Escaneo completado exitosamente")
                    return True
                else:
                    print(f">> Error en escaneo: codigo {result.returncode}")
                    return False
            except Exception as e:
                print(f">> Excepcion en escaneo: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        self.hilo_escaneo = Hilo(callback_escaneo)
        self.hilo_escaneo.terminado.connect(self.on_escaneo_terminado)
        self.hilo_escaneo.error.connect(self.on_escaneo_error)
        self.hilo_escaneo.start()
    
    def on_escaneo_terminado(self, resultado):
        """Callback Paso 1 completado"""
        if resultado:
            self.ui.statusbar.showMessage(">> Paso 1/4: Escaneo completado - Poblando DB inicial...", 0)
            # Paso 2: Poblar DB con CSV
            self.poblar_db_desde_csv()
        else:
            self.ui.statusbar.showMessage("ERROR: Error en escaneo de red", 5000)
            self.ui.btnActualizar.setEnabled(True)
    
    def on_escaneo_error(self, error):
        """Error en Paso 1"""
        self.ui.statusbar.showMessage(f"ERROR: Error en escaneo: {error}", 5000)
        self.ui.btnActualizar.setEnabled(True)
    
    def poblar_db_desde_csv(self):
        """Paso 2: Lee CSV y crea registros básicos en DB (solo IP/MAC)"""
        def callback_poblar():
            try:
                print("\n=== Poblando DB desde CSV ===")
                # Crear conexión thread-safe para este hilo
                thread_conn = ls.sql.get_thread_safe_connection()
                thread_cursor = thread_conn.cursor()
                
                # Cargar IPs del CSV
                ips_macs = ls.cargar_ips_desde_csv()
                
                if not ips_macs:
                    print("[!] No se encontraron IPs en el CSV")
                    thread_conn.close()
                    return 0
                
                print(f">> CSV cargado: {len(ips_macs)} entradas")
                insertados = 0
                actualizados = 0
                sin_mac = 0
                
                for ip, mac in ips_macs:
                    # Si tiene MAC, usarla como identificador
                    # Si no tiene MAC, crear serial temporal basado en IP
                    if mac:
                        serial_temp = f"TEMP_{mac.replace(':', '')}"
                        identificador = mac
                        sql_check, params = ls.sql.abrir_consulta("Dispositivos-select.sql", {"MAC": mac})
                    else:
                        # Sin MAC - usar IP como identificador temporal
                        serial_temp = f"TEMP_IP_{ip.replace('.', '_')}"
                        identificador = None
                        sin_mac += 1
                        # Buscar por IP en lugar de MAC
                        sql_check = "SELECT serial, MAC FROM Dispositivos WHERE ip = ?"
                        params = (ip,)
                    
                    # Verificar si ya existe
                    thread_cursor.execute(sql_check, params)
                    existe = thread_cursor.fetchone()
                    
                    if not existe:
                        # Insertar dispositivo básico
                        # serial, DTI, user, MAC, model, processor, GPU, RAM, disk, license_status, ip, activo
                        datos_basicos = (
                            serial_temp,             # Serial temporal
                            None,                    # DTI
                            None,                    # user
                            mac,                     # MAC (puede ser None)
                            "Pendiente escaneo",     # model
                            None,                    # processor
                            None,                    # GPU
                            0,                       # RAM
                            None,                    # disk
                            False,                   # license_status
                            ip,                      # ip
                            False                    # activo (aún no confirmado)
                        )
                        # Insertar usando la conexión del hilo
                        thread_cursor.execute(
                            """INSERT INTO Dispositivos (serial, DTI, user, MAC, model, processor, GPU, RAM, disk, license_status, ip, activo)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            datos_basicos
                        )
                        insertados += 1
                        mac_display = mac if mac else "sin MAC"
                        print(f"  + Insertado: {ip} ({mac_display})")
                    else:
                        # Actualizar IP (y MAC si ahora la tiene)
                        serial_existente = existe[0]
                        mac_existente = existe[1]
                        
                        if mac and not mac_existente:
                            # Ahora tiene MAC, actualizarla también
                            thread_cursor.execute(
                                "UPDATE Dispositivos SET ip = ?, MAC = ? WHERE serial = ?",
                                (ip, mac, serial_existente)
                            )
                            print(f"  ↻ Actualizado IP+MAC: {ip} ({mac})")
                        else:
                            # Solo actualizar IP
                            thread_cursor.execute(
                                "UPDATE Dispositivos SET ip = ? WHERE serial = ?",
                                (ip, serial_existente)
                            )
                            print(f"  ↻ Actualizado IP: {ip}")
                        actualizados += 1
                
                thread_conn.commit()
                thread_conn.close()
                print(f"\n>> Resumen poblado DB:")
                print(f"   - Insertados: {insertados}")
                print(f"   - Actualizados: {actualizados}")
                print(f"   - Sin MAC (pendiente): {sin_mac}")
                print(f"   - Total en DB: {insertados + actualizados}")
                return insertados
                
            except Exception as e:
                print(f">> Error poblando DB: {e}")
                import traceback
                traceback.print_exc()
                return 0
        
        self.hilo_poblado = Hilo(callback_poblar)
        self.hilo_poblado.terminado.connect(self.on_poblado_terminado)
        self.hilo_poblado.error.connect(self.on_poblado_error)
        self.hilo_poblado.start()

    def on_poblado_terminado(self, insertados):
        """Callback Paso 2 completado"""
        self.ui.statusbar.showMessage(f">> Paso 2/4: DB poblada ({insertados} nuevos) - Anunciando servidor...", 0)
        # Paso 3: Anunciar servidor y esperar conexiones
        self.anunciar_y_esperar_clientes()
    
    def on_poblado_error(self, error):
        """Error en Paso 2"""
        self.ui.statusbar.showMessage(f"ERROR: Error poblando DB: {error}", 5000)
        self.ui.btnActualizar.setEnabled(True)
    
    def anunciar_y_esperar_clientes(self):
        """Paso 3: Anuncia servidor y consulta cada cliente con actualizaciones en tiempo real"""
        def callback_anuncio(callback_progreso=None):
            try:
                print("\n=== Anunciando servidor y consultando clientes ===")
                # Anunciar presencia
                print(">> Enviando broadcast...")
                ls.anunciar_ip()
                
                # Esperar un poco para que clientes respondan
                import time
                time.sleep(2)
                
                # Consultar dispositivos desde CSV con callback de progreso
                print(">> Consultando dispositivos...")
                activos, total = ls.consultar_dispositivos_desde_csv(callback_progreso=callback_progreso)
                
                print(f">> Consulta completada: {activos}/{total} dispositivos respondieron")
                return (activos, total)
                
            except Exception as e:
                print(f">> Error en consulta: {e}")
                import traceback
                traceback.print_exc()
                return (0, 0)
        
        # Usar HiloConProgreso para recibir actualizaciones en tiempo real
        self.hilo_consulta = HiloConProgreso(callback_anuncio)
        self.hilo_consulta.progreso.connect(self.on_consulta_progreso)
        self.hilo_consulta.terminado.connect(self.on_consulta_terminada)
        self.hilo_consulta.error.connect(self.on_consulta_error)
        self.hilo_consulta.start()
    
    def on_consulta_terminada(self, resultado):
        """Callback Paso 3 completado"""
        activos, total = resultado
        self.ui.statusbar.showMessage(f">> Paso 3/4: {activos}/{total} clientes respondieron - Actualizando vista...", 0)
        # Paso 4: Recargar tabla
        self.finalizar_escaneo_completo()
    
    def on_consulta_error(self, error):
        """Error en Paso 3"""
        self.ui.statusbar.showMessage(f"ERROR: Error consultando clientes: {error}", 5000)
        self.ui.btnActualizar.setEnabled(True)
    
    def finalizar_escaneo_completo(self):
        """Paso 4: Recargar tabla con datos actualizados"""
        print("\n=== Finalizando escaneo completo ===")
        self.cargar_dispositivos()
        self.ui.statusbar.showMessage(">> Escaneo completo finalizado exitosamente", 5000)
        self.ui.btnActualizar.setEnabled(True)
        print(">> Proceso completado\n")



app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication(sys.argv)

window = InventarioWindow()
window.show()
sys.exit(app.exec())