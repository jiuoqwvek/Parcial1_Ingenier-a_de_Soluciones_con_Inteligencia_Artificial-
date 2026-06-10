import requests
import json
import time
import random
from typing import List, Dict

BACKEND_URL = "http://localhost/api"
# Si ejecutas sin Docker: BACKEND_URL = "http://localhost:8000"

def test_inventory_queries(num_requests: int = 10):
    """Genera consultas al inventario para pruebas."""
    queries = [
        "¿Qué productos tienen stock crítico?",
        "¿Cuál es el inventario actual?",
        "¿Cuántas unidades de arroz tenemos?",
        "Muestra productos con menos de 100 unidades",
        "¿Cuál es el producto más vendido?",
    ]
    
    print(f"\n📊 Generando {num_requests} consultas de inventario...")
    for i in range(num_requests):
        query = random.choice(queries)
        try:
            response = requests.post(
                f"{BACKEND_URL}/inventory/query",
                json={"question": query},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Consulta {i+1}: {query[:50]}...")
            else:
                print(f"❌ Consulta {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error en consulta {i+1}: {e}")
        time.sleep(0.5)


def test_stock_updates(num_requests: int = 10):
    """Genera actualizaciones de stock."""
    print(f"\n📦 Generando {num_requests} actualizaciones de stock...")
    skus = ["SKU-ARR-001", "SKU-PAN-001", "SKU-LEC-001"]
    
    for i in range(num_requests):
        sku = random.choice(skus)
        new_stock = random.randint(50, 500)
        try:
            response = requests.post(
                f"{BACKEND_URL}/inventory/stock",
                json={"sku_or_name": sku, "new_stock": new_stock},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Stock update {i+1}: {sku} -> {new_stock} unidades")
            else:
                print(f"❌ Stock update {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error en stock update {i+1}: {e}")
        time.sleep(0.5)


def test_orders(num_requests: int = 5):
    """Genera órdenes de prueba."""
    print(f"\n🛒 Generando {num_requests} órdenes...")
    
    for i in range(num_requests):
        items = [
            {"sku": "SKU-ARR-001", "nombre": "Arroz", "cantidad_orden": random.randint(1, 10), "precio": 2500.0},
            {"sku": "SKU-PAN-001", "nombre": "Pan", "cantidad_orden": random.randint(1, 5), "precio": 3500.0},
        ]
        total = sum(item["cantidad_orden"] * item["precio"] for item in items)
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/orders",
                json={
                    "items": items,
                    "total": total,
                    "cliente_email": f"cliente{i}@example.com",
                    "cliente_nombre": f"Cliente {i}"
                },
                timeout=10
            )
            if response.status_code == 200:
                order_data = response.json()
                order_id = order_data.get("order", {}).get("orden_id", "?")
                print(f"✅ Orden {i+1} creada: {order_id}")
            else:
                print(f"❌ Orden {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error en orden {i+1}: {e}")
        time.sleep(0.5)


def get_metrics():
    """Obtiene y muestra el resumen de métricas."""
    print("\n📊 Obteniendo métricas...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/metrics/summary",
            timeout=10
        )
        if response.status_code == 200:
            metrics = response.json().get("metrics", {})
            print(f"""
╔════════════════════════════════════════════════╗
║         RESUMEN DE MÉTRICAS                    ║
╠════════════════════════════════════════════════╣
║ Total Solicitudes: {metrics.get('total_requests', 0):<26} ║
║ Solicitudes Exitosas: {metrics.get('successful_requests', 0):<20} ║
║ Solicitudes Fallidas: {metrics.get('failed_requests', 0):<21} ║
║ Precisión: {metrics.get('precision_percent', 0):.2f}%{' ':<28} ║
║ Tasa de Error: {metrics.get('error_rate_percent', 0):.2f}%{' ':<27} ║
║ Latencia Promedio: {metrics.get('avg_latency_ms', 0):.0f}ms{' ':<23} ║
║ Latencia Mín/Máx: {metrics.get('min_latency_ms', 0):.0f}/{metrics.get('max_latency_ms', 0):.0f}ms{' ':<20} ║
║ P95 Latencia: {metrics.get('p95_latency_ms', 0):.0f}ms{' ':<27} ║
║ CPU Promedio: {metrics.get('avg_cpu_percent', 0):.2f}%{' ':<26} ║
║ Memoria Promedio: {metrics.get('avg_memory_percent', 0):.2f}%{' ':<22} ║
║ Tokens Procesados: {metrics.get('total_tokens_processed', 0):<21} ║
╚════════════════════════════════════════════════╝
            """)
        else:
            print(f"❌ Error obteniendo métricas: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_audit_log():
    """Obtiene y muestra el log de auditoría."""
    print("\n🔍 Obteniendo registro de auditoría...")
    try:
        response = requests.get(
            f"{BACKEND_URL}/audit/log?limit=10",
            timeout=10
        )
        if response.status_code == 200:
            logs = response.json().get("audit_log", [])
            print(f"\nÚltimos {len(logs)} eventos de auditoría:")
            for log in logs[-10:]:
                print(f"  • {log['timestamp']}: {log['action']} - {log['entity']}")
        else:
            print(f"❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Ejecuta el suite de pruebas."""
    print("""
╔════════════════════════════════════════════════╗
║     Script de Pruebas - Agente AI              ║
║     Generación de Datos para Observabilidad    ║
╚════════════════════════════════════════════════╝
    """)
    
    print(f"\n🔗 Backend: {BACKEND_URL}")
    time.sleep(2)
    
    # Pruebas
    test_inventory_queries(num_requests=15)
    test_stock_updates(num_requests=10)
    test_orders(num_requests=5)
    
    print("\n⏳ Esperando procesamiento de datos...")
    time.sleep(3)
    
    # Mostrar resultados
    get_metrics()
    get_audit_log()
    
    print("\n✅ Suite de pruebas completado.")


if __name__ == "__main__":
    main()
