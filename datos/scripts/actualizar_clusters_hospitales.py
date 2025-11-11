"""
Script para actualizar clusters de hospitales en MongoDB.
Lee hospitales_con_clusters.csv y actualiza la BD.
Capa: DATOS
Responsabilidad: Sincronizar clusters de K-means con MongoDB.
Estándares: PEP 8, Type hints, Docstrings
"""

import pandas as pd
from pathlib import Path
import sys

# Agregar rutas al path
ruta_base = Path(__file__).parent.parent.parent
sys.path.append(str(ruta_base))

from datos.configuracion.conexion_mongodb import ConexionMongoDB
from datos.repositorios.repositorio_hospitales import RepositorioHospitales


def actualizar_clusters() -> None:
    """
    Actualiza clusters de hospitales desde CSV a MongoDB.

    Lee hospitales_con_clusters.csv generado por el notebook
    de K-means y actualiza la colección hospitales.
    """
    print("=" * 60)
    print("ACTUALIZACION DE CLUSTERS EN MONGODB")
    print("=" * 60)

    # 1. Conectar a MongoDB
    print("\n[1/4] Conectando a MongoDB...")
    conexion = ConexionMongoDB()
    db = conexion.conectar(
        host="localhost",
        puerto=27017,
        nombre_bd="servicio_decision"
    )
    repo = RepositorioHospitales(db)
    print("   # Conexion exitosa")

    # 2. Leer CSV con clusters
    print("\n[2/4] Leyendo hospitales_con_clusters.csv...")
    ruta_csv = ruta_base / "archivos_csv" / "hospitales_con_clusters.csv"

    if not ruta_csv.exists():
        print(f"\n   ERROR: No se encontro {ruta_csv}")
        print("   Ejecuta el notebook entrenar_kmeans.ipynb primero.")
        return

    df = pd.read_csv(ruta_csv)
    print(f"   # Leidos {len(df)} hospitales")

    # 3. Preparar mapeo hospital_id -> cluster
    print("\n[3/4] Preparando actualizacion...")
    clusters_map = {}

    for _, fila in df.iterrows():
        hospital_id = fila['hospital_id']
        cluster = int(fila['cluster'])
        clusters_map[hospital_id] = cluster

    print(f"   # {len(clusters_map)} hospitales para actualizar")

    # 4. Actualizar en MongoDB
    print("\n[4/4] Actualizando clusters en MongoDB...")
    actualizados = repo.actualizar_clusters_masivo(clusters_map)

    print(f"   # {actualizados} hospitales actualizados exitosamente")

    # 5. Verificar conteo por cluster
    print("\n" + "=" * 60)
    print("VERIFICACION - HOSPITALES POR CLUSTER")
    print("=" * 60)

    conteo = repo.contar_por_cluster()
    total = 0

    for cluster_id in sorted(conteo.keys()):
        cantidad = conteo[cluster_id]
        total += cantidad
        print(f"Cluster {cluster_id}: {cantidad} hospitales")

    print("-" * 60)
    print(f"TOTAL:      {total} hospitales")
    print("=" * 60)

    print("\n# Actualizacion completada exitosamente!\n")


if __name__ == "__main__":
    try:
        actualizar_clusters()
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
