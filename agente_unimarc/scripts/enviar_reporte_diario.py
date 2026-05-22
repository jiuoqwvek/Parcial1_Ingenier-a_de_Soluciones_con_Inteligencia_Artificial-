"""
Reporte Diario Operativo de Unimarc
Muestra: estado del inventario, entregas recibidas y pedidos realizados
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.email_service import servicio_correo
from core.config import ADMIN_EMAIL

# Datos de inventario actual
inventario_actual = [
    {"sku": "SKU-ARR-001", "nombre": "Arroz", "stock": 450, "minimo": 100, "maximo": 1000},
    {"sku": "SKU-PAN-001", "nombre": "Pan", "stock": 85, "minimo": 50, "maximo": 300},
    {"sku": "SKU-LEC-001", "nombre": "Leche", "stock": 150, "minimo": 75, "maximo": 400},
    {"sku": "SKU-LAC-003", "nombre": "Queso Fresco", "stock": 25, "minimo": 30, "maximo": 100},
    {"sku": "SKU-FRU-002", "nombre": "Manzana Roja", "stock": 55, "minimo": 60, "maximo": 200},
]

# Entregas recibidas hoy
entregas_hoy = [
    {
        "proveedor": "Distribuidor A",
        "fecha_entrega": "2026-05-22 09:30",
        "productos": [
            {"nombre": "Arroz", "cantidad": 150},
            {"nombre": "Leche", "cantidad": 100}
        ],
        "total_unidades": 250
    },
    {
        "proveedor": "Agricola Sur",
        "fecha_entrega": "2026-05-22 14:00",
        "productos": [
            {"nombre": "Manzana Roja", "cantidad": 100}
        ],
        "total_unidades": 100
    }
]

# Pedidos realizados hoy
pedidos_hoy = [
    {
        "orden_id": "ORD-4B6529FB",
        "estado": "aprobada",
        "cantidad_total": 650,
        "fecha": "2026-05-22 08:00"
    },
    {
        "orden_id": "ORD-F69BE411",
        "estado": "pendiente",
        "cantidad_total": 650,
        "fecha": "2026-05-22 11:30"
    }
]

# Calcular estadísticas
total_stock = sum(p["stock"] for p in inventario_actual)
productos_bajo_minimo = [p for p in inventario_actual if p["stock"] < p["minimo"]]
total_entregas = sum(e["total_unidades"] for e in entregas_hoy)
total_pedidos_realizados = sum(p["cantidad_total"] for p in pedidos_hoy)
pedidos_aprobados = sum(1 for p in pedidos_hoy if p["estado"] == "aprobada")
pedidos_pendientes = sum(1 for p in pedidos_hoy if p["estado"] == "pendiente")

print("="*70)
print("GENERANDO REPORTE OPERATIVO UNIMARC")
print("="*70)
print(f"\nFecha: {datetime.now().strftime('%d de %B de %Y')}")
print(f"Stock total en bodega: {total_stock} unidades")
print(f"Productos bajo minimo: {len(productos_bajo_minimo)}")
print(f"Mercaderia recibida: {total_entregas} unidades")
print(f"Pedidos realizados: {len(pedidos_hoy)} ({pedidos_aprobados} aprobados, {pedidos_pendientes} pendientes)\n")

fecha_hoy = datetime.now().strftime("%d de %B de %Y")

cuerpo_reporte = f"""
<html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #404040; background-color: #fafafa; margin: 0; padding: 20px;">
        <div style="max-width: 850px; margin: 0 auto; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            
            <!-- Encabezado -->
            <div style="background-color: #2c3e50; padding: 30px; border-radius: 6px 6px 0 0;">
                <h1 style="margin: 0; font-size: 24px; color: white; font-weight: 600;">Reporte Operativo Diario - Unimarc</h1>
                <p style="margin: 8px 0 0 0; font-size: 14px; color: #ecf0f1;">{fecha_hoy}</p>
            </div>
            
            <!-- Contenido principal -->
            <div style="padding: 30px;">
                
                <!-- Estadisticas principales -->
                <h2 style="margin: 0 0 20px 0; font-size: 18px; color: #2c3e50; font-weight: 600;">Resumen Operativo</h2>
                
                <table style="width: 100%; margin-bottom: 30px;">
                    <tr>
                        <td style="width: 25%; padding: 15px; background-color: #ebf5fb; border-radius: 4px; text-align: center; margin-right: 10px;">
                            <p style="margin: 0 0 8px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">Stock Total</p>
                            <p style="margin: 0; font-size: 28px; color: #2980b9; font-weight: 600;">{total_stock}</p>
                        </td>
                        <td style="width: 25%; padding: 15px; background-color: #d5f4e6; border-radius: 4px; text-align: center; margin-right: 10px;">
                            <p style="margin: 0 0 8px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">Recibido Hoy</p>
                            <p style="margin: 0; font-size: 28px; color: #27ae60; font-weight: 600;">{total_entregas}</p>
                        </td>
                        <td style="width: 25%; padding: 15px; background-color: #fef5e7; border-radius: 4px; text-align: center; margin-right: 10px;">
                            <p style="margin: 0 0 8px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">Pedidos Hoy</p>
                            <p style="margin: 0; font-size: 28px; color: #f39c12; font-weight: 600;">{len(pedidos_hoy)}</p>
                        </td>
                        <td style="width: 25%; padding: 15px; background-color: #fadbd8; border-radius: 4px; text-align: center;">
                            <p style="margin: 0 0 8px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px;">Bajo Minimo</p>
                            <p style="margin: 0; font-size: 28px; color: #e74c3c; font-weight: 600;">{len(productos_bajo_minimo)}</p>
                        </td>
                    </tr>
                </table>
                
                <!-- Estado del inventario -->
                <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #2c3e50; font-weight: 600;">Estado del Inventario</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                    <thead>
                        <tr style="background-color: #ecf0f1; border-bottom: 2px solid #bdc3c7;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Producto</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Stock Actual</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Minimo</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Maximo</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Estado</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for i, prod in enumerate(inventario_actual):
    color_fondo = "#ffffff" if i % 2 == 0 else "#f8f9fa"
    
    # Determinar estado
    if prod["stock"] < prod["minimo"]:
        estado = "CRITICO"
        color_estado = "#e74c3c"
    elif prod["stock"] > prod["maximo"]:
        estado = "EXCESO"
        color_estado = "#f39c12"
    else:
        estado = "NORMAL"
        color_estado = "#27ae60"
    
    cuerpo_reporte += f"""
                        <tr style="background-color: {color_fondo}; border-bottom: 1px solid #ecf0f1;">
                            <td style="padding: 13px 12px; font-size: 13px; color: #34495e; font-weight: 500;">{prod['nombre']}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #34495e; font-weight: 600;">{prod['stock']}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #34495e;">{prod['minimo']}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #34495e;">{prod['maximo']}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 12px; color: white; background-color: {color_estado}; border-radius: 3px; font-weight: 600;">{estado}</td>
                        </tr>
"""

