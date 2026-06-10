import json
import logging
import os
import time
import uuid
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ORDENES_FILE = os.path.join(DATA_DIR, "ordenes_reposicion.json")

logger = logging.getLogger(__name__)


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.warning("No se pudo leer JSON en %s, iniciando archivo vacío", path)
        return default


def _write_json(path: str, content: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


class OrderStore:
    def __init__(self):
        _ensure_data_dir()
        if not os.path.exists(ORDENES_FILE):
            _write_json(ORDENES_FILE, {"ordenes": []})

    def _read_orders(self) -> List[Dict[str, Any]]:
        return _read_json(ORDENES_FILE, {"ordenes": []}).get("ordenes", [])

    def _write_orders(self, orders: List[Dict[str, Any]]) -> None:
        _write_json(ORDENES_FILE, {"ordenes": orders})

    def create_order(self, items: List[Dict[str, Any]], total: float, cliente_email: str = "", cliente_nombre: str = "") -> Dict[str, Any]:
        order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
        token = str(uuid.uuid4())
        cantidad_total = sum(int(item.get("cantidad_orden", 0)) for item in items)
        order = {
            "orden_id": order_id,
            "token": token,
            "estado": "pendiente",
            "productos": items,
            "cantidad_total": cantidad_total,
            "total": float(total),
            "cliente_email": cliente_email,
            "cliente_nombre": cliente_nombre,
            "fecha_creacion": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "fecha_resolucion": None,
            "resolucion": None,
        }
        orders = self._read_orders()
        orders.append(order)
        self._write_orders(orders)
        logger.info("Orden creada: %s", order_id)
        return order

    def list_orders(self, estado: Optional[str] = None) -> List[Dict[str, Any]]:
        orders = self._read_orders()
        if estado:
            orders = [order for order in orders if order.get("estado") == estado]
        return orders

    def update_order_status(self, token: str, status: str, razon: str = "") -> Dict[str, Any]:
        orders = self._read_orders()
        for order in orders:
            if order.get("token") == token:
                order["estado"] = status
                order["resolucion"] = status
                order["fecha_resolucion"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                if razon:
                    order["razon_rechazo"] = razon
                self._write_orders(orders)
                logger.info("Orden %s: %s", status, order.get("orden_id"))
                return {"exito": True, "orden": order}
        return {"exito": False, "mensaje": "Token inválido o orden no encontrada"}
