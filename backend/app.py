import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from agent import AgentManager
from guardrails import GuardrailsMiddleware, proteger_respuesta
from metrics import metrics_collector
from database import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agente Unificado AI",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
)

app.add_middleware(GuardrailsMiddleware)
manager = AgentManager()


class InventoryQueryRequest(BaseModel):
    question: str = Field(..., example="¿Qué productos tienen stock crítico hoy?")


class StockUpdateRequest(BaseModel):
    sku_or_name: str = Field(..., example="SKU-ARR-001")
    new_stock: int = Field(..., example=320)


class OrderItem(BaseModel):
    sku: str
    nombre: str
    cantidad_orden: int
    precio: Optional[float] = 0.0


class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    total: float
    cliente_email: Optional[str] = Field(None, example="cliente@example.com")
    cliente_nombre: Optional[str] = Field(None, example="Juan Pérez")


class OrderActionRequest(BaseModel):
    razon: Optional[str] = Field(None, example="Duplicado")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "El backend AI está activo"}


@app.get("/inventory")
def get_inventory():
    inventario = manager.list_inventory()
    return {"success": True, "inventory": inventario, "count": len(inventario)}


@app.post("/inventory/query")
def query_inventory(payload: InventoryQueryRequest):
    pregunta_segura = payload.question.strip()
    resultado = manager.query_inventory(pregunta_segura)
    respuesta_segura = proteger_respuesta(resultado["respuesta"])
    logger.info(
        "inventory.query.complete",
        extra={
            "source": resultado["metrics"]["source"],
            "latency_ms": resultado["metrics"]["latency_ms"],
            "prompt_tokens": resultado["metrics"]["prompt_tokens"],
            "completion_tokens": resultado["metrics"]["completion_tokens"],
        },
    )
    return {
        "success": True,
        "question": pregunta_segura,
        "answer": respuesta_segura,
        "metrics": resultado["metrics"],
    }


@app.post("/inventory/stock")
def update_stock(payload: StockUpdateRequest):
    producto = manager.update_inventory_stock(payload.sku_or_name, payload.new_stock)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"success": True, "product": producto}


@app.get("/orders/pending")
def get_pending_orders():
    ordenes = manager.list_pending_orders()
    return {"success": True, "pending_orders": ordenes, "count": len(ordenes)}


@app.post("/orders")
def create_order(payload: CreateOrderRequest):
    orden = manager.create_order(
        items=[item.dict() for item in payload.items],
        total=payload.total,
        cliente_email=payload.cliente_email or "",
        cliente_nombre=payload.cliente_nombre or "",
    )
    return {"success": True, "order": orden}


@app.post("/orders/{token}/approve")
def approve_order(token: str):
    resultado = manager.approve_order(token)
    if not resultado["exito"]:
        raise HTTPException(status_code=404, detail=resultado["mensaje"])
    return {"success": True, "order": resultado["orden"]}


@app.post("/orders/{token}/reject")
def reject_order(token: str, payload: OrderActionRequest):
    resultado = manager.reject_order(token, payload.razon or "")
    if not resultado["exito"]:
        raise HTTPException(status_code=404, detail=resultado["mensaje"])
    return {"success": True, "order": resultado["orden"]}


@app.get("/alerts/critical-stock")
def get_critical_stock():
    productos = manager.get_critical_products()
    return {"success": True, "critical_products": productos, "count": len(productos)}


@app.get("/metrics/summary")
def get_metrics_summary(endpoint: str = None):
    """Obtiene un resumen de métricas de observabilidad."""
    summary = metrics_collector.get_metrics_summary(endpoint=endpoint, limit=200)
    return {"success": True, "metrics": summary}


@app.get("/metrics/timeline")
def get_metrics_timeline(endpoint: str = None, limit: int = 100):
    """Obtiene un timeline de métricas para gráficos."""
    timeline = metrics_collector.get_metrics_timeline(endpoint=endpoint, limit=limit)
    return {"success": True, "timeline": timeline, "count": len(timeline)}


@app.get("/audit/log")
def get_audit_log(limit: int = 100):
    """Obtiene el log de auditoría completo."""
    logs = db.get_audit_log(limit=limit)
    return {"success": True, "audit_log": logs, "count": len(logs)}
