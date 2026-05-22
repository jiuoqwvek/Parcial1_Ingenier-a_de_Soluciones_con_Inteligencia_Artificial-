"""
Configuración centralizada del sistema.
Todas las variables de entorno se cargan aquí desde .env.
"""

import os
from dotenv import load_dotenv

# Buscar .env desde la raíz del proyecto
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(dotenv_path)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
