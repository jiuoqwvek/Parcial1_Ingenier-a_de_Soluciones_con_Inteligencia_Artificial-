import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)

MODEL_NAME = os.getenv("AGENT_MODEL", "gpt-4o-mini")
BASE_URL = os.getenv("OPENAI_BASE_URL", "")
API_KEY = os.getenv("GITHUB_TOKEN", "")

logger = logging.getLogger(__name__)


class LLMInventoryAgent:
    def __init__(self):
        self.model_name = MODEL_NAME
        self.base_url = BASE_URL
        self.api_key = API_KEY
        self.client = self._build_client()

    def _build_client(self) -> Optional[Any]:
        if not self.base_url or not self.api_key:
            logger.warning("OPENAI_BASE_URL o GITHUB_TOKEN no configurados. Se usará fallback local.")
            return None
        try:
            from openai import OpenAI

            return OpenAI(api_key=self.api_key, base_url=self.base_url.rstrip("/"))
        except ImportError:
            logger.warning("openai no instalado. Se usará fallback local.")
            return None

    def build_prompt(self, pregunta: str, inventario: List[Dict[str, Any]]) -> str:
        bloques = ["Inventario actual de Unimarc:"]
        for producto in inventario:
            bloques.append(
                f"- {producto.get('sku')}: {producto.get('nombre')} | stock {producto.get('stock')} | minimo {producto.get('minimo')} | maximo {producto.get('maximo')}"
            )
        contexto = "\n".join(bloques)
        return (
            "Eres un asistente experto en gestión de inventarios para Unimarc. "
            "Debes responder usando solo los datos del inventario actual y explicar claramente si el producto está disponible, "
            "si se puede reabastecer, o si requiere acción urgente."
            "\n\n"
            f"{contexto}\n\n"
            f"Pregunta: {pregunta}\n"
            "Responde en español de forma clara y con recomendaciones concretas."
        )

    def _call_model(self, prompt: str) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Cliente de modelo no disponible")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        choice = response.choices[0].message.content.strip()
        return {"text": choice, "usage": response.usage.model_dump() if response.usage else {}}

    def fallback_answer(self, pregunta: str, inventario: List[Dict[str, Any]]) -> str:
        pregunta_lower = pregunta.lower()
        mensaje = [
            "No hay acceso al servicio de LLM configurado. Aquí tienes un resumen seguro del inventario disponible:",
        ]
        if any(keyword in pregunta_lower for keyword in ["reabastecer", "urgente", "crítico", "critico"]):
            productos_criticos = [p for p in inventario if p.get("stock", 0) <= p.get("minimo", 0)]
            if productos_criticos:
                mensaje.append("Productos que requieren atención urgente:")
                for producto in productos_criticos:
                    mensaje.append(
                        f"- {producto.get('sku')} {producto.get('nombre')}: stock {producto.get('stock')} (mínimo {producto.get('minimo')})"
                    )
            else:
                mensaje.append("No hay productos con stock crítico. El inventario está dentro de los rangos esperados.")
        else:
            mensaje.append("Estado general del inventario:")
            for producto in inventario:
                mensaje.append(
                    f"- {producto.get('sku')} {producto.get('nombre')}: stock {producto.get('stock')}"
                )
        mensaje.append("\nPara habilitar respuestas generadas, configura OPENAI_BASE_URL y GITHUB_TOKEN.")
        return "\n".join(mensaje)

    def query_inventory(self, pregunta: str, inventario: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = self.build_prompt(pregunta, inventario)
        start = time.time()
        if self.client:
            try:
                result = self._call_model(prompt)
                latency_ms = int((time.time() - start) * 1000)
                usage = result.get("usage", {})
                return {
                    "respuesta": result.get("text", ""),
                    "metrics": {
                        "latency_ms": latency_ms,
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                        "source": "llm",
                    },
                }
            except Exception as exc:
                logger.warning("Fallo al consultar LLM: %s", exc)
        latency_ms = int((time.time() - start) * 1000)
        return {
            "respuesta": self.fallback_answer(pregunta, inventario),
            "metrics": {
                "latency_ms": latency_ms,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "source": "fallback",
            },
        }
