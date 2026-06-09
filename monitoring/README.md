# Dashboard de Monitoreo - Agente AI

Dashboard interactivo de observabilidad construido con **Streamlit** para monitoreo en tiempo real del agente unificado.

## Características

✅ **Métricas de Rendimiento:**
- Precisión, latencia, tasa de errores
- Uso de CPU y memoria
- Tokens procesados

✅ **Visualizaciones:**
- Gráficos de latencia a lo largo del tiempo
- Distribución de errores por endpoint
- Uso de recursos en tiempo real
- Timeline de eventos con filtros

✅ **Auditoría y Trazabilidad:**
- Log completo de todas las acciones (CREATE, UPDATE, APPROVE, REJECT)
- Filtros por acción y entidad
- Timestamps detallados

## Cómo usar

### Via Docker Compose
```bash
cd deploy
docker compose up --build
# Dashboard disponible en http://localhost/monitoring
```

### Localmente
```bash
pip install -r requirements.txt
BACKEND_URL=http://localhost:8000 streamlit run dashboard.py
# Abre http://localhost:8501
```

## Tabs disponibles

1. **📈 Resumen de Métricas:** KPIs principales, latencia, recursos
2. **⏱️ Latencia y Rendimiento:** Gráficos temporales, distribución de endpoints
3. **🔍 Auditoría:** Log de cambios, acciones de usuarios
4. **📋 Timeline de Eventos:** Historial detallado de solicitudes

## Endpoints de API consumidos

```
GET /health                    - Estado del backend
GET /metrics/summary          - Resumen agregado de métricas
GET /metrics/timeline         - Timeline para gráficos
GET /audit/log                - Log de auditoría
GET /inventory                - Inventario actual
GET /orders/pending           - Órdenes pendientes
GET /alerts/critical-stock    - Productos con stock crítico
```

## Interpretación de métricas

| Métrica | Significado | Objetivo |
|---------|-------------|----------|
| **Precisión** | % solicitudes exitosas | ≥ 95% |
| **Latencia P95** | 95º percentil de tiempo respuesta | < 500ms |
| **Tasa de Error** | % solicitudes fallidas | < 5% |
| **CPU/Memoria** | Promedio de recursos | < 70% |

## Datos de prueba

Ejecuta el script de pruebas para generar datos:
```bash
python ../scripts/test_metrics.py
```

Esto genera ~30 solicitudes variadas que alimentan las métricas.
