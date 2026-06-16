from services.email import EmailService
from services.inventory import InventoryStore
from services.llm_agent import LLMInventoryAgent
from services.orders import OrderStore


class AgentManager:
    def __init__(self):
        self.inventory_store = InventoryStore()
        self.order_store = OrderStore()
        self.email_service = EmailService()
        self.llm_agent = LLMInventoryAgent()

    def query_inventory(self, pregunta: str):
        inventario = self.inventory_store.get_inventory()
        return self.llm_agent.query_inventory(pregunta, inventario)

    def update_inventory_stock(self, sku_or_name: str, nuevo_stock: int):
        return self.inventory_store.update_stock(sku_or_name, nuevo_stock)

    def list_inventory(self):
        return self.inventory_store.get_inventory()

    def create_order(self, items, total: float, cliente_email: str = "", cliente_nombre: str = ""):
        orden = self.order_store.create_order(items, total, cliente_email, cliente_nombre)
        email_result = None
        if cliente_email and cliente_nombre:
            email_result = self.email_service.send_order_confirmation(
                cliente_email, cliente_nombre, orden["orden_id"], items, total
            )
        return orden, email_result

    def list_pending_orders(self):
        return self.order_store.list_orders(estado="pendiente")

    def approve_order(self, token: str):
        return self.order_store.update_order_status(token, "aprobada")

    def reject_order(self, token: str, razon: str = ""):
        return self.order_store.update_order_status(token, "rechazada", razon)

    def get_critical_products(self):
        return self.inventory_store.get_critical_products()
