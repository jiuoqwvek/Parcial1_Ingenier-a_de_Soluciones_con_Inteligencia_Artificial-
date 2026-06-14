Deploy bootstrap

Este directorio contiene un script para inicializar un servidor Ubuntu (EC2) y desplegar el proyecto usando Docker.

Uso:

1. Descargar y ejecutar en la instancia (requiere sudo/root):

   curl -fsSL https://raw.githubusercontent.com/USUARIO/REPO/main/deploy/bootstrap-ec2.sh -o bootstrap.sh
   sudo bash bootstrap.sh

2. El script clona el repositorio en /opt/ai-agent por defecto y levanta los servicios con docker compose.

Notas:
- Reemplaza USUARIO/REPO por tu usuario y repo si estás descargando desde otra ubicación.
- El script intenta copiar archivos .env.example a .env si existen.
