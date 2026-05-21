"""
Herramientas para el agente
IL2.1: Integra herramientas de consulta, escritura y razonamiento
"""

import logging
from typing import Dict, Any
from database import BaseDatos
from models import TipoDecision

logger = logging.getLogger(__name__)
db = BaseDatos()


class HerramientasConsulta:
    """Herramientas para CONSULTAR información"""
    
    @staticmethod
    def consultar_inventario() -> Dict[str, Any]:
        """Consulta estado actual del inventario"""
        productos = db.obtener_inventario()
        return {
            "tipo": "consulta_inventario",
            "datos": [
                {
                    "sku": p.sku,
                    "nombre": p.nombre,
                    "stock": p.stock,
                    "minimo": p.minimo,
                    "estado": "CRÍTICO" if p.stock < p.minimo else "OK"
                }
                for p in productos
            ]
        }
    
    @staticmethod
    def consultar_producto(sku: str) -> Dict[str, Any]:
        """Consulta detalles de un producto"""
        p = db.obtener_producto(sku)
        if p:
            return {
                "tipo": "consulta_producto",
                "sku": sku,
                "stock": p.stock,
                "minimo": p.minimo,
                "maximo": p.maximo,
                "precio": p.precio,
                "proveedor": p.proveedor,
                "disponible": p.stock >= p.minimo
            }
        return {"error": f"Producto {sku} no encontrado"}
    
    @staticmethod
    def consultar_memoria_reciente() -> Dict[str, Any]:
        """Consulta eventos recientes (memoria corto plazo)"""
        eventos = db.obtener_memoria_reciente(5)
        return {
            "tipo": "consulta_memoria_reciente",
            "eventos": eventos
        }
    
    @staticmethod
    def consultar_patrones(sku: str = None) -> Dict[str, Any]:
        """Consulta patrones aprendidos (memoria largo plazo)"""
        patrones = db.obtener_patrones(id_entidad=sku) if sku else db.obtener_patrones()
        return {
            "tipo": "consulta_patrones",
            "patrones": patrones
        }


class HerramientasEscritura:
    """Herramientas para ESCRIBIR/CAMBIAR información"""
    
    @staticmethod
    def registrar_pedido(cliente: str, items: list, total: float) -> Dict[str, Any]:
        """Registra un nuevo pedido"""
        from models import Pedido
        import uuid
        
        pedido = Pedido(
            id=f"PED-{uuid.uuid4().hex[:8]}",
            cliente=cliente,
            items=items,
            total=total,
            estado="registrado",
            fecha=__import__('datetime').datetime.now().isoformat()
        )
        
        db.guardar_pedido(pedido)
        logger.info(f"✓ Pedido registrado: {pedido.id}")
        
        return {
            "tipo": "escribir_pedido",
            "pedido_id": pedido.id,
            "cliente": cliente,
            "total": total
        }
    
    @staticmethod
    def actualizar_stock(sku: str, cantidad_delta: int) -> Dict[str, Any]:
        """Actualiza el stock de un producto"""
        db.actualizar_stock(sku, cantidad_delta)
        p = db.obtener_producto(sku)
        
        logger.info(f"✓ Stock actualizado: {sku} ({cantidad_delta:+d})")
        
        return {
            "tipo": "escribir_stock",
            "sku": sku,
            "delta": cantidad_delta,
            "stock_actual": p.stock if p else 0
        }
    
    @staticmethod
    def registrar_aprendizaje(entidad: str, id_entidad: str, patron: str, valor: Any) -> Dict[str, Any]:
        """Registra un patrón aprendido en memoria largo plazo"""
        db.registrar_patron(entidad, id_entidad, patron, valor)
        
        logger.info(f"✓ Patrón aprendido: {entidad}/{id_entidad} - {patron}")
        
        return {
            "tipo": "escribir_aprendizaje",
            "entidad": entidad,
            "patron": patron
        }


class HerramientasRazonamiento:
    """Herramientas para RAZONAR y tomar DECISIONES"""
    
    @staticmethod
    def evaluar_disponibilidad(sku: str, cantidad_solicitada: int) -> Dict[str, Any]:
        """
        Razona sobre si hay stock disponible.
        Retorna decisión adaptativa.
        """
        p = db.obtener_producto(sku)
        
        if not p:
            decision = {
                "tipo": "razonamiento_disponibilidad",
                "sku": sku,
                "decision": TipoDecision.RECHAZAR_PEDIDO.value,
                "razon": "Producto no existe"
            }
        elif p.stock >= cantidad_solicitada:
            decision = {
                "tipo": "razonamiento_disponibilidad",
                "sku": sku,
                "decision": TipoDecision.APROBAR_PEDIDO.value,
                "stock_actual": p.stock,
                "cantidad_solicitada": cantidad_solicitada,
                "razon": "Stock disponible"
            }
        elif p.stock > 0:
            decision = {
                "tipo": "razonamiento_disponibilidad",
                "sku": sku,
                "decision": TipoDecision.ESPERAR_REPOSICION.value,
                "stock_actual": p.stock,
                "cantidad_solicitada": cantidad_solicitada,
                "razon": "Stock parcial, esperar reposición"
            }
        else:
            decision = {
                "tipo": "razonamiento_disponibilidad",
                "sku": sku,
                "decision": TipoDecision.GENERAR_ORDEN_URGENTE.value,
                "cantidad_necesaria": cantidad_solicitada,
                "razon": "Sin stock, generar orden urgente"
            }
        
        return decision
    
    @staticmethod
    def evaluar_prioridad_reposicion() -> Dict[str, Any]:
        """
        Razona sobre qué productos necesitan reposición urgente.
        Adapta decisión según condiciones cambiantes.
        """
        productos = db.obtener_inventario()
        criticos = []
        
        for p in productos:
            deficit = p.minimo - p.stock
            if deficit > 0:
                criticos.append({
                    "sku": p.sku,
                    "nombre": p.nombre,
                    "stock": p.stock,
                    "minimo": p.minimo,
                    "deficit": deficit,
                    "prioridad": "CRÍTICA" if deficit > p.minimo * 0.5 else "ALTA"
                })
        
        return {
            "tipo": "razonamiento_reposicion",
            "productos_criticos": criticos,
            "cantidad_total": len(criticos),
            "decision": "GENERAR_ORDENES" if criticos else "NO_ACCION"
        }
    
    @staticmethod
    def evaluar_patron_cliente(cliente: str) -> Dict[str, Any]:
        """
        Razona sobre patrones del cliente usando memoria largo plazo.
        Adapta comportamiento según historial.
        """
        patrones = db.obtener_patrones(entidad="cliente", id_entidad=cliente)
        
        caracteristicas = {
            "es_cliente_frecuente": any(p["patron"] == "cliente_frecuente" for p in patrones),
            "tiene_deudas": any(p["patron"] == "tiene_deuda" for p in patrones),
            "es_corporativo": any(p["patron"] == "es_corporativo" for p in patrones),
        }
        
        # Lógica adaptativa
        if caracteristicas["tiene_deudas"]:
            riesgo = "ALTO"
        elif caracteristicas["es_cliente_frecuente"]:
            riesgo = "BAJO"
        else:
            riesgo = "MEDIO"
        
        return {
            "tipo": "razonamiento_cliente",
            "cliente": cliente,
            "caracteristicas": caracteristicas,
            "riesgo_crediticio": riesgo
        }
