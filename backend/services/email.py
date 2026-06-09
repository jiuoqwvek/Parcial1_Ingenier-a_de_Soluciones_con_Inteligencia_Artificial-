import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")


class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.from_email = FROM_EMAIL
        self.password = SMTP_PASSWORD
        self.admin_email = ADMIN_EMAIL

    @property
    def configured(self) -> bool:
        return bool(self.from_email and self.password)

    def _send_html(self, destinatario: str, asunto: str, cuerpo_html: str) -> dict:
        try:
            mensaje = MIMEMultipart("alternative")
            mensaje["Subject"] = asunto
            mensaje["From"] = self.from_email
            mensaje["To"] = destinatario
            mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=20) as smtp:
                smtp.starttls()
                smtp.login(self.from_email, self.password)
                smtp.sendmail(self.from_email, destinatario, mensaje.as_string())

            logger.info("Correo enviado a %s", destinatario)
            return {"exito": True, "destinatario": destinatario}
        except Exception as exc:
            logger.warning("No se pudo enviar correo: %s", exc)
            return {"exito": False, "error": str(exc), "destinatario": destinatario}

    def send_order_confirmation(self, correo_cliente: str, nombre_cliente: str, pedido_id: str, items: list, total: float) -> dict:
        if not self.configured:
            return {"exito": False, "razon": "SMTP no configurado"}

        asunto = f"Confirmación de Pedido #{pedido_id} - Supermercado"
        filas_items = ""
        for item in items:
            filas_items += (
                f"<tr>"
                f"<td style=\"padding: 8px; border-bottom: 1px solid #ddd;\">{item.get('nombre', 'Producto')}</td>"
                f"<td style=\"padding: 8px; border-bottom: 1px solid #ddd; text-align: center;\">{item.get('cantidad_orden', 0)}</td>"
                f"<td style=\"padding: 8px; border-bottom: 1px solid #ddd; text-align: right;\">${item.get('precio', 0):.2f}</td>"
                f"</tr>"
            )

        cuerpo_html = (
            f"<html><body style=\"font-family: Arial, sans-serif; color: #333;\">"
            f"<div style=\"max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;\">"
            f"<h2 style=\"color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px;\">✓ Pedido Confirmado</h2>"
            f"<p>Hola <strong>{nombre_cliente}</strong>,</p>"
            f"<p>Gracias por tu compra. Tu pedido ha sido procesado exitosamente.</p>"
            f"<div style=\"background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;\">"
            f"<p><strong>ID del Pedido:</strong> {pedido_id}</p>"
            f"<p><strong>Total:</strong> ${total:.2f}</p>"
            f"</div>"
            f"<table style=\"width: 100%; border-collapse: collapse;\">"
            f"<thead><tr style=\"background-color: #27ae60; color: white;\">"
            f"<th style=\"padding: 10px; text-align: left;\">Producto</th>"
            f"<th style=\"padding: 10px; text-align: center;\">Cantidad</th>"
            f"<th style=\"padding: 10px; text-align: right;\">Precio</th>"
            f"</tr></thead><tbody>{filas_items}</tbody></table>"
            f"<p style=\"margin-top: 20px; color: #7f8c8d; font-size: 12px;\">Correo automático del sistema de gestión de supermercado.</p>"
            f"</div></body></html>"
        )

        return self._send_html(correo_cliente, asunto, cuerpo_html)
