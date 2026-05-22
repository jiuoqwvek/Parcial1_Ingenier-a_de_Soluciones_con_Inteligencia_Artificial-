import json
import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from models import Producto, Pedido, MemoriaCortoplazo, MemoriaLargoPlazo

logger = logging.getLogger(__name__)

DB_PATH = "databases"
DB_INVENTARIO = os.path.join(DB_PATH, "inventario.json")
DB_PEDIDOS = os.path.join(DB_PATH, "pedidos.json")
DB_MEMORIA_CORTO = os.path.join(DB_PATH, "memoria_corto.json")
DB_MEMORIA_LARGO = os.path.join(DB_PATH, "memoria_largo.json")


class BaseDatos:
    """Persistencia de datos"""
    
    def __init__(self):
        self._inicializar()
    
    def _inicializar(self):
        """Crea BD si no existen"""
        os.makedirs(DB_PATH, exist_ok=True)
        
        if not os.path.exists(DB_INVENTARIO):
            self._crear_archivo(DB_INVENTARIO, {
                "productos": [
                    {"sku": "SKU-ARR-001", "nombre": "Arroz", "stock": 500, "minimo": 100, "maximo": 1000, "precio": 2500.0, "proveedor": "Distrib A"},
                    {"sku": "SKU-PAN-001", "nombre": "Pan", "stock": 150, "minimo": 50, "maximo": 300, "precio": 3500.0, "proveedor": "Panadería B"},
                    {"sku": "SKU-LEC-001", "nombre": "Leche", "stock": 200, "minimo": 75, "maximo": 400, "precio": 2000.0, "proveedor": "Lácteos C"},
                ]
            })
        
        if not os.path.exists(DB_PEDIDOS):
            self._crear_archivo(DB_PEDIDOS, {"pedidos": []})
        
        if not os.path.exists(DB_MEMORIA_CORTO):
            self._crear_archivo(DB_MEMORIA_CORTO, {"eventos": []})
        
        if not os.path.exists(DB_MEMORIA_LARGO):
            self._crear_archivo(DB_MEMORIA_LARGO, {"patrones": []})
    
    def _crear_archivo(self, ruta: str, contenido: Dict):
        with open(ruta, 'w') as f:
            json.dump(contenido, f, indent=2)
    
    def _leer(self, ruta: str) -> Dict:
        try:
            with open(ruta, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _escribir(self, ruta: str, contenido: Dict):
        with open(ruta, 'w') as f:
            json.dump(contenido, f, indent=2)
    
    # INVENTARIO
    def obtener_inventario(self) -> List[Producto]:
        datos = self._leer(DB_INVENTARIO)
        return [Producto(**p) for p in datos.get("productos", [])]
    
    def obtener_producto(self, sku: str) -> Optional[Producto]:
        for p in self.obtener_inventario():
            if p.sku == sku:
                return p
        return None
    
    def actualizar_stock(self, sku: str, delta: int):
        datos = self._leer(DB_INVENTARIO)
        for p in datos["productos"]:
            if p["sku"] == sku:
                p["stock"] = max(0, p["stock"] + delta)
        self._escribir(DB_INVENTARIO, datos)
    
    # PEDIDOS
    def guardar_pedido(self, pedido: Pedido):
        datos = self._leer(DB_PEDIDOS)
        datos["pedidos"].append(pedido.to_dict())
        self._escribir(DB_PEDIDOS, datos)
    
    def obtener_pedidos(self) -> List[Pedido]:
        datos = self._leer(DB_PEDIDOS)
        return [Pedido(**p) for p in datos.get("pedidos", [])]
    
    # MEMORIA CORTO PLAZO
    def registrar_evento(self, tipo: str, desc: str, datos: Dict):
        """Memoria de eventos recientes"""
        evento = MemoriaCortoplazo(
            timestamp=datetime.now().isoformat(),
            tipo_evento=tipo,
            descripcion=desc,
            datos=datos
        )
        datos_db = self._leer(DB_MEMORIA_CORTO)
        datos_db["eventos"].append(evento.to_dict())
        
        # Mantener solo últimos 100 eventos
        if len(datos_db["eventos"]) > 100:
            datos_db["eventos"] = datos_db["eventos"][-100:]
        
        self._escribir(DB_MEMORIA_CORTO, datos_db)
    
    def obtener_memoria_reciente(self, cantidad: int = 10) -> List[Dict]:
        """Obtiene eventos recientes"""
        datos = self._leer(DB_MEMORIA_CORTO)
        return datos.get("eventos", [])[-cantidad:]
    
    # MEMORIA LARGO PLAZO
    def registrar_patron(self, entidad: str, id_entidad: str, patron: str, valor: Any):
        """Almacena aprendizajes a largo plazo"""
        patron_mem = MemoriaLargoPlazo(
            entidad=entidad,
            id_entidad=id_entidad,
            patron=patron,
            valor=valor,
            fecha_aprendizaje=datetime.now().isoformat()
        )
        datos = self._leer(DB_MEMORIA_LARGO)
        datos["patrones"].append(patron_mem.to_dict())
        self._escribir(DB_MEMORIA_LARGO, datos)
    
    def obtener_patrones(self, entidad: str = None, id_entidad: str = None) -> List[Dict]:
        """Recupera patrones aprendidos"""
        datos = self._leer(DB_MEMORIA_LARGO)
        patrones = datos.get("patrones", [])
        
        if entidad:
            patrones = [p for p in patrones if p["entidad"] == entidad]
        if id_entidad:
            patrones = [p for p in patrones if p["id_entidad"] == id_entidad]
        
        return patrones
