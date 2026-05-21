"""
Ejemplos de Ejecución
Demuestra planificación, memoria, y decisiones adaptativas
"""

import logging
from agent import AgenteUnimarc

# Configurar logging
logging.basicConfig(
    level="INFO",
    format="%(message)s"
)
logger = logging.getLogger(__name__)


def ejemplo_1_pedido_exitoso():
    """
    Ejemplo 1: Pedido con stock disponible.
    Demuestra: decisión adaptativa, escritura, memoria.
    """
    print("\n" + "="*70)
    print("EJEMPLO 1: Pedido Exitoso (Stock Disponible)")
    print("="*70)
    
    agente = AgenteUnimarc()
    
    resultado = agente.procesar_pedido_adaptativo(
        cliente="Supermercado Central",
        items=[
            {"sku": "SKU-ARR-001", "cantidad": 50},
            {"sku": "SKU-LEC-001", "cantidad": 30}
        ]
    )
    
    print(f"Resultado: {resultado['decision']}")
    print()


def ejemplo_2_pedido_stock_insuficiente():
    """
    Ejemplo 2: Pedido sin stock suficiente.
    Demuestra: decisión adaptativa que cambia según condición.
    """
    print("\n" + "="*70)
    print("EJEMPLO 2: Pedido con Stock Insuficiente")
    print("="*70)
    
    agente = AgenteUnimarc()
    
    # Intentar pedir más de lo disponible
    resultado = agente.procesar_pedido_adaptativo(
        cliente="Minimarket Local",
        items=[
            {"sku": "SKU-PAN-001", "cantidad": 500}  # Disponible: 150
        ]
    )
    
    print(f"Resultado: {resultado['decision']}")
    print()


def ejemplo_3_reposicion():
    """
    Ejemplo 3: Planificación adaptativa de reposición.
    Demuestra: multi-etapa, agrupar por proveedor, razonamiento.
    """
    print("\n" + "="*70)
    print("EJEMPLO 3: Reposición Adaptativa")
    print("="*70)
    
    agente = AgenteUnimarc()
    
    resultado = agente.reposicion_adaptativa()
    
    print(f"Resultado: {resultado['ordenes_generadas']} órdenes generadas")
    print()


def ejemplo_4_memoria_y_patrones():
    """
    Ejemplo 4: Memoria corto/largo plazo en acción.
    Demuestra: cómo el agente aprende y recuerda.
    """
    print("\n" + "="*70)
    print("EJEMPLO 4: Memoria Corto y Largo Plazo")
    print("="*70)
    
    agente = AgenteUnimarc()
    
    # Procesar varios pedidos
    agente.procesar_pedido_adaptativo(
        cliente="Cliente A",
        items=[{"sku": "SKU-ARR-001", "cantidad": 10}]
    )
    
    agente.procesar_pedido_adaptativo(
        cliente="Cliente B",
        items=[{"sku": "SKU-PAN-001", "cantidad": 5}]
    )
    
    # Generar reporte que muestra memoria
    print("\n" + "-"*70)
    print("Generando reporte con información de memoria:")
    print("-"*70)
    
    agente.generar_reporte()
    print()


def ejemplo_5_flujo_completo():
    """
    Ejemplo 5: Flujo completo con múltiples decisiones.
    Demuestra: la orquestación de todo el sistema.
    """
    print("\n" + "="*70)
    print("EJEMPLO 5: Flujo Completo del Sistema")
    print("="*70)
    
    agente = AgenteUnimarc()
    
    print("\n[FASE 1] Procesando pedidos...")
    agente.procesar_pedido_adaptativo(
        cliente="Carrefour",
        items=[
            {"sku": "SKU-ARR-001", "cantidad": 100},
            {"sku": "SKU-LEC-001", "cantidad": 50}
        ]
    )
    
    print("\n[FASE 2] Evaluando reposición...")
    agente.reposicion_adaptativa()
    
    print("\n[FASE 3] Generando reporte final...")
    agente.generar_reporte()
    print()


def menu_interactivo():
    """Menú para ejecutar ejemplos"""
    while True:
        print("\n" + "="*70)
        print("🤖 AGENTE INTELIGENTE UNIMARC - EJEMPLOS")
        print("="*70)
        print("1. Pedido exitoso (stock disponible)")
        print("2. Pedido sin stock")
        print("3. Reposición adaptativa")
        print("4. Memoria corto/largo plazo")
        print("5. Flujo completo del sistema")
        print("6. Ejecutar todo")
        print("0. Salir")
        print("-"*70)
        
        opcion = input("Selecciona opción: ").strip()
        
        if opcion == "1":
            ejemplo_1_pedido_exitoso()
        elif opcion == "2":
            ejemplo_2_pedido_stock_insuficiente()
        elif opcion == "3":
            ejemplo_3_reposicion()
        elif opcion == "4":
            ejemplo_4_memoria_y_patrones()
        elif opcion == "5":
            ejemplo_5_flujo_completo()
        elif opcion == "6":
            ejemplo_1_pedido_exitoso()
            ejemplo_2_pedido_stock_insuficiente()
            ejemplo_3_reposicion()
            ejemplo_4_memoria_y_patrones()
            ejemplo_5_flujo_completo()
        elif opcion == "0":
            print("\n👋 Hasta luego!\n")
            break
        else:
            print("❌ Opción no válida")


if __name__ == "__main__":
    # Ejecutar demo automática si se pasa --auto
    import sys
    
    if "--auto" in sys.argv or "auto" in sys.argv:
        ejemplo_1_pedido_exitoso()
        ejemplo_2_pedido_stock_insuficiente()
        ejemplo_3_reposicion()
        ejemplo_4_memoria_y_patrones()
        ejemplo_5_flujo_completo()
    else:
        menu_interactivo()