cuerpo_reporte += """
                    </tbody>
                </table>
                
                <!-- Entregas recibidas -->
                <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #2c3e50; font-weight: 600;">Mercaderia Recibida Hoy</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                    <thead>
                        <tr style="background-color: #ecf0f1; border-bottom: 2px solid #bdc3c7;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Proveedor</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Productos</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Total Unidades</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Hora Entrega</th>
                        </tr>
                    </thead>
                    <tbody>
"""

if entregas_hoy:
    for i, entrega in enumerate(entregas_hoy):
        color_fondo = "#ffffff" if i % 2 == 0 else "#f8f9fa"
        productos_texto = ", ".join([f"{p['nombre']} (x{p['cantidad']})" for p in entrega["productos"]])
        hora = entrega["fecha_entrega"].split(" ")[1]
        
        cuerpo_reporte += f"""
                        <tr style="background-color: {color_fondo}; border-bottom: 1px solid #ecf0f1;">
                            <td style="padding: 13px 12px; font-size: 13px; color: #34495e; font-weight: 500;">{entrega['proveedor']}</td>
                            <td style="padding: 13px 12px; font-size: 13px; color: #555;">{productos_texto}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #27ae60; font-weight: 600;">{entrega['total_unidades']}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #34495e;">{hora}</td>
                        </tr>
"""
else:
    cuerpo_reporte += """
                        <tr style="background-color: #ffffff; border-bottom: 1px solid #ecf0f1;">
                            <td colspan="4" style="padding: 20px; text-align: center; font-size: 13px; color: #7f8c8d;">No se recibieron entregas hoy</td>
                        </tr>
"""

