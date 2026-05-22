"""
Módulo para enviar confirmaciones de aprobación/rechazo de órdenes
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.email_service import servicio_correo
from core.config import ADMIN_EMAIL


def enviar_confirmacion_aprobacion(orden):
    """Envía correo de confirmación de aprobación"""
    
    orden_id = orden['orden_id']
    cantidad = orden['cantidad_total']
    fecha_resolucion = orden.get('fecha_resolucion', datetime.now().isoformat())
    
    cuerpo = f"""
<html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #404040; background-color: #fafafa; margin: 0; padding: 20px;">
        <div style="max-width: 650px; margin: 0 auto; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            
            <div style="background-color: #27ae60; padding: 25px; border-radius: 6px 6px 0 0;">
                <h1 style="margin: 0; font-size: 22px; color: white; font-weight: 600;">Orden Aprobada</h1>
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #ecf0f1;">Sistema de Gestion Unimarc</p>
            </div>
            
            <div style="padding: 30px;">
                <p style="margin: 0 0 20px 0; font-size: 14px; color: #404040;">Hola Proveedor,</p>
                
                <p style="margin: 0 0 25px 0; font-size: 14px; color: #555;">
                    Tu orden de reposicion ha sido <strong>APROBADA</strong> por el administrador.
                </p>
                
                <div style="background-color: #f0fdf4; padding: 20px; border-radius: 4px; margin-bottom: 25px; border-left: 3px solid #27ae60;">
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #166534; text-transform: uppercase;">Numero de Orden</p>
                    <p style="margin: 0 0 15px 0; font-size: 16px; color: #27ae60; font-weight: 600;">{orden_id}</p>
                    
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #166534; text-transform: uppercase;">Cantidad Aprobada</p>
                    <p style="margin: 0 0 15px 0; font-size: 16px; color: #27ae60; font-weight: 600;">{cantidad} unidades</p>
                    
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #166534; text-transform: uppercase;">Fecha de Aprobacion</p>
                    <p style="margin: 0; font-size: 14px; color: #27ae60;">{fecha_resolucion}</p>
                </div>
                
                <p style="margin: 0 0 25px 0; font-size: 14px; color: #555;">
                    Por favor, procede con el envio de la mercaderia conforme a los terminos pactados.
                </p>
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
        asunto=f"Confirmacion: Orden #{orden_id} Aprobada",
        cuerpo_html=cuerpo
    )
    
    return resultado


def enviar_confirmacion_rechazo(orden, razon=""):
    """Envía correo de confirmación de rechazo"""
    
    orden_id = orden['orden_id']
    cantidad = orden['cantidad_total']
    fecha_resolucion = orden.get('fecha_resolucion', datetime.now().isoformat())
    
    razon_texto = f"<p style=\"margin: 0; font-size: 13px; color: #555;\"><strong>Razon:</strong> {razon}</p>" if razon else ""
    
    cuerpo = f"""
<html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #404040; background-color: #fafafa; margin: 0; padding: 20px;">
        <div style="max-width: 650px; margin: 0 auto; background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            
            <div style="background-color: #e74c3c; padding: 25px; border-radius: 6px 6px 0 0;">
                <h1 style="margin: 0; font-size: 22px; color: white; font-weight: 600;">Orden Rechazada</h1>
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #ecf0f1;">Sistema de Gestion Unimarc</p>
            </div>
            
            <div style="padding: 30px;">
                <p style="margin: 0 0 20px 0; font-size: 14px; color: #404040;">Hola Proveedor,</p>
                
                <p style="margin: 0 0 25px 0; font-size: 14px; color: #555;">
                    Tu orden de reposicion ha sido <strong>RECHAZADA</strong> por el administrador.
                </p>
                
                <div style="background-color: #fef2f2; padding: 20px; border-radius: 4px; margin-bottom: 25px; border-left: 3px solid #e74c3c;">
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #991b1b; text-transform: uppercase;">Numero de Orden</p>
                    <p style="margin: 0 0 15px 0; font-size: 16px; color: #e74c3c; font-weight: 600;">{orden_id}</p>
                    
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #991b1b; text-transform: uppercase;">Cantidad Solicitada</p>
                    <p style="margin: 0 0 15px 0; font-size: 16px; color: #e74c3c; font-weight: 600;">{cantidad} unidades</p>
                    
                    <p style="margin: 0 0 10px 0; font-size: 12px; color: #991b1b; text-transform: uppercase;">Fecha de Rechazo</p>
                    <p style="margin: 0 0 15px 0; font-size: 14px; color: #e74c3c;">{fecha_resolucion}</p>
                    
                    {razon_texto}
                </div>
                
                <p style="margin: 0 0 25px 0; font-size: 14px; color: #555;">
                    Por favor, contacta al administrador para obtener mas informacion o revisar los terminos de la orden.
                </p>
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
        asunto=f"Confirmacion: Orden #{orden_id} Rechazada",
        cuerpo_html=cuerpo
    )
    
    return resultado
