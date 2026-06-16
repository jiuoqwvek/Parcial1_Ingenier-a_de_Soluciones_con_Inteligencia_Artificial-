import json
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Agente Unificado AI", layout="wide")
st.title("Agente Unificado: Inventario + Correos")

if "last_response" not in st.session_state:
    st.session_state.last_response = None

menu = st.sidebar.selectbox(
    "Navegación",
    ["Estado", "Inventario", "Consulta AI", "Stock", "Órdenes", "Alertas", "Email"],
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Backend**: `{BACKEND_URL}`")


def api_get(path):
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=15)
        if response.status_code >= 400:
            return {"error": response.json().get("detail", f"HTTP {response.status_code}")}
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


def api_post(path, payload):
    try:
        response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=20)
        if response.status_code >= 400:
            return {"error": response.json().get("detail", f"HTTP {response.status_code}")}
        return response.json()
    except Exception as exc:
        return {"error": str(exc)}


if menu == "Estado":
    st.header("Estado del ecosistema")
    health = api_get("/health")
    st.json(health)

elif menu == "Inventario":
    st.header("Inventario actual")
    inventario = api_get("/inventory")
    if inventario.get("success"):
        st.write(f"Productos: {inventario.get('count')}")
        st.table(inventario.get("inventory", []))
    else:
        st.error(inventario)

elif menu == "Consulta AI":
    st.header("Consulta de inventario con IA")
    pregunta = st.text_area("Describe tu consulta:", height=120)
    if st.button("Enviar consulta"):
        if pregunta.strip():
            resultado = api_post("/inventory/query", {"question": pregunta})
            if "error" in resultado:
                st.error(f"Consulta bloqueada por seguridad: {resultado['error']}")
            st.session_state.last_response = resultado
    if st.session_state.last_response:
        st.subheader("Respuesta")
        st.json(st.session_state.last_response)

elif menu == "Stock":
    st.header("Actualizar stock")
    with st.form(key="stock_form"):
        sku = st.text_input("SKU o nombre del producto")
        nuevo_stock = st.number_input("Nuevo stock", min_value=0, value=0)
        enviar = st.form_submit_button("Actualizar")
    if enviar:
        if sku.strip():
            resultado = api_post("/inventory/stock", {"sku_or_name": sku, "new_stock": int(nuevo_stock)})
            if resultado.get("success"):
                st.success("Stock actualizado")
                st.json(resultado)
            else:
                st.error(resultado)

elif menu == "Órdenes":
    st.header("Gestión de órdenes")
    with st.expander("Crear nueva orden"):
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
            height=200,
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
                st.json(resultado)
                email_info = resultado.get("email")
                if email_info:
                    if email_info.get("exito"):
                        st.success(f"Correo enviado a {email_info.get('destinatario')}")
                    elif email_info.get("razon"):
                        st.warning(f"Correo no enviado: {email_info['razon']}")
                    else:
                        st.error(f"Error al enviar correo: {email_info.get('error', 'desconocido')}")
            except Exception as exc:
                st.error(f"Error al procesar orden: {exc}")

    st.markdown("---")
    st.subheader("Órdenes pendientes")
    pending = api_get("/orders/pending")
    if pending.get("success"):
        st.write(f"Pendientes: {pending.get('count')}")
        for orden in pending.get("pending_orders", []):
            with st.expander(f"{orden.get('orden_id')} - {orden.get('cliente_nombre')}"):
                st.json(orden)
                token = orden.get("token")
                col1, col2 = st.columns(2)
                if col1.button(f"Aprobar {orden.get('orden_id')}", key=f"aprobar-{token}"):
                    resultado = api_post(f"/orders/{token}/approve", {})
                    st.json(resultado)
                if col2.button(f"Rechazar {orden.get('orden_id')}", key=f"rechazar-{token}"):
                    razon = st.text_input("Razón de rechazo", key=f"razon-{token}")
                    if razon.strip():
                        resultado = api_post(f"/orders/{token}/reject", {"razon": razon})
                        st.json(resultado)
    else:
        st.error(pending)

elif menu == "Alertas":
    st.header("Alertas de stock crítico")
    criticos = api_get("/alerts/critical-stock")
    if criticos.get("success"):
        st.write(f"Productos críticos: {criticos.get('count')}")
        st.table(criticos.get("critical_products", []))
    else:
        st.error(criticos)

elif menu == "Email":
    st.header("Prueba de envío de correo")
    with st.form("test_email_form"):
        dest = st.text_input("Correo destino", placeholder="tu-email@ejemplo.com")
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
