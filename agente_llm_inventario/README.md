# Parcial 1 - Agente LLM para Sincronización de Inventario (Caso: Unimarc)

---

> Este es el **Parcial 1** del proyecto. El repositorio completo incluye también el **Parcial 2** (agente de gestión de correos). Ver [`../README.md`](../README.md) para la documentación general.

---

## 1. Introducción
Este repositorio contiene el desarrollo de una solución integral basada en agentes LLM y pipelines RAG, aplicada al sector de retail en Chile. El proyecto busca optimizar la gestión de stock para mejorar la experiencia de usuario en plataformas de pedidos digitales.

## 2. Identificación del Problema
En cadenas como Unimarc o Santa Isabel, existe una desincronización crítica entre el stock físico de bodega y lo que el cliente ve en la aplicación.

- **Desafío:** Los productos aparecen disponibles en la app, pero están agotados en la góndola real.
- **Impacto:** Pérdida de ventas, frustración del cliente y ineficiencia en el trabajo de los repartidores.
- **Causa:** Falta de un puente de información en tiempo real que procese datos de inventario y los traduzca a disponibilidad digital.

## 3. Solución con IA
Se propone un Agente Inteligente de Gestión de Existencias que utiliza:


- **Pipeline RAG (Generación Aumentada por Recuperación):** Para conectar las fuentes de datos internas (inventario de bodega) con las respuestas del modelo, asegurando precisión absoluta.
- **Agentes LLM:** Para procesar discrepancias de nombres entre sistemas y generar alertas automáticas de reposición.
- **Prompts Optimizados:** Diseñados para actuar como un gestor de tienda experto, ajustando el contenido según el requerimiento organizacional

## 4. Requisitos del Sistema (¡IMPORTANTE!)

Para que este proyecto funcione correctamente, es **obligatorio** tener instalado y configurado lo siguiente:

