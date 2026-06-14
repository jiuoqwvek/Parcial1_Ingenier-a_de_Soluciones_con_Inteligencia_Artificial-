import json
import logging
import re
import time
import uuid
from typing import Any

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from metrics import metrics_collector

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history = {}

    def allow_request(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        requests = self.history.get(client_id, [])
        requests = [timestamp for timestamp in requests if timestamp > window_start]
        if len(requests) >= self.max_requests:
            self.history[client_id] = requests
            return False
        requests.append(now)
        self.history[client_id] = requests
        return True

rate_limiter = RateLimiter()

PROMPT_INJECTION_PATTERNS = [
    r"ignore (previous|prior) instructions",
    r"forget (your|the) rules",
    r"you are now .*agent",
    r"jailbreak",
    r"override your programming",
    r"ignore all previous",
    r"bypass.*safety",
    r"disregard.*instructions",
    r"use the following format",
    r"do not answer the previous",
    r"only answer with",
    r"bypasses the filter",
    r"system prompt",
    r"if you are.*assistant",
    r"respond with.*nothing else",
    r"you must obey the following demands",
    r"disclose confidential",
    r"show me the source",
    r"delete previous instructions",
]

PII_PATTERNS = [
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    r"\b\d{1,2}\.\d{3}\.\d{3}-[0-9kK]\b",
    r"\b\d{7,8}-[0-9kK]\b",
    r"\b\d{3}[ .-]?\d{3}[ .-]?\d{4}\b",
    r"\b\d{4}[ .-]?\d{4}[ .-]?\d{4}[ .-]?\d{4}\b",
]


def detectar_prompt_injection(prompt: str) -> bool:
    if not isinstance(prompt, str):
        return False
    prompt_lower = prompt.lower()
    return any(re.search(patron, prompt_lower, flags=re.IGNORECASE) for patron in PROMPT_INJECTION_PATTERNS)


def redactar_pii(texto: str) -> str:
    if not isinstance(texto, str):
        return texto
    for patron in PII_PATTERNS:
        texto = re.sub(patron, "[DATO PROTEGIDO]", texto)
    return texto


def sanitizar_prompt(prompt: str) -> str:
    if detectar_prompt_injection(prompt):
        raise ValueError("Intento de inyección de prompt detectado")
    return redactar_pii(prompt)


def validar_payload(data: Any) -> None:
    if isinstance(data, dict):
        for value in data.values():
            validar_payload(value)
    elif isinstance(data, list):
        for item in data:
            validar_payload(item)
    elif isinstance(data, str):
        if detectar_prompt_injection(data):
            raise ValueError("Solicitud de entrada maliciosa detectada")


def sanitizar_payload(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: sanitizar_payload(value) for key, value in data.items()}
    if isinstance(data, list):
        return [sanitizar_payload(item) for item in data]
    if isinstance(data, str):
        return redactar_pii(data)
    return data


def proteger_respuesta(respuesta: str) -> str:
    return redactar_pii(respuesta)


class GuardrailsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        request_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else "unknown"

        # Start a metrics record for the incoming request. This captures cpu/memory start values
        try:
            metrics_collector.start_request(request_id=request_id, endpoint=str(request.url.path), method=request.method)
        except Exception:
            # Metrics collection should not block request processing
            logger.debug("No se pudo iniciar métrica para request %s", request_id)

        if not rate_limiter.allow_request(client_ip):
            raise HTTPException(status_code=429, detail="Límite de solicitudes excedido. Intenta de nuevo más tarde.")

        if request.method in {"POST", "PUT", "PATCH"}:
            raw_body = await request.body()
            if raw_body:
                try:
                    payload = json.loads(raw_body.decode("utf-8"))
                    validar_payload(payload)
                    sanitized = sanitizar_payload(payload)
                    request._body = json.dumps(sanitized, ensure_ascii=False).encode("utf-8")
                except ValueError as exc:
                    raise HTTPException(status_code=400, detail=str(exc))
                except json.JSONDecodeError:
                    pass

        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            "request.completed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
            },
        )
        # Nota: no finalizamos métricas aquí. Los endpoints deben proporcionar
        # tokens y metadatos específicos (p. ej. prompt/completion tokens) y
        # llamar a metrics_collector.end_request() al finalizar el procesamiento.
        # Esto evita perder información útil proveniente del LLM.
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        return response
