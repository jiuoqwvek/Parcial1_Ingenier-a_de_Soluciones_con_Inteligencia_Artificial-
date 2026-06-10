# Observabilidad - Agente AI

## Indicadores de Logro (Rúbrica)

Este despliegue cumple con los requisitos de **Evaluación Parcial N°3**:

### IE1: Métricas de observabilidad (Precisión, Consistencia, Errores)
- ✅ `deploy/backend/metrics.py`: recopila precisión (% exitosas), tasa de errores
- ✅ Disponible en endpoint `/metrics/summary`
- ✅ Adaptado a escenarios variados (inventario, órdenes, alertas)

### IE2: Métricas de latencia y recursos
- ✅ Latencia: min/avg/max/p95 en ms por request
- ✅ Recursos: CPU y memoria promedio por ventana
- ✅ Tokens procesados (entrada/salida)
- ✅ Endpoint: `/metrics/timeline`

### IE3: Análisis de logs y trazabilidad
- ✅ `deploy/backend/database.py`: log de auditoría completo
- ✅ Cada acción registra: timestamp UTC, usuario, acción (CREATE/UPDATE/APPROVE/REJECT), detalles
- ✅ Endpoint: `/audit/log`

### IE4: Identificar patrones y anomalías
- ✅ Dashboard detecta:
  - Picos de latencia (gráfico temporal)
  - Incremento de tasa de errores
  - Distribución desigual por endpoint
  - Patrones de horario

### IE5: Dashboard visual de monitoreo
- ✅ `deploy/monitoring/dashboard.py`: 4 tabs interactivos
  - Tab 1: KPIs (precisión, latencia, errores, recursos)
  - Tab 2: Gráficos temporales (latencia, tasa de error)
  - Tab 3: Auditoría con filtros
  - Tab 4: Timeline de eventos

### IE6: Protocolos de seguridad y responsabilidad
- ✅ `deploy/backend/guardrails.py`: 
  - Detección de prompt injection
  - Redacción de PII (emails, RUT, números de tarjeta)
  - Rate limiting (20 req/min/IP)
  - Validación de payload antes de procesar
- ✅ `deploy/backend/database.py`: auditoría inmutable
- ✅ Variables sensibles en `.env.example`

### IE7: Propuestas de mejora basadas en datos
- ✅ Documentado en `deploy/README.md` - Sección "Propuestas de mejora"
- Críticas: Autenticación, HTTPS, persistencia escalable
- Recomendadas: Alertas automáticas, Prometheus/Grafana

### IE8/IE9: Informe técnico y redacción clara
- ✅ README.md estructurado
- ✅ Documentación técnica en cada módulo
- ✅ Capturas y gráficos generados por dashboard interactivo

---

## Cómo ejecutar para demostración

### 1. Levantar servicios
```bash
cd deploy
docker compose up --build
```

### 2. Generar datos de prueba
```bash
python scripts/test_metrics.py
```

### 3. Visualizar métricas
- Dashboard: http://localhost/monitoring
- API: http://localhost/api/docs

---

## Estructura de archivos

```
deploy/
├── README.md                      # Guía principal
├── docker-compose.yml             # Orquestación de 4 servicios
├── Caddyfile                      # Proxy inverso
│
├── backend/                       # API FastAPI
│   ├── app.py                    # Endpoints principales + métricas
│   ├── metrics.py                # IE1, IE2: Recopilación de métricas
│   ├── database.py               # IE3, IE6: Log de auditoría
│   ├── guardrails.py             # IE6: Seguridad y validación
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── data/                     # JSON persistence
│
├── frontend/                      # UI Streamlit
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── monitoring/                    # IE5: Dashboard observabilidad
│   ├── dashboard.py              # 4 tabs interactivos
│   ├── README.md
│   ├── requirements.txt
│   └── Dockerfile
│
└── scripts/                       # Pruebas y generación de datos
    └── test_metrics.py           # 30 requests para generar métricas
```

---

## Mapeo a rúbrica

| IE | Componente | Archivo | Endpoint |
|----|-----------|---------|----------|
| IE1 | Métricas precisión/errores | metrics.py | `/metrics/summary` |
| IE2 | Latencia/recursos | metrics.py | `/metrics/timeline` |
| IE3 | Logs y trazabilidad | database.py | `/audit/log` |
| IE4 | Anomalías | dashboard.py | Gráficos Tab 2 |
| IE5 | Dashboard visual | dashboard.py | `/monitoring` |
| IE6 | Seguridad | guardrails.py + database.py | Middleware + audit |
| IE7 | Mejoras | README.md | Sección "Propuestas" |
| IE8 | Informe técnico | README.md | Todo |
| IE9 | Redacción técnica | Todo el código | - |

---

## Validación de implementación

Accede al dashboard en http://localhost/monitoring y verifica:

- [ ] Tab 1: Muestra KPIs (precisión ≥95%, latencia <200ms para cache)
- [ ] Tab 2: Gráficos temporales muestran evolución
- [ ] Tab 3: Log de auditoría muestra CREATE/APPROVE/REJECT
- [ ] Tab 4: Timeline lista eventos recientes
- [ ] Metrics summary reporta estadísticas agregadas
- [ ] Audit log muestra cambios de órdenes y stock
