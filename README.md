# Parcial 2 - Ingeniería de Soluciones con IA

**Sistema inteligente para gestión automatizada de correos: órdenes de reposición, alertas de inventario y reportes operativos para Unimarc.**

## Qué es esto

Un sistema que automatiza todo el proceso de órdenes de reposición:

1. **Crear órdenes** → Se envía correo automáticamente
2. **Aprobar/rechazar** → Desde terminal, sin web
3. **Alertas** → Notificaciones cuando stock es bajo
4. **Reportes** → Reporte operativo diario
5. **Registro** → Toda orden queda en base de datos local

Todo funciona desde terminal. Simple, profesional, sin dependencias web complejas.

## Estructura

```
.
├── README.md                        ← Estás aquí
├── .env.example                     # Copia a .env y agrega credenciales
├── .gitignore                       # Archivos ignorados en Git
├── CONFIGURACION_GMAIL.md           # Cómo configurar SMTP
│
└── agente_unimarc/                  # Sistema principal
    ├── scripts/
    │   ├── demo_flujo.py           # Crear orden
    │   ├── gestor_ordenes.py       # Aprobar/rechazar
    │   ├── enviar_alerta_inventario.py
    │   └── enviar_reporte_diario.py
    ├── core/                        # Lógica interna
    ├── databases/
    │   └── ordenes_reposicion.json  # BD con todas las órdenes
    └── README.md                    # Documentación técnica
```

## Inicio Rápido

### 1. Preparar

```bash
# Configurar credenciales
cp .env.example .env

# Editar .env y agregar:
# SMTP_FROM_EMAIL=
# SMTP_PASSWORD=
# ADMIN_EMAIL=
```

Ayuda: Leer [`CONFIGURACION_GMAIL.md`](CONFIGURACION_GMAIL.md)

### 2. Instalar

```bash
cd agente_unimarc
pip install -r requirements.txt
```

### 3. Usar

```bash
# Crear orden
python scripts/demo_flujo.py

# Aprobar/rechazar
python scripts/gestor_ordenes.py

# Otras funciones
python scripts/enviar_alerta_inventario.py
python scripts/enviar_reporte_diario.py
```

## Documentación

| Documento | Para qué |
|-----------|----------|
| [`CONFIGURACION_GMAIL.md`](CONFIGURACION_GMAIL.md) | Paso a paso para configurar Gmail SMTP |
| [`agente_unimarc/README.md`](agente_unimarc/README.md) | Documentación técnica interna |

## Correos

Todos se envían al correo configurado en `ADMIN_EMAIL` del `.env`

| Acción | Correo |
|--------|--------|
| Crear orden | Notificación pendiente |
| Aprobar orden | Confirmación de aprobación |
| Rechazar orden | Confirmación de rechazo |
| Stock bajo | Alerta de inventario |
| Reporte | Operativo diario |

## Base de Datos

Todo se guarda en: `agente_unimarc/databases/ordenes_reposicion.json`

Estructura de una orden:
```json
{
  "orden_id": "ORD-A3BAE290",
  "estado": "aprobada",
  "cantidad_total": 650,
  "fecha_creacion": "2026-05-22T16:35:19",
  "fecha_resolucion": "2026-05-22T16:36:45"
}
```

## Requisitos

- Python 3.8+
- pip
- Cuenta de Gmail (con contraseña de aplicación)
- Conexión a internet

## Seguridad

 **IMPORTANTE:**

- El archivo `.env` contiene credenciales y **NO debe subirse a Git**
- Está protegido en `.gitignore` automáticamente
- Usa contraseña de **aplicación**, no tu contraseña personal de Gmail
- Si la compartiste accidentalmente, regenera contraseña en Google

## Flujo Completo (5 minutos)

```bash
# 1. Crear orden (terminal)
python agente_unimarc/scripts/demo_flujo.py
# → Se envía correo al ADMIN_EMAIL configurado

# 2. Leer correo
# → Abre email y lee la orden

# 3. Gestionar orden (terminal)
python agente_unimarc/scripts/gestor_ordenes.py
# → Opción 1: Listar (ver token)
# → Opción 2: Aprobar
# → Se envía confirmación automática

# 4. Verificar BD
cat agente_unimarc/databases/ordenes_reposicion.json

# 5. Reporte
python agente_unimarc/scripts/enviar_reporte_diario.py
```

## ¿Cómo funciona?

1. **Scripts** (`agente_unimarc/scripts/`) - Lo que ejecutas
2. **Core** (`agente_unimarc/core/`) - La lógica de negocio
3. **Email** (`email_service.py`) - Envía correos por SMTP
4. **Órdenes** (`orden_manager.py`) - Gestiona estados de órdenes
5. **Database** (`database.py`) - Guarda en JSON local

No hay servidor web, no hay URLs complicadas, todo desde terminal.

## Para Más Detalles

1. **Primero leer**: [`README.md`](README.md) (este)
2. **Código**: [`agente_unimarc/README.md`](agente_unimarc/README.md)

---

**¿Listo para empezar?**

1. Copia `.env.example` a `.env`
2. Agrega tus credenciales de Gmail
3. Lee [`CONFIGURACION_GMAIL.md`](CONFIGURACION_GMAIL.md) si necesitas ayuda
4. Ejecuta `python agente_unimarc/scripts/demo_flujo.py`
