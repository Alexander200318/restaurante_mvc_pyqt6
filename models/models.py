from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Cliente:
    nombre: str
    mesa: int

    def __str__(self) -> str:
        return f"{self.nombre} (Mesa {self.mesa})"


@dataclass
class Plato:
    nombre: str
    precio: float

    def __str__(self) -> str:
        return f"{self.nombre} - ${self.precio:.2f}"


@dataclass
class Pedido:
    cliente: Cliente
    lista_platos: List[Plato] = field(default_factory=list)

    def agregar_plato(self, plato: Plato) -> None:
        self.lista_platos.append(plato)

    def calcular_total(self) -> float:
        return sum(plato.precio for plato in self.lista_platos)

    def detalle_texto(self) -> str:
        lineas = ["=" * 50, f"Cliente: {self.cliente}", "=" * 50]
        if not self.lista_platos:
            lineas.append("  (Sin platos)")
        else:
            for i, plato in enumerate(self.lista_platos, 1):
                lineas.append(f"  {i}. {plato}")
        lineas.extend(["-" * 50, f"TOTAL: ${self.calcular_total():.2f}", "=" * 50])
        return "\n".join(lineas)


class RestauranteModel:
    def __init__(self) -> None:
        self.platos_disponibles: List[Plato] = []
        self.clientes_registrados: List[Cliente] = []
        self.pedidos_realizados: List[Pedido] = []
        self.pedido_en_proceso: Optional[Pedido] = None

    def registrar_plato(self, nombre: str, precio: float) -> Plato:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del plato no puede estar vacio")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0")

        plato = Plato(nombre=nombre, precio=precio)
        self.platos_disponibles.append(plato)
        return plato

    def registrar_cliente(self, nombre: str, mesa: int) -> Cliente:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del cliente no puede estar vacio")
        if mesa <= 0:
            raise ValueError("El numero de mesa debe ser mayor a 0")

        cliente = Cliente(nombre=nombre, mesa=mesa)
        self.clientes_registrados.append(cliente)
        return cliente

    def iniciar_pedido(self, indice_cliente: int) -> Pedido:
        if not self.clientes_registrados:
            raise ValueError("No hay clientes registrados")
        if not self.platos_disponibles:
            raise ValueError("No hay platos disponibles")
        if not (0 <= indice_cliente < len(self.clientes_registrados)):
            raise ValueError("Cliente invalido")

        cliente = self.clientes_registrados[indice_cliente]
        self.pedido_en_proceso = Pedido(cliente=cliente)
        return self.pedido_en_proceso

    def agregar_plato_a_pedido(self, indice_plato: int) -> Plato:
        if self.pedido_en_proceso is None:
            raise ValueError("No hay pedido en proceso")
        if not (0 <= indice_plato < len(self.platos_disponibles)):
            raise ValueError("Plato invalido")

        plato = self.platos_disponibles[indice_plato]
        self.pedido_en_proceso.agregar_plato(plato)
        return plato

    def finalizar_pedido(self) -> Pedido:
        if self.pedido_en_proceso is None:
            raise ValueError("No hay pedido en proceso")
        if not self.pedido_en_proceso.lista_platos:
            raise ValueError("No se agregaron platos. Pedido cancelado")

        pedido = self.pedido_en_proceso
        self.pedidos_realizados.append(pedido)
        self.pedido_en_proceso = None
        return pedido

    def cancelar_pedido(self) -> None:
        self.pedido_en_proceso = None

    def total_general_pedidos(self) -> float:
        return sum(pedido.calcular_total() for pedido in self.pedidos_realizados)
