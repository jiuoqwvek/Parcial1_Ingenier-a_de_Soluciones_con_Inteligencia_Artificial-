#!/bin/bash
# Script para subir el deploy a un repo nuevo en GitHub

# 1. CREAR REPO EN GITHUB
# Ve a https://github.com/new
# Nombre: agente-ia-deploy (o el que prefieras)
# Descripción: Backend unificado con observabilidad y guardrails
# Selecciona: Private (o Public si lo prefieres)
# NO inicialices con README (ya tenemos archivos)

# 2. EJECUTA ESTOS COMANDOS

# Reemplaza USER_NAME y REPO_NAME con tus valores
GITHUB_USER="jiuoqwvek"
REPO_NAME="agente-ia-deploy"

# Agregar remote
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git

# Cambiar rama a main (opcional, si GitHub lo requiere)
git branch -M main

# Hacer push
git push -u origin main

echo "✅ Repo subido a: https://github.com/$GITHUB_USER/$REPO_NAME"
