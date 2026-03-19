from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from controllers import RestauranteController


class RestauranteWindow(QMainWindow):
    def __init__(self, controller: RestauranteController) -> None:
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Sistema de Restaurante - MVC")
        self.resize(980, 650)

        self._build_ui()
        self.refresh_all()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        titulo = QLabel("Sistema de Restaurante - PyQt6 MVC")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_tab_registros(), "Registros")
        self.tabs.addTab(self._create_tab_pedido(), "Crear pedido")
        self.tabs.addTab(self._create_tab_pedidos(), "Pedidos")
        self.tabs.addTab(self._create_tab_totales(), "Totales")
        layout.addWidget(self.tabs)

    def _create_tab_registros(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)

        box_plato = QGroupBox("Registrar plato")
        box_plato_layout = QFormLayout(box_plato)
        self.input_plato_nombre = QLineEdit()
        self.input_plato_precio = QDoubleSpinBox()
        self.input_plato_precio.setRange(0.01, 100000.0)
        self.input_plato_precio.setDecimals(2)
        self.input_plato_precio.setPrefix("$")
        btn_plato = QPushButton("Registrar plato")
        btn_plato.clicked.connect(self.on_registrar_plato)

        box_plato_layout.addRow("Nombre:", self.input_plato_nombre)
        box_plato_layout.addRow("Precio:", self.input_plato_precio)
        box_plato_layout.addRow(btn_plato)

        box_cliente = QGroupBox("Registrar cliente")
        box_cliente_layout = QFormLayout(box_cliente)
        self.input_cliente_nombre = QLineEdit()
        self.input_cliente_mesa = QSpinBox()
        self.input_cliente_mesa.setRange(1, 10000)
        btn_cliente = QPushButton("Registrar cliente")
        btn_cliente.clicked.connect(self.on_registrar_cliente)

        box_cliente_layout.addRow("Nombre:", self.input_cliente_nombre)
        box_cliente_layout.addRow("Mesa:", self.input_cliente_mesa)
        box_cliente_layout.addRow(btn_cliente)

        layout.addWidget(box_plato)
        layout.addWidget(box_cliente)
        return tab

    def _create_tab_pedido(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        fila_superior = QHBoxLayout()
        self.combo_clientes = QComboBox()
        btn_iniciar = QPushButton("Iniciar pedido")
        btn_iniciar.clicked.connect(self.on_iniciar_pedido)

        fila_superior.addWidget(QLabel("Cliente:"))
        fila_superior.addWidget(self.combo_clientes)
        fila_superior.addWidget(btn_iniciar)
        layout.addLayout(fila_superior)

        seccion_listas = QHBoxLayout()

        box_platos = QGroupBox("Platos disponibles")
        box_platos_layout = QVBoxLayout(box_platos)
        self.list_platos = QListWidget()
        btn_agregar = QPushButton("Agregar plato al pedido")
        btn_agregar.clicked.connect(self.on_agregar_plato)
        box_platos_layout.addWidget(self.list_platos)
        box_platos_layout.addWidget(btn_agregar)

        box_pedido = QGroupBox("Pedido en proceso")
        box_pedido_layout = QVBoxLayout(box_pedido)
        self.label_cliente_actual = QLabel("Sin pedido en proceso")
        self.list_pedido_actual = QListWidget()
        self.label_total_actual = QLabel("Total actual: $0.00")

        fila_acciones = QHBoxLayout()
        btn_finalizar = QPushButton("Finalizar pedido")
        btn_finalizar.clicked.connect(self.on_finalizar_pedido)
        btn_cancelar = QPushButton("Cancelar pedido")
        btn_cancelar.clicked.connect(self.on_cancelar_pedido)
        fila_acciones.addWidget(btn_finalizar)
        fila_acciones.addWidget(btn_cancelar)

        box_pedido_layout.addWidget(self.label_cliente_actual)
        box_pedido_layout.addWidget(self.list_pedido_actual)
        box_pedido_layout.addWidget(self.label_total_actual)
        box_pedido_layout.addLayout(fila_acciones)

        seccion_listas.addWidget(box_platos)
        seccion_listas.addWidget(box_pedido)
        layout.addLayout(seccion_listas)
        return tab

    def _create_tab_pedidos(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.text_pedidos = QTextEdit()
        self.text_pedidos.setReadOnly(True)
        btn_refrescar = QPushButton("Refrescar pedidos")
        btn_refrescar.clicked.connect(self.refresh_all)

        layout.addWidget(self.text_pedidos)
        layout.addWidget(btn_refrescar)
        return tab

    def _create_tab_totales(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.list_totales = QListWidget()
        self.label_total_general = QLabel("Total general: $0.00")
        self.label_total_general.setStyleSheet("font-size: 18px; font-weight: bold;")
        btn_refrescar = QPushButton("Refrescar totales")
        btn_refrescar.clicked.connect(self.refresh_all)

        layout.addWidget(self.list_totales)
        layout.addWidget(self.label_total_general)
        layout.addWidget(btn_refrescar)
        return tab

    def on_registrar_plato(self) -> None:
        nombre = self.input_plato_nombre.text()
        precio = float(self.input_plato_precio.value())
        try:
            mensaje = self.controller.registrar_plato(nombre, precio)
        except ValueError as err:
            self._show_error(str(err))
            return

        self.input_plato_nombre.clear()
        self.input_plato_precio.setValue(0.01)
        self.refresh_all()
        self._show_info(mensaje)

    def on_registrar_cliente(self) -> None:
        nombre = self.input_cliente_nombre.text()
        mesa = int(self.input_cliente_mesa.value())
        try:
            mensaje = self.controller.registrar_cliente(nombre, mesa)
        except ValueError as err:
            self._show_error(str(err))
            return

        self.input_cliente_nombre.clear()
        self.input_cliente_mesa.setValue(1)
        self.refresh_all()
        self._show_info(mensaje)

    def on_iniciar_pedido(self) -> None:
        indice = self.combo_clientes.currentIndex()
        if indice < 0:
            self._show_error("Debe registrar y seleccionar un cliente")
            return

        try:
            mensaje = self.controller.iniciar_pedido(indice)
        except ValueError as err:
            self._show_error(str(err))
            return

        self.refresh_all()
        self._show_info(mensaje)

    def on_agregar_plato(self) -> None:
        if not self.controller.hay_pedido_en_proceso():
            self._show_error("Primero inicie un pedido")
            return

        indice = self.list_platos.currentRow()
        if indice < 0:
            self._show_error("Seleccione un plato para agregar")
            return

        try:
            mensaje = self.controller.agregar_plato_a_pedido(indice)
        except ValueError as err:
            self._show_error(str(err))
            return

        self.refresh_all()
        self._show_info(mensaje)

    def on_finalizar_pedido(self) -> None:
        try:
            mensaje = self.controller.finalizar_pedido()
        except ValueError as err:
            self._show_error(str(err))
            return

        self.refresh_all()
        self._show_info(mensaje)

    def on_cancelar_pedido(self) -> None:
        if not self.controller.hay_pedido_en_proceso():
            self._show_error("No hay pedido en proceso")
            return

        mensaje = self.controller.cancelar_pedido()
        self.refresh_all()
        self._show_info(mensaje)

    def refresh_all(self) -> None:
        self._refresh_clientes()
        self._refresh_platos()
        self._refresh_pedido_actual()
        self._refresh_pedidos_texto()
        self._refresh_totales()

    def _refresh_clientes(self) -> None:
        clientes = self.controller.obtener_clientes()
        self.combo_clientes.clear()
        self.combo_clientes.addItems(clientes)

    def _refresh_platos(self) -> None:
        platos = self.controller.obtener_platos()
        self.list_platos.clear()
        self.list_platos.addItems(platos)

    def _refresh_pedido_actual(self) -> None:
        cliente, platos, total = self.controller.obtener_pedido_en_proceso()
        self.label_cliente_actual.setText(f"Cliente actual: {cliente}")

        self.list_pedido_actual.clear()
        self.list_pedido_actual.addItems(platos)
        self.label_total_actual.setText(f"Total actual: ${total:.2f}")

    def _refresh_pedidos_texto(self) -> None:
        self.text_pedidos.setText(self.controller.obtener_pedidos_detalle())

    def _refresh_totales(self) -> None:
        lineas = self.controller.obtener_total_pedidos_lineas()
        total = self.controller.obtener_total_general()

        self.list_totales.clear()
        self.list_totales.addItems(lineas)
        self.label_total_general.setText(f"Total general: ${total:.2f}")

    def _show_info(self, mensaje: str) -> None:
        QMessageBox.information(self, "Informacion", mensaje)

    def _show_error(self, mensaje: str) -> None:
        QMessageBox.warning(self, "Error", mensaje)
