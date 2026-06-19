import json
import os
import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(
    page_title="Unimarc AI - Gestión de Inventario",
    layout="wide",
    page_icon="🛒"
)

# ============================================================
# ESTILOS CSS PERSONALIZADOS - DISEÑO UNIMARC
# ============================================================
st.markdown(
    """
    <style>
    /* ===== TEMA GENERAL ===== */
    .stApp {
        background: #f0f2f6;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    /* ===== ELIMINAR PADDING EXTRA ===== */
    .main > div {
        padding-top: 0rem;
    }
    
    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: #1a2a3a !important;
        padding: 1.5rem 1rem !important;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #b0c4d8 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown strong {
        color: #ffffff !important;
    }
    
    /* ===== ESTILO DEL SELECTBOX EN SIDEBAR ===== */
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
        background: #243447 !important;
        border-radius: 8px !important;
        border: 1px solid #3a4a5a !important;
        padding: 0.2rem 0.5rem !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] select {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* ===== BOTONES PRINCIPALES ===== */
    .stButton > button {
        background: linear-gradient(135deg, #E2001A 0%, #c40016 100%) !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.25s ease !important;
        width: 100%;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 8px rgba(226, 0, 26, 0.25);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(226, 0, 26, 0.35);
        background: linear-gradient(135deg, #c40016 0%, #a00012 100%) !important;
    }
    
    /* ===== ENCABEZADOS ===== */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e8eaed;
    }
    .section-header h2 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        color: #1a2a3a;
        letter-spacing: -0.3px;
    }
    .section-header .subtitle {
        color: #6b7a8a;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.1rem;
    }
    .section-header .badge-unimarc {
        background: #E2001A;
        color: white;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* ===== TABLAS ===== */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    .stDataFrame thead tr th {
        background: #1a2a3a !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.7rem 0.5rem !important;
    }
    .stDataFrame tbody tr:hover {
        background: #f8f9fa !important;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: #f8f9fa !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #1a2a3a !important;
        border-left: 4px solid #E2001A !important;
    }
    .streamlit-expanderHeader:hover {
        background: #eef0f2 !important;
    }
    
    /* ===== INPUTS ===== */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        border-radius: 6px !important;
        border: 1.5px solid #dde1e6 !important;
        transition: border-color 0.2s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #E2001A !important;
        box-shadow: 0 0 0 3px rgba(226, 0, 26, 0.10) !important;
    }
    
    /* ===== ALERTAS ===== */
    .stAlert {
        border-radius: 8px !important;
        border-left: 5px solid #E2001A !important;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .section-header {
            flex-direction: column;
            align-items: flex-start;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# ============================================================
# SIDEBAR - CON MENÚ E INFORMACIÓN (SIN LOGO)
# ============================================================
with st.sidebar:
    menu = st.selectbox(
        "MENU PRINCIPAL",
        ["Estado", "Inventario", "Consulta AI", "Stock", "Ordenes", "Alertas"],
        key="main_menu"
    )
    
    st.markdown(
        """
        <div style='color: #b0c4d8; font-size: 0.8rem; padding: 0.5rem; text-align: center; margin-top: 1rem;'>
            <strong>Unimarc AI</strong><br>
            Panel de gestion inteligente<br>
            <span style='color: #6b8a9e;'>v2.0 · Conectado</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"`{BACKEND_URL}`")

# ============================================================
# FUNCIONES DE API
# ============================================================
def api_get(path):
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=15)
        if response.status_code >= 400:
            try:
                return {"error": response.json().get("detail", f"HTTP {response.status_code}")}
            except Exception:
                return {"error": response.text or f"HTTP {response.status_code}"}
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def api_post(path, payload):
    try:
        response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=20)
        if response.status_code >= 400:
            try:
                return {"error": response.json().get("detail", f"HTTP {response.status_code}")}
            except Exception:
                return {"error": response.text or f"HTTP {response.status_code}"}
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def render_section_header(title, subtitle=None, badge=None):
    badge_html = f"<span class='badge-unimarc'>{badge}</span>" if badge else ""
    subtitle_html = f"<div class='subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class='section-header'>
            <div>
                <h2>{title}</h2>
                {subtitle_html}
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# PÁGINAS - SIN SEPARADORES VACÍOS
# ============================================================

