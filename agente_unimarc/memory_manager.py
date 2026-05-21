"""
Gestor de Memoria
IL2.2: Configura procesos de memoria y recuperación de contexto
- Memoria corto plazo: eventos recientes
- Memoria largo plazo: patrones aprendidos
"""

import logging
from typing import Dict, List, Any
from database import BaseDatos

logger = logging.getLogger(__name__)
db = BaseDatos()


class GestorMemoria:
    """
    Gestiona memoria corto y largo plazo del agente.
    Permite continuidad en tareas prolongadas.
    """
    
    def __init__(self):
        self.contexto_actual = {}  # Contexto de la tarea actual
        self.conversacion = []  # Historial de interacciones
    
    # ===== MEMORIA CORTO PLAZO =====
    
    def registrar_evento(self, tipo: str, descripcion: str, datos: Dict):
        """
        Registra evento en memoria corto plazo.
        Mantiene los últimos 100 eventos.
        """
        db.registrar_evento(tipo, descripcion, datos)
        self.conversacion.append({
            "tipo": tipo,
            "descripcion": descripcion,
            "datos": datos
        })
        logger.info(f"📝 Evento registrado: {tipo}")
    
    def obtener_contexto_reciente(self, cantidad: int = 5) -> List[Dict]:
        """
        Recupera contexto reciente para continuidad de tareas.
        Útil para recordar qué pasó en interacciones anteriores.
        """
        eventos = db.obtener_memoria_reciente(cantidad)
        logger.info(f"📖 Recuperados {len(eventos)} eventos recientes")
        return eventos
    
    def establecer_contexto(self, contexto: Dict):
        """
        Establece contexto para la tarea actual.
        Se usa durante tareas multi-etapa.
        """
        self.contexto_actual = contexto
        logger.info(f"🎯 Contexto establecido: {list(contexto.keys())}")
    
    def obtener_contexto(self) -> Dict:
        """Obtiene contexto actual"""
        return self.contexto_actual
    
    # ===== MEMORIA LARGO PLAZO =====
    
    def aprender_patron(self, entidad: str, id_entidad: str, patron: str, valor: Any):
        """
        Registra un patrón aprendido para decisiones futuras.
        Ejemplos:
        - entidad="cliente", id="Cliente X", patron="cliente_frecuente", valor=True
        - entidad="producto", id="SKU-001", patron="producto_lento", valor=2.5 (días)
        """
        db.registrar_patron(entidad, id_entidad, patron, valor)
        logger.info(f"🧠 Patrón aprendido: {entidad}/{id_entidad}/{patron}")
    
    def recuperar_patrones(self, entidad: str = None, id_entidad: str = None) -> List[Dict]:
        """
        Recupera patrones aprendidos para adaptar comportamiento.
        Ejemplo: ¿Este cliente siempre incumple? ¿Este producto es lento?
        """
        patrones = db.obtener_patrones(entidad, id_entidad)
        logger.info(f"🧠 Recuperados {len(patrones)} patrones")
        return patrones
    
    # ===== CONTINUIDAD EN TAREAS PROLONGADAS =====
    
    def iniciar_tarea_multipasos(self, tarea_id: str, pasos_totales: int):
        """
        Inicia una tarea que tiene múltiples etapas.
        Mantiene estado entre etapas.
        """
        self.contexto_actual = {
            "tarea_id": tarea_id,
            "pasos_totales": pasos_totales,
            "paso_actual": 0,
            "estado": "iniciada",
            "resultados_parciales": []
        }
        self.registrar_evento(
            "tarea_iniciada",
            f"Tarea {tarea_id} iniciada con {pasos_totales} pasos",
            self.contexto_actual
        )
        logger.info(f"▶️ Tarea multi-pasos iniciada: {tarea_id}")
    
    def avanzar_paso(self, resultado: Any):
        """
        Avanza a siguiente paso y guarda resultado parcial.
        Permite recuperación en caso de error.
        """
        if not self.contexto_actual:
            return False
        
        self.contexto_actual["paso_actual"] += 1
        self.contexto_actual["resultados_parciales"].append(resultado)
        
        self.registrar_evento(
            "paso_completado",
            f"Paso {self.contexto_actual['paso_actual']}/{self.contexto_actual['pasos_totales']} completado",
            {"resultado": resultado}
        )
        
        logger.info(f"✓ Paso {self.contexto_actual['paso_actual']}/{self.contexto_actual['pasos_totales']}")
        return True
    
    def completar_tarea(self) -> Dict:
        """
        Marca tarea como completada y retorna resumen.
        """
        if not self.contexto_actual:
            return {}
        
        self.contexto_actual["estado"] = "completada"
        
        self.registrar_evento(
            "tarea_completada",
            f"Tarea {self.contexto_actual['tarea_id']} completada",
            self.contexto_actual
        )
        
        logger.info(f"✅ Tarea completada: {self.contexto_actual['tarea_id']}")
        return self.contexto_actual
    
    # ===== UTILIDADES =====
    
    def resumen_conversacion(self) -> str:
        """
        Genera resumen de la conversación/interacciones.
        Útil para tareas que necesitan contexto largo.
        """
        eventos = self.obtener_contexto_reciente(10)
        
        resumen = f"Últimas {len(eventos)} acciones:\n"
        for i, evt in enumerate(eventos, 1):
            resumen += f"{i}. {evt['tipo']}: {evt.get('descripcion', 'N/A')}\n"
        
        return resumen
    
    def limpiar_contexto(self):
        """Limpia contexto actual (fin de tarea)"""
        self.contexto_actual = {}
        logger.info("🧹 Contexto limpiado")
