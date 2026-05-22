"""
Script para aprobar o rechazar órdenes de reposición
Simula lo que pasaría cuando el admin hace click en los botones del correo
"""

import sys
import os

# Agregar la carpeta padre (agente_correos) al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orden_manager import gestor_ordenes

def listar_ordenes_pendientes():
    """Muestra todas las órdenes pendientes"""
    ordenes = gestor_ordenes.obtener_ordenes_pendientes()
    
    if not ordenes:
        print("\n[INFO] No hay órdenes pendientes")
        return
    
    print("\n" + "="*70)
    print("ORDENES PENDIENTES DE APROBACION")
    print("="*70)
    
    for i, orden in enumerate(ordenes, 1):
        print(f"\n{i}. Orden: {orden['orden_id']}")
        print(f"   Cantidad: {orden['cantidad_total']} unidades")
        print(f"   Productos: {len(orden['productos'])}")
        print(f"   Fecha: {orden['fecha_creacion']}")
        print(f"   Token: {orden['token']}")
    
    print("\n" + "="*70)


def aprobar_orden_interactivo():
    """Permite aprobar una orden ingresando el token"""
    print("\n" + "="*70)
    print("APROBAR ORDEN DE REPOSICION")
    print("="*70)
    
    token = input("\nIngresa el TOKEN de la orden a aprobar: ").strip()
    
    if not token:
        print("[ERROR] Token requerido")
        return
    
    resultado = gestor_ordenes.aprobar_orden(token)
    
    print("\n" + "="*70)
    if resultado['exito']:
        print("[OK] Orden aprobada exitosamente!")
        print(f"  Mensaje: {resultado['mensaje']}")
        print(f"  Orden ID: {resultado['orden']['orden_id']}")
        print(f"  Estado: {resultado['orden']['estado']}")
        print(f"  Fecha de resolucion: {resultado['orden']['fecha_resolucion']}")
    else:
        print("[ERROR]", resultado['mensaje'])
    print("="*70)


def rechazar_orden_interactivo():
    """Permite rechazar una orden ingresando el token y razon"""
    print("\n" + "="*70)
    print("RECHAZAR ORDEN DE REPOSICION")
    print("="*70)
    
    token = input("\nIngresa el TOKEN de la orden a rechazar: ").strip()
    
    if not token:
        print("[ERROR] Token requerido")
        return
    
    razon = input("Ingresa la razon del rechazo (opcional): ").strip()
    
    resultado = gestor_ordenes.rechazar_orden(token, razon)
    
    print("\n" + "="*70)
    if resultado['exito']:
        print("[OK] Orden rechazada exitosamente!")
        print(f"  Mensaje: {resultado['mensaje']}")
        print(f"  Orden ID: {resultado['orden']['orden_id']}")
        print(f"  Estado: {resultado['orden']['estado']}")
        if razon:
            print(f"  Razon: {razon}")
        print(f"  Fecha de resolucion: {resultado['orden']['fecha_resolucion']}")
    else:
        print("[ERROR]", resultado['mensaje'])
    print("="*70)


def menu_interactivo():
    """Menu principal para gestionar órdenes"""
    while True:
        print("\n" + "="*70)
        print("GESTOR DE ORDENES DE REPOSICION")
        print("="*70)
        print("1. Listar ordenes pendientes")
        print("2. Aprobar una orden")
        print("3. Rechazar una orden")
        print("0. Salir")
        print("-"*70)
        
        opcion = input("Selecciona opcion: ").strip()
        
        if opcion == "1":
            listar_ordenes_pendientes()
        elif opcion == "2":
            aprobar_orden_interactivo()
        elif opcion == "3":
            rechazar_orden_interactivo()
        elif opcion == "0":
            print("\nSaliendo...\n")
            break
        else:
            print("[ERROR] Opcion no valida")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo comando directo
        # python gestor_ordenes.py listar
        # python gestor_ordenes.py aprobar TOKEN
        # python gestor_ordenes.py rechazar TOKEN "RAZON"
        comando = sys.argv[1]
        
        if comando == "listar":
            listar_ordenes_pendientes()
        elif comando == "aprobar" and len(sys.argv) > 2:
            token = sys.argv[2]
            resultado = gestor_ordenes.aprobar_orden(token)
            print("\n" + "="*70)
            if resultado['exito']:
                print("[OK]", resultado['mensaje'])
            else:
                print("[ERROR]", resultado['mensaje'])
            print("="*70)
        elif comando == "rechazar" and len(sys.argv) > 2:
            token = sys.argv[2]
            razon = sys.argv[3] if len(sys.argv) > 3 else ""
            resultado = gestor_ordenes.rechazar_orden(token, razon)
            print("\n" + "="*70)
            if resultado['exito']:
                print("[OK]", resultado['mensaje'])
            else:
                print("[ERROR]", resultado['mensaje'])
            print("="*70)
        else:
            print("Uso: python gestor_ordenes.py [listar|aprobar|rechazar] [TOKEN]")
    else:
        # Modo interactivo
        menu_interactivo()
