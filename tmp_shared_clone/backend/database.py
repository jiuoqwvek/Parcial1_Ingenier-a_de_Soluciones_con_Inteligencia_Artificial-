import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class JSONDatabase:
    """Persistencia simple basada en JSON para inventario, órdenes y trazabilidad."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.inventory_file = self.data_dir / "inventory.json"
        self.orders_file = self.data_dir / "orders.json"
        self.audit_log_file = self.data_dir / "audit_log.json"
        self._ensure_files()

    def _ensure_files(self):
        """Asegura que existan los archivos JSON."""
        if not self.inventory_file.exists():
            self._write_json(self.inventory_file, [])
        if not self.orders_file.exists():
            self._write_json(self.orders_file, [])
        if not self.audit_log_file.exists():
            self._write_json(self.audit_log_file, [])

    def _read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"Error leyendo {file_path}: {exc}")
            return []

    def _write_json(self, file_path: Path, data: List[Dict[str, Any]]):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.error(f"Error escribiendo {file_path}: {exc}")

    def _log_audit(self, action: str, entity: str, details: Dict[str, Any]) -> None:
        """Registra acciones para auditoría y trazabilidad."""
        from datetime import datetime
        import uuid

        audit_record = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "entity": entity,
            "details": details,
        }
        logs = self._read_json(self.audit_log_file)
        logs.append(audit_record)
        self._write_json(self.audit_log_file, logs)

    # Inventario
    def get_inventory(self) -> List[Dict[str, Any]]:
        return self._read_json(self.inventory_file)

    def add_product(self, sku: str, nombre: str, stock: int, precio: float) -> Dict[str, Any]:
        productos = self.get_inventory()
        nuevo = {
            "sku": sku,
            "nombre": nombre,
            "stock": stock,
            "precio": precio,
            "created_at": self._now(),
        }
        productos.append(nuevo)
        self._write_json(self.inventory_file, productos)
        self._log_audit("CREATE", "PRODUCTO", {"sku": sku, "nombre": nombre})
        return nuevo

    def update_stock(self, sku: str, new_stock: int) -> Dict[str, Any]:
        productos = self.get_inventory()
        for p in productos:
            if p["sku"] == sku:
                old_stock = p["stock"]
                p["stock"] = new_stock
                p["updated_at"] = self._now()
                self._write_json(self.inventory_file, productos)
                self._log_audit(
                    "UPDATE", "STOCK", {"sku": sku, "old_stock": old_stock, "new_stock": new_stock}
                )
                return p
        return None

    def get_critical_stock(self, threshold: int = 50) -> List[Dict[str, Any]]:
        return [p for p in self.get_inventory() if p["stock"] < threshold]

    # Órdenes
    def get_orders(self) -> List[Dict[str, Any]]:
        return self._read_json(self.orders_file)

    def create_order(self, items: List[Dict], total: float, cliente_email: str, cliente_nombre: str) -> Dict[str, Any]:
        import uuid

        ordenes = self.get_orders()
        orden = {
            "orden_id": str(uuid.uuid4())[:8].upper(),
            "token": str(uuid.uuid4()),
            "items": items,
            "total": total,
            "cliente_email": cliente_email,
            "cliente_nombre": cliente_nombre,
            "estado": "pendiente",
            "created_at": self._now(),
        }
        ordenes.append(orden)
        self._write_json(self.orders_file, ordenes)
        self._log_audit("CREATE", "ORDEN", {"orden_id": orden["orden_id"], "total": total})
        return orden

    def get_pending_orders(self) -> List[Dict[str, Any]]:
        return [o for o in self.get_orders() if o["estado"] == "pendiente"]

    def approve_order(self, token: str) -> Dict[str, Any]:
        ordenes = self.get_orders()
        for o in ordenes:
            if o["token"] == token:
                o["estado"] = "aprobada"
                o["updated_at"] = self._now()
                self._write_json(self.orders_file, ordenes)
                self._log_audit("APPROVE", "ORDEN", {"orden_id": o["orden_id"]})
                return o
        return None

    def reject_order(self, token: str, razon: str) -> Dict[str, Any]:
        ordenes = self.get_orders()
        for o in ordenes:
            if o["token"] == token:
                o["estado"] = "rechazada"
                o["razon"] = razon
                o["updated_at"] = self._now()
                self._write_json(self.orders_file, ordenes)
                self._log_audit("REJECT", "ORDEN", {"orden_id": o["orden_id"], "razon": razon})
                return o
        return None

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        logs = self._read_json(self.audit_log_file)
        return logs[-limit:]

    @staticmethod
    def _now() -> str:
        from datetime import datetime

        return datetime.utcnow().isoformat()


# Instancia global
db = JSONDatabase()
