# Proyecto: Sincronización Inteligente de Inventario (Caso: Unimarc)

---

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Jupyter Notebook](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)
![LangChain](https://img.shields.io/badge/LangChain-AI-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-black.svg)

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


## 4. Clonar repositorio

```bash
# 1. Clonar tu repositorio en la terminal de VS Code
git clone https://github.com/TU-USUARIO/Parcial1_Ingenier-a_de_Soluciones_con_Inteligencia_Artificial.git
# 2. Utilizar comando cd para ingresar a la carpeta
cd Parcial1_Ingenier-a_de_Soluciones_con_Inteligencia_Artificial-
```

## 5. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

## 6. Instalar Dependencias

```bash
#  Necesario tener archivo de requirements.txt incluido en la carpeta
pip install -r requirements.txt
```

## 7. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
OPENAI_BASE_URL="https://models.inference.ai.azure.com"
GITHUB_BASE_URL="https://models.inference.ai.azure.com"
OPENAI_EMBEDDINGS_URL="https://models.github.ai/inference"
GITHUB_TOKEN="tu_github_token_aqui"
LANGSMITH_TRACING="true"
LANGSMITH_API_KEY="tu_langsmith_api_key_aqui"
LANGSMITH_PROJECT="ingenieria_soluciones_con_ia"
```

## 8. Configuración Avanzada: Memoria Dinámica, Sesiones y Streaming

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

# Cargar variables de entorno
load_dotenv()

# Configurar el modelo de lenguaje y la sesión de chat
llm = ChatOpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["GITHUB_TOKEN"],
    model="gpt-4o",
    temperature=0.7,
    streaming=True,
    max_tokens=4096,
    top_p=1
)

#### 2. Gestión del Historial y Lógica de Resumen
Creamos un diccionario para almacenar las sesiones y una función que previene el desbordamiento de tokens resumiendo los mensajes más antiguos.

```python
# Estructura para almacenar el historial de conversaciones por sesión
sesion_unimarc = {}

def historial_de_conversacion(sesion_id: str):
    if sesion_id not in sesion_unimarc:
        sesion_unimarc[sesion_id] = InMemoryChatMessageHistory()
    return sesion_unimarc[sesion_id]

# Función para sincronizar el contexto del historial (Resumen Dinámico)
def sincronizar_contexto_stock(sesion_id: str, max_mensajes=6):
    historial = historial_de_conversacion(sesion_id)

    # Si hay más de 6 mensajes, resumimos los más antiguos
    if len(historial.messages) > max_mensajes:
        mensajes_a_resumir = historial.messages[:-2] # Tomamos todos menos los 2 últimos
        
        conversation_text = ""
        for msj in mensajes_a_resumir:
            role = "Usuario" if msj.type == "human" else "Asistente"
            conversation_text += f"{role}: {msj.content}\n"
        
        # Pedimos al LLM que resuma
        summary_response = llm.invoke(f"Resume esta conversación de inventario en 2 líneas:\n{conversation_text}")
        summary = summary_response.content
        
        # Guardamos los 2 últimos mensajes para mantener la vigencia
        recent_messages = historial.messages[-2:]
        historial.clear()
        
        # Inyectamos el resumen y volvemos a colocar los mensajes recientes
        historial.add_ai_message(f"[RESUMEN]: {summary}")
        historial.messages.extend(recent_messages)

        
