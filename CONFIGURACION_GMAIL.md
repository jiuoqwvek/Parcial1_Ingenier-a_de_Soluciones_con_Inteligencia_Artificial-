# Configuración de Gmail

Para que el sistema pueda enviar correos, necesitas configurar una contraseña de aplicación en Gmail.

## Pasos

### 1. Habilitar verificación de dos pasos

1. Ve a https://myaccount.google.com/security
2. En la sección "Verificación en dos pasos", haz clic en "Empezar"
3. Sigue los pasos para configurar

### 2. Generar contraseña de aplicación

1. Ve a https://myaccount.google.com/apppasswords
2. Selecciona:
   - **Aplicación**: "Correo"
   - **Dispositivo**: "Windows/Mac/Linux" (o el tuyo)
3. Google generará una contraseña de 16 caracteres
4. **Copia esta contraseña** (sin espacios)

### 3. Configurar el archivo .env

1. En la carpeta `agente_correos/`, crea un archivo llamado `.env`
2. Copia el contenido de `agente_correos/.env.example`:

```
SMTP_FROM_EMAIL=
SMTP_PASSWORD=
ADMIN_EMAIL=
```

3. Completa los valores con tus datos reales:

### 4. Verificar que funciona

```bash
cd agente_correos
python scripts/demo_flujo.py
```

Si ves "Correo enviado exitosamente", ¡está funcionando!

## Troubleshooting

### Error: "Authentication failed"
- Verifica que la contraseña sea la de **aplicación**, no la personal
- Verifica que no haya espacios extras
- Regenera una nueva contraseña en apppasswords

### Error: "Server rejected with error: SMTP 535"
- Verifica que hayas habilitado verificación de dos pasos
- La contraseña de app solo funciona CON 2FA activo

### No llegan los correos
- Revisa la carpeta de spam
- Verifica que `ADMIN_EMAIL` sea el correo que estés chequeando
- Los correos pueden tardar unos segundos

## ⚠️ Seguridad

- **NUNCA** compartas tu archivo `.env`
- **NUNCA** uses tu contraseña personal de Gmail
- Usa siempre contraseña de **aplicación**
- El archivo `.env` está en `.gitignore`, así que no se subirá a Git

---

¿Necesitas más ayuda? Consulta la [documentación completa](../README.md).
