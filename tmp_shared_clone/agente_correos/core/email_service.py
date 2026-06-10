"""
Servicio de correos SMTP para el agente de supermercado
Envía notificaciones de pedidos, alertas de inventario, etc.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any
from datetime import datetime
import os

from core.config import FROM_EMAIL, SMTP_PASSWORD, ADMIN_EMAIL

logger = logging.getLogger(__name__)


class ServicioCorreo:
    """Servicio centralizado para envío de correos SMTP"""
    
    def __init__(self):
        """Inicializa la configuración SMTP desde variables de entorno"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.from_email = FROM_EMAIL
        self.password = SMTP_PASSWORD
        self.use_tls = True
        self.admin_email = ADMIN_EMAIL
        
        self._validar_config()
    
    def _validar_config(self) -> None:
        """Valida que las credenciales SMTP estén configuradas"""
        if not self.from_email or not self.password:
            logger.warning("⚠️ SMTP no configurado. Verifica .env con SMTP_FROM_EMAIL y SMTP_PASSWORD")
    
    def enviar_confirmacion_pedido(self, 
                                   correo_cliente: str,
                                   nombre_cliente: str,
                                   pedido_id: str,
                                   items: List[Dict],
                                   total: float) -> Dict[str, Any]:
        """
        Envía confirmación de pedido al cliente
        
        Args:
            correo_cliente: Email del cliente
            nombre_cliente: Nombre del cliente
            pedido_id: ID del pedido
            items: Lista de items del pedido
            total: Total del pedido
        """
        asunto = f"Confirmación de Pedido #{pedido_id} - Supermercado"
        
        # Construir tabla HTML de items
        filas_items = ""
        for item in items:
            filas_items += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item.get('nombre', 'Producto')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{item.get('cantidad', 0)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">${item.get('precio', 0):.2f}</td>
            </tr>
            """
        
        cuerpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px;">
                        ✓ Pedido Confirmado
                    </h2>
                    
                    <p>Hola <strong>{nombre_cliente}</strong>,</p>
                    
                    <p>Gracias por tu compra en nuestro supermercado. Tu pedido ha sido procesado exitosamente.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>ID del Pedido:</strong> {pedido_id}</p>
                        <p><strong>Fecha:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">Detalle de Compra</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #27ae60; color: white;">
                                <th style="padding: 10px; text-align: left;">Producto</th>
                                <th style="padding: 10px; text-align: center;">Cantidad</th>
                                <th style="padding: 10px; text-align: right;">Precio</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_items}
                        </tbody>
                        <tfoot>
                            <tr style="background-color: #ecf0f1; font-weight: bold;">
                                <td colspan="2" style="padding: 10px; text-align: right;">Total:</td>
                                <td style="padding: 10px; text-align: right; color: #27ae60; font-size: 18px;">${total:.2f}</td>
                            </tr>
                        </tfoot>
                    </table>
                    
                    <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px;">
                        Este es un correo automático del sistema de gestión de supermercado. 
                        No responda a este correo.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self._enviar_correo(correo_cliente, asunto, cuerpo_html)
    
    def enviar_alerta_inventario(self,
                                  productos_criticos: List[Dict]) -> Dict[str, Any]:
        """
        Envía alerta de productos con stock crítico al administrador
        
        Args:
            productos_criticos: Lista de productos bajo stock mínimo
        """
        asunto = f"⚠️ ALERTA: {len(productos_criticos)} productos con stock crítico"
        
        filas_productos = ""
        for prod in productos_criticos:
            filas_productos += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{prod.get('nombre', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">
                    <span style="color: red; font-weight: bold;">{prod.get('stock', 0)}</span>
                </td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{prod.get('minimo', 0)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{prod.get('proveedor', 'N/A')}</td>
            </tr>
            """
        
        cuerpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #c0392b; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
                        ⚠️ ALERTA DE INVENTARIO
                    </h2>
                    
                    <p>Se han detectado <strong>{len(productos_criticos)} productos</strong> con stock por debajo del mínimo.</p>
                    
                    <h3 style="color: #c0392b;">Productos Críticos</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #e74c3c; color: white;">
                                <th style="padding: 10px; text-align: left;">Producto</th>
                                <th style="padding: 10px; text-align: center;">Stock Actual</th>
                                <th style="padding: 10px; text-align: center;">Mínimo</th>
                                <th style="padding: 10px; text-align: left;">Proveedor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_productos}
                        </tbody>
                    </table>
                    
                    <p style="margin-top: 20px; padding: 10px; background-color: #fdeaea; border-left: 4px solid #e74c3c;">
                        <strong>Acción recomendada:</strong> Revisa el sistema de gestión de inventario 
                        y considera generar órdenes de compra urgentes.
                    </p>
                    
                    <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px;">
                        Generado automáticamente el {datetime.now().strftime("%d/%m/%Y %H:%M")}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self._enviar_correo(self.admin_email, asunto, cuerpo_html)
    
    def enviar_notificacion_reposicion(self,
                                       orden_id: str,
                                       productos: List[Dict],
                                       cantidad_total: int) -> Dict[str, Any]:
        """
        Envía notificación de orden de reposición al administrador
        
        Args:
            orden_id: ID de la orden de reposición
            productos: Lista de productos reordenados
            cantidad_total: Cantidad total de items
        """
        asunto = f"Orden de Reposición Generada #{orden_id}"
        
        filas_productos = ""
        for prod in productos:
            filas_productos += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{prod.get('sku', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{prod.get('nombre', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: center;">{prod.get('cantidad_orden', 0)}</td>
            </tr>
            """
        
        cuerpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #2980b9; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
                        📦 Orden de Reposición Generada
                    </h2>
                    
                    <div style="background-color: #ebf5fb; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>ID de Orden:</strong> {orden_id}</p>
                        <p><strong>Total de Items:</strong> {cantidad_total}</p>
                        <p><strong>Fecha:</strong> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
                    </div>
                    
                    <h3 style="color: #2980b9;">Productos a Reabastecer</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background-color: #3498db; color: white;">
                                <th style="padding: 10px; text-align: left;">SKU</th>
                                <th style="padding: 10px; text-align: left;">Nombre Producto</th>
                                <th style="padding: 10px; text-align: center;">Cantidad</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_productos}
                        </tbody>
                    </table>
                    
                    <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px;">
                        Esta orden fue generada automáticamente por el sistema de gestión inteligente.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self._enviar_correo(self.admin_email, asunto, cuerpo_html)
    
    def enviar_rechazo_pedido(self,
                              correo_cliente: str,
                              nombre_cliente: str,
                              pedido_id: str,
                              razon: str) -> Dict[str, Any]:
        """
        Envía notificación de rechazo de pedido al cliente
        
        Args:
            correo_cliente: Email del cliente
            nombre_cliente: Nombre del cliente
            pedido_id: ID del pedido
            razon: Razón del rechazo
        """
        asunto = f"Pedido Rechazado #{pedido_id} - Información Importante"
        
        cuerpo_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                    <h2 style="color: #c0392b; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
                        ✗ Pedido No Procesado
                    </h2>
                    
                    <p>Hola <strong>{nombre_cliente}</strong>,</p>
                    
                    <p>Lamentablemente, no hemos podido procesar tu pedido. Aquí está el detalle:</p>
                    
                    <div style="background-color: #fdeaea; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #c0392b;">
                        <p><strong>ID del Pedido:</strong> {pedido_id}</p>
                        <p><strong>Motivo:</strong> {razon}</p>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        Por favor, <strong>intenta nuevamente</strong> o <strong>contacta a nuestro equipo de atención al cliente</strong> 
                        para más información.
                    </p>
                    
                    <p style="margin-top: 20px; color: #7f8c8d; font-size: 12px;">
                        Timestamp: {datetime.now().strftime("%d/%m/%Y %H:%M")}
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self._enviar_correo(correo_cliente, asunto, cuerpo_html)
    
    def _enviar_correo(self, 
                       destinatario: str,
                       asunto: str,
                       cuerpo_html: str) -> Dict[str, Any]:
        """
        Envía un correo SMTP usando Gmail o cualquier servidor SMTP
        
        Args:
            destinatario: Email del destinatario
            asunto: Asunto del correo
            cuerpo_html: Cuerpo del correo en formato HTML
            
        Returns:
            Dict con resultado del envío
        """
        try:
            # Validar configuración
            if not self.from_email or not self.password:
                return {
                    "tipo": "envio_correo",
                    "exito": False,
                    "error": "SMTP no configurado. Verifica las variables de entorno.",
                    "destinatario": destinatario
                }
            
            # Crear mensaje
            mensaje = MIMEMultipart('alternative')
            mensaje['Subject'] = asunto
            mensaje['From'] = self.from_email
            mensaje['To'] = destinatario
            
            # Agregar versión de texto plano
            cuerpo_texto = f"Supermercado - {asunto}\n\nPor favor, abre este correo en un cliente que soporte HTML."
            parte_texto = MIMEText(cuerpo_texto, 'plain')
            
            # Agregar versión HTML
            parte_html = MIMEText(cuerpo_html, 'html')
            
            mensaje.attach(parte_texto)
            mensaje.attach(parte_html)
            
            # Enviar correo
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as servidor:
                if self.use_tls:
                    servidor.starttls()
                
                servidor.login(self.from_email, self.password)
                servidor.send_message(mensaje)
            
            logger.info(f"✓ Correo enviado a: {destinatario}")
            
            return {
                "tipo": "envio_correo",
                "exito": True,
                "destinatario": destinatario,
                "asunto": asunto,
                "timestamp": datetime.now().isoformat()
            }
            
        except smtplib.SMTPException as e:
            logger.error(f"✗ Error SMTP: {str(e)}")
            return {
                "tipo": "envio_correo",
                "exito": False,
                "error": f"Error de SMTP: {str(e)}",
                "destinatario": destinatario
            }
        except Exception as e:
            logger.error(f"✗ Error inesperado: {str(e)}")
            return {
                "tipo": "envio_correo",
                "exito": False,
                "error": f"Error inesperado: {str(e)}",
                "destinatario": destinatario
            }


# Instancia global del servicio
servicio_correo = ServicioCorreo()
