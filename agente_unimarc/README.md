# AGENTE INTELIGENTE UNIMARC

## Documentación Técnica

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura General](#arquitectura-general)
3. [Indicadores de Logro (IL) Implementados](#indicadores-de-logro-implementados)
4. [Componentes Principales](#componentes-principales)
5. [Sistema de Memoria](#sistema-de-memoria)
6. [Planificación y Decisiones Adaptativas](#planificación-y-decisiones-adaptativas)
7. [Ejemplos de Ejecución](#ejemplos-de-ejecución)
8. [Diagrama de Orquestación](#diagrama-de-orquestación)
9. [Referencias Bibliográficas](#referencias-bibliográficas)

---

## RESUMEN EJECUTIVO

El agente inteligente UNIMARC es un sistema de automatización organizacional que demuestra la integración de técnicas de IA para resolver problemas reales de gestión de inventario. El agente combina:

- **Herramientas especializadas** (consulta, escritura, razonamiento)
- **Memoria persistente** (corto y largo plazo)
- **Planificación adaptativa** (múltiples etapas, decisiones cambiantes)
- **Documentación técnica completa**

El sistema es completamente funcional y puede ser ejecutado de manera autónoma para demostrar su capacidad de razonamiento y toma de decisiones.

---

## ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────┐
│              AGENTE INTELIGENTE UNIMARC                 │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌────────┐       ┌─────────┐      ┌──────────┐
    │ MEMORIA│       │  TOOLS  │      │ORQUESTADOR│
    └────────┘       └─────────┘      └──────────┘
        │                 │                 │
        ├─ Corto plazo   ├─ Consulta      ├─ Planificación
        ├─ Largo plazo   ├─ Escritura     ├─ Decisiones
        └─ Contexto      └─ Razonamiento  └─ Control
        
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    ┌─────▼─────┐
                    │ BASE DATOS │ (JSON)
                    └───────────┘
```

---

## INDICADORES DE LOGRO IMPLEMENTADOS

### IL2.1: Agentes Funcionales con Herramientas

**Objetivo**: Integrar herramientas de consulta, escritura y razonamiento en un agente funcional.

**Implementación**:

```python
# tools.py - Tres categorías de herramientas:

1. HerramientasConsulta
   - consultar_inventario()      # Lee estado actual
   - consultar_producto()         # Lee detalles de producto
   - consultar_memoria_reciente() # Lee eventos pasados
   - consultar_patrones()         # Lee aprendizajes

2. HerramientasEscritura
   - registrar_pedido()          # Escribe nuevo pedido
   - actualizar_stock()          # Modifica inventario
   - registrar_aprendizaje()     # Guarda patrones

3. HerramientasRazonamiento
   - evaluar_disponibilidad()    # Lógica de stock
   - evaluar_prioridad_reposicion() # Lógica de urgencia
   - evaluar_patron_cliente()    # Lógica de riesgo
```

**Demostración**: El agente ejecuta estas herramientas en combinación durante procesos complejos.

---

### IL2.2: Configuración de Memoria y Recuperación de Contexto

**Objetivo**: Implementar memoria de corto y largo plazo para continuidad en tareas prolongadas.

#### Memoria Corto Plazo (Buffer de eventos)

```python
# memory_manager.py - GestorMemoria.registrar_evento()

Características:
- Guarda últimos 100 eventos
- Formato: {timestamp, tipo_evento, descripción, datos}
- Recuperación rápida para contexto inmediato
- Ejemplo: "Se aprobó pedido de Cliente X"
```

**Implementación técnica**:
- Almacenamiento en JSON (`databases/memoria_corto.json`)
- Índice temporal para búsquedas rápidas
- Límite de 100 eventos para evitar memoria infinita

#### Memoria Largo Plazo (Patrones aprendidos)

```python
# memory_manager.py - GestorMemoria.aprender_patron()

Patrones registrados:
- Cliente frecuente: ¿Este cliente compra regularmente?
- Producto lento: ¿Cuánto tiempo tarda realmente?
- Tiene deuda: ¿El cliente ha incumplido antes?
- Es corporativo: ¿Es una empresa grande?

Estructura:
{
  "entidad": "cliente",           # Qué tipo de entidad
  "id_entidad": "Cliente X",      # Identificador
  "patron": "cliente_frecuente",  # Tipo de patrón
  "valor": true,                  # Valor del patrón
  "fecha_aprendizaje": "2024-05-21T10:30:00"
}
```

#### Continuidad en Tareas Prolongadas

```python
# memory_manager.py - iniciar_tarea_multipasos()

Ejemplo: Procesar pedido en 4 etapas
1. Etapa 1: Evaluar disponibilidad → RESULTADO 1
2. Etapa 2: Evaluar cliente → RESULTADO 2
3. Etapa 3: Tomar decisión → RESULTADO 3
4. Etapa 4: Registrar aprendizaje → RESULTADO 4

El sistema mantiene contexto entre etapas:
- paso_actual: 0 → 1 → 2 → 3 → 4
- resultados_parciales: [res1, res2, res3, res4]
```

---

### IL2.3: Planificación y Toma de Decisiones Adaptativas

**Objetivo**: Adaptar comportamiento del agente ante tareas con múltiples etapas y condiciones cambiantes.

#### Decisiones Adaptativas

El agente ajusta sus decisiones según el contexto:

```python
# agent.py - procesar_pedido_adaptativo()

┌─ ETAPA 1: ¿Hay stock disponible?
│  ├─ SÍ → continúa
│  └─ NO → adapta a ESPERAR o RECHAZAR
│
├─ ETAPA 2: ¿Cliente es de riesgo?
│  ├─ BAJO → aprueba
│  ├─ MEDIO → espera
│  └─ ALTO → rechaza
│
└─ ETAPA 3: Decisión final adaptada al contexto
   ├─ APROBAR (stock + cliente OK)
   ├─ ESPERAR (stock insuficiente)
   └─ RECHAZAR (cliente riesgoso o no existe)
```

#### Ejemplo Concreto

```python
# Escenario 1: Stock disponible + cliente bueno → APROBAR
# Escenario 2: Stock bajo + cliente frecuente → ESPERAR
# Escenario 3: Sin stock + cliente nuevo → GENERAR_ORDEN_URGENTE
```

#### Planificación Multi-Etapa

```python
# agent.py - reposicion_adaptativa()

Etapa 1: Identificar productos críticos
  └─ Consultar inventario
  └─ Identificar bajos vs mínimo

Etapa 2: Agrupar por proveedor
  └─ Optimizar: reducir número de órdenes
  └─ Ahorrar: combinar items del mismo proveedor

Etapa 3: Crear órdenes
  └─ Una orden por proveedor
  └─ Cantidad = máximo - actual
```

---

### IL2.4: Documentación de Diseño e Implementación

Este documento explica completamente:

✅ Arquitectura del agente (sección 2)
✅ Integración de herramientas (sección 4)
✅ Sistema de memoria (sección 5)
✅ Estrategias de decisión (sección 6)
✅ Orquestación de componentes (sección 8)

---

## COMPONENTES PRINCIPALES

### 1. models.py (Modelos de datos)

Define las estructuras de datos:

```python
- Producto: sku, nombre, stock, minimo, maximo, precio
- Pedido: id, cliente, items, total, estado, decisiones
- MemoriaCortoplazo: evento reciente con timestamp
- MemoriaLargoPlazo: patrón aprendido
```

**Responsabilidad**: Tipificación y validación de datos.

### 2. database.py (Persistencia)

Gestiona lectura/escritura en JSON:

```python
- Operaciones CRUD para inventario
- Guardado de pedidos
- Registro de memoria corto/largo plazo
- Recuperación de contexto
```

**Responsabilidad**: Persisten los datos del agente.

### 3. tools.py (Herramientas)

Implementa las 3 categorías de herramientas:

```python
HerramientasConsulta (7 métodos)
  └─ Lectura de estado

HerramientasEscritura (3 métodos)
  └─ Cambios en BD

HerramientasRazonamiento (3 métodos)
  └─ Lógica de decisión
```

**Responsabilidad**: Acciones que el agente puede ejecutar.

### 4. memory_manager.py (Gestor de memoria)

Orquesta memoria corto/largo plazo:

```python
GestorMemoria
  ├─ registrar_evento() - corto plazo
  ├─ obtener_contexto_reciente() - recuperar contexto
  ├─ aprender_patron() - largo plazo
  ├─ iniciar_tarea_multipasos() - inicio de tarea
  ├─ avanzar_paso() - avance de etapa
  └─ completar_tarea() - fin de tarea
```

**Responsabilidad**: Continuidad y contexto del agente.

### 5. agent.py (Agente Principal)

Orquesta todo: herramientas + memoria + decisiones

```python
AgenteUnimarc
  ├─ procesar_pedido_adaptativo() - 4 etapas
  ├─ reposicion_adaptativa() - 3 etapas
  └─ generar_reporte() - usa toda la memoria
```

**Responsabilidad**: Inteligencia y toma de decisiones.

### 6. ejemplos.py (Demostraciones)

5 ejemplos que demuestran capacidades:

```python
1. Pedido exitoso
2. Pedido sin stock
3. Reposición adaptativa
4. Memoria en acción
5. Flujo completo
```

**Responsabilidad**: Validación y demostración del sistema.

---

## SISTEMA DE MEMORIA

### Diagrama de Flujo de Memoria

```
┌──────────────────────────────────┐
│   EVENTO OCURRE EN EL AGENTE     │
└────────────┬─────────────────────┘
             │
        ┌────▼────┐
        │Registrado│
        └────┬────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────────┐  ┌──────────────┐
│ CORTO PLAZO │  │ LARGO PLAZO  │
│ (100 eventos)    │ (Patrones)   │
├─────────────┤  ├──────────────┤
│ • Timestamp │  │ • Entidad    │
│ • Tipo      │  │ • Patrón     │
│ • Datos     │  │ • Valor      │
└──────┬──────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
    ┌───────────▼───────────┐
    │  RECUPERABLE POR      │
    │  FUTURA ACCIÓN        │
    └───────────────────────┘
```

### Ejemplo Real

```python
# Se procesa un pedido
agente.procesar_pedido_adaptativo("Cliente X", [...])

# Se registran eventos automáticamente:
1. pedido_iniciado → MEMORIA CORTO PLAZO
2. evaluar_disponibilidad → MEMORIA CORTO PLAZO
3. evaluar_cliente → MEMORIA CORTO PLAZO
4. decision_tomada → MEMORIA CORTO PLAZO

# Se aprenden patrones:
1. cliente_procesado (Cliente X) → MEMORIA LARGO PLAZO
2. Si cliente X falla: tiene_deuda (Cliente X, true) → MEMORIA LARGO PLAZO

# Próximo pedido de Cliente X:
- Recupera patrón: ¿tiene_deuda?
- Adapta decisión: RECHAZA
```

---

## PLANIFICACIÓN Y DECISIONES ADAPTATIVAS

### Flujo de Decisión Adaptativa

```python
PROCESAR PEDIDO: Cliente X pide 100 kg de Leche
  │
  ├─ ETAPA 1: ¿Hay 100 kg de leche?
  │   ├─ Consultamos: stock = 50 kg
  │   └─ Razonamiento: NO hay suficiente
  │
  ├─ ETAPA 2: ¿Quién es Cliente X?
  │   ├─ Consultamos memoria: cliente_frecuente = true
  │   └─ Razonamiento: RIESGO = BAJO
  │
  ├─ ETAPA 3: Decisión Adaptativa
  │   ├─ Condición 1: Stock insuficiente ✗
  │   ├─ Condición 2: Cliente confiable ✓
  │   └─ DECISIÓN: ESPERAR REPOSICIÓN (no rechazar)
  │
  └─ ETAPA 4: Registrar aprendizaje
      └─ Guardar: "Cliente X es frecuente"
```

### Comparación con Sistema No-Adaptativo

```
NO-ADAPTATIVO:
  Si stock < cantidad → RECHAZAR (siempre)

ADAPTATIVO:
  Si stock < cantidad:
    ├─ ¿Cliente frecuente? → ESPERAR
    ├─ ¿Cliente nuevo? → RECHAZAR
    └─ ¿Emergencia? → GENERAR_ORDEN_URGENTE
```

---

## EJEMPLOS DE EJECUCIÓN

### Ejecución 1: Pedido Exitoso

```
$ python ejemplos.py
Opción: 1

[Resultado esperado]
PROCESANDO PEDIDO - Cliente: Supermercado Central
✓ Etapa 1: Disponibilidad verificada
✓ Etapa 2: Cliente evaluado
✅ DECISIÓN: APROBAR PEDIDO
✓ Stock actualizado
✓ Aprendizaje registrado
```

### Ejecución 2: Ejecución Automática

```
$ python ejemplos.py --auto

Ejecuta automáticamente:
1. Pedido exitoso
2. Pedido sin stock
3. Reposición adaptativa
4. Memoria en acción
5. Flujo completo
```

---

## DIAGRAMA DE ORQUESTACIÓN

### Flujo Completo de Decisión

```
                    ┌─────────────────┐
                    │ AGENTE INICIA   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ RECIBE SOLICITUD│
                    │ (Pedido cliente)│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐         ┌────────┐         ┌──────────┐
    │CONSULTA│         │MEMORIA │         │RAZONAMIENTO│
    ├────────┤         ├────────┤         ├──────────┤
    │Inventario       │Contexto │         │Decisión  │
    │Productos         │Patrones │         │Adaptativa│
    └────┬───┘         └────┬───┘         └────┬─────┘
         │                  │                   │
         └──────────────┬───┴───────────────────┘
                        │
                   ┌────▼────┐
                   │COMBINAR  │
                   │INFORMACIÓN│
                   └────┬────┘
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
        ┌────┐    ┌────────┐   ┌────────┐
        │APROBAR │ │ESPERAR │   │RECHAZAR│
        └────┘    └────────┘   └────────┘
           │            │            │
           └────────┬───┴───────────┘
                    │
            ┌───────▼──────┐
            │ ESCRITURA BD │
            │ (Guardar)    │
            └───────┬──────┘
                    │
            ┌───────▼──────────┐
            │ REGISTRAR EVENTO │
            │ (Memoria corto)  │
            └───────┬──────────┘
                    │
            ┌───────▼──────────┐
            │APRENDER PATRÓN   │
            │(Memoria largo)   │
            └───────┬──────────┘
                    │
            ┌───────▼──────────┐
            │  TAREA COMPLETA  │
            └──────────────────┘
```

---

## REFERENCIAS BIBLIOGRÁFICAS

### Frameworks y Librerías Utilizadas

1. **Python Software Foundation** (2024). *Python 3.10 Documentation*. Recuperado de https://docs.python.org/3.10/

2. **JSON Official** (2024). *Introducing JSON*. Recuperado de https://www.json.org/

### Conceptos de Agentes Inteligentes

3. Russel, S. J., & Norvig, P. (2020). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

4. Wooldridge, M. (2009). *An introduction to multiagent systems* (2nd ed.). John Wiley & Sons.

5. Negnevitsky, M. (2005). *Artificial intelligence: A guide to intelligent systems* (2nd ed.). Pearson.

### Memoria en Sistemas de IA

6. Graves, A., Wayne, G., & Danihelka, I. (2014). Neural Turing machines. *arXiv preprint arXiv:1410.5401*.

7. Sukhbaatar, S., Szlam, A., Weston, J., & Fergus, R. (2015). End-to-end memory networks. *Advances in neural information processing systems*, 28.

### Planificación y Razonamiento

8. Ghallab, M., Nau, D., & Traverso, P. (2004). *Automated planning: theory and practice*. Morgan Kaufmann Publishers.

9. Jackson, P. (1999). *Introduction to expert systems* (3rd ed.). Addison-Wesley.

### Sistemas de Automatización

10. Brynjolfsson, E., & McAfee, A. (2014). *The second machine age: Work, progress, and prosperity in a time of brilliant technologies*. WW Norton & Company.

### Gestión de Inventario

11. Stadtler, H., Kilger, C., & Meyr, H. (Eds.). (2015). *Supply chain management and advanced planning: Concepts, models, software, and case studies* (5th ed.). Springer.

---

## CONCLUSIÓN

El agente inteligente UNIMARC demuestra exitosamente:

✅ **IL2.1**: Integración de herramientas (consulta, escritura, razonamiento)
✅ **IL2.2**: Sistema de memoria robusto (corto y largo plazo)
✅ **IL2.3**: Planificación adaptativa y toma de decisiones inteligentes
✅ **IL2.4**: Documentación técnica completa

El sistema es completamente funcional y puede resolver problemas reales de automatización organizacional.

---

**Autores**: [Tu nombre y tu compañera]
**Fecha**: 21 de mayo de 2024
**Institución**: [Tu institución]
**Asignatura**: Ingeniería de Soluciones con Inteligencia Artificial
**Evaluación**: Parcial 2
