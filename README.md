# Proyecto - Ingeniería de Soluciones con IA

**Caso: Unimarc (Supermercado)**

Repositorio que integra el desarrollo completo de dos soluciones basadas en inteligencia artificial para la cadena de supermercados Unimarc.

---

## Contenido del Proyecto

| Carpeta | Parcial | Descripción |
|---------|---------|-------------|
| [`agente_llm_inventario/`](agente_llm_inventario/README.md) | **Parcial 1** | Agente LLM con pipeline RAG para sincronización inteligente de inventario |
| [`agente_correos/`](agente_correos/README.md) | **Parcial 2** | Sistema automatizado de gestión de correos: órdenes, alertas y reportes |

---

## Parcial 1 - Agente LLM para Inventario

Solución basada en **LangChain + RAG** que actúa como un asistente inteligente de gestión de existencias.

**Archivos:**
- [`agente_llm_inventario/solucion_unimarc.ipynb`](agente_llm_inventario/solucion_unimarc.ipynb) - Notebook principal con el agente
- [`agente_llm_inventario/requirements.txt`](agente_llm_inventario/requirements.txt) - Dependencias (LangChain, OpenAI, etc.)
- [`agente_llm_inventario/README.md`](agente_llm_inventario/README.md) - Documentación completa

**Funcionalidades:**
- Pipeline RAG para conectar datos de inventario con respuestas del modelo
- Agente LLM con memoria dinámica y resumen de contexto
- Extracción estructurada de datos de inventario
- Streaming de respuestas en tiempo real

[➡ Ver documentación de Parcial 1](agente_llm_inventario/README.md)

---

## Parcial 2 - Sistema de Gestión de Correos Unimarc

Sistema automatizado para gestionar órdenes de reposición, alertas de inventario y reportes operativos.

**Estructura:**
```
agente_correos/
├── scripts/                  # Scripts ejecutables
│   ├── demo_flujo.py        # Crear orden
│   ├── gestor_ordenes.py    # Aprobar/rechazar
│   ├── enviar_alerta_inventario.py
│   └── enviar_reporte_diario.py
├── core/                     # Lógica interna
├── databases/
│   └── ordenes_reposicion.json
└── README.md
```

**Funcionalidades:**
- Crear y enviar órdenes de reposición por correo
- Aprobar o rechazar órdenes desde terminal
- Alertas automáticas de stock bajo
- Reporte operativo diario
- Base de datos local con tracking de estados

### Inicio Rápido (Parcial 2)

```bash
# 1. Ir a la carpeta y configurar credenciales
cd agente_correos
cp .env.example .env
# Editar .env con SMTP_FROM_EMAIL, SMTP_PASSWORD, ADMIN_EMAIL

# 2. Instalar
pip install -r requirements.txt

# 3. Usar
python scripts/demo_flujo.py          # Crear orden
python scripts/gestor_ordenes.py      # Gestionar órdenes
python scripts/enviar_reporte_diario.py  # Reporte diario
```

[➡ Ver documentación de Parcial 2](agente_correos/README.md)

---

## Estructura General

```
.
├── README.md                           # Este archivo
├── .gitignore                          # Archivos ignorados
│
├── agente_llm_inventario/              # Parcial 1 - Agente LLM
│   ├── README.md
│   ├── solucion_unimarc.ipynb
│   ├── requirements.txt
│   └── .env.ejemplo
│
└── agente_correos/                     # Parcial 2 - Gestión de correos
    ├── README.md
    ├── CONFIGURACION_GMAIL.md          # Setup Gmail SMTP
    ├── requirements.txt
    ├── .env.example                    # Credenciales SMTP
    ├── core/
    ├── scripts/
    └── databases/
```

## Requisitos Generales

- Python 3.8+
- pip
- Git

### Parcial 1
- GitHub Token (GitHub Models)
- LangSmith API Key

### Parcial 2
- Cuenta de Gmail (con contraseña de aplicación)
- Conexión a internet

## Seguridad

⚠️ Los archivos `.env` contienen credenciales y **NO deben subirse a Git**.
Están protegidos en `.gitignore` automáticamente.

---

| Parcial | Documentación |
|---------|---------------|
| Parcial 1 | [`agente_llm_inventario/README.md`](agente_llm_inventario/README.md) |
| Parcial 2 | [`agente_correos/README.md`](agente_correos/README.md) |
