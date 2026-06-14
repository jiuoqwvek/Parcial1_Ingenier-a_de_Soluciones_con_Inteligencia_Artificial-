Deploy bootstrap

Este directorio contiene un script para inicializar un servidor Ubuntu (EC2) y desplegar el proyecto usando Docker.

Uso:

1. Descargar y ejecutar en la instancia (requiere sudo/root):

- Opción rápida (descarga directa del script via HTTPS):

  curl -fsSL https://raw.githubusercontent.com/USUARIO/REPO/main/deploy/bootstrap-ec2.sh -o bootstrap.sh
  sudo bash bootstrap.sh

- Opción clonando el repo por SSH (recomendada si tienes clave SSH configurada):

  sudo apt update && sudo apt install -y git
  sudo mkdir -p /opt/ai-agent
  sudo chown $USER:$USER /opt/ai-agent
  git clone git@github.com:USUARIO/REPO.git /opt/ai-agent
  cd /opt/ai-agent/deploy
  # Ejecuta el bootstrap desde la copia local (opcional)
  sudo bash bootstrap-ec2.sh

2. El script clona el repositorio en /opt/ai-agent por defecto y levanta los servicios con docker compose.

Notas:
- Reemplaza USUARIO/REPO por tu usuario y repo si estás descargando desde otra ubicación.
- Si usas la opción SSH, asegúrate de tener configurada tu clave pública en GitHub (Settings > SSH and GPG keys).
- El script intenta copiar archivos .env.example a .env si existen.
