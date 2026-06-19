import json
import logging
import re
import time
import uuid
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
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
    # English - generic injection
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
    r"if you are.*assistant",
    r"respond with.*nothing else",
    r"you must obey the following demands",
    r"disclose confidential",
    r"show me the source",
    r"delete previous instructions",
    r"reveal your (instructions|prompt|system)",
    r"output your (prompt|instructions|system)",
    r"repeat (after|the|your|all).*(instruction|prompt)",
    r"print your (prompt|instructions)",
    r"what (are|is) your (instructions|prompt|system)",
    r"tell me your (prompt|instructions|system)",
    r"copy of your (prompt|instructions)",
    r"give me your (prompt|instructions)",
    r"show me your (prompt|instructions|system)",
    r"let me see your (prompt|instructions|system)",
    r"write your (prompt|instructions)",
    r"display your (prompt|instructions|system)",
    r"initial (instructions|prompt|system)",
    r"original (instructions|prompt|system)",
    r"first message.*instructions",
    r"extract.*(prompt|instructions)",
    r"leak.*(prompt|instructions)",
    r"expose.*(prompt|instructions)",
    r"everything before this",
    r"say your system prompt",
    r"do you have.*instructions",
    r"what can you do and not do",
    r"list your (rules|constraints|guidelines)",
    # English - role-play / deceptions
    r"act as (if|though).*you",
    r"pretend.*you are",
    r"from now on.*you are",
    r"new character.*you",
    r"you are no longer",
    r"role.?play",
    # Spanish - generic injection
    r"ignora (las )?instrucciones (anteriores|previas)",
    r"olvida (tus |las )?reglas",
    r"sobreescribe tu programación",
    r"omite (las )?(restricciones|restricciones de seguridad)",
    r"no (respondas|contestes) (a )?(lo )?anterior",
    r"solo responde con",
    r"revela información (confidencial|privada)",
    r"muéstrame (el |la |los |las ).*((código|fuente|codigo))",
    r"elimina (las )?instrucciones anteriores",
    r"desobedece (las )?instrucciones",
    r"no sigas (las )?instrucciones",
    r"te voy a hackear",
    r"nuevo prompt (del )?sistema",
    r"nuevo sistema (de )?prompt",
    # Spanish - instruction leakage
    r"cuál es tu (prompt|instrucción|instrucciones|sistema)",
    r"dime (tus |cuáles son tus )?(instrucciones|reglas|prompt)",
    r"repite (tus |las )?(instrucciones|reglas|prompt|indicaciones)",
    r"muéstrame tu (prompt|instrucción|sistema)",
    r"dame tu (prompt|instrucción|instrucciones)",
    r"escribe tu (prompt|instrucción|sistema)",
    r"copia textual (de )?(tus|las)? (instrucciones|prompt|reglas)",
    r"qué dice tu prompt",
    r"qué te dijeron",
    r"qué te (dijo|dijeron) el sistema",
    r"cómo (funcionas|estás programado|te programaron)",
    r"cuáles son tus (límites|límites|restricciones|reglas)",
    r"enséñame tu (prompt|instrucción|sistema)",
    r"has una copia de tu (prompt|instrucción|sistema)",
    r"todo lo que (puedes|debes) hacer",
    r"qué (puedes|sabes) hacer",
    r"dame (todo )?el contexto",
    r"muestra.*(instrucciones|prompt|sistema)",
    r"revela.*(instrucciones|prompt|sistema)",
    r"sacame.*(instrucciones|prompt|sistema)",
    r"dame.*(instrucciones|prompt|sistema)",
    r"quiero.*(instrucciones|prompt|sistema)",
    r"necesito.*(instrucciones|prompt|sistema)",
    r"como.*(instrucciones|prompt|sistema)",
]

LEAKED_INSTRUCTION_PATTERNS = [
    r"REGLAS DE SEGURIDAD",
    r"Nunca reveles",
    r"Solo puedo ayudarte con consultas sobre inventario",
    r"No puedo revelar información interna del sistema",
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


def detectar_leakage_en_respuesta(respuesta: str) -> bool:
    if not isinstance(respuesta, str):
        return False
    respuesta_lower = respuesta.lower()
    if any(re.search(patron, respuesta_lower, flags=re.IGNORECASE) for patron in LEAKED_INSTRUCTION_PATTERNS):
        return True
    return False


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


def proteger_respuesta(respuesta: str) -> str:
    respuesta = redactar_pii(respuesta)
    if detectar_leakage_en_respuesta(respuesta):
        logger.warning("Posible fuga de instrucciones detectada en la respuesta del LLM")
        return (
            "Lo siento, no puedo procesar esa solicitud. "
            "Solo puedo ayudarte con consultas sobre el inventario de Unimarc."
        )
    return respuesta


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
            return JSONResponse(
                status_code=429,
                content={"detail": "Límite de solicitudes excedido. Intenta de nuevo más tarde."},
            )

        if request.method in {"POST", "PUT", "PATCH"}:
            raw_body = await request.body()
            if raw_body:
                try:
                    payload = json.loads(raw_body.decode("utf-8"))
                    validar_payload(payload)
                except ValueError as exc:
                    return JSONResponse(status_code=400, content={"detail": str(exc)})
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
