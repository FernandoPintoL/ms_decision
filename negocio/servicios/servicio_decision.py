"""
Servicio de decisión médica integrado.
Capa: NEGOCIO / SERVICIOS
Responsabilidad: Orquestar ML supervisado + no supervisado + repositorios.
Estándares: PEP 8, Type hints, Docstrings, SOLID
"""

from typing import Dict, List, Tuple, Any, Optional
from pymongo.database import Database
import math

from negocio.ml.prediccion_severidad import PredictorSeveridad
from negocio.ml.clustering_hospitales import ClusteringHospitales
from datos.repositorios.repositorio_hospitales import RepositorioHospitales

# Importación condicional de CNN (Deep Learning)
try:
    from negocio.ml.clasificador_imagenes import ClasificadorImagenes
    CNN_DISPONIBLE = True
except (ImportError, Exception) as e:
    CNN_DISPONIBLE = False
    print(f"⚠ CNN no disponible: {str(e)}")


class ServicioDecision:
    """
    Servicio principal de decisión médica.

    Integra:
    - Random Forest para severidad
    - K-means para clustering de hospitales
    - Repositorios para acceso a datos

    Principios SOLID:
    - SRP: Solo orquesta decisiones médicas
    - OCP: Extensible para nuevos modelos ML
    - DIP: Depende de abstracciones (PredictorSeveridad, ClusteringHospitales)
    """

    def __init__(self, base_datos: Database):
        """
        Inicializa servicio con modelos ML y repositorios.

        Args:
            base_datos: Instancia de MongoDB Database
        """
        self.predictor = PredictorSeveridad()
        self.clusterer = ClusteringHospitales()
        self.repo_hospitales = RepositorioHospitales(base_datos)

        # Inicializar CNN (Deep Learning) si está disponible
        if CNN_DISPONIBLE:
            try:
                self.clasificador_imagenes = ClasificadorImagenes()
            except Exception as e:
                self.clasificador_imagenes = None
                print(f"Advertencia: CNN no pudo cargarse - {str(e)}")
        else:
            self.clasificador_imagenes = None

    def evaluar_paciente(
        self,
        datos_paciente: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evalúa un paciente y determina severidad usando Random Forest.

        Args:
            datos_paciente: Datos del paciente con signos vitales

        Returns:
            Dict con severidad, probabilidades y recomendación

        Example:
            >>> servicio = ServicioDecision(db)
            >>> datos = {
            ...     'edad': 65,
            ...     'sexo': 'M',
            ...     'presion_sistolica': 180,
            ...     'presion_diastolica': 110,
            ...     'frecuencia_cardiaca': 120,
            ...     'temperatura': 38.5,
            ...     'saturacion_oxigeno': 88,
            ...     'nivel_dolor': 9,
            ...     'tipo_incidente': 'problema_cardiaco',
            ...     'tiempo_desde_incidente': 15
            ... }
            >>> resultado = servicio.evaluar_paciente(datos)
            >>> resultado['severidad']
            'crítico'
            >>> resultado['requiere_traslado']
            True
        """
        # 1. Predecir severidad con Random Forest
        severidad, probabilidades = self.predictor.predecir(datos_paciente)

        # 2. Determinar si requiere traslado
        requiere_traslado = severidad in ['crítico', 'alto']

        # 3. Calcular confianza de la predicción
        max_prob = max(probabilidades.values())

        return {
            'severidad': severidad,
            'probabilidades': probabilidades,
            'confianza': round(max_prob * 100, 2),
            'requiere_traslado': requiere_traslado,
            'tipo_incidente': datos_paciente.get('tipo_incidente', 'desconocido')
        }

    def recomendar_hospitales(
        self,
        datos_paciente: Dict[str, Any],
        ubicacion_paciente: Dict[str, float],
        top_n: int = 5
    ) -> Dict[str, Any]:
        """
        Recomienda hospitales usando severidad + K-means + distancia GPS.

        Flujo:
        1. Predecir severidad (Random Forest)
        2. Determinar cluster adecuado (K-means)
        3. Filtrar hospitales del cluster con capacidad
        4. Calcular distancias GPS
        5. Ordenar y retornar TOP N

        Args:
            datos_paciente: Datos del paciente
            ubicacion_paciente: Dict con 'latitud' y 'longitud'
            top_n: Número de hospitales a recomendar (default: 5)

        Returns:
            Dict con evaluación y hospitales recomendados

        Example:
            >>> ubicacion = {'latitud': -12.0464, 'longitud': -77.0428}
            >>> recomendacion = servicio.recomendar_hospitales(
            ...     datos_paciente,
            ...     ubicacion
            ... )
            >>> len(recomendacion['hospitales_recomendados'])
            5
            >>> recomendacion['hospitales_recomendados'][0]['distancia_km']
            2.3
        """
        # 1. Evaluar severidad
        evaluacion = self.evaluar_paciente(datos_paciente)

        # 2. Si no requiere traslado, retornar evaluación sin hospitales
        if not evaluacion['requiere_traslado']:
            return {
                'evaluacion': evaluacion,
                'hospitales_recomendados': [],
                'mensaje': 'Severidad baja/media. Atención in situ recomendada.'
            }

        # 3. Determinar cluster adecuado usando K-means
        tipo_emergencia = datos_paciente.get('tipo_incidente', 'general')
        cluster_objetivo = self.clusterer.obtener_cluster_por_tipo_emergencia(
            tipo_emergencia
        )

        # 4. Obtener especialidades del cluster
        especialidades_cluster = self.clusterer.obtener_especialidades_cluster(
            cluster_objetivo
        )

        # 5. Consultar hospitales del cluster con capacidad disponible
        hospitales_disponibles = self.repo_hospitales.obtener_por_cluster(
            cluster=cluster_objetivo,
            capacidad_disponible=True
        )

        # 6. Si no hay hospitales en el cluster, buscar en todos
        if not hospitales_disponibles:
            hospitales_disponibles = self.repo_hospitales.obtener_disponibles()
            cluster_objetivo = None  # Indica que se buscó en todos

        # 7. Calcular distancias GPS para cada hospital
        for hospital in hospitales_disponibles:
            distancia = self._calcular_distancia_haversine(
                ubicacion_paciente['latitud'],
                ubicacion_paciente['longitud'],
                hospital['ubicacion']['latitud'],
                hospital['ubicacion']['longitud']
            )
            hospital['distancia_km'] = round(distancia, 2)

            # Calcular disponibilidad porcentual
            capacidad_actual = hospital['capacidad']['actual']
            capacidad_maxima = hospital['capacidad']['maxima']
            disponibilidad = (
                (capacidad_maxima - capacidad_actual) / capacidad_maxima * 100
            )
            hospital['disponibilidad_porcentaje'] = round(disponibilidad, 1)

        # 8. Ordenar por distancia (más cercano primero)
        hospitales_ordenados = sorted(
            hospitales_disponibles,
            key=lambda h: h['distancia_km']
        )

        # 9. Seleccionar TOP N
        top_hospitales = hospitales_ordenados[:top_n]

        return {
            'evaluacion': evaluacion,
            'cluster_utilizado': cluster_objetivo,
            'especialidades_cluster': especialidades_cluster,
            'hospitales_recomendados': top_hospitales,
            'total_disponibles': len(hospitales_disponibles),
            'mensaje': f'Se encontraron {len(top_hospitales)} hospitales adecuados.'
        }

    def _calcular_distancia_haversine(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calcula distancia entre dos puntos GPS usando fórmula Haversine.

        Args:
            lat1: Latitud punto 1
            lon1: Longitud punto 1
            lat2: Latitud punto 2
            lon2: Longitud punto 2

        Returns:
            Distancia en kilómetros

        Example:
            >>> # Lima Centro a Miraflores
            >>> distancia = servicio._calcular_distancia_haversine(
            ...     -12.0464, -77.0428,
            ...     -12.1191, -77.0383
            ... )
            >>> distancia
            8.09
        """
        # Radio de la Tierra en km
        R = 6371.0

        # Convertir grados a radianes
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Diferencias
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Fórmula Haversine
        a = (
            math.sin(dlat / 2)**2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distancia = R * c

        return distancia

    def obtener_estadisticas_clusters(self) -> Dict[int, Dict[str, Any]]:
        """
        Obtiene información completa de todos los clusters.

        Returns:
            Dict con info de cada cluster

        Example:
            >>> estadisticas = servicio.obtener_estadisticas_clusters()
            >>> for cluster_id, info in estadisticas.items():
            ...     print(f"Cluster {cluster_id}: {info['especialidades']}")
            Cluster 0: ['trauma', 'ortopedia']
            Cluster 1: ['pediatria', 'general']
            ...
        """
        return self.clusterer.obtener_info_clusters()

    def obtener_hospitales_por_especialidad(
        self,
        especialidad: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene hospitales que tienen una especialidad específica.

        Args:
            especialidad: Nombre de la especialidad

        Returns:
            Lista de hospitales

        Example:
            >>> hospitales = servicio.obtener_hospitales_por_especialidad('cardiologia')
            >>> len(hospitales)
            12
        """
        todos_hospitales = self.repo_hospitales.obtener_todos()

        hospitales_con_especialidad = [
            hospital for hospital in todos_hospitales
            if hospital['especialidades'].get(especialidad) == 1
        ]

        return hospitales_con_especialidad

    def evaluar_paciente_con_imagen(
        self,
        datos_paciente: Dict[str, Any],
        imagen_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evalúa paciente combinando Random Forest (vitales) + CNN (imagen visual).

        DEEP LEARNING: Este método utiliza tanto ML tradicional como Deep Learning
        para una evaluación más completa y precisa.

        Flujo:
        1. Evaluación por signos vitales (Random Forest)
        2. Si hay imagen, evaluación visual (CNN - Deep Learning)
        3. Fusión de predicciones con pesos ponderados
        4. Decisión final combinada

        Args:
            datos_paciente: Datos del paciente (signos vitales, edad, etc.)
            imagen_base64: Imagen de la herida/quemadura en base64 (opcional)

        Returns:
            Dict con:
            - severidad: Severidad final (combinada o solo vitales)
            - probabilidades: Probabilidades finales
            - severidad_vitales: Predicción por Random Forest
            - severidad_imagen: Predicción por CNN (si hay imagen)
            - metodo: 'hibrido' o 'solo_vitales'
            - confianza: Confianza de la predicción final
            - requiere_traslado: Boolean

        Example:
            >>> # Con imagen
            >>> resultado = servicio.evaluar_paciente_con_imagen(
            ...     datos_paciente,
            ...     imagen_base64="iVBORw0KGg..."
            ... )
            >>> resultado['metodo']
            'hibrido'
            >>> resultado['severidad']
            'alto'

            >>> # Sin imagen
            >>> resultado = servicio.evaluar_paciente_con_imagen(
            ...     datos_paciente
            ... )
            >>> resultado['metodo']
            'solo_vitales'
        """
        # 1. Evaluación por signos vitales (Random Forest)
        severidad_vitales, probs_vitales = self.predictor.predecir(datos_paciente)

        # 2. Si NO hay imagen o CNN no disponible, solo usar Random Forest
        if not imagen_base64 or self.clasificador_imagenes is None:
            return {
                'severidad': severidad_vitales,
                'probabilidades': probs_vitales,
                'confianza': round(max(probs_vitales.values()) * 100, 2),
                'requiere_traslado': severidad_vitales in ['crítico', 'alto'],
                'tipo_incidente': datos_paciente.get('tipo_incidente', 'desconocido'),
                'metodo': 'solo_vitales',
                'severidad_vitales': severidad_vitales,
                'severidad_imagen': None
            }

        # 3. Evaluación visual con CNN (Deep Learning)
        try:
            severidad_imagen, probs_imagen = self.clasificador_imagenes.predecir(
                imagen_base64
            )
        except Exception as e:
            # Si falla CNN, usar solo Random Forest
            print(f"Error en CNN: {str(e)}")
            return {
                'severidad': severidad_vitales,
                'probabilidades': probs_vitales,
                'confianza': round(max(probs_vitales.values()) * 100, 2),
                'requiere_traslado': severidad_vitales in ['crítico', 'alto'],
                'tipo_incidente': datos_paciente.get('tipo_incidente', 'desconocido'),
                'metodo': 'solo_vitales',
                'severidad_vitales': severidad_vitales,
                'severidad_imagen': None,
                'error_cnn': str(e)
            }

        # 4. Fusión de predicciones (60% vitales + 40% imagen)
        severidad_final, probs_finales = self._fusionar_predicciones(
            severidad_vitales, probs_vitales,
            severidad_imagen, probs_imagen,
            peso=0.6, peso_imagen=0.4
        )

        return {
            'severidad': severidad_final,
            'probabilidades': probs_finales,
            'confianza': round(max(probs_finales.values()) * 100, 2),
            'requiere_traslado': severidad_final in ['crítico', 'alto'],
            'tipo_incidente': datos_paciente.get('tipo_incidente', 'desconocido'),
            'metodo': 'hibrido',
            'severidad_vitales': severidad_vitales,
            'severidad_imagen': severidad_imagen,
            'confianza_vitales': round(max(probs_vitales.values()) * 100, 2),
            'confianza_imagen': round(max(probs_imagen.values()) * 100, 2)
        }

    def _fusionar_predicciones(
        self,
        sev_vitales: str,
        probs_vitales: Dict[str, float],
        peso: float,
        sev_imagen: str,
        probs_imagen: Dict[str, float],
        peso_imagen: float
    ) -> Tuple[str, Dict[str, float]]:
        """
        Fusiona predicciones de Random Forest y CNN con pesos ponderados.

        Args:
            sev_vitales: Severidad predicha por Random Forest
            probs_vitales: Probabilidades de Random Forest
            peso: Peso para Random Forest (ej: 0.6 = 60%)
            sev_imagen: Severidad predicha por CNN
            probs_imagen: Probabilidades de CNN
            peso_imagen: Peso para CNN (ej: 0.4 = 40%)

        Returns:
            Tupla (severidad_final, probabilidades_finales)

        Example:
            >>> sev, probs = servicio._fusionar_predicciones(
            ...     'alto', {'critico': 0.1, 'alto': 0.7, 'medio': 0.15, 'bajo': 0.05}, 0.6,
            ...     'critico', {'critico': 0.8, 'alto': 0.15, 'medio': 0.03, 'bajo': 0.02}, 0.4
            ... )
            >>> sev
            'alto'
        """
        # Combinar probabilidades con pesos
        clases = ['critico', 'alto', 'medio', 'bajo']
        probs_fusionadas = {}

        for clase in clases:
            prob_v = probs_vitales.get(clase, probs_vitales.get('crítico' if clase == 'critico' else clase, 0.0))
            prob_i = probs_imagen.get(clase, 0.0)

            probs_fusionadas[clase] = (prob_v * peso) + (prob_i * peso_imagen)

        # Severidad final = clase con mayor probabilidad fusionada
        severidad_final = max(probs_fusionadas, key=probs_fusionadas.get)

        return severidad_final, probs_fusionadas
