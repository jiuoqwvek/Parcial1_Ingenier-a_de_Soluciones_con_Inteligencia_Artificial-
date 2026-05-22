"""
Script para enviar alertas de inventario bajo
Notifica al administrador cuando productos están por debajo del mínimo
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.email_service import servicio_correo
from core.config import ADMIN_EMAIL

# Productos con stock crítico
productos_criticos = [
    {
        "sku": "SKU-PAN-001",
        "nombre": "Pan Integral Artesanal",
        "stock": 5,
        "minimo": 50,
        "proveedor": "Panaderia Local"
    },
    {
        "sku": "SKU-LEC-001",
        "nombre": "Lechuga Fresca Hidroponica",
        "stock": 8,
        "minimo": 40,
        "proveedor": "Agricola Sur"
    },
    {
        "sku": "SKU-LAC-003",
        "nombre": "Queso Fresco 500g",
        "stock": 12,
        "minimo": 30,
        "proveedor": "Lacteos Premium"
    },
    {
        "sku": "SKU-FRU-002",
        "nombre": "Manzana Roja Importada",
        "stock": 20,
        "minimo": 60,
        "proveedor": "Frutas Andinas"
    }
]

print("="*70)
print("ENVIANDO ALERTA DE INVENTARIO BAJO")
print("="*70)
print(f"\nDatos de la alerta:")
print(f"  Productos criticos: {len(productos_criticos)}")
print(f"  Destinatario: Administrador\n")

# Construir el correo COMPLETO
cuerpo_alerta = f"""
<html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #404040; background-color: #fafafa; margin: 0; padding: 20px;">
        <div style="max-width: 650px; margin: 0 auto; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            
            <!-- Encabezado alerta -->
            <div style="background-color: #c0392b; padding: 25px; border-radius: 6px 6px 0 0;">
                <h1 style="margin: 0; font-size: 22px; color: white; font-weight: 600;">Alerta de Inventario</h1>
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #fadbd8;">Sistema de Gestion Unimarc</p>
            </div>
            
            <!-- Contenido principal -->
            <div style="padding: 30px;">
                
                <!-- Saludo -->
                <p style="margin: 0 0 20px 0; font-size: 14px; color: #404040; line-height: 1.6;">
                    Hola Administrador,
                </p>
                
                <p style="margin: 0 0 25px 0; font-size: 14px; color: #555; line-height: 1.6;">
                    Se han detectado <strong>{len(productos_criticos)} productos</strong> con stock por debajo del nivel minimo. 
                    Se recomienda gestionar urgentemente estas reposiciones.
                </p>
                
                <!-- Caja de advertencia -->
                <div style="background-color: #fadbd8; padding: 15px; border-radius: 4px; margin-bottom: 25px; border-left: 3px solid #c0392b;">
                    <p style="margin: 0; font-size: 13px; color: #78281f;">
                        <strong>Atencion:</strong> El nivel de stock es critico en algunos productos. 
                        Considera generar ordenes de reposicion lo antes posible.
                    </p>
                </div>
                
                <!-- Tabla de productos criticos -->
                <h3 style="margin: 0 0 15px 0; font-size: 14px; color: #2c3e50; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Productos Criticos</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                    <thead>
                        <tr style="background-color: #ecf0f1; border-bottom: 2px solid #bdc3c7;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">SKU</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Producto</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Stock</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Minimo</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Proveedor</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Agregar todas las filas de productos críticos
for i, prod in enumerate(productos_criticos):
    color_fondo = "#ffffff" if i % 2 == 0 else "#f8f9fa"
    # Calcular diferencia
    diferencia = prod.get('minimo', 0) - prod.get('stock', 0)
    
    cuerpo_alerta += f"""
                        <tr style="background-color: {color_fondo}; border-bottom: 1px solid #ecf0f1;">
                            <td style="padding: 13px 12px; font-size: 13px; color: #34495e; font-weight: 500;">{prod.get('sku', 'N/A')}</td>
                            <td style="padding: 13px 12px; font-size: 13px; color: #555;">{prod.get('nombre', 'N/A')}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #e74c3c; font-weight: 600;">{prod.get('stock', 0)}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #34495e;">{prod.get('minimo', 0)}</td>
                            <td style="padding: 13px 12px; font-size: 13px; color: #555;">{prod.get('proveedor', 'N/A')}</td>
                        </tr>
"""

cuerpo_alerta += """
                    </tbody>
                </table>
                
                <!-- Acciones recomendadas -->
                <div style="background-color: #fef9e7; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 3px solid #f39c12;">
                    <h4 style="margin: 0 0 10px 0; font-size: 13px; color: #7d6608; font-weight: 600;">Acciones Recomendadas:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #7d6608; font-size: 13px; line-height: 1.6;">
                        <li>Generar ordenes de compra urgentes para estos productos</li>
                        <li>Contactar a los proveedores para disponibilidad inmediata</li>
                        <li>Considerar ofertas o ajustes de precios mientras se repone</li>
                        <li>Revisar historico de ventas para ajustar niveles minimos</li>
                    </ul>
                </div>
                
                <!-- Nota final -->
                <p style="margin: 0; font-size: 12px; color: #7f8c8d; line-height: 1.5;">
                    Esta alerta fue generada automaticamente por el sistema de gestion inteligente de Unimarc. 
                    Puedes generar una orden de reposicion directamente desde el sistema.
                </p>
            </div>
            
            <!-- Pie de pagina -->
            <div style="background-color: #f8f9fa; padding: 20px; border-top: 1px solid #ecf0f1; border-radius: 0 0 6px 6px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #95a5a6;">
                    Sistema de Gestion Inteligente Unimarc<br>
                    Generado el 22 de Mayo de 2026
                </p>
            </div>
        </div>
    </body>
</html>
"""

# ENVIAR UN SOLO CORREO CON TODO JUNTO
print("Enviando alerta al administrador...")
resultado = servicio_correo._enviar_correo(
    destinatario=ADMIN_EMAIL,
    asunto=f"ALERTA: {len(productos_criticos)} productos con stock critico",
    cuerpo_html=cuerpo_alerta
)

print("\n" + "="*70)
if resultado['exito']:
    print("[OK] Alerta de inventario enviada exitosamente!")
    print(f"  Asunto: {resultado['asunto']}")
    print(f"  Timestamp: {resultado['timestamp']}")
else:
    print("[ERROR] No se pudo enviar la alerta")
    print(f"  Error: {resultado.get('error', 'Error desconocido')}")
print("="*70)
