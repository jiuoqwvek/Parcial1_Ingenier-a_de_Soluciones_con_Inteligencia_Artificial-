"""
Módulo para gestionar órdenes de reposición pendientes
Permite guardar, aprobar y rechazar órdenes de reposición
"""

import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

DB_PATH = "databases"
DB_ORDENES = os.path.join(DB_PATH, "ordenes_reposicion.json")


class GestorOrdenes:
    """Gestiona órdenes de reposición con aprobaciones"""
    
    def __init__(self):
        self._inicializar()
    
    def _inicializar(self):
        """Crea archivo de órdenes si no existe"""
        os.makedirs(DB_PATH, exist_ok=True)
        
        if not os.path.exists(DB_ORDENES):
            self._escribir({
                "ordenes": []
            })
    
    def _leer(self) -> Dict:
        try:
            with open(DB_ORDENES, 'r') as f:
                return json.load(f)
        except:
            return {"ordenes": []}
    
    def _escribir(self, contenido: Dict):
        with open(DB_ORDENES, 'w') as f:
            json.dump(contenido, f, indent=2)
    
    def crear_orden(self, productos: List[Dict], cantidad_total: int) -> Dict:
        """Crea una nueva orden de reposición pendiente"""
        orden_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
        token = str(uuid.uuid4())  # Token para aprobación/rechazo
        
        orden = {
            "orden_id": orden_id,
            "token": token,
            "estado": "pendiente",
            "productos": productos,
            "cantidad_total": cantidad_total,
            "fecha_creacion": datetime.now().isoformat(),
            "fecha_resolucion": None,
            "resolucion": None  # "aprobada" o "rechazada"
        }
        
        datos = self._leer()
        datos["ordenes"].append(orden)
        self._escribir(datos)
        
        logger.info(f"Orden creada: {orden_id}")
        return orden
    
    def obtener_orden(self, orden_id: str) -> Optional[Dict]:
        """Obtiene una orden por ID"""
        datos = self._leer()
        for orden in datos["ordenes"]:
            if orden["orden_id"] == orden_id:
                return orden
        return None
    
    def obtener_orden_por_token(self, token: str) -> Optional[Dict]:
        """Obtiene una orden por su token de confirmación"""
        datos = self._leer()
        for orden in datos["ordenes"]:
            if orden["token"] == token:
                return orden
        return None
    
    def obtener_ordenes_pendientes(self) -> List[Dict]:
        """Obtiene todas las órdenes pendientes"""
        datos = self._leer()
        return [o for o in datos["ordenes"] if o["estado"] == "pendiente"]
    
    def aprobar_orden(self, token: str) -> Dict:
        """Aprueba una orden de reposición"""
        datos = self._leer()
        
        for orden in datos["ordenes"]:
            if orden["token"] == token:
                orden["estado"] = "aprobada"
                orden["resolucion"] = "aprobada"
                orden["fecha_resolucion"] = datetime.now().isoformat()
                self._escribir(datos)
                logger.info(f"Orden aprobada: {orden['orden_id']}")
                return {
                    "exito": True,
                    "mensaje": f"Orden {orden['orden_id']} aprobada",
                    "orden": orden
                }
        
        return {
            "exito": False,
            "mensaje": "Token invalido o orden no encontrada"
        }
    
    def rechazar_orden(self, token: str, razon: str = "") -> Dict:
        """Rechaza una orden de reposición"""
        datos = self._leer()
        
        for orden in datos["ordenes"]:
            if orden["token"] == token:
                orden["estado"] = "rechazada"
                orden["resolucion"] = "rechazada"
                orden["fecha_resolucion"] = datetime.now().isoformat()
                orden["razon_rechazo"] = razon
                self._escribir(datos)
                logger.info(f"Orden rechazada: {orden['orden_id']}")
                return {
                    "exito": True,
                    "mensaje": f"Orden {orden['orden_id']} rechazada",
                    "orden": orden
                }
        
        return {
            "exito": False,
            "mensaje": "Token invalido o orden no encontrada"
        }


# Instancia global
gestor_ordenes = GestorOrdenes()
