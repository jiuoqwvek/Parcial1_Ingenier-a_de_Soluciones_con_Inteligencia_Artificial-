import json
import os
import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Agente Unificado AI", layout="wide")

st.markdown(
    """
    <style>
    /* Tema General Unimarc */
    .stApp {
        background: #f4f6f9;
        color: #2b2b2b;
    }
    /* Botones dinámicos y llamativos */
    .stButton>button {
        background-color: #E2001A !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        width: 100%;
        padding: 0.6rem !important;
    }
    .stButton>button:hover {
        background-color: #B20014 !important;
        box-shadow: 0 4px 12px rgba(226, 0, 26, 0.3) !important;
        transform: translateY(-2px);
    }
    /* Cajas estilizadas */
    .box-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 5px solid #E2001A;
        box-shadow: 0 4px 8px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    /* Encabezados y textos */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .section-header h2 {
        margin: 0;
        font-size: 1.45rem;
    }
    .section-subtitle {
        color: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "last_response" not in st.session_state:
    st.session_state.last_response = None

menu = st.sidebar.selectbox(
    "Navegación",
    ["Estado", "Inventario", "Consulta AI", "Stock", "Órdenes", "Alertas"],
)

st.sidebar.markdown("# Navegación")
st.sidebar.markdown(
    "Bienvenido al panel de gestión AI para inventario, órdenes y alertas. Usa el menú para moverte entre secciones.")
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Backend**: `{BACKEND_URL}`")


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


def render_section_header(title, subtitle=None):
    subtitle_html = f"<div class='section-subtitle'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class='section-header'>
            <div>
                <h2>{title}</h2>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if menu == "Estado":
    render_section_header("Estado del ecosistema", "Monitoreo inmediato del backend y la disponibilidad de servicios.")
    health = api_get("/health")
    if isinstance(health, dict) and health.get("status") == "ok":
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.subheader("Detalles técnicos del Servidor")
        for llave, valor in health.items():
            st.markdown(f"**{llave.capitalize()}:** `{valor}`")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(health)

elif menu == "Inventario":
    render_section_header("Inventario actual", "Visión clara del stock y los niveles de abastecimiento.")
    inventario = api_get("/inventory")
    if inventario.get("success"):
        inventory_data = inventario.get("inventory", [])
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.write("### Lista de productos")
        st.dataframe(inventory_data, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(inventario)

elif menu == "Consulta AI":
    render_section_header("Consulta de inventario con IA", "Responde preguntas sobre stock, productos y estado general del almacén.")
    
    pregunta = st.text_area("Describe tu consulta:", height=170)
    if st.button("Enviar consulta"):
        if pregunta.strip():
            resultado = api_post("/inventory/query", {"question": pregunta})
            if "error" in resultado:
                st.error(f"Consulta bloqueada por seguridad: {resultado['error']}")
            st.session_state.last_response = resultado
        else:
            st.warning("Escribe tu pregunta antes de enviar.")

    if st.session_state.last_response:
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.subheader("Respuesta del Agente")
        resp = st.session_state.last_response
        
        if isinstance(resp, str):
            st.markdown(resp)
        elif isinstance(resp, dict):
            # Buscamos la llave más probable que contenga el texto de la IA
            mensaje = resp.get("answer") or resp.get("respuesta") or resp.get("response") or resp.get("mensaje") or resp.get("text")
            
            if mensaje:
                st.markdown(mensaje)
            else:
                # Si es un formato desconocido, extrae solo los valores como texto plano
                texto_plano = " ".join([str(v) for v in resp.values()])
                st.markdown(texto_plano)
        else:
            st.write(str(resp))
            
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Stock":
    render_section_header("Actualizar stock", "Ajusta niveles de inventario de forma rápida y confiable.")
    with st.form(key="stock_form"):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("SKU o nombre del producto")
        with col2:
            nuevo_stock = st.number_input("Nuevo stock", min_value=0, value=0)
        enviar = st.form_submit_button("Actualizar stock")
        
    if enviar:
        if sku.strip():
            resultado = api_post("/inventory/stock", {"sku_or_name": sku, "new_stock": int(nuevo_stock)})
            if resultado.get("success"):
                st.success("Stock actualizado con éxito.")
                st.info(f"Nuevos niveles registrados en sistema para {sku}.")
            else:
                st.error(f"Error al actualizar: {resultado.get('error', 'Desconocido')}")
        else:
            st.warning("Completa el SKU o nombre del producto.")

elif menu == "Órdenes":
    render_section_header("Gestión de órdenes", "Crea solicitudes y administra el flujo de aprobación desde un solo panel.")
    with st.expander("Crear nueva orden", expanded=True):
        st.markdown("Completa los datos de la orden y presiona crear para enviar la solicitud y notificar al cliente.")
        cliente_email = st.text_input("Email del cliente")
        cliente_nombre = st.text_input("Nombre del cliente")
        
        st.write("**Artículos de la orden**")
        df_inicial = pd.DataFrame([
            {"sku": "SKU-ARR-001", "nombre": "Arroz", "cantidad_orden": 10, "precio": 2500.0},
            {"sku": "SKU-PAN-001", "nombre": "Pan", "cantidad_orden": 5, "precio": 3500.0}
        ])

        df_editado = st.data_editor(df_inicial, num_rows="dynamic", use_container_width=True)
        items = df_editado.to_dict('records') 

        total = st.number_input("Total de la orden", min_value=0.0, value=0.0)
        
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
                        st.warning(f"Correo no enviado: {email_info['razon']}")
                    else:
                        st.error(f"Error al enviar correo: {email_info.get('error', 'desconocido')}")
            except Exception as exc:
                st.error(f"Error al procesar orden: {exc}")

    st.markdown("---")
    st.subheader("Revisión de Órdenes Pendientes")
    pending = api_get("/orders/pending")
    
    if pending.get("success"):
        st.write(f"Órdenes pendientes de aprobación: {pending.get('count')}")
        for orden in pending.get("pending_orders", []):
            with st.expander(f"Orden {orden.get('orden_id')} - {orden.get('cliente_nombre')}"):
                st.markdown("<div class='box-card'>", unsafe_allow_html=True)
                
                st.markdown(f"""
                **Cliente:** {orden.get('cliente_nombre', 'N/A')} | {orden.get('cliente_email', 'Sin correo')}  
                **Total:** ${orden.get('total', 0):,.0f}  
                **Estado:** Pendiente de revisión
                """)
                
                if orden.get('items'):
                    st.table(pd.DataFrame(orden.get('items')))
                st.markdown("</div>", unsafe_allow_html=True)
                
                token = orden.get("token")
                col1, col2 = st.columns(2)
                
                if col1.button("Aprobar", key=f"aprobar-{token}"):
                    resultado = api_post(f"/orders/{token}/approve", {})
                    if resultado.get("success"):
                        st.success("Orden aprobada exitosamente.")
                    else:
                        st.error("Hubo un problema al aprobar la orden.")
                        
                if col2.button("Rechazar", key=f"rechazar-{token}"):
                    razon = st.text_input("Razón de rechazo", key=f"razon-{token}")
                    if razon.strip():
                        resultado = api_post(f"/orders/{token}/reject", {"razon": razon})
                        if resultado.get("success"):
                            st.success("Orden rechazada en el sistema.")
                        else:
                            st.error("Hubo un problema al rechazar la orden.")
    else:
        st.error(pending.get("error", "No se pudieron cargar las órdenes pendientes."))

elif menu == "Alertas":
    render_section_header("Alertas de stock crítico", "Visualiza los productos que requieren atención inmediata.")
    criticos = api_get("/alerts/critical-stock")
    if criticos.get("success"):
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.write(f"**Productos críticos encontrados:** {criticos.get('count')}")
        st.dataframe(criticos.get("critical_products", []), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(criticos)