# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inventario.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        MainWindow.setMinimumSize(QSize(1280, 720))
        MainWindow.setStyleSheet("\n" '    @import url("Combinear.qss");\n' "  ")
        self.actionExportarExcel = QAction(MainWindow)
        self.actionExportarExcel.setObjectName("actionExportarExcel")
        self.actionExportarCSV = QAction(MainWindow)
        self.actionExportarCSV.setObjectName("actionExportarCSV")
        self.actionSalir = QAction(MainWindow)
        self.actionSalir.setObjectName("actionSalir")
        self.actionVerEstadisticas = QAction(MainWindow)
        self.actionVerEstadisticas.setObjectName("actionVerEstadisticas")
        self.actionVerReportes = QAction(MainWindow)
        self.actionVerReportes.setObjectName("actionVerReportes")
        self.actionConfiguracion = QAction(MainWindow)
        self.actionConfiguracion.setObjectName("actionConfiguracion")
        self.actionBackupBD = QAction(MainWindow)
        self.actionBackupBD.setObjectName("actionBackupBD")
        self.actionAcercaDe = QAction(MainWindow)
        self.actionAcercaDe.setObjectName("actionAcercaDe")
        self.actionManual = QAction(MainWindow)
        self.actionManual.setObjectName("actionManual")
        self.actiondetener = QAction(MainWindow)
        self.actiondetener.setObjectName("actiondetener")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.frameHeader = QFrame(self.centralwidget)
        self.frameHeader.setObjectName("frameHeader")
        self.frameHeader.setMaximumSize(QSize(16777215, 66))
        self.frameHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalLayout_header = QHBoxLayout(self.frameHeader)
        self.horizontalLayout_header.setSpacing(15)
        self.horizontalLayout_header.setObjectName("horizontalLayout_header")
        self.labelTitle = QLabel(self.frameHeader)
        self.labelTitle.setObjectName("labelTitle")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.labelTitle.setFont(font)

        self.horizontalLayout_header.addWidget(self.labelTitle)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_header.addItem(self.horizontalSpacer)

        self.labelBuscar = QLabel(self.frameHeader)
        self.labelBuscar.setObjectName("labelBuscar")

        self.horizontalLayout_header.addWidget(self.labelBuscar)

        self.lineEditBuscar = QLineEdit(self.frameHeader)
        self.lineEditBuscar.setObjectName("lineEditBuscar")
        self.lineEditBuscar.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_header.addWidget(self.lineEditBuscar)

        self.ip_start_input = QLineEdit(self.frameHeader)
        self.ip_start_input.setObjectName("ip_start_input")

        self.horizontalLayout_header.addWidget(self.ip_start_input)

        self.ip_end_input = QLineEdit(self.frameHeader)
        self.ip_end_input.setObjectName("ip_end_input")

        self.horizontalLayout_header.addWidget(self.ip_end_input)

        self.scan_button = QPushButton(self.frameHeader)
        self.scan_button.setObjectName("scan_button")

        self.horizontalLayout_header.addWidget(self.scan_button)

        self.labelFiltro = QLabel(self.frameHeader)
        self.labelFiltro.setObjectName("labelFiltro")

        self.horizontalLayout_header.addWidget(self.labelFiltro)

        self.comboBoxFiltro = QComboBox(self.frameHeader)
        self.comboBoxFiltro.addItem("")
        self.comboBoxFiltro.addItem("")
        self.comboBoxFiltro.addItem("")
        self.comboBoxFiltro.addItem("")
        self.comboBoxFiltro.addItem("")
        self.comboBoxFiltro.addItem("")
        self.comboBoxFiltro.setObjectName("comboBoxFiltro")
        self.comboBoxFiltro.setMinimumSize(QSize(150, 0))

        self.horizontalLayout_header.addWidget(self.comboBoxFiltro)

        self.verticalLayout.addWidget(self.frameHeader)

        self.splitterPrincipal = QSplitter(self.centralwidget)
        self.splitterPrincipal.setObjectName("splitterPrincipal")
        self.splitterPrincipal.setMinimumSize(QSize(0, 0))
        self.splitterPrincipal.setOrientation(Qt.Orientation.Horizontal)
        self.splitterPrincipal.setHandleWidth(10)
        self.widgetTabla = QWidget(self.splitterPrincipal)
        self.widgetTabla.setObjectName("widgetTabla")
        self.verticalLayout_tabla = QVBoxLayout(self.widgetTabla)
        self.verticalLayout_tabla.setSpacing(8)
        self.verticalLayout_tabla.setObjectName("verticalLayout_tabla")
        self.verticalLayout_tabla.setContentsMargins(0, 0, 0, 0)
        self.labelContador = QLabel(self.widgetTabla)
        self.labelContador.setObjectName("labelContador")
        font1 = QFont()
        font1.setPointSize(9)
        self.labelContador.setFont(font1)

        self.verticalLayout_tabla.addWidget(self.labelContador)

        self.tableDispositivos = QTableWidget(self.widgetTabla)
        if self.tableDispositivos.columnCount() < 10:
            self.tableDispositivos.setColumnCount(10)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableDispositivos.setHorizontalHeaderItem(9, __qtablewidgetitem9)
        self.tableDispositivos.setObjectName("tableDispositivos")
        self.tableDispositivos.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tableDispositivos.setAlternatingRowColors(False)
        self.tableDispositivos.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tableDispositivos.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tableDispositivos.setSortingEnabled(True)
        self.tableDispositivos.setColumnCount(10)
        self.tableDispositivos.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_tabla.addWidget(self.tableDispositivos)

        self.splitterPrincipal.addWidget(self.widgetTabla)
        self.widgetDetalles = QWidget(self.splitterPrincipal)
        self.widgetDetalles.setObjectName("widgetDetalles")
        self.widgetDetalles.setMinimumSize(QSize(380, 0))
        self.widgetDetalles.setMaximumSize(QSize(450, 16777215))
        self.verticalLayout_detalles = QVBoxLayout(self.widgetDetalles)
        self.verticalLayout_detalles.setSpacing(10)
        self.verticalLayout_detalles.setObjectName("verticalLayout_detalles")
        self.verticalLayout_detalles.setContentsMargins(0, 0, 0, 0)
        self.groupBoxInfo = QGroupBox(self.widgetDetalles)
        self.groupBoxInfo.setObjectName("groupBoxInfo")
        self.verticalLayout_info = QVBoxLayout(self.groupBoxInfo)
        self.verticalLayout_info.setObjectName("verticalLayout_info")
        self.gridLayoutInfo = QGridLayout()
        self.gridLayoutInfo.setObjectName("gridLayoutInfo")
        self.gridLayoutInfo.setHorizontalSpacing(10)
        self.gridLayoutInfo.setVerticalSpacing(8)
        self.labelInfoSerial = QLabel(self.groupBoxInfo)
        self.labelInfoSerial.setObjectName("labelInfoSerial")
        font2 = QFont()
        font2.setBold(True)
        self.labelInfoSerial.setFont(font2)

        self.gridLayoutInfo.addWidget(self.labelInfoSerial, 0, 0, 1, 1)

        self.labelInfoSerialValue = QLabel(self.groupBoxInfo)
        self.labelInfoSerialValue.setObjectName("labelInfoSerialValue")
        self.labelInfoSerialValue.setWordWrap(True)

        self.gridLayoutInfo.addWidget(self.labelInfoSerialValue, 0, 1, 1, 1)

        self.labelInfoDTI = QLabel(self.groupBoxInfo)
        self.labelInfoDTI.setObjectName("labelInfoDTI")
        self.labelInfoDTI.setFont(font2)

        self.gridLayoutInfo.addWidget(self.labelInfoDTI, 1, 0, 1, 1)

        self.labelInfoDTIValue = QLabel(self.groupBoxInfo)
        self.labelInfoDTIValue.setObjectName("labelInfoDTIValue")

        self.gridLayoutInfo.addWidget(self.labelInfoDTIValue, 1, 1, 1, 1)

        self.labelInfoMAC = QLabel(self.groupBoxInfo)
        self.labelInfoMAC.setObjectName("labelInfoMAC")
        self.labelInfoMAC.setFont(font2)

        self.gridLayoutInfo.addWidget(self.labelInfoMAC, 2, 0, 1, 1)

        self.labelInfoMACValue = QLabel(self.groupBoxInfo)
        self.labelInfoMACValue.setObjectName("labelInfoMACValue")
        self.labelInfoMACValue.setWordWrap(True)

        self.gridLayoutInfo.addWidget(self.labelInfoMACValue, 2, 1, 1, 1)

        self.labelInfoDisco = QLabel(self.groupBoxInfo)
        self.labelInfoDisco.setObjectName("labelInfoDisco")
        self.labelInfoDisco.setFont(font2)

        self.gridLayoutInfo.addWidget(self.labelInfoDisco, 3, 0, 1, 1)

        self.labelInfoDiscoValue = QLabel(self.groupBoxInfo)
        self.labelInfoDiscoValue.setObjectName("labelInfoDiscoValue")
        self.labelInfoDiscoValue.setWordWrap(True)

        self.gridLayoutInfo.addWidget(self.labelInfoDiscoValue, 3, 1, 1, 1)

        self.verticalLayout_info.addLayout(self.gridLayoutInfo)

        self.verticalLayout_detalles.addWidget(self.groupBoxInfo)

        self.groupBoxCambio = QGroupBox(self.widgetDetalles)
        self.groupBoxCambio.setObjectName("groupBoxCambio")
        self.verticalLayout_cambio = QVBoxLayout(self.groupBoxCambio)
        self.verticalLayout_cambio.setObjectName("verticalLayout_cambio")
        self.labelUltimoCambioFecha = QLabel(self.groupBoxCambio)
        self.labelUltimoCambioFecha.setObjectName("labelUltimoCambioFecha")
        font3 = QFont()
        font3.setPointSize(9)
        font3.setItalic(True)
        self.labelUltimoCambioFecha.setFont(font3)

        self.verticalLayout_cambio.addWidget(self.labelUltimoCambioFecha)

        self.textEditUltimoCambio = QTextEdit(self.groupBoxCambio)
        self.textEditUltimoCambio.setObjectName("textEditUltimoCambio")
        self.textEditUltimoCambio.setMaximumSize(QSize(16777215, 100))
        self.textEditUltimoCambio.setReadOnly(True)

        self.verticalLayout_cambio.addWidget(self.textEditUltimoCambio)

        self.btnVerHistorialCambios = QPushButton(self.groupBoxCambio)
        self.btnVerHistorialCambios.setObjectName("btnVerHistorialCambios")

        self.verticalLayout_cambio.addWidget(self.btnVerHistorialCambios)

        self.verticalLayout_detalles.addWidget(self.groupBoxCambio)

        self.groupBoxAcciones = QGroupBox(self.widgetDetalles)
        self.groupBoxAcciones.setObjectName("groupBoxAcciones")
        self.verticalLayout_acciones = QVBoxLayout(self.groupBoxAcciones)
        self.verticalLayout_acciones.setSpacing(8)
        self.verticalLayout_acciones.setObjectName("verticalLayout_acciones")
        self.btnVerDiagnostico = QPushButton(self.groupBoxAcciones)
        self.btnVerDiagnostico.setObjectName("btnVerDiagnostico")

        self.verticalLayout_acciones.addWidget(self.btnVerDiagnostico)

        self.btnVerAplicaciones = QPushButton(self.groupBoxAcciones)
        self.btnVerAplicaciones.setObjectName("btnVerAplicaciones")

        self.verticalLayout_acciones.addWidget(self.btnVerAplicaciones)

        self.btnVerAlmacenamiento = QPushButton(self.groupBoxAcciones)
        self.btnVerAlmacenamiento.setObjectName("btnVerAlmacenamiento")

        self.verticalLayout_acciones.addWidget(self.btnVerAlmacenamiento)

        self.btnVerMemoria = QPushButton(self.groupBoxAcciones)
        self.btnVerMemoria.setObjectName("btnVerMemoria")

        self.verticalLayout_acciones.addWidget(self.btnVerMemoria)

        self.verticalLayout_detalles.addWidget(self.groupBoxAcciones)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_detalles.addItem(self.verticalSpacer)

        self.splitterPrincipal.addWidget(self.widgetDetalles)

        self.verticalLayout.addWidget(self.splitterPrincipal)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setFont(font1)
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 21))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName("menuArchivo")
        self.menuVer = QMenu(self.menubar)
        self.menuVer.setObjectName("menuVer")
        self.menuHerramientas = QMenu(self.menubar)
        self.menuHerramientas.setObjectName("menuHerramientas")
        self.menuAyuda = QMenu(self.menubar)
        self.menuAyuda.setObjectName("menuAyuda")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuVer.menuAction())
        self.menubar.addAction(self.menuHerramientas.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())
        self.menuArchivo.addAction(self.actionExportarExcel)
        self.menuArchivo.addAction(self.actionExportarCSV)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionSalir)
        self.menuVer.addAction(self.actionVerEstadisticas)
        self.menuVer.addAction(self.actionVerReportes)
        self.menuHerramientas.addAction(self.actionConfiguracion)
        self.menuHerramientas.addAction(self.actionBackupBD)
        self.menuAyuda.addAction(self.actionAcercaDe)
        self.menuAyuda.addAction(self.actionManual)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate(
                "MainWindow",
                "Sistema de Inventario - \u00c1rea de Inform\u00e1tica",
                None,
            )
        )
        MainWindow.setProperty(
            "qss_file",
            QCoreApplication.translate("MainWindow", "ui/Combinear.qss", None),
        )
        self.actionExportarExcel.setText(
            QCoreApplication.translate("MainWindow", "Exportar a Excel", None)
        )
        self.actionExportarCSV.setText(
            QCoreApplication.translate("MainWindow", "Exportar a CSV", None)
        )
        self.actionSalir.setText(
            QCoreApplication.translate("MainWindow", "Salir", None)
        )
        self.actionVerEstadisticas.setText(
            QCoreApplication.translate("MainWindow", "Estad\u00edsticas", None)
        )
        self.actionVerReportes.setText(
            QCoreApplication.translate("MainWindow", "Generar Reportes", None)
        )
        self.actionConfiguracion.setText(
            QCoreApplication.translate("MainWindow", "Configuraci\u00f3n", None)
        )
        self.actionBackupBD.setText(
            QCoreApplication.translate("MainWindow", "Respaldar Base de Datos", None)
        )
        self.actionAcercaDe.setText(
            QCoreApplication.translate("MainWindow", "Acerca de", None)
        )
        self.actionManual.setText(
            QCoreApplication.translate("MainWindow", "Manual de Usuario", None)
        )
        self.actiondetener.setText(
            QCoreApplication.translate(
                "MainWindow", "Detener anuncios (broadcast)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.actiondetener.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Para reducir ruido en la red, ahorrar recursos, prevenir problemas de seguridad/duplicaci\u00f3n y permitir tareas de mantenimiento o apagado ordenado",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelTitle.setText(
            QCoreApplication.translate("MainWindow", "Inventario de Dispositivos", None)
        )
        self.labelBuscar.setText(
            QCoreApplication.translate("MainWindow", "Buscar:", None)
        )
        self.lineEditBuscar.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "Serial, DTI, Usuario, Modelo...", None
            )
        )
        self.ip_start_input.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "IP Inicio", None)
        )
        self.ip_end_input.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "IP Fin (opcional)", None)
        )
        self.scan_button.setText(
            QCoreApplication.translate("MainWindow", "Iniciar Escaneo", None)
        )
        self.labelFiltro.setText(
            QCoreApplication.translate("MainWindow", "Filtrar:", None)
        )
        self.comboBoxFiltro.setItemText(
            0, QCoreApplication.translate("MainWindow", "Todos", None)
        )
        self.comboBoxFiltro.setItemText(
            1, QCoreApplication.translate("MainWindow", "Activos", None)
        )
        self.comboBoxFiltro.setItemText(
            2, QCoreApplication.translate("MainWindow", "Inactivos", None)
        )
        self.comboBoxFiltro.setItemText(
            3, QCoreApplication.translate("MainWindow", "Encendidos", None)
        )
        self.comboBoxFiltro.setItemText(
            4, QCoreApplication.translate("MainWindow", "Apagados", None)
        )
        self.comboBoxFiltro.setItemText(
            5, QCoreApplication.translate("MainWindow", "Sin Licencia", None)
        )

        self.labelContador.setText(
            QCoreApplication.translate("MainWindow", "Mostrando 0 dispositivos", None)
        )
        ___qtablewidgetitem = self.tableDispositivos.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MainWindow", "Estado", None)
        )
        ___qtablewidgetitem1 = self.tableDispositivos.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MainWindow", "DTI", None)
        )
        ___qtablewidgetitem2 = self.tableDispositivos.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("MainWindow", "Serial", None)
        )
        ___qtablewidgetitem3 = self.tableDispositivos.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("MainWindow", "Usuario", None)
        )
        ___qtablewidgetitem4 = self.tableDispositivos.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("MainWindow", "Modelo", None)
        )
        ___qtablewidgetitem5 = self.tableDispositivos.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("MainWindow", "Procesador", None)
        )
        ___qtablewidgetitem6 = self.tableDispositivos.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate("MainWindow", "RAM (GB)", None)
        )
        ___qtablewidgetitem7 = self.tableDispositivos.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(
            QCoreApplication.translate("MainWindow", "GPU", None)
        )
        ___qtablewidgetitem8 = self.tableDispositivos.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(
            QCoreApplication.translate("MainWindow", "Licencia", None)
        )
        ___qtablewidgetitem9 = self.tableDispositivos.horizontalHeaderItem(9)
        ___qtablewidgetitem9.setText(
            QCoreApplication.translate("MainWindow", "IP", None)
        )
        self.groupBoxInfo.setTitle(
            QCoreApplication.translate(
                "MainWindow", "Informaci\u00f3n del Dispositivo", None
            )
        )
        self.labelInfoSerial.setText(
            QCoreApplication.translate("MainWindow", "Serial:", None)
        )
        self.labelInfoSerialValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.labelInfoDTI.setText(
            QCoreApplication.translate("MainWindow", "DTI:", None)
        )
        self.labelInfoDTIValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.labelInfoMAC.setText(
            QCoreApplication.translate("MainWindow", "MAC:", None)
        )
        self.labelInfoMACValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.labelInfoDisco.setText(
            QCoreApplication.translate("MainWindow", "Disco:", None)
        )
        self.labelInfoDiscoValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.groupBoxCambio.setTitle(
            QCoreApplication.translate(
                "MainWindow", "\u00daltimo Cambio Registrado", None
            )
        )
        self.labelUltimoCambioFecha.setText(
            QCoreApplication.translate("MainWindow", "Fecha: -", None)
        )
        self.textEditUltimoCambio.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "Seleccione un dispositivo para ver los cambios...", None
            )
        )
        self.btnVerHistorialCambios.setText(
            QCoreApplication.translate("MainWindow", "Ver Historial Completo", None)
        )
        self.groupBoxAcciones.setTitle(
            QCoreApplication.translate("MainWindow", "Acciones", None)
        )
        self.btnVerDiagnostico.setText(
            QCoreApplication.translate(
                "MainWindow", "Ver Diagn\u00f3stico Completo", None
            )
        )
        self.btnVerAplicaciones.setText(
            QCoreApplication.translate(
                "MainWindow", "Ver Aplicaciones Instaladas", None
            )
        )
        self.btnVerAlmacenamiento.setText(
            QCoreApplication.translate(
                "MainWindow", "Ver Detalles de Almacenamiento", None
            )
        )
        self.btnVerMemoria.setText(
            QCoreApplication.translate(
                "MainWindow", "Ver Detalles de Memoria RAM", None
            )
        )
        self.menuArchivo.setTitle(
            QCoreApplication.translate("MainWindow", "Archivo", None)
        )
        self.menuVer.setTitle(QCoreApplication.translate("MainWindow", "Ver", None))
        self.menuHerramientas.setTitle(
            QCoreApplication.translate("MainWindow", "Herramientas", None)
        )
        self.menuAyuda.setTitle(QCoreApplication.translate("MainWindow", "Ayuda", None))

    # retranslateUi