# ---- ESTADO ----
if menu == "Estado":
    render_section_header(
        "Estado del Sistema",
        "Monitoreo en tiempo real del backend y servicios",
        "OPERATIVO"
    )
    
    health = api_get("/health")
    if isinstance(health, dict) and health.get("status") == "ok":
        st.info("El sistema se encuentra funcionando correctamente. Todos los servicios estan disponibles.")
    else:
        st.error(health)

# ---- INVENTARIO ----
elif menu == "Inventario":
    render_section_header(
        "Inventario Unimarc",
        "Vision completa del stock y niveles de abastecimiento"
    )
    
    inventario = api_get("/inventory")
    if inventario.get("success"):
        inventory_data = inventario.get("inventory", [])
        
        if inventory_data:
            total_items = len(inventory_data)
            total_stock = sum(item.get('stock', 0) for item in inventory_data if isinstance(item, dict))
            low_stock = sum(1 for item in inventory_data if isinstance(item, dict) and item.get('stock', 0) < 10)
            
            st.write("### Resumen")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Articulos", total_items)
            with col2:
                st.metric("Stock Total", total_stock)
            with col3:
                st.metric("Stock Critico", low_stock)
        
        st.write("### Lista de Productos")
        st.dataframe(inventory_data)
    else:
        st.error(inventario)

# ---- CONSULTA AI ----
elif menu == "Consulta AI":
    render_section_header(
        "Asistente IA de Inventario",
        "Pregunta sobre stock, productos y estado del almacen"
    )
    
    st.markdown("""
    <div style='background: #eef2f7; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #E2001A;'>
        <strong>Ejemplos:</strong><br>
        - "¿Cuanto stock tengo de arroz?"<br>
        - "Muestrame los productos con menos de 5 unidades"<br>
        - "¿Cual es el producto mas vendido?"
    </div>
    """, unsafe_allow_html=True)
    
    pregunta = st.text_area(
        "Escribe tu consulta:",
        height=120,
        placeholder="Ej: ¿Que productos necesitan reposicion urgente?"
    )
    
    if st.button("Consultar IA"):
        if pregunta.strip():
            resultado = api_post("/inventory/query", {"question": pregunta})
            if "error" in resultado:
                st.error(f"Error: {resultado['error']}")
            st.session_state.last_response = resultado
        else:
            st.warning("Escribe una pregunta antes de consultar.")

    if st.session_state.last_response:
        st.subheader("Respuesta del Agente")
        resp = st.session_state.last_response
        
        if isinstance(resp, str):
            st.markdown(resp)
        elif isinstance(resp, dict):
            mensaje = (
                resp.get("answer") or 
                resp.get("respuesta") or 
                resp.get("response") or 
                resp.get("mensaje") or 
                resp.get("text")
            )
            if mensaje:
                st.markdown(f"<div style='font-size: 1.05rem;'>{mensaje}</div>", unsafe_allow_html=True)
            else:
                st.write(str(resp))
        else:
            st.write(str(resp))

# ---- STOCK ----
elif menu == "Stock":
    render_section_header(
        "Agregar / Actualizar Stock",
        "Agrega un nuevo producto o ajusta el stock existente"
    )
    
    with st.form(key="stock_form"):
        sku = st.text_input("SKU o nombre del producto", placeholder="Ej: SKU-ARR-001")
        nuevo_stock = st.number_input("Nuevo stock", min_value=0, value=0, step=1)
        enviar = st.form_submit_button("Guardar")
    
    if enviar:
        if sku.strip():
            payload = {"sku_or_name": sku, "new_stock": int(nuevo_stock)}
            resultado = api_post("/inventory/stock", payload)
            if resultado.get("success"):
                if resultado.get("created"):
                    st.success(f"Producto {sku} creado con {nuevo_stock} unidades")
                else:
                    st.success(f"Stock actualizado para {sku}")
                    st.info(f"Nuevo nivel: {nuevo_stock} unidades")
            else:
                st.error(f"Error: {resultado.get('error', 'Error desconocido')}")
        else:
            st.warning("Completa el SKU o nombre del producto.")

