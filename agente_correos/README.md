# agente_correos

**Sistema de gestión de órdenes de reposición, alertas de inventario y reportes operativos para Unimarc.**

Este directorio contiene el código ejecutable del sistema.

## Qué hay aquí

```
core/                              # Módulos de lógica
├── email_service.py              # Servicio SMTP para enviar correos
├── orden_manager.py              # Crear/aprobar/rechazar órdenes
├── database.py                   # Guardar datos en JSON
└── models.py                     # Constantes y configuración

scripts/                           # Scripts para ejecutar
├── demo_flujo.py                 # Crear orden de reposicion
├── gestor_ordenes.py             # Aprobar/rechazar órdenes
├── enviar_alerta_inventario.py   # Enviar alertas de stock bajo
├── enviar_reporte_diario.py      # Enviar reporte operativo
└── procesar_respuesta_orden.py   # (Módulo interno para confirmaciones)

databases/                         # Datos guardados localmente
└── ordenes_reposicion.json       # Todas las órdenes creadas
```

## Scripts Principales (Ejecutar estos)

### 1. Crear orden
```bash
python scripts/demo_flujo.py
```

### 2. Gestionar órdenes
```bash
python scripts/gestor_ordenes.py
```

### 3. Alertas de inventario
```bash
python scripts/enviar_alerta_inventario.py
```

### 4. Reporte diario
```bash
python scripts/enviar_reporte_diario.py
```

## Base de Datos

`databases/ordenes_reposicion.json` - Guarda todas las órdenes con su estado.

Esta es la **única base de datos real**. Se actualiza automáticamente cuando creas, apruebas o rechazas órdenes.

## Para Entender Más

- **Documentación general**: Ver [`../README.md`](../README.md)
- **Configuración SMTP**: Ver [`./CONFIGURACION_GMAIL.md`](./CONFIGURACION_GMAIL.md)

## Requisitos

- Python 3.8+
- `.env` configurado en esta misma carpeta (ver [`./.env.example`](./.env.example))
- `pip install -r requirements.txt`
