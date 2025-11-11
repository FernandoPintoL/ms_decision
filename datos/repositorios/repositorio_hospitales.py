"""
Repositorio para gestión de hospitales en MongoDB.
Capa: DATOS
Responsabilidad: CRUD de hospitales, consultas específicas.
Estándares: PEP 8, Type hints, Docstrings, SOLID
"""

from typing import List, Dict, Optional, Any
from pymongo.database import Database
from pymongo.collection import Collection


class RepositorioHospitales:
    """
    Repositorio para operaciones de hospitales en MongoDB.

    Principios SOLID:
    - SRP: Solo maneja datos de hospitales
    - OCP: Extensible para nuevas consultas
    - DIP: Depende de abstracción Database
    """

    def __init__(self, base_datos: Database):
        """
        Inicializa repositorio con conexión a MongoDB.

        Args:
            base_datos: Instancia de MongoDB Database
        """
        self.db: Database = base_datos
        self.coleccion: Collection = self.db["hospitales"]

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los hospitales.

        Returns:
            Lista de hospitales

        Example:
            >>> repo = RepositorioHospitales(db)
            >>> hospitales = repo.obtener_todos()
            >>> len(hospitales)
            30
        """
        return list(self.coleccion.find({}, {"_id": 0}))

    def obtener_por_id(self, hospital_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un hospital por su ID.

        Args:
            hospital_id: ID del hospital

        Returns:
            Datos del hospital o None si no existe

        Example:
            >>> hospital = repo.obtener_por_id("HOSP001")
            >>> hospital['nombre']
            'Hospital Central'
        """
        return self.coleccion.find_one(
            {"hospital_id": hospital_id},
            {"_id": 0}
        )

    def obtener_por_cluster(
        self,
        cluster: int,
        capacidad_disponible: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene hospitales de un cluster específico.

        Args:
            cluster: Número de cluster
            capacidad_disponible: Si True, solo hospitales con capacidad

        Returns:
            Lista de hospitales del cluster

        Example:
            >>> hospitales = repo.obtener_por_cluster(0)
            >>> all(h['cluster'] == 0 for h in hospitales)
            True
        """
        filtro = {"cluster": cluster}

        if capacidad_disponible:
            filtro["$expr"] = {
                "$lt": ["$capacidad.actual", "$capacidad.maxima"]
            }

        return list(self.coleccion.find(filtro, {"_id": 0}))

    def obtener_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene hospitales con capacidad disponible.

        Returns:
            Lista de hospitales disponibles

        Example:
            >>> hospitales = repo.obtener_disponibles()
            >>> all(h['capacidad']['actual'] < h['capacidad']['maxima']
            ...     for h in hospitales)
            True
        """
        return list(self.coleccion.find(
            {
                "$expr": {
                    "$lt": ["$capacidad.actual", "$capacidad.maxima"]
                }
            },
            {"_id": 0}
        ))

    def actualizar_cluster(
        self,
        hospital_id: str,
        cluster: int
    ) -> bool:
        """
        Actualiza el cluster de un hospital.

        Args:
            hospital_id: ID del hospital
            cluster: Nuevo cluster

        Returns:
            True si se actualizó, False si no existe

        Example:
            >>> exito = repo.actualizar_cluster("HOSP001", 2)
            >>> exito
            True
        """
        resultado = self.coleccion.update_one(
            {"hospital_id": hospital_id},
            {"$set": {"cluster": cluster}}
        )
        return resultado.modified_count > 0

    def actualizar_clusters_masivo(
        self,
        clusters_map: Dict[str, int]
    ) -> int:
        """
        Actualiza clusters de múltiples hospitales.

        Args:
            clusters_map: Dict {hospital_id: cluster}

        Returns:
            Número de hospitales actualizados

        Example:
            >>> clusters = {"HOSP001": 0, "HOSP002": 1}
            >>> actualizados = repo.actualizar_clusters_masivo(clusters)
            >>> actualizados
            2
        """
        actualizados = 0
        for hospital_id, cluster in clusters_map.items():
            if self.actualizar_cluster(hospital_id, cluster):
                actualizados += 1
        return actualizados

    def contar_por_cluster(self) -> Dict[int, int]:
        """
        Cuenta hospitales por cluster.

        Returns:
            Dict {cluster: cantidad}

        Example:
            >>> conteo = repo.contar_por_cluster()
            >>> conteo
            {0: 8, 1: 6, 2: 10, 3: 6}
        """
        pipeline = [
            {"$group": {"_id": "$cluster", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        resultado = self.coleccion.aggregate(pipeline)
        return {doc["_id"]: doc["count"] for doc in resultado}
