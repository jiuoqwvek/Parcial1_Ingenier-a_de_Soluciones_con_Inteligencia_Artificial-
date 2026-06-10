import json
import os
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="Monitoreo - Agente AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard de Monitoreo - Agente Unificado AI")

def api_get(path):
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=15)
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}

# Sidebar para filtros
st.sidebar.markdown("## Filtros y Opciones")
refresh_interval = st.sidebar.slider("Refrescar cada (segundos)", 10, 300, 30)
endpoint_filter = st.sidebar.selectbox(
    "Filtrar por endpoint",
    ["Todos", "/inventory/query", "/inventory/stock", "/orders", "/alerts/critical-stock"]
)
metrics_limit = st.sidebar.slider("Últimos registros", 50, 500, 100)

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Resumen de Métricas",
    "⏱️ Latencia y Rendimiento",
    "🔍 Auditoría",
    "📋 Timeline de Eventos"
])

# ============= TAB 1: RESUMEN DE MÉTRICAS =============
with tab1:
    col1, col2 = st.columns(2)
    
    # Obtener datos
    endpoint_param = None if endpoint_filter == "Todos" else endpoint_filter
    metrics_data = api_get(f"/metrics/summary?endpoint={endpoint_param}" if endpoint_param else "/metrics/summary")
    
    if metrics_data.get("success"):
        metrics = metrics_data.get("metrics", {})
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Total Solicitudes",
                f"{metrics.get('total_requests', 0)}",
                delta=f"{metrics.get('successful_requests', 0)} exitosas"
            )
        
        with col2:
            precision = metrics.get('precision_percent', 0)
            st.metric(
                "✅ Precisión",
                f"{precision:.1f}%",
                delta=f"{metrics.get('successful_requests', 0)}/{metrics.get('total_requests', 0)}"
            )
        
        with col3:
            error_rate = metrics.get('error_rate_percent', 0)
            st.metric(
                "❌ Tasa de Error",
                f"{error_rate:.1f}%",
                delta=f"{metrics.get('failed_requests', 0)} errores"
            )
        
        with col4:
            st.metric(
                "⚡ Latencia Promedio",
                f"{metrics.get('avg_latency_ms', 0):.0f}ms",
                delta=f"P95: {metrics.get('p95_latency_ms', 0):.0f}ms"
            )
        
        st.divider()
        
        # Gráfico de latencia
        col1, col2 = st.columns(2)
        
        with col1:
            latency_fig = go.Figure(data=[
                go.Bar(name="Min", x=["Latencia"], y=[metrics.get('min_latency_ms', 0)]),
                go.Bar(name="Promedio", x=["Latencia"], y=[metrics.get('avg_latency_ms', 0)]),
                go.Bar(name="P95", x=["Latencia"], y=[metrics.get('p95_latency_ms', 0)]),
                go.Bar(name="Max", x=["Latencia"], y=[metrics.get('max_latency_ms', 0)]),
            ])
            latency_fig.update_layout(title="Estadísticas de Latencia (ms)", height=350, showlegend=True)
            st.plotly_chart(latency_fig, use_container_width=True)
        
        with col2:
            # Gráfico de recursos
            cpu = metrics.get('avg_cpu_percent', 0)
            mem = metrics.get('avg_memory_percent', 0)
            
            resource_fig = go.Figure(data=[
                go.Bar(name="CPU", x=["Uso de Recursos"], y=[cpu]),
                go.Bar(name="Memoria", x=["Uso de Recursos"], y=[mem]),
            ])
            resource_fig.update_layout(title="Uso Promedio de Recursos (%)", height=350, showlegend=True)
            st.plotly_chart(resource_fig, use_container_width=True)
        
        st.divider()
        
        # Tabla de resumen
        summary_table = pd.DataFrame({
            "Métrica": [
                "Total de Solicitudes",
                "Solicitudes Exitosas",
                "Solicitudes Fallidas",
                "Precisión (%)",
                "Tasa de Error (%)",
                "Latencia Promedio (ms)",
                "Latencia Mínima (ms)",
                "Latencia Máxima (ms)",
                "P95 Latencia (ms)",
                "CPU Promedio (%)",
                "Memoria Promedio (%)",
                "Tokens Procesados",
            ],
            "Valor": [
                metrics.get('total_requests', 0),
                metrics.get('successful_requests', 0),
                metrics.get('failed_requests', 0),
                f"{metrics.get('precision_percent', 0):.2f}",
                f"{metrics.get('error_rate_percent', 0):.2f}",
                f"{metrics.get('avg_latency_ms', 0):.2f}",
                f"{metrics.get('min_latency_ms', 0):.2f}",
                f"{metrics.get('max_latency_ms', 0):.2f}",
                f"{metrics.get('p95_latency_ms', 0):.2f}",
                f"{metrics.get('avg_cpu_percent', 0):.2f}",
                f"{metrics.get('avg_memory_percent', 0):.2f}",
                metrics.get('total_tokens_processed', 0),
            ]
        })
        st.dataframe(summary_table, use_container_width=True, hide_index=True)
    else:
        st.error(metrics_data)