# ---- ÓRDENES ----
elif menu == "Ordenes":
    render_section_header(
        "Gestion de Ordenes",
        "Crea solicitudes y administra el flujo de aprobacion",
        "PENDIENTES"
    )
    
    with st.expander("Crear nueva orden", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cliente_email = st.text_input("Email del cliente", placeholder="cliente@ejemplo.com")
        with col2:
            cliente_nombre = st.text_input("Nombre del cliente", placeholder="Nombre completo")
        
        st.write("### Articulos de la orden")
        df_inicial = pd.DataFrame([
            {"sku": "SKU-ARR-001", "nombre": "Arroz", "cantidad_orden": 10, "precio": 2500.0},
            {"sku": "SKU-PAN-001", "nombre": "Pan", "cantidad_orden": 5, "precio": 3500.0}
        ])
        df_editado = st.data_editor(df_inicial, num_rows="dynamic")
        items = df_editado.to_dict('records')
        
        total = sum(item.get("cantidad_orden", 0) * item.get("precio", 0) for item in items)
        st.metric("Total de la orden", f"${total:,.0f}")
        
        if st.button("Crear orden"):
            try:
                payload = {
                    "items": items,
                    "total": float(total),
                    "cliente_email": cliente_email,
                    "cliente_nombre": cliente_nombre,
                }
                resultado = api_post("/orders", payload)
                if resultado.get("success"):
                    st.success("Orden creada correctamente.")
                
                email_info = resultado.get("email")
                if isinstance(email_info, dict):
                    if email_info.get("exito"):
                        st.success(f"Correo enviado a {email_info.get('destinatario')}")
                    elif email_info.get("razon"):
                        st.warning(f"Advertencia: {email_info['razon']}")
                    else:
                        st.error(f"Error: {email_info.get('error', 'Error al enviar correo')}")
            except Exception as exc:
                st.error(f"Error al procesar orden: {exc}")

    st.subheader("Ordenes Pendientes de Aprobacion")
    
    pending = api_get("/orders/pending")
    if pending.get("success"):
        count = pending.get('count', 0)
        st.info(f"{count} ordenes pendientes" if count > 0 else "No hay ordenes pendientes")
        
        for orden in pending.get("pending_orders", []):
            with st.expander(f"Orden #{orden.get('orden_id')} - {orden.get('cliente_nombre')}"):
                st.markdown(f"""
                **Cliente:** {orden.get('cliente_nombre', 'N/A')} | {orden.get('cliente_email', 'Sin correo')}  
                **Total:** ${orden.get('total', 0):,.0f}  
                **Estado:** Pendiente de revision
                """)
                if orden.get('items'):
                    st.table(pd.DataFrame(orden.get('items')))
                
                token = orden.get("token")
                col1, col2 = st.columns(2)
                if col1.button("Aprobar", key=f"aprobar-{token}"):
                    resultado = api_post(f"/orders/{token}/approve", {})
                    if resultado.get("success"):
                        st.success("Orden aprobada exitosamente.")
                    else:
                        st.error("Error al aprobar la orden.")
                
                if col2.button("Rechazar", key=f"rechazar-{token}"):
                    razon = st.text_input("Motivo del rechazo:", key=f"razon-{token}")
                    if razon.strip():
                        resultado = api_post(f"/orders/{token}/reject", {"razon": razon})
                        if resultado.get("success"):
                            st.success("Orden rechazada.")
                        else:
                            st.error("Error al rechazar la orden.")
    else:
        st.error(pending.get("error", "No se pudieron cargar las ordenes pendientes."))

# ---- ALERTAS ----
elif menu == "Alertas":
    criticos = api_get("/alerts/critical-stock")
    
    render_section_header(
        "Alertas de Stock Critico",
        "Productos que requieren atencion inmediata",
        f"{len(criticos.get('critical_products', [])) if criticos.get('success') else 0} ALERTAS"
    )
    
    if criticos.get("success"):
        critical_products = criticos.get("critical_products", [])
        
        if critical_products:
            st.warning(f"**{len(critical_products)}** productos con stock critico")
            st.dataframe(critical_products)
        else:
            st.success("No hay productos con stock critico. Todo en orden!")
    else:
        st.error(criticos)