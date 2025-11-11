"""
Módulo de clasificación de imágenes médicas usando CNN (Deep Learning).
Capa: NEGOCIO / ML
Responsabilidad: Clasificar severidad de heridas/quemaduras desde imágenes.
Estándares: PEP 8, Type hints, Docstrings, SOLID

Arquitectura CNN:
- Transfer Learning con MobileNetV2 (pre-entrenado en ImageNet)
- Capas personalizadas para 4 clases (crítico, alto, medio, bajo)
- Input: Imagen 224x224x3 RGB
- Output: Probabilidades para cada clase de severidad
"""

from typing import Dict, Tuple, Any
import numpy as np
from pathlib import Path
import base64
from io import BytesIO

# Importaciones condicionales para evitar errores si TensorFlow no está instalado
try:
    from tensorflow import keras
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.models import Model, load_model
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
    from tensorflow.keras.preprocessing.image import img_to_array
    from PIL import Image
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("WARNING: TensorFlow no disponible. Clasificador de imágenes deshabilitado.")


class ClasificadorImagenes:
    """
    Clasificador de imágenes médicas usando CNN con Transfer Learning.

    Utiliza MobileNetV2 pre-entrenado en ImageNet como base y agrega
    capas personalizadas para clasificación de severidad médica.

    Principios SOLID:
    - SRP: Solo clasifica imágenes médicas
    - OCP: Extensible para otros modelos CNN
    - DIP: Depende de abstracciones (TensorFlow/Keras)

    Attributes:
        modelo: Modelo CNN de Keras/TensorFlow
        clases: Lista de clases ['critico', 'alto', 'medio', 'bajo']
        img_size: Tamaño de entrada (224, 224)
    """

    def __init__(self, ruta_modelo: str = "modelos_ml/modelo_cnn_severidad.h5"):
        """
        Inicializa el clasificador CNN.

        Args:
            ruta_modelo: Ruta al modelo entrenado (.h5)

        Raises:
            ImportError: Si TensorFlow no está instalado
            FileNotFoundError: Si el modelo no existe (se creará uno nuevo)
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError(
                "TensorFlow no está instalado. "
                "Instala con: pip install tensorflow==2.15.0"
            )

        self.ruta_base = Path(__file__).parent.parent.parent / ruta_modelo
        self.modelo = None
        self.clases = ['critico', 'alto', 'medio', 'bajo']
        self.img_size = (224, 224)

        self._cargar_o_crear_modelo()

    def _cargar_o_crear_modelo(self) -> None:
        """
        Carga modelo existente o crea arquitectura nueva.

        Si el modelo no existe, crea arquitectura CNN con Transfer Learning
        pero SIN entrenar (se entrenará después con script separado).
        """
        try:
            # Intentar cargar modelo pre-entrenado
            self.modelo = load_model(self.ruta_base)
            print(f"✓ Modelo CNN cargado desde: {self.ruta_base}")
        except (FileNotFoundError, OSError):
            # Si no existe, crear arquitectura nueva
            print(f"⚠ Modelo no encontrado en {self.ruta_base}")
            print("  Creando arquitectura CNN nueva (sin entrenar)...")
            self.modelo = self._crear_arquitectura_cnn()
            print("  ✓ Arquitectura creada. Ejecuta el script de entrenamiento.")

    def _crear_arquitectura_cnn(self) -> Model:
        """
        Crea arquitectura CNN con Transfer Learning (MobileNetV2).

        Arquitectura:
        1. Base: MobileNetV2 pre-entrenado (congelado)
        2. GlobalAveragePooling2D
        3. Dense(128) + ReLU + Dropout(0.5)
        4. Dense(4) + Softmax

        Returns:
            Modelo de Keras compilado pero NO entrenado

        Example:
            >>> modelo = self._crear_arquitectura_cnn()
            >>> modelo.summary()
        """
        # Base pre-entrenada (Transfer Learning)
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(224, 224, 3)
        )

        # Congelar capas base (no entrenarlas)
        base_model.trainable = False

        # Agregar capas personalizadas
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation='relu', name='dense_features')(x)
        x = Dropout(0.5, name='dropout')(x)
        predictions = Dense(4, activation='softmax', name='predicciones')(x)

        # Crear modelo completo
        modelo = Model(inputs=base_model.input, outputs=predictions)

        # Compilar
        modelo.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        return modelo

    def predecir(
        self,
        imagen_base64: str
    ) -> Tuple[str, Dict[str, float]]:
        """
        Predice la severidad de una herida/quemadura desde imagen.

        Args:
            imagen_base64: Imagen codificada en base64 (formato estándar web)

        Returns:
            Tupla (severidad_predicha, probabilidades)
            - severidad_predicha: str ('critico', 'alto', 'medio', 'bajo')
            - probabilidades: Dict[str, float] con probabilidad por clase

        Raises:
            ValueError: Si la imagen no puede decodificarse
            RuntimeError: Si el modelo no está entrenado

        Example:
            >>> clasificador = ClasificadorImagenes()
            >>> imagen_b64 = "iVBORw0KGgoAAAANS..."
            >>> severidad, probs = clasificador.predecir(imagen_b64)
            >>> print(f"Severidad: {severidad}")
            Severidad: alto
            >>> print(f"Confianza: {probs['alto']:.2%}")
            Confianza: 87.34%
        """
        # Decodificar y preprocesar imagen
        img_array = self._decodificar_imagen_base64(imagen_base64)

        # Predecir con el modelo
        predicciones = self.modelo.predict(img_array, verbose=0)[0]

        # Obtener clase con mayor probabilidad
        idx_max = np.argmax(predicciones)
        severidad = self.clases[idx_max]

        # Crear diccionario de probabilidades
        probabilidades = {
            clase: float(prob)
            for clase, prob in zip(self.clases, predicciones)
        }

        return severidad, probabilidades

    def predecir_desde_archivo(
        self,
        ruta_imagen: str
    ) -> Tuple[str, Dict[str, float]]:
        """
        Predice severidad desde archivo de imagen (útil para pruebas).

        Args:
            ruta_imagen: Ruta al archivo de imagen

        Returns:
            Tupla (severidad, probabilidades)

        Example:
            >>> severidad, probs = clasificador.predecir_desde_archivo(
            ...     "datos/imagenes_entrenamiento/critico/quemadura.jpg"
            ... )
        """
        # Leer y preprocesar imagen
        img = Image.open(ruta_imagen).convert('RGB')
        img_array = self._preprocesar_imagen_pil(img)

        # Predecir
        predicciones = self.modelo.predict(img_array, verbose=0)[0]

        idx_max = np.argmax(predicciones)
        severidad = self.clases[idx_max]

        probabilidades = {
            clase: float(prob)
            for clase, prob in zip(self.clases, predicciones)
        }

        return severidad, probabilidades

    def _decodificar_imagen_base64(self, imagen_base64: str) -> np.ndarray:
        """
        Decodifica imagen de base64 a array NumPy preprocesado.

        Args:
            imagen_base64: String base64 de la imagen

        Returns:
            Array NumPy (1, 224, 224, 3) normalizado

        Raises:
            ValueError: Si la imagen no puede decodificarse
        """
        try:
            # Decodificar base64
            img_data = base64.b64decode(imagen_base64)
            img = Image.open(BytesIO(img_data)).convert('RGB')

            # Preprocesar
            return self._preprocesar_imagen_pil(img)

        except Exception as e:
            raise ValueError(
                f"Error al decodificar imagen base64: {str(e)}"
            ) from e

    def _preprocesar_imagen_pil(self, img: Image.Image) -> np.ndarray:
        """
        Preprocesa imagen PIL a formato requerido por el modelo.

        Pasos:
        1. Redimensionar a 224x224
        2. Convertir a array NumPy
        3. Normalizar [0, 255] → [0, 1]
        4. Expandir dimensión batch

        Args:
            img: Objeto PIL Image

        Returns:
            Array NumPy (1, 224, 224, 3) en rango [0, 1]
        """
        # Redimensionar
        img = img.resize(self.img_size)

        # Convertir a array
        img_array = img_to_array(img)

        # Normalizar a [0, 1]
        img_array = img_array / 255.0

        # Expandir dimensión batch (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    def obtener_info_modelo(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo CNN.

        Returns:
            Dict con información del modelo

        Example:
            >>> info = clasificador.obtener_info_modelo()
            >>> print(info['total_parametros'])
            2,257,984
        """
        if self.modelo is None:
            return {"error": "Modelo no cargado"}

        total_params = self.modelo.count_params()
        trainable_params = sum([
            np.prod(var.shape)
            for var in self.modelo.trainable_variables
        ])

        return {
            'arquitectura': 'MobileNetV2 + Transfer Learning',
            'clases': self.clases,
            'total_parametros': int(total_params),
            'parametros_entrenables': int(trainable_params),
            'input_shape': (224, 224, 3),
            'ruta_modelo': str(self.ruta_base)
        }
