#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/jiuoqwvek/Repo_prueba.git}"
BRANCH="${BRANCH:-main}"
TARGET_DIR="${TARGET_DIR:-/opt/ai-agent}"

echo "[bootstrap] Repo: $REPO_URL"
echo "[bootstrap] Branch: $BRANCH"
echo "[bootstrap] Target dir: $TARGET_DIR"

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root or with sudo. Re-run with sudo." >&2
  exit 1
fi

echo "[bootstrap] Installing prerequisites..."
dnf update -y
dnf install -y git docker

echo "[bootstrap] Starting Docker..."
systemctl enable docker
systemctl start docker

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

echo "[bootstrap] Checking Docker..."

docker --version

if docker compose version >/dev/null 2>&1; then
    echo "[bootstrap] Building and starting services..."
    docker compose up -d --build
else
    echo "[ERROR] Docker Compose is not installed."
    exit 1
fi

echo "[bootstrap] Deployment finished."
docker ps