1.  **Git:** Necesario para clonar el repositorio.
    * [Descargar Git aquí](https://git-scm.com/downloads)
2.  **Python 3.10+:** El proyecto requiere esta versión para asegurar la compatibilidad con LangChain.
    * [Descargar Python aquí](https://www.python.org/downloads/)
3.  **GitHub Token (Access Models):** Este proyecto consume modelos de **GitHub Marketplace**.
    * Genera tu **Personal Access Token (classic)** aquí: [GitHub Settings - Tokens](https://github.com/settings/tokens).
    * Puedes explorar los modelos disponibles en: [GitHub Models](https://github.com/marketplace/models).
4.  **LangSmith API Key:** Necesaria para el rastreo y observabilidad de la IA.
    * Regístrate y obtén tu llave en: [LangSmith Dashboard](https://smith.langchain.com/).

## 5. Clonar repositorio
Sigue estos pasos en tu terminal:
```bash
# 1. Clonar el repositorio principal (si no lo tienes)
git clone https://github.com/jiuoqwvek/Ing.-de-soluciones-con-ia-parcial-2-pruebas.git

# 2. Ingresar a la carpeta del proyecto y luego a parcial 1
cd Ing.-de-soluciones-con-ia-parcial-2-pruebas/agente_llm_inventario
```

## 6. Crear Entorno Virtual
Sigue estos pasos en tu terminal:
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

## 7. Instalar Dependencias
Sigue estos pasos en tu terminal:
```bash
pip install -r requirements.txt
```

## 8. Configurar Variables de Entorno
Crea un archivo `.env` a partir del ejemplo:
```bash
# Copiar el archivo de ejemplo
cp .env.ejemplo .env
```

Ya creado, edita el archivo `.env` con tus credenciales:

```env
OPENAI_BASE_URL="https://models.inference.ai.azure.com"
GITHUB_BASE_URL="https://models.inference.ai.azure.com"
OPENAI_EMBEDDINGS_URL="https://models.github.ai/inference"
GITHUB_TOKEN="tu_github_token_aqui"
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="tu_langsmith_api_key_aqui"
LANGSMITH_PROJECT="ingenieria_soluciones_con_ia"
```

## 9. Configuración Avanzada: Memoria Dinámica, Sesiones y Streaming

Para asegurar que la experiencia sea fluida y el consumo de tokens sea eficiente, implementamos una arquitectura moderna utilizando **LCEL (LangChain Expression Language)**. Esta configuración permite:

1. **Gestión de múltiples sesiones:** Capacidad de manejar diferentes chats simultáneos (`session_id`).
2. **Resumen Inteligente de Contexto:** Una función personalizada que monitorea el historial. Si este supera los 6 mensajes, un LLM resume la conversación antigua y mantiene intactos los 2 últimos mensajes para no perder el hilo inmediato.
3. **Streaming Manual:** Las respuestas se iteran y se imprimen en consola en tiempo real (token a token).

### Implementación Paso a Paso

A continuación, se detalla el script principal que levanta el asistente de inventario en la terminal.

#### 1. Importación y Configuración del Modelo
En esta sección se cargan las dependencias de LangChain y se configuran dos instancias de GPT-4.1:

* **LLM de Interacción (llm):** Configurado con `streaming=True` y temperatura 0.3. Proporciona respuestas fluidas en tiempo real con precisión técnica.
* **LLM de Utilidad (llm_util):** Configurado con `temperature=0` y sin streaming. Actúa como motor determinista para la extracción de JSON y resúmenes, garantizando datos exactos.

Las credenciales y URLs base se gestionan de forma segura mediante un archivo `.env` y la librería `python-dotenv`.
```python
import os
import re
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# #1. CARGAR CONFIGURACIÓN DESDE EL .ENV
load_dotenv()

MODEL_ID = "gpt-4.1"

# #2. CONFIGURACIÓN DE LOS MODELOS (LLM)
# Se configuran usando las llaves exactas de tu archivo .env

# LLM para la conversación (con Streaming)
llm = ChatOpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=MODEL_ID,
    temperature=0.3,
    streaming=True,
    max_tokens=300
)

# LLM para procesos de extracción y resumen (Determinista)
llm_util = ChatOpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model=MODEL_ID,
    temperature=0,
    streaming=False
)

```

#### 2. Gestión del Historial y Extracción de Datos

En esta parte el código se encarga de la memoria del chat y de transformar las palabras del usuario en datos estructurados:

* **Historial por sesión:** Se utiliza un diccionario para almacenar la conversación de cada usuario de forma independiente en la memoria RAM, permitiendo que el asistente mantenga el contexto de la charla.
* **Extracción de Inventario (`extraer_datos_inventario`):** Esta función analiza el mensaje del usuario buscando productos y cantidades. Si encuentra datos, los convierte automáticamente a un formato JSON limpio para su uso posterior en bases de datos.
* **Sincronización de contexto:** El sistema incluye una lógica de resumen que se activa al superar los 6 mensajes. Esto comprime el historial antiguo para ahorrar tokens, pero bajo una "regla de oro": nunca omitir códigos de productos, nombres ni stock, manteniendo siempre la información crítica a mano.

El proceso asegura que el asistente no "olvide" los productos mencionados y que la información técnica se mantenga siempre precisa.
```python
# #3. ESTRUCTURA PARA EL HISTORIAL
sesion_unimarc = {}

def historial_de_conversacion(sesion_id : str):
    if sesion_id not in sesion_unimarc:
        sesion_unimarc[sesion_id] = InMemoryChatMessageHistory()
    return sesion_unimarc[sesion_id]

# #4. FUNCIÓN PARA EXTRAER INFORMACIÓN DE INVENTARIO (Texto original restaurado)
def extraer_datos_inventario(texto_usuario: str) -> dict:
    """
    Analiza el texto del usuario y extrae un JSON estructurado de productos.
    """
    prompt_extraccion = (
        "Eres un experto en logística de Unimarc. "
        "Extrae los datos de inventario del siguiente texto y entrégalos "
        "EXCLUSIVAMENTE en formato JSON. No incluyas saludos ni explicaciones.\n\n"
        "Si el texto NO contiene información de inventario, responde solo: null\n\n"
        "Formato requerido:\n"
        "{\n"
        "  \"productos\": [\n"
        "    {\"nombre\": \"nombre del producto\", \"cantidad\": numero, \"unidad\": \"kg/unidades/cajas\"}\n"
        "  ]\n"
        "}\n\n"
        f"Texto: \"{texto_usuario}\"\n"
        "JSON:"
    )
    
    try:
        response = llm_util.invoke([HumanMessage(content=prompt_extraccion)])
        contenido = response.content.strip()
        
        # Limpieza de bloques de código markdown
        contenido = re.sub(r'```json|```', '', contenido).strip()

        # Búsqueda del bloque entre llaves
        match = re.search(r'\{.*\}', contenido, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"[DEBUG ERROR EXTRAER]: {e}")
        return None

```
#### 3. Prompts y Cadena de Ejecución (LCEL)

En esta sección se define la lógica de interacción y la personalidad del asistente de Unimarc:

* **Configuración del Sistema:** El prompt establece directrices estrictas: tono profesional, sin emojis, respuestas breves y un formato de lectura específico (bloques angostos con saltos de línea frecuentes). Su objetivo es mantener el foco exclusivamente en la gestión de inventario.
* **Control de Memoria Dinámica:** Se integra la función `sincronizar_contexto_stock` para optimizar el uso de tokens. Si la conversación excede los 6 mensajes, el sistema utiliza el `llm_util` para generar un resumen técnico que preserva datos críticos (códigos y stock) mientras libera espacio en la memoria.
* **Cadena de Ejecución (LCEL):** Se utiliza `RunnableWithMessageHistory` para vincular el modelo con el historial de mensajes de forma nativa. Esto permite que el asistente recuerde el contexto previo de cada sesión de usuario de manera automática y eficiente.

Esta estructura garantiza que el bot no solo responda de forma coherente, sino que siempre priorice la integridad de la información logística.
```python
# #5. Crear el prompt de conversación con el contexto del historial
# Definición de la personalidad del agente y las restricciones de formato (no emojis, saltos de línea)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente de Inventario de Unimarc. \n"
    "Ayudas a los usuarios a gestionar su inventario, responder preguntas sobre productos, y proporcionar información relevante sobre el stock y las operaciones de la tienda.\n" 
    "Tienes que ser amigable, eficiente y siempre estar dispuesto a ayudar. \n"
    "Si no sabes la respuesta a una pregunta, es mejor admitirlo que inventar una respuesta incorrecta.\n"
    "Siempre debes mantener un tono profesional y cortés en tus respuestas. \n"
    "Las respuestas deben ser breves y al punto, evitando información innecesaria. \n"
    "Si el usuario hace una pregunta que no está relacionada con el inventario o las operaciones de la tienda, debes redirigir la conversación de vuelta a temas relevantes para Unimarc.\n"
    "Recuerda que tu objetivo principal es ayudar a los usuarios a gestionar su inventario de manera efectiva y proporcionar información precisa sobre los productos y operaciones de la tienda.\n"
    "No uses emojis, manten limpio el formato de tus respuestas.\n"
    "Escribe en bloques de texto ANGOSTOS.\n"
    "Presiona 'Enter' (salto de línea) cada 8 o 10 palabras.\n"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

conversation = RunnableWithMessageHistory(
    prompt | llm,
    historial_de_conversacion,
    input_messages_key="input",
    history_messages_key="chat_history"
)

```
#### 4. Interfaz de Usuario y Motor de Streaming

En esta sección final se configura la interacción directa en la terminal y el flujo de salida de datos:

* **Respuesta en Tiempo Real (Streaming):** La función `ejecutar_chat` procesa la entrada del usuario y utiliza un bucle de *chunks* para mostrar la respuesta del modelo palabra por palabra. Esto mejora la experiencia de usuario al eliminar tiempos de espera largos.
* **Ciclo de Control:** Se implementa un bucle principal (`while`) que mantiene la sesión activa, permitiendo ingresos continuos de stock o consultas, e incluye comandos de salida (`salir`, `exit`) para finalizar la sesión de forma segura.

El resultado es una terminal logística funcional que combina el procesamiento de lenguaje natural con una gestión de datos eficiente y dinámica.
```python
# #7. FUNCIÓN DE EJECUCIÓN
def ejecutar_chat(input_text, session_id):
    sincronizar_contexto_stock(session_id)

    config = {"configurable": {"session_id": session_id}}
    
    print(f"\n[USUARIO]: {input_text}")
    print(f"[OUTPUT]: ", end="", flush=True)
    
    try:
        for chunk in conversation.stream({"input": input_text}, config=config):
            if chunk.content:
                print(chunk.content, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"\n[ERROR_LOG]: {e}")

# #8. BUCLE TERMINAL
if __name__ == "__main__":
    SID = "SYS-LOG-01"
    print(f"--- TERMINAL UNIMARC | MODELO: {MODEL_ID} ---")
    while True:
        user_input = input("[INPUT]: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            break
        if user_input.strip():
            ejecutar_chat(user_input, SID)
```
## 10. Solución de Problemas Comunes (Troubleshooting)

Al trabajar con APIs de Inteligencia Artificial y entornos virtuales, es posible que te encuentres con algunos errores comunes. Aquí detallamos cómo solucionarlos rápidamente:

### 1. Error de Autenticación o Variables de Entorno no encontradas
**Síntoma en terminal:** `KeyError: 'OPENAI_BASE_URL'` o `AuthenticationError: Incorrect API key provided`.
* **Causa:** El script no está encontrando tus credenciales.
* **Solución:** 1. Verifica que tu archivo de credenciales se llame exactamente `.env` (sin extensiones ocultas como `.env.txt`).
  2. Asegúrate de que el archivo `.env` esté en la misma carpeta desde donde estás ejecutando el script.
  3. Revisa que no haya espacios extra alrededor del signo `=` en tu archivo `.env` (ej: `GITHUB_TOKEN="tu_token"`).

### 2. Error de Librería o Módulo no encontrado
**Síntoma en terminal:** `ModuleNotFoundError: No module named 'langchain_openai'` o similares.
* **Causa:** Las dependencias no están instaladas en el entorno actual.
* **Solución:** 1. Verifica que tu entorno virtual esté activado (deberías ver `(.venv)` al inicio de la línea de tu terminal).
  2. Vuelve a instalar las dependencias ejecutando: 
     ```bash
     pip install -r requirements.txt
     ```
  3. Si el error persiste específicamente con LangChain, fuerza la instalación manual: `pip install langchain langchain-openai langchain-core`.

### 3. Límite de Tasa (Rate Limit) o Créditos Agotados
**Síntoma en terminal:** `RateLimitError: Error code: 429` o la terminal se queda "pensando" indefinidamente y lanza un error de *Timeout*.
* **Causa:** Estás haciendo demasiadas peticiones por minuto a la API o te has quedado sin saldo/cuota en tu token de GitHub Models/OpenAI.
* **Solución:** 1. Espera unos minutos antes de volver a consultar el chat.
  2. Revisa el panel de tu proveedor de API para confirmar si tienes cuota disponible en el modelo `gpt-4o`.

### 4. El Streaming se ve desordenado o no imprime bien los caracteres
**Síntoma en terminal:** Las palabras aparecen amontonadas o con símbolos extraños como `\n` impresos literalmente.
* **Causa:** Incompatibilidad de codificación (Encoding) en ciertas terminales (muy común en el CMD antiguo de Windows).
* **Solución:** 1. Te recomendamos usar terminales modernas como **Windows Terminal**, **Git Bash** o la terminal integrada de **VS Code**.
  2. Si estás en Windows, puedes forzar la codificación UTF-8 ejecutando este comando en la consola antes de iniciar Python:
     ```cmd
     chcp 65001
     ```

        
