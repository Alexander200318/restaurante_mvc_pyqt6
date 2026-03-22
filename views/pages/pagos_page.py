"""
Página: Gestión de Pagos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.pagos_controller import PagosController
from views.components.treeview_widget import TreeViewWidget
from views.components.dialog_utils import DialogUtils
import config

class PagosPage(ctk.CTkFrame):
    """Módulo de Pagos"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.controller = PagosController()
        self.tabla_pendientes = None
        self.tabla_completados = None
        self.pago_seleccionado = None
        
        self._crear_ui()
        self.refrescar_tablas()
    
    def _crear_ui(self):
        """Crear interfaz"""
        frame_header = ctk.CTkFrame(self, fg_color=config.COLORS["primary"])
        frame_header.pack(fill="x", padx=10, pady=10)
        
        titulo = ctk.CTkLabel(
            frame_header,
            text="💳 Gestión de Pagos",
            text_color=config.COLORS["text_light"],
            font=("Arial", 18, "bold")
        )
        titulo.pack(side="left", padx=10, pady=10)
        
        btn_registrar = ctk.CTkButton(
            frame_header,
            text="💰 Registrar Pago",
            command=self.registrar_pago,
            fg_color=config.COLORS["success"],
            hover_color="#45a049"
        )
        btn_registrar.pack(side="right", padx=5, pady=10)
        
        btn_completar = ctk.CTkButton(
            frame_header,
            text="✓ Completar",
            command=self.completar_pago,
            fg_color=config.COLORS["primary"],
            hover_color="#0d47a1"
        )
        btn_completar.pack(side="right", padx=5, pady=10)
        
        # Pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab: Pendientes
        tab_pendientes = self.tabview.add("⏳ Pendientes")
        frame_pendientes = ctk.CTkFrame(tab_pendientes)
        frame_pendientes.pack(fill="both", expand=True)
        
        self.tabla_pendientes = TreeViewWidget(
            frame_pendientes,
            columnas=["ID", "Cliente", "Mesa", "Monto", "Estado"],
            altura=20
        )
        self.tabla_pendientes.pack(fill="both", expand=True)
        self.tabla_pendientes.set_on_select(self._on_pago_select)
        
        # Tab: Todos
        tab_todos = self.tabview.add("Todos")
        frame_todos = ctk.CTkFrame(tab_todos)
        frame_todos.pack(fill="both", expand=True)
        
        self.tabla_completados = TreeViewWidget(
            frame_todos,
            columnas=["ID", "Cliente", "Monto", "Método", "Estado", "Fecha"],
            altura=20
        )
        self.tabla_completados.pack(fill="both", expand=True)
        
        # Info
        frame_info = ctk.CTkFrame(self, fg_color=config.COLORS["light_bg"])
        frame_info.pack(fill="x", padx=10, pady=10)
        
        self.label_info = ctk.CTkLabel(
            frame_info,
            text="Selecciona un pago pendiente",
            text_color=config.COLORS["text_dark"]
        )
        self.label_info.pack(padx=10, pady=10)
    
    def _on_pago_select(self, datos):
        self.pago_seleccionado = datos
        if datos:
            self.label_info.configure(text=f"Pago #{datos[0]} - {datos[1]}")
    
    def refrescar_tablas(self):
        # Tabla pendientes
        success, datos, msg = self.controller.obtener_pagos_pendientes_formateados()
        if success:
            self.tabla_pendientes.limpiar()
            self.tabla_pendientes.agregar_filas(datos)
        
        # Tabla todos
        success, datos, msg = self.controller.obtener_todos_pagos_formateados()
        if success:
            self.tabla_completados.limpiar()
            self.tabla_completados.agregar_filas(datos)
    
    def registrar_pago(self):
        if not self.pago_seleccionado:
            DialogUtils.mostrar_advertencia(
                "Advertencia",
                "Selecciona un pago pendiente"
            )
            return

        self._abrir_dialogo_pago()
    

    def completar_pago(self):
        if not self.pago_seleccionado:
            DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un pago")
            return

        pago_id = self.pago_seleccionado[0]

        success, _, msg = self.controller.completar_pago(pago_id)

        if success:
        
            self._mostrar_ticket(pago_id)
            self.refrescar_tablas()
        else:
            DialogUtils.mostrar_error("Error", msg)


    def _abrir_dialogo_pago(self):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Registrar Pago")
        dialogo.geometry("350x500")
        dialogo.configure(fg_color="white")
        COLOR_NARANJA = "#ff8c00"

        # -------- Tipo de pago --------
        ctk.CTkLabel(
        dialogo,
        text="Tipo de Pago",
        text_color="black").pack(pady=(10, 0))

        tipo_pago_var = ctk.StringVar(value="Completo")

        ctk.CTkRadioButton(
            dialogo,
            text="Pagar completo",
            variable=tipo_pago_var,
            value="Completo",
            fg_color=COLOR_NARANJA,
            hover_color="#e67600",
            text_color="black"
        ).pack(anchor="w", padx=20)

        ctk.CTkRadioButton(
            dialogo,
            text="Dividir cuenta",
            variable=tipo_pago_var,
            value="Dividido",
            fg_color=COLOR_NARANJA,
            hover_color="#e67600",
            text_color="black"
        ).pack(anchor="w", padx=20)

        # -------- Método de pago --------
        ctk.CTkLabel(dialogo, text="Método de Pago").pack(pady=(15, 0))

        metodos = self.controller.obtener_metodos_disponibles()
        
        metodo_var = ctk.StringVar(value=metodos[0])

        combo_metodo = ctk.CTkComboBox(
            dialogo,
            values=metodos,
            variable=metodo_var,
            fg_color="white",
            border_color=COLOR_NARANJA,
            button_color=COLOR_NARANJA,
            button_hover_color="#e67600",
            text_color="black"
        )
        combo_metodo.pack(pady=5)
        ## .--------------------------

        # -------- Monto --------
        ctk.CTkLabel(dialogo, text="Monto.").pack(pady=(15, 0))
        entry_monto = ctk.CTkEntry(dialogo)
        entry_monto.pack(pady=5)

        # -------- Propina --------
        ctk.CTkLabel(dialogo, text="Propina.").pack(pady=(15, 0))
        entry_propina = ctk.CTkEntry(dialogo)
        entry_propina.pack(pady=5)

        # -------- Función para calcular propina --------
        def calcular_propina(event=None):
            try:
                monto_texto = entry_monto.get()

                if not monto_texto:
                    entry_propina.delete(0, "end")
                    return

                monto = float(monto_texto)
                propina = self.controller.calcular_propina_sugerida(monto)

                entry_propina.delete(0, "end")
                entry_propina.insert(0, str(propina))

            except ValueError:
                entry_propina.delete(0, "end")

        # -------- AQUÍ recién se hace el bind --------
        entry_monto.bind("<KeyRelease>", calcular_propina)



        # -------- Label cliente --------
        label_cliente = ctk.CTkLabel(dialogo, text="", text_color="black")
        label_cliente.pack(pady=(5, 0))

        # -------- Función buscar cliente --------
        def buscar_cliente():
            cedula = entry_cedula.get()

            success, cliente, msg = self.controller.buscar_cliente_por_cedula(cedula)

            if success and cliente:
                nombre_completo = f"{cliente.nombre} {cliente.apellido}"
                label_cliente.configure(text=f"Cliente: {nombre_completo}")
            else:
                label_cliente.configure(text="Cliente no encontrado")




        # -------- Cédula --------
        ctk.CTkLabel(dialogo, text="Cédula").pack(pady=(15, 0))

        frame_cedula = ctk.CTkFrame(dialogo, fg_color="transparent")
        frame_cedula.pack(pady=5)

        entry_cedula = ctk.CTkEntry(frame_cedula)
        entry_cedula.pack(side="left", padx=(0, 5))

        btn_buscar = ctk.CTkButton(
            frame_cedula,
            text="Buscar",
            width=80,
            fg_color=COLOR_NARANJA,
            command=lambda: buscar_cliente()
        )
        btn_buscar.pack(side="left")
                



        # -------- Botón confirmar --------
        def confirmar():
            if not self.pago_seleccionado:
                DialogUtils.mostrar_advertencia("Advertencia", "Selecciona un pago primero")
                return

            pago_id = self.pago_seleccionado[0]
            tipo_pago = tipo_pago_var.get()
            metodo = metodo_var.get()
            monto = entry_monto.get()
            propina = entry_propina.get()
            cedula = entry_cedula.get()

            if not monto:
                DialogUtils.mostrar_advertencia("Advertencia", "Ingresa el monto")
                return

            try:
                monto = float(monto)
                propina = float(propina) if propina else 0.0
            except ValueError:
                DialogUtils.mostrar_error("Error", "Monto o propina inválidos")
                return
            

            if not cedula:
                DialogUtils.mostrar_advertencia("Advertencia", "Ingresa la cédula")
                return

            # -------------------------
            # Obtener datos reales del pago
            # -------------------------
            success_pago, pago, msg = self.controller.obtener_pago(pago_id)
            if not success_pago or not pago:
                DialogUtils.mostrar_error("Error", "No se pudo obtener el pago")
                return

            # -------------------------
            # Evitar pagar dos veces
            # -------------------------
            if pago.estado.value == "PAGADO":
                DialogUtils.mostrar_advertencia("Advertencia", "Este pago ya está completado")
                return

            # -------------------------
            # Procesar pago completo
            # -------------------------
            if tipo_pago == "Completo":
                # Actualizar método primero
                success, _, msg = self.controller.actualizar_pago(
                    pago_id,
                    metodo=metodo
                )

                if success:
                    success, _, msg = self.controller.completar_pago(
                        pago_id,
                        cambio=propina
                    )

            # -------------------------
            # Procesar pago parcial
            # -------------------------
            else:
                if monto <= 0:
                    DialogUtils.mostrar_error("Error", "El monto debe ser mayor a 0")
                    return

                success, _, msg = self.controller.actualizar_pago(
                    pago_id,
                    monto=monto,
                    metodo=metodo
                )

            # -------------------------
            # Resultado final
            # -------------------------
            if success:
                dialogo.destroy()
                self._mostrar_ticket(pago_id)
                self.refrescar_tablas()

            else:
                DialogUtils.mostrar_error("Error", msg)

        #-----------------------------------------------------




        #------------------------------------------------------




        # -------- Botón confirmar --------
        btn_confirmar = ctk.CTkButton(
            dialogo,
            text="Confirmar Pago",
            command=confirmar,
            fg_color=COLOR_NARANJA,
            hover_color="#e67600",
            text_color="black"
        )

        btn_confirmar.pack(
            pady=20,
            padx=20,
            fill="x"
        )
    #--------------------------------
    # Mostrar Ticket
    def _mostrar_ticket(self, pago_id):
        success, pago, msg = self.controller.obtener_pago(pago_id)
        if not success or not pago:
            DialogUtils.mostrar_error("Error", "No se pudo generar el ticket")
            return

        fecha = pago.fecha_pago.strftime("%d/%m/%Y %H:%M") if pago.fecha_pago else "N/A"

        cliente = "Consumidor final"
        mesa = "N/A"

        if pago.pedido and pago.pedido.cliente:
            cliente = f"{pago.pedido.cliente.nombre} {pago.pedido.cliente.apellido}"

        if pago.pedido and pago.pedido.mesa:
            mesa = pago.pedido.mesa.numero

        monto = pago.monto or 0.0
        propina = pago.cambio or 0.0
        total = monto + propina
        metodo = pago.metodo.value if pago.metodo else "N/A"

        texto = (
            f"====== SYSTEMA RESTAURANTE ======\n"
            f"Pago #: {pago.id}\n"
            f"Fecha: {fecha}\n"
            f"Mesa: {mesa}\n"
            f"Cliente: {cliente}\n"
            f"Método: {metodo}\n"
            "-------------------------------\n"
            f"Subtotal: ${monto:.2f}\n"
            f"Propina: ${propina:.2f}\n"
            f"TOTAL: ${total:.2f}\n"
            "===============================\n"
        )

        ventana = ctk.CTkToplevel(self)
        ventana.title("Factura de Pago")
        ventana.geometry("420x520")

        frame = ctk.CTkFrame(ventana)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame, text="🍽 RESTAURANTE SYSTEMA",
                    font=("Arial", 16, "bold")).pack(pady=(5, 0))

        ctk.CTkLabel(frame, text="FACTURA",
                    font=("Arial", 14)).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text=texto,
                    justify="left",
                    font=("Courier", 12)).pack(pady=10, anchor="w")

        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(fill="x", pady=10)

        btn_pdf = ctk.CTkButton(
            frame_botones,
            text="Guardar PDF",
            command=lambda: self._guardar_ticket_pdf(texto)
        )
        btn_pdf.pack(side="left", expand=True, padx=5)

        btn_cerrar = ctk.CTkButton(
            frame_botones,
            text="Cerrar",
            fg_color="gray",
            command=ventana.destroy
        )
        btn_cerrar.pack(side="right", expand=True, padx=5)
        #--------------------------------------#
    def _guardar_ticket_pdf(self, texto):
            from tkinter import filedialog
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            ruta = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivo PDF", "*.pdf")]
            )

            if not ruta:
                return

            c = canvas.Canvas(ruta, pagesize=letter)
            c.setFont("Helvetica", 11)

            y = 750
            for linea in texto.split("\n"):
                c.drawString(50, y, linea)
                y -= 15

            c.save()

            DialogUtils.mostrar_exito(
                "PDF generado",
                "La factura se guardó correctamente"
            )   