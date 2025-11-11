"""
Módulo de predicción de severidad usando Random Forest.
Capa: NEGOCIO / ML
Responsabilidad: Predecir severidad de emergencias médicas.
Estándares: PEP 8, Type hints, Docstrings, SOLID
"""

from typing import Dict, List, Tuple, Any
import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class PredictorSeveridad:
    """
    Predictor de severidad de emergencias médicas usando Random Forest.

    Principios SOLID:
    - SRP: Solo predice severidad
    - OCP: Extensible para otros modelos
    - DIP: Depende de abstracciones (joblib)
    """

    def __init__(self, ruta_modelos: str = "modelos_ml"):
        """
        Inicializa el predictor cargando modelo y encoders.

        Args:
            ruta_modelos: Directorio donde están los modelos entrenados
        """
        self.ruta_base = Path(__file__).parent.parent.parent / ruta_modelos
        self.modelo = None
        self.encoder_sexo = None
        self.encoder_tipo_incidente = None
        self.features_list = None
        self._cargar_modelos()

    def _cargar_modelos(self) -> None:
        """Carga modelo Random Forest y encoders desde disco."""
        try:
            self.modelo = joblib.load(self.ruta_base / "modelo_severidad.pkl")
            self.encoder_sexo = joblib.load(self.ruta_base / "encoder_sexo.pkl")
            self.encoder_tipo_incidente = joblib.load(
                self.ruta_base / "encoder_tipo_incidente.pkl"
            )
            self.features_list = joblib.load(self.ruta_base / "features_list.pkl")
            print(f"Modelos cargados desde: {self.ruta_base}")
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"No se encontraron los modelos en {self.ruta_base}. "
                f"Ejecuta el notebook de entrenamiento primero."
            ) from e

    def predecir(
        self,
        datos_paciente: Dict[str, Any]
    ) -> Tuple[str, Dict[str, float]]:
        """
        Predice la severidad de una emergencia médica.

        Args:
            datos_paciente: Diccionario con datos del paciente:
                - edad: int
                - presion_sistolica: float
                - presion_diastolica: float
                - frecuencia_cardiaca: int
                - frecuencia_respiratoria: int
                - temperatura: float
                - saturacion_oxigeno: float
                - nivel_dolor: int (0-10)
                - tiempo_desde_incidente: int (minutos)
                - sexo: str ('M' o 'F')
                - tipo_incidente: str

        Returns:
            Tupla (severidad_predicha, probabilidades)
            - severidad_predicha: str ('crítico', 'alto', 'medio', 'bajo')
            - probabilidades: Dict[str, float] con probabilidad por clase

        Raises:
            ValueError: Si faltan datos requeridos

        Example:
            >>> predictor = PredictorSeveridad()
            >>> datos = {
            ...     'edad': 65,
            ...     'presion_sistolica': 180,
            ...     'saturacion_oxigeno': 88,
            ...     'sexo': 'M',
            ...     'tipo_incidente': 'cardiovascular',
            ...     ...
            ... }
            >>> severidad, probs = predictor.predecir(datos)
            >>> print(f"Severidad: {severidad}")
            Severidad: crítico
        """
        # Validar datos
        self._validar_datos(datos_paciente)

        # Preprocesar datos
        X = self._preprocesar_datos(datos_paciente)

        # Predecir
        severidad = self.modelo.predict(X)[0]
        probs_array = self.modelo.predict_proba(X)[0]

        # Formatear probabilidades
        probabilidades = {
            clase: float(prob)
            for clase, prob in zip(self.modelo.classes_, probs_array)
        }

        return severidad, probabilidades

    def _validar_datos(self, datos: Dict[str, Any]) -> None:
        """
        Valida que los datos del paciente estén completos.

        Args:
            datos: Datos del paciente

        Raises:
            ValueError: Si falta algún campo requerido
        """
        campos_requeridos = [
            'edad', 'presion_sistolica', 'presion_diastolica',
            'frecuencia_cardiaca', 'frecuencia_respiratoria',
            'temperatura', 'saturacion_oxigeno', 'nivel_dolor',
            'tiempo_desde_incidente', 'sexo', 'tipo_incidente'
        ]

        faltantes = [campo for campo in campos_requeridos if campo not in datos]

        if faltantes:
            raise ValueError(
                f"Faltan campos requeridos: {', '.join(faltantes)}"
            )

    def _preprocesar_datos(self, datos: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocesa datos del paciente para predicción.

        Args:
            datos: Datos del paciente

        Returns:
            DataFrame con features en el orden correcto
        """
        # Copiar datos
        datos_proc = datos.copy()

        # Codificar variables categóricas
        datos_proc['sexo_encoded'] = self.encoder_sexo.transform(
            [datos['sexo']]
        )[0]
        datos_proc['tipo_incidente_encoded'] = self.encoder_tipo_incidente.transform(
            [datos['tipo_incidente']]
        )[0]

        # Crear DataFrame con features en orden correcto
        X = pd.DataFrame([datos_proc])[self.features_list]

        return X

    def obtener_features_importantes(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Obtiene las features más importantes del modelo.

        Args:
            top_n: Número de features a retornar

        Returns:
            Lista de tuplas (nombre_feature, importancia)
        """
        importancias = self.modelo.feature_importances_
        features_importancia = list(zip(self.features_list, importancias))
        features_importancia.sort(key=lambda x: x[1], reverse=True)

        return features_importancia[:top_n]
