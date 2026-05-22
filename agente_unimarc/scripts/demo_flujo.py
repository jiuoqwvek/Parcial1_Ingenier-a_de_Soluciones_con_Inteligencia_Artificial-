"""
Script de demostración del sistema completo
Muestra cómo funciona:
1. Enviar orden de reposición
2. Admin aprueba/rechaza usando gestor_ordenes.py
3. Envía confirmación automática
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.email_service import servicio_correo
from core.orden_manager import gestor_ordenes
from core.config import ADMIN_EMAIL

def demo_flujo_completo():
    """Demostración del flujo completo"""
    
    print("\n" + "="*70)
    print("DEMO: SISTEMA DE GESTION DE ORDENES UNIMARC")
    print("="*70)
    
    # Datos de ejemplo
    productos = [
        {
            "sku": "SKU-ARR-001",
            "nombre": "Arroz Integral Premium 5kg",
            "cantidad_orden": 150
        },
        {
            "sku": "SKU-LEC-001",
            "nombre": "Lechuga Fresca Hidroponica",
            "cantidad_orden": 200
        },
        {
            "sku": "SKU-PAN-001",
            "nombre": "Pan Integral Artesanal",
            "cantidad_orden": 300
        }
    ]
    
    cantidad_total = sum(p["cantidad_orden"] for p in productos)
    
    print("\n[PASO 1] Creando orden de reposicion...")
    
    # Crear la orden en la base de datos
    orden = gestor_ordenes.crear_orden(productos, cantidad_total)
    orden_id = orden["orden_id"]
    
    print(f"  ID Orden: {orden_id}")
    print(f"  Cantidad Total: {cantidad_total} unidades")
    print(f"  Estado: PENDIENTE")
    
    print("\n[PASO 2] Enviando notificacion por correo...")
    
    # Construir cuerpo del correo
    cuerpo_correo = f"""
<html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #404040; background-color: #fafafa; margin: 0; padding: 20px;">
        <div style="max-width: 650px; margin: 0 auto; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            
            <div style="background-color: #2c3e50; padding: 25px; border-radius: 6px 6px 0 0;">
                <h1 style="margin: 0; font-size: 22px; color: white; font-weight: 600;">Orden de Reposicion Pendiente</h1>
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #ecf0f1;">Sistema de Gestion Unimarc</p>
            </div>
            
            <div style="padding: 30px;">
                <p style="margin: 0 0 20px 0; font-size: 14px; color: #404040;">Hola Administrador,</p>
                
                <p style="margin: 0 0 25px 0; font-size: 14px; color: #555;">
                    El sistema ha generado una nueva orden de reposicion que requiere tu aprobacion.
                </p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 4px; margin-bottom: 25px; border-left: 3px solid #34495e;">
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase;">Numero de Orden</p>
                    <p style="margin: 0 0 15px 0; font-size: 16px; color: #2c3e50; font-weight: 600;">{orden_id}</p>
                    
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase;">Cantidad Total</p>
                    <p style="margin: 0; font-size: 16px; color: #27ae60; font-weight: 600;">{cantidad_total} unidades</p>
                </div>
                
                <h3 style="margin: 0 0 15px 0; font-size: 14px; color: #2c3e50; font-weight: 600;">Productos a Reabastecer</h3>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
                    <thead>
                        <tr style="background-color: #ecf0f1; border-bottom: 2px solid #bdc3c7;">
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600;">SKU</th>
                            <th style="padding: 12px; text-align: left; font-size: 12px; color: #34495e; font-weight: 600;">Producto</th>
                            <th style="padding: 12px; text-align: center; font-size: 12px; color: #34495e; font-weight: 600;">Cantidad</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for i, prod in enumerate(productos):
        color_fondo = "#ffffff" if i % 2 == 0 else "#f8f9fa"
        cuerpo_correo += f"""
                        <tr style="background-color: {color_fondo}; border-bottom: 1px solid #ecf0f1;">
                            <td style="padding: 13px 12px; font-size: 13px; color: #34495e; font-weight: 500;">{prod.get('sku')}</td>
                            <td style="padding: 13px 12px; font-size: 13px; color: #555;">{prod.get('nombre')}</td>
                            <td style="padding: 13px 12px; text-align: center; font-size: 13px; color: #27ae60; font-weight: 600;">{prod.get('cantidad_orden')}</td>
                        </tr>
"""
    
    cuerpo_correo += f"""
                    </tbody>
                </table>
                
                <p style="margin: 0 0 25px 0; font-size: 13px; color: #555;">
                    Haz click en uno de los botones para aprobar o rechazar la orden:
                </p>
                
                <table style="width: 100%; margin-bottom: 25px;">
                    <tr>
                        <td style="padding: 0 10px 0 0; width: 50%;">
                            <div style="display: block; background-color: #27ae60; color: white; text-align: center; padding: 12px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 14px;">
                                APROBAR ORDEN
                            </div>
                        </td>
                        <td style="padding: 0 0 0 10px; width: 50%;">
                            <div style="display: block; background-color: #e74c3c; color: white; text-align: center; padding: 12px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 14px;">
                                RECHAZAR ORDEN
                            </div>
                        </td>
                    </tr>
                </table>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px; border-left: 3px solid #34495e; text-align: center;">
                    <p style="margin: 0; font-size: 12px; color: #7f8c8d;">
                        Una vez realizada tu eleccion, podras gestionarla en el sistema mediante terminal.
                    </p>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-top: 1px solid #ecf0f1; border-radius: 0 0 6px 6px; text-align: center;">
                <p style="margin: 0; font-size: 11px; color: #95a5a6;">
                    Sistema de Gestion Inteligente Unimarc
                </p>
            </div>
        </div>
    </body>
</html>
"""
    
    resultado = servicio_correo._enviar_correo(
        destinatario=ADMIN_EMAIL,
        asunto=f"Orden de Reposicion #{orden_id} - Requiere Aprobacion",
        cuerpo_html=cuerpo_correo
    )
    
    if resultado['exito']:
        print("  Correo enviado exitosamente!")
    else:
        print(f"  Error al enviar correo: {resultado.get('error')}")
    
    print("\n[PASO 3] Proximos pasos:")
    print("  1. Abre tu correo")
    print("  2. Ejecuta en terminal: python scripts/gestor_ordenes.py")
    print("  3. Selecciona 'Listar ordenes pendientes' para ver esta orden")
    print("  4. Elige APROBAR o RECHAZAR")
    print("\n" + "="*70)


if __name__ == "__main__":
    demo_flujo_completo()
