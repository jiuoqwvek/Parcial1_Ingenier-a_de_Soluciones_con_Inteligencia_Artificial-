#!/usr/bin/env bash
# Bootstrap script for Ubuntu EC2 to deploy the project using Docker
# Usage:
# curl -fsSL https://raw.githubusercontent.com/USUARIO/REPO/main/deploy/bootstrap-ec2.sh -o bootstrap.sh
# bash bootstrap.sh

set -euo pipefail
REPO_URL="${REPO_URL:-https://github.com/jiuoqwvek/Ingenier-a-de-Soluciones-con-Inteligencia-Artificial.git}"
BRANCH="${BRANCH:-main}"
TARGET_DIR="${TARGET_DIR:-/opt/ai-agent}"

echo "[bootstrap] Repo: $REPO_URL"
echo "[bootstrap] Branch: $BRANCH"
echo "[bootstrap] Target dir: $TARGET_DIR"

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root or with sudo. Re-run with sudo." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "[bootstrap] Updating apt and installing prerequisites..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release git software-properties-common

echo "[bootstrap] Installing Docker Engine and docker-compose plugin..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker

echo "[bootstrap] Preparing application directory..."
if [ -d "$TARGET_DIR" ]; then
  echo "[bootstrap] Target exists, pulling latest..."
  git -C "$TARGET_DIR" fetch --all --prune
  git -C "$TARGET_DIR" checkout "$BRANCH"
  git -C "$TARGET_DIR" pull origin "$BRANCH"
else
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$TARGET_DIR"
fi

cd "$TARGET_DIR"

echo "[bootstrap] Copying example env files (if present)..."
if [ -f backend/.env.example ] && [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env || true
fi
if [ -f agente_llm_inventario/.env.ejemplo ] && [ ! -f agente_llm_inventario/.env ]; then
  cp agente_llm_inventario/.env.ejemplo agente_llm_inventario/.env || true
fi

echo "[bootstrap] Building and starting services with docker compose..."
# If repository uses docker compose v2 plugin (docker compose), prefer it
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  docker compose up -d --build
else
  # Fallback to docker-compose binary if available
  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose up -d --build
  else
    echo "No docker compose available. Installed Docker but couldn't run compose." >&2
    exit 1
  fi
fi

echo "[bootstrap] Deployment finished. Services should be up."
echo "Use 'docker ps' to verify running containers. Check logs with 'docker compose logs -f'."
