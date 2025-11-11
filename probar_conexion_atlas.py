"""
Script para probar la conexión a MongoDB Atlas
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar ruta al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datos.configuracion.conexion_mongodb import conexion_db

def probar_conexion():
    """Prueba la conexión a MongoDB Atlas"""
    try:
        print("=" * 60)
        print("PRUEBA DE CONEXIÓN A MONGODB ATLAS")
        print("=" * 60)

        # Conectar a la base de datos
        bd = conexion_db.conectar()

        print("\n✓ Conexión exitosa!")
        print(f"✓ Base de datos: {bd.name}")

        # Probar una operación simple
        print("\nProbando operación ping...")
        resultado = bd.client.admin.command('ping')

        if resultado.get('ok') == 1:
            print("✓ Ping exitoso!")

        # Listar colecciones existentes
        print("\nColecciones existentes:")
        colecciones = bd.list_collection_names()
        if colecciones:
            for col in colecciones:
                print(f"  - {col}")
        else:
            print("  (Sin colecciones aún)")

        # Insertar un documento de prueba
        print("\nInsertando documento de prueba...")
        resultado_insert = bd['prueba_conexion'].insert_one({
            'mensaje': 'Conexión exitosa a MongoDB Atlas',
            'timestamp': datetime.now()
        })
        print(f"✓ Documento insertado con ID: {resultado_insert.inserted_id}")

        # Recuperar el documento
        print("\nRecuperando documento...")
        doc = bd['prueba_conexion'].find_one({'_id': resultado_insert.inserted_id})
        print(f"✓ Documento recuperado: {doc}")

        # Limpiar (opcional)
        print("\nLimpiando documento de prueba...")
        bd['prueba_conexion'].delete_one({'_id': resultado_insert.inserted_id})
        print("✓ Documento eliminado")

        print("\n" + "=" * 60)
        print("¡TODAS LAS PRUEBAS EXITOSAS!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error al conectar: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        return False
    finally:
        # Cerrar conexión
        conexion_db.cerrar_conexion()
        print("\n✓ Conexión cerrada")

if __name__ == "__main__":
    probar_conexion()