# ============= TAB 2: LATENCIA Y RENDIMIENTO =============
with tab2:
    timeline_data = api_get(f"/metrics/timeline?endpoint={endpoint_param}&limit={metrics_limit}" if endpoint_param else f"/metrics/timeline?limit={metrics_limit}")
    
    if timeline_data.get("success") and timeline_data.get("timeline"):
        timeline = timeline_data.get("timeline", [])
        
        df = pd.DataFrame(timeline)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Gráfico de latencia a lo largo del tiempo
        latency_line = px.line(
            df,
            x='timestamp',
            y='latency_ms',
            title='Latencia a lo Largo del Tiempo',
            labels={'timestamp': 'Hora', 'latency_ms': 'Latencia (ms)'},
            hover_data=['endpoint', 'status_code', 'source']
        )
        latency_line.update_layout(height=400)
        st.plotly_chart(latency_line, use_container_width=True)
        
        # Gráfico de tasa de error
        df['success'] = df['success'].astype(int)
        error_rate = df.groupby(pd.Grouper(key='timestamp', freq='5min'))['success'].apply(
            lambda x: (1 - x.mean()) * 100 if len(x) > 0 else 0
        ).reset_index()
        error_rate.columns = ['timestamp', 'error_rate_percent']
        
        error_line = px.line(
            error_rate,
            x='timestamp',
            y='error_rate_percent',
            title='Tasa de Error a lo Largo del Tiempo (%)',
            labels={'timestamp': 'Hora', 'error_rate_percent': 'Tasa de Error (%)'}
        )
        error_line.update_layout(height=400)
        st.plotly_chart(error_line, use_container_width=True)
        
        # Distribución de endpoints
        endpoint_dist = df['endpoint'].value_counts()
        pie_fig = px.pie(
            values=endpoint_dist.values,
            names=endpoint_dist.index,
            title='Distribución de Solicitudes por Endpoint'
        )
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No hay datos de timeline disponibles. Realiza algunas consultas primero.")

# ============= TAB 3: AUDITORÍA =============
with tab3:
    audit_data = api_get("/audit/log?limit=200")
    
    if audit_data.get("success"):
        audit_logs = audit_data.get("audit_log", [])
        
        if audit_logs:
            df_audit = pd.DataFrame(audit_logs)
            df_audit['timestamp'] = pd.to_datetime(df_audit['timestamp'])
            
            # Filtros de auditoría
            col1, col2 = st.columns(2)
            with col1:
                action_filter = st.multiselect(
                    "Filtrar por acción",
                    df_audit['action'].unique(),
                    default=df_audit['action'].unique()
                )
            with col2:
                entity_filter = st.multiselect(
                    "Filtrar por entidad",
                    df_audit['entity'].unique(),
                    default=df_audit['entity'].unique()
                )
            
            df_audit = df_audit[
                (df_audit['action'].isin(action_filter)) &
                (df_audit['entity'].isin(entity_filter))
            ]
            
            # Tabla de auditoría
            st.subheader("Registro de Auditoría")
            display_cols = ['timestamp', 'action', 'entity', 'details', 'audit_id']
            st.dataframe(df_audit[display_cols], use_container_width=True, hide_index=True)
            
            # Gráfico de acciones
            action_counts = df_audit['action'].value_counts()
            action_fig = px.bar(
                x=action_counts.index,
                y=action_counts.values,
                title='Distribución de Acciones de Auditoría',
                labels={'x': 'Acción', 'y': 'Cantidad'}
            )
            st.plotly_chart(action_fig, use_container_width=True)
        else:
            st.info("No hay registros de auditoría disponibles.")
    else:
        st.error(audit_data)

# ============= TAB 4: TIMELINE DE EVENTOS =============
with tab4:
    timeline_data = api_get(f"/metrics/timeline?endpoint={endpoint_param}&limit={metrics_limit}" if endpoint_param else f"/metrics/timeline?limit={metrics_limit}")
    
    if timeline_data.get("success") and timeline_data.get("timeline"):
        timeline = timeline_data.get("timeline", [])
        df = pd.DataFrame(timeline)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        # Tabla de eventos con colores de estado
        st.subheader("Eventos Recientes")
        
        for idx, row in df.head(50).iterrows():
            status_color = "🟢" if row['success'] else "🔴"
            cols = st.columns([0.5, 1, 1, 1, 1, 1])
            
            with cols[0]:
                st.write(status_color)
            with cols[1]:
                st.write(f"**{row['timestamp'].strftime('%H:%M:%S')}**")
            with cols[2]:
                st.write(f"`{row['endpoint']}`")
            with cols[3]:
                st.write(f"{row['latency_ms']:.0f}ms")
            with cols[4]:
                st.write(f"Status: {row['status_code']}")
            with cols[5]:
                st.write(f"Tokens: {row.get('total_tokens', 0)}")
    else:
        st.info("No hay eventos disponibles.")

# Footer
st.divider()
st.markdown(f"""
**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Backend URL:** `{BACKEND_URL}`  
**Intervalo de refresco:** {refresh_interval}s
""")
