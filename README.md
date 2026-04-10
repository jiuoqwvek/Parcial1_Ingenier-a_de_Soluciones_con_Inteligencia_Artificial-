# Proyecto: Sincronización Inteligente de Inventario (Caso: Unimarc)

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
2.  **Python 3.13:** El proyecto requiere esta versión específica para asegurar la compatibilidad con LangChain.
    * [Descargar Python 3.13 aquí](https://www.python.org/downloads/)
3.  **GitHub Token (Access Models):** Este proyecto consume modelos de **GitHub Marketplace**.
    * Genera tu **Personal Access Token (classic)** aquí: [GitHub Settings - Tokens](https://github.com/settings/tokens).
    * Puedes explorar los modelos disponibles en: [GitHub Models](https://github.com/marketplace/models).
4.  **LangSmith API Key:** Necesaria para el rastreo y observabilidad de la IA.
    * Regístrate y obtén tu llave en: [LangSmith Dashboard](https://smith.langchain.com/).

## 5. Clonar repositorio
Sigue estos pasos en tu terminal:
```bash
# 1. Clonar tu repositorio en la terminal de VS Code
git clone https://github.com/TU-USUARIO/Parcial1_Ingenier-a_de_Soluciones_con_Inteligencia_Artificial.git
# 2. Utilizar comando cd para ingresar a la carpeta
cd Parcial1_Ingenier-a_de_Soluciones_con_Inteligencia_Artificial-
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
Crea un nuevo archivo .env para ejecutar la IA
Sigue estos pasos en la terminal:
```bash
# Copiar el archivo de ejemplo
cp .env.example .env
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
Utilizamos `ChatOpenAI` configurado con `streaming=True` para permitir la respuesta en tiempo real.

```python
import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# #1. Cargar variables de entorno
# Carga las credenciales y configuraciones desde el archivo .env para proteger datos sensibles
load_dotenv()

# #2. Configurar el modelo de lenguaje y la sesión de chat openai
# Se inicializa el modelo GPT-4o a través de la interfaz de ChatOpenAI
llm = ChatOpenAI(
    # Punto de enlace de la API (en este caso usando el proxy de GitHub Models)
    base_url=os.environ["OPENAI_BASE_URL"],

    # Token de autenticación obtenido de las variables de entorno
    api_key=os.environ["GITHUB_TOKEN"],

    # Modelo de última generación seleccionado para el procesamiento de lenguaje natural
    model="gpt-4o",

    # Grado de creatividad (0.7 permite respuestas fluidas y naturales sin perder coherencia)
    temperature=0.7,

    # Habilitación de streaming para recibir la respuesta fragmento a fragmento en tiempo real
    streaming=True,

    # Límite máximo de tokens para la generación de la respuesta
    max_tokens=4096,
    
    # Configuración de muestreo por núcleo para mayor estabilidad en la calidad de salida
    top_p=1
)
```

#### 2. Gestión del Historial y Lógica de Resumen
Creamos un diccionario para almacenar las sesiones y una función que previene el desbordamiento de tokens resumiendo los mensajes más antiguos.

```python
# #3. Crear una estructura para almacenar el historial de conversaciones por sesión
# Se utiliza un diccionario para persistir la memoria de diferentes usuarios en la RAM del servidor
sesion_unimarc = {}

def historial_de_conversacion(sesion_id : str):
    # Si el ID de sesión no existe, se crea una nueva instancia de historial en memoria
    if sesion_id not in sesion_unimarc:
        sesion_unimarc[sesion_id] = InMemoryChatMessageHistory()
    return sesion_unimarc[sesion_id]

# #4. Función para sincronizar el contexto del historial de conversación, resumiendo si es necesario(VERSIÓN OPTIMIZADA)
def sincronizar_contexto_stock(sesion_id: str, max_mensajes=6):
    """
    Gestiona el límite de tokens mediante una estrategia de resumen.
    Cuando se supera el umbral, se comprimen los mensajes antiguos manteniendo 
    los datos críticos de inventario.
    """
    historial = historial_de_conversacion(sesion_id)

    if len(historial.messages) > max_mensajes:
        # Se separan los mensajes para resumir el pasado y mantener fresca la interacción inmediata
        mensajes_a_resumir = historial.messages[:-2]
        recientes = historial.messages[-2:]

        # Transformación del historial de objetos a texto plano para el procesamiento del LLM
        conversation_text = ""
        for msj in mensajes_a_resumir:
            role = "Usuario" if msj.type == "human" else "Asistente"
            conversation_text += f"{role}: {msj.content}\n"
        
        # Prompt de ingeniería de alta precisión para evitar pérdida de entidades (códigos/stock)
        prompt_resumen = (
            "Eres un experto en logística de Unimarc. Resume la siguiente conversación. "
            "REGLA DE ORO: No omitas códigos de productos, nombres de artículos ni cantidades de stock. "
            "Resume el resto en máximo 2 líneas de forma técnica.\n\n"
            f"Historial a resumir:\n{conversation_text}"
        )

        # Generación del resumen técnico optimizado en tokens
        summary_response = llm.invoke(prompt_resumen, max_tokens=150)
        summary = summary_response.content
        
        # Actualización del historial: Se limpia el exceso y se reinserta el resumen como contexto base
        historial.clear()
        historial.add_ai_message(f"[MEMORIA DE STOCK]: {summary}")
        historial.messages.extend(recientes)
```
#### 3. Prompts y Cadena de Ejecución (LCEL)
Definimos la personalidad del Asistente de Unimarc y vinculamos el prompt con el historial utilizando `RunnableWithMessageHistory`.

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

# Construcción de la cadena con soporte nativo para gestión de historial por sesión
conversation = RunnableWithMessageHistory(
    prompt | llm,
    historial_de_conversacion,
    input_messages_key="input",
    history_messages_key="chat_history"
)
```
#### 4. Motor de Streaming y Terminal de Usuario
Finalmente, creamos la interfaz de terminal interactiva que ejecuta el ciclo de chat, procesando los *chunks* de texto a medida que llegan.

```python
# #6. Función para ejecutar la conversación, sincronizando el contexto y mostrando la respuesta en tiempo real
def ejecutar_chat(input_text, session_id):
    # Ejecución de la lógica de resumen preventivo
    sincronizar_contexto_stock(session_id)
    
    config = {"configurable": {"session_id": session_id}}
    
    # Visualización clara de la interacción en la terminal
    print (f"[USUARIO]: {input_text}")
    print(f"[OUTPUT]: ", end="", flush=True)
    
    try:
        # Implementación de streaming para mejorar la fluidez de la respuesta
        for chunk in conversation.stream({"input": input_text}, config=config):
            print(chunk.content, end="", flush=True)
        print("\n")
    except Exception as e:
        # Manejo de excepciones para evitar el cierre inesperado del programa
        print(f"\n[ERROR_LOG]: {e}")

# #7. Simulación de una sesión de chat en la terminal
id_actual = "SYS-LOG-01"
print(f"TERMINAL DE GESTIÓN UNIMARC | SESIÓN: {id_actual}")
print("-" * 50)

# Bucle principal de ejecución del asistente
while True:
    user_input = input("[INPUT]: ")
    
    # Control de salida de la aplicación
    if user_input.lower() in ["exit", "quit", "salir"]:
        print("[SISTEMA]: Sesión finalizada.")
        break
    
    # Procesamiento solo de entradas con contenido
    if user_input.strip():
        ejecutar_chat(user_input, id_actual)
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

        
