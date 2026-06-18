import json
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Agente Unificado AI", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: #eef4fb;
            color: #1f2937;
        }
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .page-header h1 {
            margin: 0;
            font-size: 2.5rem;
            letter-spacing: -0.04em;
        }
        .page-header p {
            margin: 0.35rem 0 0;
            color: #4b5563;
            font-size: 1rem;
        }
        .header-badge {
            background: #0f172a;
            color: #f8fafc;
            padding: 0.75rem 1rem;
            border-radius: 999px;
            font-weight: 600;
            font-size: 0.95rem;
        }
        .metric-card,
        .box-card {
            background: #ffffff;
            border-radius: 20px;
            padding: 1.35rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 18px 35px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }
        .metric-card-title {
            color: #475569;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-card-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            color: #0f172a;
        }
        .metric-card-note {
            color: #64748b;
            margin-top: 0.45rem;
            font-size: 0.93rem;
        }
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
    ["Estado", "Inventario", "Consulta AI", "Stock", "Órdenes", "Alertas", "Email"],
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


def render_metric(title, value, note=None):
    note_html = f"<div class='metric-card-note'>{note}</div>" if note else ""
    st.markdown(
        f"""
        <div class='metric-card'>
            <div class='metric-card-title'>{title}</div>
            <div class='metric-card-value'>{value}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        col1, col2 = st.columns(2)
        col1.markdown("<div class='metric-card'><div class='metric-card-title'>API</div><div class='metric-card-value'>Disponible</div></div>", unsafe_allow_html=True)
        col2.markdown(
            f"<div class='metric-card'><div class='metric-card-title'>Mensaje</div><div class='metric-card-value'>{health.get('message', 'Activo')}</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.subheader("Detalles técnicos")
        st.json(health)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(health)

elif menu == "Inventario":
    render_section_header("Inventario actual", "Visión clara del stock y los niveles de abastecimiento.")
    inventario = api_get("/inventory")
    if inventario.get("success"):
        inventory_data = inventario.get("inventory", [])
        total_products = inventario.get("count", len(inventory_data))
        low_stock = sum(1 for item in inventory_data if item.get("stock", 0) <= 5)
        critical_stock = sum(1 for item in inventory_data if item.get("stock", 0) == 0)

        card1, card2, card3 = st.columns([1, 1, 1])
        card1.markdown(
            f"<div class='metric-card'><div class='metric-card-title'>Total de productos</div><div class='metric-card-value'>{total_products}</div></div>",
            unsafe_allow_html=True,
        )
        card2.markdown(
            f"<div class='metric-card'><div class='metric-card-title'>Stock bajo</div><div class='metric-card-value'>{low_stock}</div></div>",
            unsafe_allow_html=True,
        )
        card3.markdown(
            f"<div class='metric-card'><div class='metric-card-title'>Sin stock</div><div class='metric-card-value'>{critical_stock}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.write("### Lista de productos")
        st.dataframe(inventory_data, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(inventario)

elif menu == "Consulta AI":
    render_section_header("Consulta de inventario con IA", "Responde preguntas sobre stock, productos y estado general del almacén.")
    with st.container():
        left, right = st.columns([2, 1])
        with left:
            pregunta = st.text_area("Describe tu consulta:", height=170)
            if st.button("Enviar consulta"):
                if pregunta.strip():
                    resultado = api_post("/inventory/query", {"question": pregunta})
                    if "error" in resultado:
                        st.error(f"Consulta bloqueada por seguridad: {resultado['error']}")
                    st.session_state.last_response = resultado
                else:
                    st.warning("Escribe tu pregunta antes de enviar.")

        with right:
            st.markdown("<div class='metric-card'><div class='metric-card-title'>Consejo rápido</div><div class='metric-card-value' style='font-size:1rem;'>Pregunta al agente por niveles de stock, fechas de reposición o problemas críticos.</div></div>", unsafe_allow_html=True)
    if st.session_state.last_response:
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.subheader("Respuesta del agente")
        st.json(st.session_state.last_response)
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
                st.json(resultado)
            else:
                st.error(resultado)
        else:
            st.warning("Completa el SKU o nombre del producto.")

elif menu == "Órdenes":
    render_section_header("Gestión de órdenes", "Crea solicitudes y administra el flujo de aprobación desde un solo panel.")
    with st.expander("Crear nueva orden", expanded=True):
        st.markdown("Completa los datos de la orden y presiona crear para enviar la solicitud y notificar al cliente.")
        cliente_email = st.text_input("Email del cliente")
        cliente_nombre = st.text_input("Nombre del cliente")
        items_text = st.text_area(
            "Items JSON",
            value=json.dumps(
                [
                    {"sku": "SKU-ARR-001", "nombre": "Arroz", "cantidad_orden": 10, "precio": 2500.0},
                    {"sku": "SKU-PAN-001", "nombre": "Pan", "cantidad_orden": 5, "precio": 3500.0},
                ],
                indent=2,
                ensure_ascii=False,
            ),
            height=190,
        )
        total = st.number_input("Total de la orden", min_value=0.0, value=0.0)
        if st.button("Crear orden"):
            try:
                items = json.loads(items_text)
                payload = {
                    "items": items,
                    "total": float(total),
                    "cliente_email": cliente_email,
                    "cliente_nombre": cliente_nombre,
                }
                resultado = api_post("/orders", payload)
                if resultado.get("success"):
                    st.success("Orden creada correctamente.")
                st.json(resultado)
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
    pending = api_get("/orders/pending")
    if pending.get("success"):
        st.write(f"Órdenes pendientes: {pending.get('count')}")
        for orden in pending.get("pending_orders", []):
            with st.expander(f"{orden.get('orden_id')} - {orden.get('cliente_nombre')}"):
                st.markdown("<div class='box-card'>", unsafe_allow_html=True)
                st.write("**Detalles de la orden**")
                st.json(orden)
                st.markdown("</div>", unsafe_allow_html=True)
                token = orden.get("token")
                col1, col2 = st.columns(2)
                if col1.button(f"Aprobar", key=f"aprobar-{token}"):
                    resultado = api_post(f"/orders/{token}/approve", {})
                    st.json(resultado)
                if col2.button(f"Rechazar", key=f"rechazar-{token}"):
                    razon = st.text_input("Razón de rechazo", key=f"razon-{token}")
                    if razon.strip():
                        resultado = api_post(f"/orders/{token}/reject", {"razon": razon})
                        st.json(resultado)
    else:
        st.error(pending)

elif menu == "Alertas":
    render_section_header("Alertas de stock crítico", "Visualiza los productos que requieren atención inmediata.")
    criticos = api_get("/alerts/critical-stock")
    if criticos.get("success"):
        st.markdown(
            f"<div class='metric-card'><div class='metric-card-title'>Productos críticos</div><div class='metric-card-value'>{criticos.get('count')}</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='box-card'>", unsafe_allow_html=True)
        st.dataframe(criticos.get("critical_products", []), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(criticos)

elif menu == "Email":
    render_section_header("Prueba de envío de correo", "Verifica la configuración de correos con un envío de prueba rápido.")
    with st.form("test_email_form"):
        col1, col2 = st.columns(2)
        with col1:
            dest = st.text_input("Correo destino", placeholder="tu-email@ejemplo.com")
        with col2:
            nombre = st.text_input("Nombre", placeholder="Tu nombre")
        enviar = st.form_submit_button("Enviar correo de prueba")
    if enviar:
        if dest.strip() and nombre.strip():
            res = api_post("/test-email", {"destinatario": dest, "nombre": nombre})
            if res.get("success"):
                st.success("Correo enviado exitosamente")
            else:
                st.error(res.get("error", "Error desconocido"))
                detalle = res.get("email_result", {})
                if detalle:
                    st.code(detalle.get("error", "Sin detalle"))
        else:
            st.warning("Completa ambos campos")
