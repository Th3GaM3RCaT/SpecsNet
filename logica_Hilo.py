
from PySide6.QtCore import QObject, QThread, Signal

class Hilo(QObject):
    terminado = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread = QThread()  # type: ignore
        self.moveToThread(self.thread)  # type: ignore
        self.thread.started.connect(self._run)  # type: ignore
        self.thread.finished.connect(self.thread.deleteLater)  # type: ignore

    def _run(self):
        try:
            resultado = self.func(*self.args, **self.kwargs)
            self.terminado.emit(resultado)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.thread.quit()  # type: ignore

    def start(self):
        self.thread.start()  # type: ignore


class HiloConProgreso(QObject):
    """Hilo con señal de progreso para actualizar UI en tiempo real"""
    terminado = Signal(object)
    error = Signal(str)
    progreso = Signal(object)  # Emite datos de progreso (ip, estado, index, total, etc)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread = QThread()  # type: ignore
        self.moveToThread(self.thread)  # type: ignore
        self.thread.started.connect(self._run)  # type: ignore
        self.thread.finished.connect(self.thread.deleteLater)  # type: ignore

    def _run(self):
        try:
            # La función debe aceptar un callback de progreso
            resultado = self.func(*self.args, callback_progreso=self.progreso.emit, **self.kwargs)
            self.terminado.emit(resultado)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.thread.quit()  # type: ignore

    def start(self):
        self.thread.start()  # type: ignore
