import sys
import socket
from logica_Hilo import Hilo

modo_tarea = "--tarea" in sys.argv

def escuchar_broadcast(port=37020, on_message=None):
    """Escucha broadcasts UDP en el puerto especificado."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    print(f"Escuchando broadcast en puerto {port}...")

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode(errors="ignore")
            print(f"Mensaje recibido de {addr}: {mensaje}")
            
            if on_message:
                try:
                    on_message(mensaje, addr)
                except Exception as e:
                    print(f"Error en callback: {e}")
    except KeyboardInterrupt:
        print("Cliente detenido.")
    finally:
        sock.close()


if modo_tarea:
    # Modo tarea programada: escucha broadcasts en background
    import threading
    hilo = threading.Thread(target=escuchar_broadcast, daemon=True)
    hilo.start()
    hilo.join()
else:
    # Modo GUI: interfaz gráfica
    from sys import argv
    from json import dump
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow,
                                   QPushButton, QScrollArea, QVBoxLayout,
                                   QWidget)
    from ui.specs_window_ui import Ui_MainWindow
    import logica_specs as lsp

    app = QApplication(argv)
    class MainWindow(QMainWindow, Ui_MainWindow):
        """Ventana principal del cliente de especificaciones."""

        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.hilo_enviar = None
            self.hilo_informe = None
            self.hilo_infDirectX = None
            self.vbox = QVBoxLayout()
            self.initUI()

        def initUI(self):
            """Inicializa señales y conexiones de la UI."""
            self.run_button.clicked.connect(self.iniciar_informe)
            self.send_button.clicked.connect(self.enviar)
            self.actionDetener_ejecuci_n.triggered.connect(lambda: lsp.configurar_tarea(2))
            self.actionProgramar_hora_de_ejecuci_n.triggered.connect(lambda: lsp.configurar_tarea(0))

        def informeDirectX(self):
            """Ejecuta reporte DirectX en background."""
            from datos.informeDirectX import get_from_inform
            self.hilo_infDirectX = Hilo(get_from_inform)
            self.hilo_infDirectX.error.connect(lambda e: self.statusbar.showMessage(f"Error: {e}"))
            self.hilo_infDirectX.start()
        
        def iniciar_informe(self):
            """Inicia recopilación de información del sistema."""
            self.informeDirectX()
            self.run_button.setEnabled(False)
            self.hilo_informe = Hilo(lsp.informe)
            self.hilo_informe.terminado.connect(self.entregar_informe_seguro)
            self.hilo_informe.error.connect(lambda e: self.statusbar.showMessage(f"Error: {e}"))
            self.hilo_informe.start()
       
        def entregar_informe_seguro(self, resultado):
            """Actualiza UI con el informe generado (thread-safe)."""
            self.entregar_informe(resultado)
            widget = QWidget()
            widget.setLayout(self.vbox)
            self.info_scrollArea.setWidget(widget)

        def entregar_informe(self, informe=dict()):
            """Muestra el informe en la interfaz."""
            for keys, values in informe.items():
                label = QLabel(f"{keys}: {values}")
                label.setTextInteractionFlags(
                    Qt.TextInteractionFlag.TextSelectableByMouse
                    | Qt.TextInteractionFlag.TextSelectableByKeyboard
                )
                self.vbox.addWidget(label)
            self.send_button.setEnabled(True)

        def enviar(self):
            """Envía especificaciones al servidor."""
            self.send_button.setEnabled(False)
            with open("salida.json", "w", encoding="utf-8") as f:
                dump(lsp.new, f, indent=4)
            self.hilo_enviar = Hilo(lsp.enviar_a_servidor)
            self.hilo_enviar.start()


    if __name__ == "__main__":
        if "--task" in argv:
            print("modo tarea")
        else:
            window = MainWindow()
            window.show()
            sys.exit(app.exec())
