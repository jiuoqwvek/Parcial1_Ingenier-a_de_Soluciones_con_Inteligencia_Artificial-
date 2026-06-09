import os
import json
import re
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVENTARIO_FILE = os.path.join(BASE_DIR, "inventario.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

MODEL_ID = "gpt-4.1"
BASE_URL = os.environ.get("OPENAI_BASE_URL")
API_KEY = os.environ.get("GITHUB_TOKEN")


def cargar_inventario():
    if not os.path.exists(INVENTARIO_FILE):
        inventario = {
            "productos": [
                {"sku": "SKU-ARR-001", "nombre": "Arroz", "stock": 500, "minimo": 100, "maximo": 1000},
                {"sku": "SKU-PAN-001", "nombre": "Pan", "stock": 150, "minimo": 50, "maximo": 300},
                {"sku": "SKU-LEC-001", "nombre": "Leche", "stock": 200, "minimo": 75, "maximo": 400}
            ]
        }
        with open(INVENTARIO_FILE, "w", encoding="utf-8") as f:
            json.dump(inventario, f, indent=2, ensure_ascii=False)
        return inventario

    with open(INVENTARIO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_inventario(inventario):
    with open(INVENTARIO_FILE, "w", encoding="utf-8") as f:
        json.dump(inventario, f, indent=2, ensure_ascii=False)


def crear_llm():
    if not BASE_URL or not API_KEY:
        raise ValueError("Falta OPENAI_BASE_URL o GITHUB_TOKEN en .env")
    return ChatOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_ID,
        temperature=0.3,
        streaming=False,
        max_tokens=1024,
    )


def generar_contexto(inventario):
    bloques = [
        "Inventario actual de Unimarc:",
    ]
    for producto in inventario.get("productos", []):
        bloques.append(
            f"- {producto['sku']}: {producto['nombre']} | stock {producto['stock']} | minimo {producto['minimo']} | maximo {producto['maximo']}"
        )
    return "\n".join(bloques)


def actualizar_stock_por_sku(inventario, sku, nuevo_stock):
    sku = sku.strip().upper()
    for producto in inventario.get("productos", []):
        if producto["sku"].upper() == sku or producto["nombre"].lower() == sku.lower():
            producto["stock"] = max(0, int(nuevo_stock))
            guardar_inventario(inventario)
            return producto
    return None


def buscar_producto(inventario, texto):
    texto_minuscula = texto.lower()
    for producto in inventario.get("productos", []):
        if producto["sku"].lower() in texto_minuscula or producto["nombre"].lower() in texto_minuscula:
            return producto
    return None


def construir_prompt(pregunta, inventario):
    contexto = generar_contexto(inventario)
    prompt = (
        "Eres un asistente experto en gestión de inventarios para Unimarc. "
        "Debes responder usando solo los datos del inventario actual y explicar claramente si el producto está disponible, si se puede reabastecer, "
        "o si requiere acción urgente."
        "\n\n"
        f"{contexto}\n\n"
        f"Pregunta: {pregunta}\n"
        "Responde en español de forma clara y con recomendaciones concretas."
    )
    return prompt


def hacer_pregunta(llm, pregunta, inventario):
    prompt = construir_prompt(pregunta, inventario)
    respuesta = llm.invoke([HumanMessage(content=prompt)])
    return respuesta.content.strip()


def main():
    print("\n=== Agente LLM de Inventario Unimarc ===\n")
    inventario = cargar_inventario()
    llm = crear_llm()

    while True:
        print("Opciones:")
        print("  1. Consultar inventario")
        print("  2. Sincronizar stock por SKU")
        print("  3. Ver inventario local")
        print("  0. Salir")
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            pregunta = input("Escribe tu consulta sobre inventario: ").strip()
            if not pregunta:
                print("No escribiste ninguna pregunta. Intenta de nuevo.\n")
                continue
            try:
                respuesta = hacer_pregunta(llm, pregunta, inventario)
                print("\nRespuesta del agente:\n")
                print(respuesta)
                print()
            except Exception as exc:
                print(f"Error al consultar el agente: {exc}")

        elif opcion == "2":
            sku = input("SKU o nombre del producto: ").strip()
            cantidad = input("Nuevo stock o cantidad final: ").strip()
            if not sku or not cantidad.isdigit():
                print("SKU inválido o cantidad inválida. Usa un número entero.\n")
                continue
            producto = actualizar_stock_por_sku(inventario, sku, int(cantidad))
            if producto:
                print(f"Stock actualizado: {producto['sku']} - {producto['nombre']} -> {producto['stock']} unidades\n")
            else:
                print("No se encontró el producto solicitado en el inventario.\n")

        elif opcion == "3":
            print("\nInventario local:")
            for producto in inventario.get("productos", []):
                print(
                    f"  {producto['sku']}: {producto['nombre']} | stock {producto['stock']} | minimo {producto['minimo']} | maximo {producto['maximo']}"
                )
            print()

        elif opcion == "0":
            print("Saliendo.")
            break

        else:
            print("Opción no válida. Intenta nuevamente.\n")


if __name__ == "__main__":
    main()
