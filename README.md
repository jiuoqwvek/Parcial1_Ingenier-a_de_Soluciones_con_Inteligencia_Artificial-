# Deploy Artifact

Despliegue completo de agente AI unificado con observabilidad integrada.

## Estructura

- `backend/`: microservicio FastAPI que unifica inventario, órdenes y correo con middleware de guardrails.
- `frontend/`: interfaz Streamlit que consume los endpoints del backend.
- `monitoring/`: dashboard de observabilidad en tiempo real con Streamlit.
- `scripts/`: herramientas de prueba y generación de datos.
- `Caddyfile`: proxy inverso para enrutar `/api/*`, `/monitoring/*` y frontend.
- `docker-compose.yml`: orquesta los cuatro servicios.

## Cómo ejecutar

### Con Docker Compose
```bash
cd deploy
cp backend/.env.example backend/.env
# Edita backend/.env con tus credenciales

docker compose up --build
```

Acceso a servicios:
- **Frontend UI**: http://localhost/
- **API Backend**: http://localhost/api/
- **Monitoring Dashboard**: http://localhost/monitoring
- **API Docs**: http://localhost/api/docs

### Localmente (sin Docker)
```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py  # En otro terminal: uvicorn app:app --reload

# Frontend
cd ../frontend
pip install -r requirements.txt
streamlit run app.py

# Monitoring
cd ../monitoring
pip install -r requirements.txt
BACKEND_URL=http://localhost:8000 streamlit run dashboard.py
```

## Generación de datos de prueba

```bash
# Genera ~30 solicitudes variadas para alimentar métricas
python scripts/test_metrics.py
```

Luego visualiza en el dashboard de monitoreo.

## Arquitectura de observabilidad

### Métricas recopiladas (IE1, IE2)
- **Precisión**: % de solicitudes exitosas
- **Latencia**: min/avg/max/p95 en ms
- **Errores**: tasa de fallos, conteos por estado
- **Recursos**: CPU y memoria promedio
- **Tokens**: tokens de entrada/salida procesados

### Logging y trazabilidad (IE3)
- Cada solicitud genera un record de métrica con request_id
- Log de auditoría completo: quién hizo qué, cuándo y por qué
- Timestamps UTC, duraciones, códigos HTTP

### Dashboard (IE5)
- 4 tabs: Resumen, Latencia/Rendimiento, Auditoría, Timeline
- Gráficos interactivos con Plotly
- Filtros por endpoint, rango temporal, acciones

## Seguridad (IE6)
- `guardrails.py`: detección de prompt injection, redacción de PII, rate limiting (20 req/min/IP)
- `database.py`: log de auditoría inmutable con timestamps
- Variables sensibles en `.env.example` (no versionar `.env` real)
- HTTPS recomendado en producción (Caddy lo soporta)

## Propuestas de mejora (IE7)

### Críticas para producción:
1. **Autenticación**: agregar JWT/OAuth2 en endpoints sensibles (`/orders/{token}/approve`, etc.)
2. **HTTPS**: configurar certificados en Caddy
3. **Persistencia escalable**: cambiar JSON → PostgreSQL/MongoDB
4. **Rate limiting distribuido**: usar Redis en lugar de dict en memoria

### Recomendadas:
5. Mejorar detección de PII (falsos negativos en regex)
6. Alertas automáticas cuando error_rate > 5% o p95_latency > 1000ms
7. Exportar métricas a Prometheus/Grafana para alertas más robustas

## Despliegue AWS

### ECS (Fargate)
```bash
# Usa docker-compose.yml como referencia
# Crea task definitions para cada servicio
# Configura ALB para enrutamiento
```

### RDS para persistencia
```
Reemplaza JSONDatabase con SQLAlchemy + PostgreSQL RDS
```

### CloudWatch para logs y métricas
```
Integra logging con boto3 para enviar a CloudWatch
```

## Notas de seguridad

- `deploy/backend/guardrails.py` valida y sanitiza el payload **antes** de procesar
- `deploy/backend/database.py` mantiene log de auditoría inmutable
- Rate limiter por IP para prevenir DDoS básico
- Redacción de PII en respuestas antes de retornar al cliente

