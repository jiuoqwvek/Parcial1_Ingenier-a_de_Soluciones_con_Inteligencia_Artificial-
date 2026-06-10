import json
import logging
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Recopila métricas de observabilidad del agente: latencia, precisión, errores, recursos."""

    def __init__(self, metrics_file: str = "data/metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_request = None

    def start_request(self, request_id: str, endpoint: str, method: str) -> None:
        """Inicia el cronómetro de una solicitud."""
        self.current_request = {
            "request_id": request_id,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "start_time": time.time(),
            "cpu_percent_start": psutil.cpu_percent(interval=0.1),
            "memory_percent_start": psutil.virtual_memory().percent,
        }

    def end_request(
        self,
        status_code: int,
        response_time_ms: int,
        tokens_in: int = 0,
        tokens_out: int = 0,
        error: str = None,
        source: str = "cache",
    ) -> Dict[str, Any]:
        """Finaliza la solicitud y registra las métricas."""
        if not self.current_request:
            return {}

        now = datetime.utcnow().isoformat()
        cpu_end = psutil.cpu_percent(interval=0.1)
        mem_end = psutil.virtual_memory().percent

        metric_record = {
            "request_id": self.current_request["request_id"],
            "endpoint": self.current_request["endpoint"],
            "method": self.current_request["method"],
            "timestamp": self.current_request["timestamp"],
            "completed_at": now,
            "status_code": status_code,
            "latency_ms": response_time_ms,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "total_tokens": tokens_in + tokens_out,
            "source": source,
            "error": error,
            "cpu_usage_percent": (self.current_request["cpu_percent_start"] + cpu_end) / 2,
            "memory_usage_percent": (self.current_request["memory_percent_start"] + mem_end) / 2,
            "success": status_code < 400,
        }

        self._append_metric(metric_record)
        self.current_request = None
        return metric_record

    def _append_metric(self, record: Dict[str, Any]) -> None:
        """Guarda el registro de métrica en el archivo JSON."""
        try:
            metrics = []
            if self.metrics_file.exists():
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    metrics = json.load(f)
            metrics.append(record)
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
            logger.debug(f"Métrica registrada: {record['request_id']}")
        except Exception as exc:
            logger.error(f"Error al guardar métrica: {exc}")

    def get_metrics_summary(self, endpoint: str = None, limit: int = 100) -> Dict[str, Any]:
        """Obtiene un resumen de métricas (precisión, latencia promedio, tasa de errores)."""
        try:
            if not self.metrics_file.exists():
                return self._empty_summary()

            with open(self.metrics_file, "r", encoding="utf-8") as f:
                metrics = json.load(f)

            if endpoint:
                metrics = [m for m in metrics if m["endpoint"] == endpoint]

            metrics = metrics[-limit:]  # Últimos N registros

            if not metrics:
                return self._empty_summary()

            total = len(metrics)
            successful = sum(1 for m in metrics if m["success"])
            failed = total - successful

            latencies = [m["latency_ms"] for m in metrics]
            tokens_in = sum(m.get("tokens_input", 0) for m in metrics)
            tokens_out = sum(m.get("tokens_output", 0) for m in metrics)

            return {
                "total_requests": total,
                "successful_requests": successful,
                "failed_requests": failed,
                "error_rate_percent": (failed / total * 100) if total > 0 else 0,
                "precision_percent": (successful / total * 100) if total > 0 else 0,
                "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
                "min_latency_ms": min(latencies) if latencies else 0,
                "max_latency_ms": max(latencies) if latencies else 0,
                "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0,
                "avg_cpu_percent": sum(m.get("cpu_usage_percent", 0) for m in metrics) / len(metrics),
                "avg_memory_percent": sum(m.get("memory_usage_percent", 0) for m in metrics) / len(metrics),
                "total_tokens_processed": tokens_in + tokens_out,
                "endpoints": list(set(m["endpoint"] for m in metrics)),
            }
        except Exception as exc:
            logger.error(f"Error al obtener resumen de métricas: {exc}")
            return self._empty_summary()

    def get_metrics_timeline(self, endpoint: str = None, limit: int = 200) -> List[Dict[str, Any]]:
        """Obtiene un timeline de métricas para gráficos."""
        try:
            if not self.metrics_file.exists():
                return []

            with open(self.metrics_file, "r", encoding="utf-8") as f:
                metrics = json.load(f)

            if endpoint:
                metrics = [m for m in metrics if m["endpoint"] == endpoint]

            return metrics[-limit:]
        except Exception as exc:
            logger.error(f"Error al obtener timeline de métricas: {exc}")
            return []

    def _empty_summary(self) -> Dict[str, Any]:
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "error_rate_percent": 0,
            "precision_percent": 0,
            "avg_latency_ms": 0,
            "min_latency_ms": 0,
            "max_latency_ms": 0,
            "p95_latency_ms": 0,
            "avg_cpu_percent": 0,
            "avg_memory_percent": 0,
            "total_tokens_processed": 0,
            "endpoints": [],
        }


# Instancia global
metrics_collector = MetricsCollector()
