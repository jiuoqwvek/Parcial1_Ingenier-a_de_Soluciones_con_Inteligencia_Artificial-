"""Validación post-deploy ligera:
- Ejecuta scripts/test_metrics.py (no interfiere si se hace desde dentro del contenedor; asume docker compose ya levantado)
- Comprueba que backend/data/metrics.json y backend/data/audit_log.json contengan al menos N registros.
"""
import json
import subprocess
from pathlib import Path
import time

ROOT = Path(__file__).parent.parent
METRICS_FILE = ROOT / "backend" / "data" / "metrics.json"
AUDIT_FILE = ROOT / "backend" / "data" / "audit_log.json"


def run_test_metrics():
    try:
        subprocess.run(["python3", "scripts/test_metrics.py"], check=True)
    except Exception as exc:
        print("No se pudo ejecutar scripts/test_metrics.py:", exc)


def check_file(path: Path, min_records: int = 1):
    if not path.exists():
        return False, 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return len(data) >= min_records, len(data)
    except Exception:
        return False, 0


def main():
    print("Ejecutando pruebas de carga local para generar métricas...")
    run_test_metrics()
    print("Esperando 2s para que se persistan métricas...")
    time.sleep(2)

    ok_metrics, count_metrics = check_file(METRICS_FILE, min_records=1)
    ok_audit, count_audit = check_file(AUDIT_FILE, min_records=1)

    print(f"metrics.json: exists and >=1? {ok_metrics} (records={count_metrics})")
    print(f"audit_log.json: exists and >=1? {ok_audit} (records={count_audit})")

    result = {"metrics_records": count_metrics, "audit_records": count_audit}
    Path("scripts").joinpath("post_deploy_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Validación escrita en scripts/post_deploy_validation.json")


if __name__ == "__main__":
    main()