cuerpo_reporte += f"""
                    </tbody>
                </table>
                
                <!-- Pedidos realizados -->
                <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #2c3e50; font-weight: 600;">Pedidos de Reposicion Realizados</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                    <thead>
                        <tr style="background-color: #ecf0f1; border-bottom: 2px solid #bdc3c7;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Orden</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Cantidad</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Estado</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Hora Pedido</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for i, pedido in enumerate(pedidos_hoy):
    color_fondo = "#ffffff" if i % 2 == 0 else "#f8f9fa"
    
    # Color según estado
    if pedido["estado"] == "aprobada":
        color_estado = "#27ae60"
        color_fondo_estado = "#d5f4e6"
    else:
        color_estado = "#f39c12"
        color_fondo_estado = "#fef5e7"
    
    hora = pedido["fecha"].split(" ")[1]
    
    cuerpo_reporte += f"""
                        <tr style="background-color: {color_fondo}; border-bottom: 1px solid #ecf0f1;">
                            <td style="padding: 13px 12px; font-size: 13px; color: #34495e; font-weight: 600;">{pedido['orden_id']}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #27ae60; font-weight: 600;">{pedido['cantidad_total']} unidades</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 12px; color: white; background-color: {color_estado}; border-radius: 3px; font-weight: 600;">{pedido['estado'].upper()}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #34495e;">{hora}</td>
                        </tr>
"""

cuerpo_reporte += f"""
                    </tbody>
                </table>
                
                <!-- Alertas y observaciones -->
"""

if productos_bajo_minimo:
    cuerpo_reporte += """
                <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #2c3e50; font-weight: 600;">Alertas de Inventario</h3>
                
                <div style="background-color: #fadbd8; padding: 20px; border-radius: 4px; border-left: 3px solid #e74c3c; margin-bottom: 20px;">
                    <p style="margin: 0 0 10px 0; font-size: 13px; color: #c0392b; font-weight: 600;">Productos bajo nivel minimo:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #c0392b; font-size: 13px;">
"""
    
    for prod in productos_bajo_minimo:
        diferencia = prod["minimo"] - prod["stock"]
        cuerpo_reporte += f"<li>{prod['nombre']}: {prod['stock']} unidades (falta {diferencia} para minimo)</li>"
    
    cuerpo_reporte += """
                    </ul>
                </div>
"""

cuerpo_reporte += f"""
                <!-- Resumen final -->
                <div style="background-color: #d5f4e6; padding: 20px; border-radius: 4px; border-left: 3px solid #27ae60;">
                    <p style="margin: 0; font-size: 13px; color: #27ae60;">
                        <strong>Resumen del dia:</strong> Se cuenta con {total_stock} unidades en bodega. 
                        Se recibieron {total_entregas} unidades de {len(entregas_hoy)} proveedores. 
                        Se realizaron {len(pedidos_hoy)} pedidos de reposicion 
                        ({pedidos_aprobados} aprobados, {pedidos_pendientes} pendientes).
                    </p>
                </div>
            </div>
            
            <!-- Pie de pagina -->
            <div style="background-color: #f8f9fa; padding: 20px; border-top: 1px solid #ecf0f1; border-radius: 0 0 6px 6px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #95a5a6;">
                    Sistema de Gestion Inteligente Unimarc<br>
                    Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}
                </p>
            </div>
        </div>
    </body>
</html>
"""

# Enviar correo
print("Enviando reporte operativo al administrador...\n")

resultado = servicio_correo._enviar_correo(
    destinatario=ADMIN_EMAIL,
    asunto=f"Reporte Operativo Diario Unimarc - {fecha_hoy}",
    cuerpo_html=cuerpo_reporte
)

print("="*70)
if resultado['exito']:
    print("[OK] Reporte operativo enviado exitosamente!")
    print(f"\nDatos del reporte:")
    print(f"  Stock total en bodega: {total_stock} unidades")
    print(f"  Productos bajo minimo: {len(productos_bajo_minimo)}")
    print(f"  Mercaderia recibida hoy: {total_entregas} unidades ({len(entregas_hoy)} entregas)")
    print(f"  Pedidos realizados: {len(pedidos_hoy)} ({pedidos_aprobados} aprobados, {pedidos_pendientes} pendientes)")
else:
    print("[ERROR] No se pudo enviar el reporte")
    print(f"  Error: {resultado.get('error', 'Error desconocido')}")
print("="*70)
