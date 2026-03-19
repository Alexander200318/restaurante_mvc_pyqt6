from models import RestauranteModel


class RestauranteController:
    def __init__(self, model: RestauranteModel) -> None:
        self.model = model

    def registrar_plato(self, nombre: str, precio: float) -> str:
        plato = self.model.registrar_plato(nombre, precio)
        return f"Plato '{plato.nombre}' registrado exitosamente"

    def registrar_cliente(self, nombre: str, mesa: int) -> str:
        cliente = self.model.registrar_cliente(nombre, mesa)
        return f"Cliente '{cliente.nombre}' registrado en la mesa {cliente.mesa}"

    def iniciar_pedido(self, indice_cliente: int) -> str:
        pedido = self.model.iniciar_pedido(indice_cliente)
        return f"Pedido iniciado para {pedido.cliente}"

    def agregar_plato_a_pedido(self, indice_plato: int) -> str:
        plato = self.model.agregar_plato_a_pedido(indice_plato)
        return f"'{plato.nombre}' agregado al pedido"

    def finalizar_pedido(self) -> str:
        pedido = self.model.finalizar_pedido()
        return (
            "Pedido creado exitosamente\n\n"
            f"{pedido.detalle_texto()}"
        )

    def cancelar_pedido(self) -> str:
        self.model.cancelar_pedido()
        return "Pedido en proceso cancelado"

    def obtener_clientes(self) -> list[str]:
        return [str(cliente) for cliente in self.model.clientes_registrados]

    def obtener_platos(self) -> list[str]:
        return [str(plato) for plato in self.model.platos_disponibles]

    def obtener_pedido_en_proceso(self) -> tuple[str, list[str], float]:
        pedido = self.model.pedido_en_proceso
        if pedido is None:
            return "Sin pedido en proceso", [], 0.0
        platos = [str(plato) for plato in pedido.lista_platos]
        return str(pedido.cliente), platos, pedido.calcular_total()

    def hay_pedido_en_proceso(self) -> bool:
        return self.model.pedido_en_proceso is not None

    def obtener_pedidos_detalle(self) -> str:
        if not self.model.pedidos_realizados:
            return "No hay pedidos registrados."

        lineas: list[str] = []
        for i, pedido in enumerate(self.model.pedidos_realizados, 1):
            lineas.append(f"Pedido #{i}")
            lineas.append(pedido.detalle_texto())
            lineas.append("")
        return "\n".join(lineas).strip()

    def obtener_total_pedidos_lineas(self) -> list[str]:
        if not self.model.pedidos_realizados:
            return ["No hay pedidos registrados."]

        lineas: list[str] = []
        for i, pedido in enumerate(self.model.pedidos_realizados, 1):
            lineas.append(f"Pedido #{i} - {pedido.cliente}: ${pedido.calcular_total():.2f}")
        return lineas

    def obtener_total_general(self) -> float:
        return self.model.total_general_pedidos()
