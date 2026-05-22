from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EstadoTarea(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    ERROR = "error"


class TipoDecision(str, Enum):
    APROBAR_PEDIDO = "aprobar_pedido"
    GENERAR_ORDEN_URGENTE = "generar_orden_urgente"
    ESPERAR_REPOSICION = "esperar_reposicion"
    RECHAZAR_PEDIDO = "rechazar_pedido"


@dataclass
class Producto:
    sku: str
    nombre: str
    stock: int
    minimo: int
    maximo: int
    precio: float
    proveedor: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Pedido:
    id: str
    cliente: str
    items: List[Dict]
    total: float
    estado: str
    fecha: str
    decisiones: List[Dict] = field(default_factory=list)
    
    def to_dict(self):
        data = asdict(self)
        return data


@dataclass
class MemoriaCortoplazo:
    """Registra eventos recientes del agente"""
    timestamp: str
    tipo_evento: str
    descripcion: str
    datos: Dict[str, Any]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class MemoriaLargoPlazo:
    """Almacena patrones y decisiones históricas"""
    entidad: str  # "producto", "cliente", "proveedor"
    id_entidad: str
    patron: str  # "cliente_frecuente", "producto_lento", etc
    valor: Any
    fecha_aprendizaje: str
    
    def to_dict(self):
        return asdict(self)
