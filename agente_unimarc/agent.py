"""
Agente Inteligente UNIMARC
IL2.1: Agente que integra herramientas (consulta, escritura, razonamiento)
IL2.3: Planificación y toma de decisiones adaptativas
"""

import logging
from typing import Dict, Any, List
from memory_manager import GestorMemoria
from tools import HerramientasConsulta, HerramientasEscritura, HerramientasRazonamiento
from database import BaseDatos

logger = logging.getLogger(__name__)


class AgenteUnimarc:
    """
    Agente inteligente que automatiza procesos de inventario.
    
    Características:
    - Integra 3 tipos de herramientas (consulta, escritura, razonamiento)
    - Usa memoria corto/largo plazo para continuidad
    - Planifica tareas multi-etapa
    - Adapta decisiones según condiciones cambiantes
    """
    
    def __init__(self):
        self.memoria = GestorMemoria()
        self.db = BaseDatos()
        
        # Herramientas disponibles
        self.consulta = HerramientasConsulta()
        self.escritura = HerramientasEscritura()
        self.razonamiento = HerramientasRazonamiento()
        
        logger.info("✅ Agente inicializado")
    
    # ===== IL2.3: PLANIFICACIÓN Y TOMA DE DECISIONES =====
    
    def procesar_pedido_adaptativo(self, cliente: str, items: List[Dict]) -> Dict:
        """
        Procesa pedido con planificación adaptativa.
        Se adapta según disponibilidad y patrones.
        
        Etapas:
        1. Evaluar disponibilidad (razonamiento)
        2. Verificar cliente (razonamiento + memoria)
        3. Tomar decisión (escribir o rechazar)
        4. Registrar aprendizaje
        """
        
        self.memoria.iniciar_tarea_multipasos("procesar_pedido", 4)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 PROCESANDO PEDIDO - Cliente: {cliente}")
        logger.info(f"{'='*60}")
        
        # ETAPA 1: Evaluar disponibilidad de cada item
        logger.info("\n📋 ETAPA 1: Evaluando disponibilidad...")
        decisiones_items = []
        puede_aprobar = True
        
        for item in items:
            sku = item["sku"]
            cantidad = item["cantidad"]
            
            # Usar razonamiento para evaluar
            decision = self.razonamiento.evaluar_disponibilidad(sku, cantidad)
            decisiones_items.append(decision)
            
            logger.info(f"  • {sku}: {decision['decision']}")
            
            if decision["decision"] != "aprobar_pedido":
                puede_aprobar = False
        
        self.memoria.avanzar_paso(decisiones_items)
        
        # ETAPA 2: Evaluar cliente (usa memoria)
        logger.info("\n👤 ETAPA 2: Evaluando cliente...")
        patron_cliente = self.razonamiento.evaluar_patron_cliente(cliente)
        logger.info(f"  • Riesgo crediticio: {patron_cliente['riesgo_crediticio']}")
        
        self.memoria.avanzar_paso(patron_cliente)
        
        # ETAPA 3: TOMAR DECISIÓN ADAPTATIVA
        logger.info("\n🤔 ETAPA 3: Tomando decisión...")
        
        if puede_aprobar and patron_cliente['riesgo_crediticio'] != "ALTO":
            decision_final = "APROBAR"
            logger.info(f"  ✅ DECISIÓN: APROBAR PEDIDO")
            
            # Registrar pedido
            total = sum(i["cantidad"] * self.db.obtener_producto(i["sku"]).precio 
                       for i in items if self.db.obtener_producto(i["sku"]))
            
            resultado = self.escritura.registrar_pedido(cliente, items, total)
            
            # Actualizar stocks
            for item in items:
                self.escritura.actualizar_stock(item["sku"], -item["cantidad"])
            
        elif patron_cliente['riesgo_crediticio'] == "ALTO":
            decision_final = "RECHAZAR"
            logger.info(f"  ❌ DECISIÓN: RECHAZAR (riesgo crediticio alto)")
            resultado = {"error": "Cliente de alto riesgo"}
            
        else:
            decision_final = "ESPERAR"
            logger.info(f"  ⏳ DECISIÓN: ESPERAR REPOSICIÓN")
            resultado = {"estado": "pendiente_reposicion"}
        
        self.memoria.avanzar_paso(decision_final)
        
        # ETAPA 4: Registrar aprendizaje
        logger.info("\n🧠 ETAPA 4: Registrando aprendizaje...")
        
        if decision_final == "APROBAR":
            self.escritura.registrar_aprendizaje("cliente", cliente, "cliente_procesado", True)
        
        contexto_final = self.memoria.completar_tarea()
        
        logger.info(f"\n✅ Pedido procesado con decisión: {decision_final}\n")
        
        return {
            "cliente": cliente,
            "decision": decision_final,
            "etapas_completadas": contexto_final["pasos_totales"],
            "resultado": resultado
        }
    
    def reposicion_adaptativa(self) -> Dict:
        """
        Planifica reposición adaptativa basada en condiciones actuales.
        Se adapta según urgencia y proveedores.
        """
        
        self.memoria.iniciar_tarea_multipasos("reposicion", 3)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📦 PLANIFICANDO REPOSICIÓN ADAPTATIVA")
        logger.info(f"{'='*60}")
        
        # ETAPA 1: Evaluar productos críticos
        logger.info("\n🔍 ETAPA 1: Identificando productos críticos...")
        
        resultado_eval = self.razonamiento.evaluar_prioridad_reposicion()
        criticos = resultado_eval["productos_criticos"]
        
        logger.info(f"  Productos críticos: {len(criticos)}")
        for p in criticos:
            logger.info(f"    • {p['nombre']}: deficit {p['deficit']}, prioridad {p['prioridad']}")
        
        self.memoria.avanzar_paso(criticos)
        
        # ETAPA 2: Agrupar por proveedor (estrategia)
        logger.info("\n🤝 ETAPA 2: Agrupando por proveedor...")
        
        por_proveedor = {}
        for p in criticos:
            sku = p['sku']
            producto = self.db.obtener_producto(sku)
            prov = producto.proveedor
            
            if prov not in por_proveedor:
                por_proveedor[prov] = []
            por_proveedor[prov].append(p)
        
        logger.info(f"  Proveedores identificados: {len(por_proveedor)}")
        for prov, items in por_proveedor.items():
            logger.info(f"    • {prov}: {len(items)} items")
        
        self.memoria.avanzar_paso(list(por_proveedor.keys()))
        
        # ETAPA 3: Crear órdenes optimizadas
        logger.info("\n📝 ETAPA 3: Creando órdenes...")
        
        ordenes_creadas = []
        for proveedor, items in por_proveedor.items():
            orden = {
                "proveedor": proveedor,
                "items": len(items),
                "total_cantidad": sum(i["deficit"] for i in items)
            }
            ordenes_creadas.append(orden)
            logger.info(f"    ✓ Orden para {proveedor}: {orden['items']} items")
        
        self.memoria.avanzar_paso(ordenes_creadas)
        contexto_final = self.memoria.completar_tarea()
        
        logger.info(f"\n✅ Reposición planificada: {len(ordenes_creadas)} órdenes\n")
        
        return {
            "ordenes_generadas": len(ordenes_creadas),
            "productos_repuestos": len(criticos),
            "ordenes": ordenes_creadas
        }
    
    # ===== RAZONAMIENTO RECUPERABLE =====
    
    def generar_reporte(self) -> Dict:
        """
        Genera reporte usando memoria (corto y largo plazo).
        Demuestra integración de información histórica.
        """
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 GENERANDO REPORTE")
        logger.info(f"{'='*60}")
        
        # Información actual
        logger.info("\n📋 ESTADO ACTUAL:")
        inventario = self.consulta.consultar_inventario()
        for p in inventario["datos"]:
            logger.info(f"  • {p['nombre']}: {p['stock']} ({p['estado']})")
        
        # Eventos recientes
        logger.info("\n📖 ÚLTIMOS EVENTOS:")
        eventos = self.memoria.obtener_contexto_reciente(5)
        for evt in eventos:
            logger.info(f"  • {evt['tipo_evento']}: {evt['descripcion']}")
        
        # Patrones aprendidos
        logger.info("\n🧠 PATRONES APRENDIDOS:")
        patrones = self.db.obtener_patrones()
        logger.info(f"  Total de patrones: {len(patrones)}")
        for p in patrones[:5]:
            logger.info(f"  • {p['entidad']}/{p['id_entidad']}: {p['patron']}")
        
        logger.info(f"\n{'='*60}\n")
        
        return {
            "productos": len(inventario["datos"]),
            "eventos_recientes": len(eventos),
            "patrones_aprendidos": len(patrones)
        }
