# Agente Inteligente Unimarc - Parcial 2

Sistema de agente con herramientas integradas, memoria adaptativa y planificación multi-etapa para gestión de inventario y procesamiento de pedidos en Unimarc.

## Estructura

```
agente_unimarc/
├── models.py              # Estructuras de datos
├── database.py            # Persistencia en JSON
├── tools.py              # 13 herramientas integradas
├── memory_manager.py     # Gestión de memoria corto/largo plazo
├── agent.py              # Orquestación del agente
├── ejemplos.py           # 5 ejemplos ejecutables
├── requirements.txt      # Dependencias mínimas
├── README.md             # Documentación técnica completa
└── databases/            # Almacenamiento persistente (auto-generado)
```

## Requisitos

- Python 3.8+
- python-dotenv

## Instalación

```bash
cd agente_unimarc
pip install -r requirements.txt
```

## Ejecución

**Modo automático (recomendado):**
```bash
python3 ejemplos.py --auto
```

**Modo interactivo:**
```bash
python3 ejemplos.py
```

## Características

### IL2.1 - Agentes con Herramientas
- **HerramientasConsulta**: 7 métodos (lectura de datos)
- **HerramientasEscritura**: 3 métodos (mutaciones y registros)
- **HerramientasRazonamiento**: 3 métodos (evaluación y decisiones)

### IL2.2 - Memoria
- **Corto plazo**: Buffer de últimos 100 eventos
- **Largo plazo**: Patrones aprendidos y comportamientos históricos
- **Persistencia**: JSON almacenado en `databases/`

### IL2.3 - Planificación Adaptativa
- **procesar_pedido_adaptativo()**: 4 etapas con decisiones contextuales
- **reposicion_adaptativa()**: 3 etapas para gestión de stock crítico
- **Decisiones adaptativas**: APROBAR, ESPERAR, GENERAR_ORDEN_URGENTE, RECHAZAR

### IL2.4 - Documentación Técnica
- README.md con 630 líneas de documentación
- Diagramas ASCII de arquitectura, memoria, decisiones y orquestación
- 11 referencias bibliográficas en formato APA

## Ejemplos

1. **Pedido Exitoso**: Stock disponible → APROBAR
2. **Stock Insuficiente**: Producto bajo mínimo → ESPERAR
3. **Reposición Adaptativa**: Identificación de críticos y generación de órdenes
4. **Memoria**: Recuperación de eventos recientes y patrones aprendidos
5. **Flujo Completo**: Orquestación end-to-end

## Documentación Completa

Consulta `agente_unimarc/README.md` para:
- Arquitectura detallada
- Explicación de cada módulo
- Sistema de memoria y contexto
- Planificación y decisiones adaptativas
- Referencias y bibliografía

## Autor

Solución desarrollada para evaluación Parcial 2 - Ingeniería de Soluciones con IA
