import json
import logging
import os
from typing import Any, Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INVENTARIO_FILE = os.path.join(DATA_DIR, "inventario.json")

logger = logging.getLogger(__name__)

DEFAULT_INVENTARIO = {
    "productos": [
        {"sku": "SKU-ARR-001", "nombre": "Arroz", "stock": 500, "minimo": 100, "maximo": 1000, "precio": 2500.0, "proveedor": "Distrib A"},
        {"sku": "SKU-PAN-001", "nombre": "Pan", "stock": 150, "minimo": 50, "maximo": 300, "precio": 3500.0, "proveedor": "Panadería B"},
        {"sku": "SKU-LEC-001", "nombre": "Leche", "stock": 200, "minimo": 75, "maximo": 400, "precio": 2000.0, "proveedor": "Lácteos C"},
    ]
}


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_json(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.warning("No se pudo leer JSON en %s, usando valores por defecto", path)
        return default


def _write_json(path: str, content: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


class InventoryStore:
    def __init__(self):
        _ensure_data_dir()
        if not os.path.exists(INVENTARIO_FILE):
            _write_json(INVENTARIO_FILE, DEFAULT_INVENTARIO)

    def get_inventory(self) -> List[Dict[str, Any]]:
        return _read_json(INVENTARIO_FILE, DEFAULT_INVENTARIO).get("productos", [])

    def find_product(self, sku_or_name: str) -> Optional[Dict[str, Any]]:
        query = sku_or_name.strip().lower()
        for producto in self.get_inventory():
            if producto.get("sku", "").lower() == query or producto.get("nombre", "").lower() == query:
                return producto
        return None

    def update_stock(self, sku_or_name: str, new_stock: int) -> Optional[Dict[str, Any]]:
        productos = self.get_inventory()
        updated_product = None
        for producto in productos:
            if producto.get("sku", "").lower() == sku_or_name.strip().lower() or producto.get("nombre", "").lower() == sku_or_name.strip().lower():
                producto["stock"] = max(0, int(new_stock))
                updated_product = producto
                break
        if updated_product:
            _write_json(INVENTARIO_FILE, {"productos": productos})
            return updated_product
        return None

    def get_critical_products(self) -> List[Dict[str, Any]]:
        return [producto for producto in self.get_inventory() if producto.get("stock", 0) <= producto.get("minimo", 0)]
