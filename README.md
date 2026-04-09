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

## 8. Configuración Avanzada: Memoria de Resumen y Streaming

Para que la experiencia del usuario sea óptima, hemos configurado nuestro Agente con dos capacidades clave utilizando la API de OpenAI y LangChain:

1. **Streaming (Tiempo real):** Las respuestas se generan palabra por palabra, eliminando los tiempos de espera largos.
2. **ConversationSummaryBufferMemory:** Una memoria avanzada que resume el historial antiguo de la conversación (para ahorrar tokens y no perder el contexto general) y mantiene intactos los últimos mensajes (para que la IA no se pierda en el tema inmediato).

### Implementación en el Código

En el archivo principal (`solucion_unimarc.ipynb`), la configuración se realiza de la siguiente manera:

```python
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 1. Configuramos el motor de la IA con Streaming activado
llm = ChatOpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("GITHUB_TOKEN"),
    model="gpt-4o",
    streaming=True, # Permite ver la respuesta palabra por palabra
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0.2 # Temperatura baja para mantener precisión en datos de stock
)

# 2. Inicializamos la Memoria Avanzada (Resumen + Buffer reciente)
# max_token_limit controla la ventana de mensajes literales. 
# Si se supera, los mensajes más antiguos se comprimen en un resumen.
memoria_avanzada = ConversationSummaryBufferMemory(
    llm=llm, 
    max_token_limit=300, 
    return_messages=True
)

# 3. Creamos la Cadena de Conversación
agente_unimarc = ConversationChain(
    llm=llm,
    memory=memoria_avanzada,
    verbose=False
)
