"""Evaluación semántica simple para IL3.1.
Envía preguntas definidas en scripts/semantic_samples.json al endpoint /inventory/query
y compara la respuesta con expected_answer usando búsqueda por substring (case-insensitive).

Salida: JSON con conteos y porcentaje de aciertos (precision simple) y consistencia básica.
"""
import json
import requests
import time
from pathlib import Path

BACKEND_URL = "http://localhost:8000"
SAMPLES_FILE = Path(__file__).parent / "semantic_samples.json"


def load_samples():
    with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_question(q: str):
    try:
        r = requests.post(f"{BACKEND_URL}/inventory/query", json={"question": q}, timeout=10)
        if r.status_code == 200:
            return r.json().get("answer", "")
        return ""
    except Exception as exc:
        return ""


def evaluate():
    samples = load_samples()
    results = []
    for s in samples:
        q = s["question"]
        expected = s.get("expected_answer", "").strip().lower()
        # Send the same question 3 times to check consistency
        answers = []
        for _ in range(3):
            ans = send_question(q)
            answers.append(ans or "")
            time.sleep(0.3)
        # Evaluate precision by substring matching
        matched = any(expected in (a or "").lower() for a in answers) if expected else False
        results.append({"question": q, "expected": expected, "matched": matched, "answers": answers})

    total = len(results)
    matched_count = sum(1 for r in results if r["matched"]) 
    consistency_issues = sum(1 for r in results if len(set(r["answers"])) > 1)

    summary = {
        "total": total,
        "matched": matched_count,
        "precision_percent": (matched_count / total * 100) if total else 0,
        "consistency_issues": consistency_issues,
    }

    out = {"summary": summary, "results": results}
    Path("scripts").joinpath("semantic_evaluation_result.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    evaluate()
