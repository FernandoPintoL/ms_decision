"""
Script para iniciar el Microservicio de Decisión Médica.
Inicia MongoDB y el servidor GraphQL automáticamente.
Multiplataforma: Windows, Mac, Linux
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path


def imprimir_banner():
    """Imprime banner de inicio."""
    print("\n" + "=" * 60)
    print("  MICROSERVICIO DE DECISION MEDICA")
    print("  Iniciando Backend...")
    print("=" * 60 + "\n")


def verificar_entorno_virtual():
    """Verifica que estamos en el entorno virtual."""
    print("[1/4] Verificando entorno virtual...")

    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("  ERROR: No estas en el entorno virtual")
        print("\n  Por favor ejecuta primero:")
        if platform.system() == "Windows":
            print("    .venv\\Scripts\\activate")
        else:
            print("    source .venv/bin/activate")
        print("\n  Luego ejecuta:")
        print("    python iniciar_servidor.py")
        return False

    print("  OK Entorno virtual activo")
    return True


def verificar_mongodb():
    """Verifica si MongoDB está corriendo."""
    print("\n[2/4] Verificando MongoDB...")

    try:
        # Intentar conectar a MongoDB
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError

        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.server_info()
        client.close()

        print("  OK MongoDB corriendo en puerto 27017")
        return True

    except ServerSelectionTimeoutError:
        print("  ERROR: MongoDB no esta corriendo")
        print("\n  Inicia MongoDB manualmente:")

        if platform.system() == "Windows":
            print('    "C:\\Program Files\\MongoDB\\Server\\8.2\\bin\\mongod.exe" --dbpath "D:/mongodb_data/db" --port 27017')
        else:
            print("    mongod --dbpath /data/db --port 27017")

        print("\n  O presiona Enter para que intente iniciarlo automaticamente...")
        input()
        return iniciar_mongodb()

    except ImportError:
        print("  ERROR: pymongo no esta instalado")
        print("\n  Ejecuta: pip install pymongo")
        return False


def iniciar_mongodb():
    """Intenta iniciar MongoDB automáticamente."""
    print("\n  Intentando iniciar MongoDB...")

    try:
        if platform.system() == "Windows":
            # Rutas comunes de MongoDB en Windows
            rutas_mongodb = [
                r"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe",
                r"C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe",
                r"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe",
            ]

            mongod_path = None
            for ruta in rutas_mongodb:
                if os.path.exists(ruta):
                    mongod_path = ruta
                    break

            if mongod_path:
                # Iniciar MongoDB en segundo plano
                subprocess.Popen(
                    [mongod_path, "--dbpath", "D:/mongodb_data/db", "--port", "27017"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                print("  OK MongoDB iniciado")
                print("  Esperando 3 segundos para que inicie...")
                time.sleep(3)
                return True
            else:
                print("  ERROR: No se encontro mongod.exe")
                return False
        else:
            # Linux/Mac
            subprocess.Popen(
                ["mongod", "--dbpath", "/data/db", "--port", "27017"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("  OK MongoDB iniciado")
            time.sleep(3)
            return True

    except Exception as e:
        print(f"  ERROR: No se pudo iniciar MongoDB: {e}")
        return False


def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas."""
    print("\n[3/4] Verificando dependencias...")

    dependencias = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'strawberry': 'Strawberry GraphQL',
        'pymongo': 'PyMongo',
    }

    faltantes = []

    for modulo, nombre in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(nombre)

    if faltantes:
        print(f"  ERROR: Faltan dependencias: {', '.join(faltantes)}")
        print("\n  Ejecuta: pip install -r requirements.txt")
        return False

    print("  OK Todas las dependencias instaladas")
    return True


def iniciar_servidor():
    """Inicia el servidor GraphQL."""
    print("\n[4/4] Iniciando servidor GraphQL...\n")
    print("=" * 60)
    print("  SERVIDOR LISTO")
    print("=" * 60)
    print("\n  API GraphQL:     http://localhost:8000/graphql")
    print("  GraphiQL IDE:    http://localhost:8000/graphql (navegador)")
    print("  Health Check:    http://localhost:8000/health")
    print("\n  Para detener el servidor presiona CTRL+C")
    print("=" * 60 + "\n")

    try:
        # Iniciar servidor con uvicorn
        import uvicorn

        uvicorn.run(
            "presentacion.servidor:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("  SERVIDOR DETENIDO")
        print("=" * 60 + "\n")
        sys.exit(0)

    except Exception as e:
        print(f"\n  ERROR: No se pudo iniciar el servidor: {e}")
        sys.exit(1)


def main():
    """Función principal."""
    imprimir_banner()

    # Verificaciones
    if not verificar_entorno_virtual():
        sys.exit(1)

    if not verificar_mongodb():
        sys.exit(1)

    if not verificar_dependencias():
        sys.exit(1)

    # Iniciar servidor
    iniciar_servidor()


if __name__ == "__main__":
    main()
