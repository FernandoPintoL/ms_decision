"""
Módulo de clustering de hospitales usando K-means.
Capa: NEGOCIO / ML
Responsabilidad: Agrupar hospitales por especialidades y recomendar según necesidad.
Estándares: PEP 8, Type hints, Docstrings, SOLID
"""

from typing import Dict, List, Tuple, Any
import joblib
import numpy as np
from pathlib import Path


class ClusteringHospitales:
    """
    Clustering de hospitales usando K-means (ML No Supervisado).

    Agrupa hospitales por especialidades similares para recomendar
    el más adecuado según el tipo de emergencia.

    Principios SOLID:
    - SRP: Solo clustering de hospitales
    - OCP: Extensible para otros algoritmos de clustering
    - DIP: Depende de abstracciones (joblib)
    """

    def __init__(self, ruta_modelos: str = "modelos_ml"):
        """
        Inicializa el clusterer cargando modelo K-means.

        Args:
            ruta_modelos: Directorio donde están los modelos entrenados
        """
        self.ruta_base = Path(__file__).parent.parent.parent / ruta_modelos
        self.modelo_kmeans = None
        self.especialidades_list = None
        self.cluster_info = None
        self._cargar_modelos()

    def _cargar_modelos(self) -> None:
        """Carga modelo K-means y metadatos desde disco."""
        try:
            self.modelo_kmeans = joblib.load(self.ruta_base / "modelo_kmeans.pkl")
            self.especialidades_list = joblib.load(
                self.ruta_base / "especialidades_list.pkl"
            )
            self.cluster_info = joblib.load(self.ruta_base / "cluster_info.pkl")
            print(f"Modelo K-means cargado desde: {self.ruta_base}")
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"No se encontraron los modelos K-means en {self.ruta_base}. "
                f"Ejecuta el notebook de entrenamiento primero."
            ) from e

    def predecir_cluster(
        self,
        especialidades_hospital: Dict[str, int]
    ) -> int:
        """
        Predice a qué cluster pertenece un hospital según sus especialidades.

        Args:
            especialidades_hospital: Dict con especialidades {nombre: 1/0}

        Returns:
            int: Número de cluster (0, 1, 2, ...)

        Example:
            >>> clusterer = ClusteringHospitales()
            >>> especialidades = {
            ...     'cardiologia': 1,
            ...     'trauma': 0,
            ...     'pediatria': 0,
            ...     'ortopedia': 0,
            ...     'neurologia': 1,
            ...     'quemados': 0,
            ...     'toxicologia': 0,
            ...     'general': 0
            ... }
            >>> cluster = clusterer.predecir_cluster(especialidades)
            >>> print(f"Cluster: {cluster}")
            Cluster: 2
        """
        # Preparar features en orden correcto
        X = np.array([
            especialidades_hospital.get(esp, 0)
            for esp in self.especialidades_list
        ]).reshape(1, -1)

        # Predecir cluster
        cluster = self.modelo_kmeans.predict(X)[0]

        return int(cluster)

    def obtener_cluster_por_tipo_emergencia(
        self,
        tipo_emergencia: str
    ) -> int:
        """
        Determina qué cluster de hospitales es más adecuado para un tipo de emergencia.

        Args:
            tipo_emergencia: Tipo de incidente (ej: 'problema_cardiaco', 'trauma')

        Returns:
            int: Cluster recomendado

        Example:
            >>> clusterer = ClusteringHospitales()
            >>> cluster = clusterer.obtener_cluster_por_tipo_emergencia('problema_cardiaco')
            >>> print(f"Cluster recomendado: {cluster}")
            Cluster recomendado: 2
        """
        # Mapeo de tipo de emergencia a especialidad requerida
        mapeo_especialidad = {
            'problema_cardiaco': 'cardiologia',
            'problema_respiratorio': 'general',
            'quemadura': 'quemados',
            'fractura': 'ortopedia',
            'alergia_severa': 'general',
            'dolor_abdominal': 'general',
            'caida': 'ortopedia',
            'herida_punzante': 'trauma',
            'accidente_auto': 'trauma',
            'intoxicacion': 'toxicologia'
        }

        especialidad_requerida = mapeo_especialidad.get(
            tipo_emergencia,
            'general'
        )

        # Buscar cluster con mayor proporción de esa especialidad
        mejor_cluster = 0
        mejor_score = 0

        for cluster_id, info in self.cluster_info.items():
            if especialidad_requerida in info['especialidades']:
                # Este cluster tiene la especialidad requerida
                # Dar mayor peso si es la especialidad dominante
                score = len(info['especialidades'])  # Más especialidades = más completo
                if info['especialidades'][0] == especialidad_requerida:
                    score += 10  # Bonus si es la principal

                if score > mejor_score:
                    mejor_score = score
                    mejor_cluster = cluster_id

        return mejor_cluster

    def filtrar_hospitales_por_cluster(
        self,
        hospitales: List[Dict[str, Any]],
        cluster_objetivo: int
    ) -> List[Dict[str, Any]]:
        """
        Filtra hospitales que pertenecen a un cluster específico.

        Args:
            hospitales: Lista de hospitales con datos completos
            cluster_objetivo: Cluster deseado

        Returns:
            Lista de hospitales del cluster objetivo

        Example:
            >>> hospitales = [
            ...     {'hospital_id': 'H001', 'cluster': 0, 'nombre': 'Hospital A'},
            ...     {'hospital_id': 'H002', 'cluster': 1, 'nombre': 'Hospital B'},
            ...     {'hospital_id': 'H003', 'cluster': 0, 'nombre': 'Hospital C'},
            ... ]
            >>> filtrados = clusterer.filtrar_hospitales_por_cluster(hospitales, 0)
            >>> len(filtrados)
            2
        """
        return [
            hospital for hospital in hospitales
            if hospital.get('cluster') == cluster_objetivo
        ]

    def obtener_especialidades_cluster(self, cluster_id: int) -> List[str]:
        """
        Obtiene las especialidades dominantes de un cluster.

        Args:
            cluster_id: ID del cluster

        Returns:
            Lista de especialidades del cluster

        Example:
            >>> especialidades = clusterer.obtener_especialidades_cluster(2)
            >>> print(especialidades)
            ['cardiologia', 'neurologia']
        """
        if cluster_id not in self.cluster_info:
            return []

        return self.cluster_info[cluster_id]['especialidades']

    def obtener_hospitales_cluster(self, cluster_id: int) -> List[str]:
        """
        Obtiene los IDs de hospitales de un cluster.

        Args:
            cluster_id: ID del cluster

        Returns:
            Lista de hospital_ids

        Example:
            >>> hospitales = clusterer.obtener_hospitales_cluster(0)
            >>> print(hospitales)
            ['HOSP001', 'HOSP005', 'HOSP012']
        """
        if cluster_id not in self.cluster_info:
            return []

        return self.cluster_info[cluster_id]['hospitales']

    def obtener_info_clusters(self) -> Dict[int, Dict[str, Any]]:
        """
        Obtiene información completa de todos los clusters.

        Returns:
            Dict con info de cada cluster

        Example:
            >>> info = clusterer.obtener_info_clusters()
            >>> for cluster_id, datos in info.items():
            ...     print(f"Cluster {cluster_id}: {datos['especialidades']}")
        """
        return self.cluster_info.copy()
