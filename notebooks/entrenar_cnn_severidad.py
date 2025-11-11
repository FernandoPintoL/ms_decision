"""
Script de entrenamiento de CNN para clasificación de severidad médica.
Entrena modelo de Deep Learning con Transfer Learning (MobileNetV2).

Uso:
    python notebooks/entrenar_cnn_severidad.py

Outputs:
    - modelos_ml/modelo_cnn_severidad.h5 (modelo entrenado)
    - modelos_ml/historial_entrenamiento.png (gráficas)

Estándares: PEP 8, Type hints, Docstrings
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reducir logs de TensorFlow

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from tensorflow import keras
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau


def crear_arquitectura_cnn() -> Model:
    """
    Crea arquitectura CNN con Transfer Learning.

    Returns:
        Modelo compilado pero no entrenado
    """
    print("\n[1/5] Creando arquitectura CNN...")

    # Base pre-entrenada
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )

    # Congelar base
    base_model.trainable = False

    # Capas personalizadas
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(4, activation='softmax')(x)

    modelo = Model(inputs=base_model.input, outputs=predictions)

    # Compilar
    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    print(f"   [OK] Total parámetros: {modelo.count_params():,}")
    print(f"   [OK] Parámetros entrenables: {sum([np.prod(v.shape) for v in modelo.trainable_variables]):,}")

    return modelo


def cargar_datos(batch_size: int = 32):
    """
    Carga y preprocesa datos de entrenamiento.

    Args:
        batch_size: Tamaño del batch

    Returns:
        Tupla (train_generator, val_generator)
    """
    print("\n[2/5] Cargando datasets...")

    data_dir = Path('datos/imagenes_entrenamiento')

    # Data Augmentation para entrenamiento
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        brightness_range=[0.8, 1.2],
        validation_split=0.2  # 80% train, 20% validation
    )

    # Sin augmentation para validación
    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2
    )

    # Generador de entrenamiento
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    # Generador de validación
    val_generator = val_datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    print(f"   [OK] Imágenes de entrenamiento: {train_generator.samples}")
    print(f"   [OK] Imágenes de validación: {val_generator.samples}")
    print(f"   [OK] Clases: {list(train_generator.class_indices.keys())}")

    return train_generator, val_generator


def entrenar_modelo(
    modelo: Model,
    train_gen,
    val_gen,
    epochs: int = 20
):
    """
    Entrena el modelo CNN.

    Args:
        modelo: Modelo a entrenar
        train_gen: Generador de entrenamiento
        val_gen: Generador de validación
        epochs: Número de épocas

    Returns:
        Historia del entrenamiento
    """
    print(f"\n[3/5] Entrenando modelo ({epochs} epochs)...")

    # Crear directorio para modelos
    models_dir = Path('modelos_ml')
    models_dir.mkdir(exist_ok=True)

    # Callbacks
    callbacks = [
        # Guardar mejor modelo
        ModelCheckpoint(
            'modelos_ml/modelo_cnn_severidad.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        # Early stopping si no mejora
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        # Reducir learning rate si se estanca
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        )
    ]

    # Entrenar
    history = modelo.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )

    print("\n   [OK] Entrenamiento completado")

    return history


def evaluar_modelo(modelo: Model, val_gen):
    """
    Evalúa el modelo con datos de validación.

    Args:
        modelo: Modelo entrenado
        val_gen: Generador de validación
    """
    print("\n[4/5] Evaluando modelo...")

    loss, accuracy = modelo.evaluate(val_gen, verbose=0)

    print(f"   [OK] Loss: {loss:.4f}")
    print(f"   [OK] Accuracy: {accuracy:.4%}")


def graficar_historial(history):
    """
    Genera gráficas del entrenamiento.

    Args:
        history: Historia del entrenamiento
    """
    print("\n[5/5] Generando gráficas...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Accuracy
    ax1.plot(history.history['accuracy'], label='Train Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
    ax1.set_title('Accuracy del Modelo', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Loss
    ax2.plot(history.history['loss'], label='Train Loss')
    ax2.plot(history.history['val_loss'], label='Val Loss')
    ax2.set_title('Loss del Modelo', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('modelos_ml/historial_entrenamiento.png', dpi=100)
    print(f"   [OK] Gráficas guardadas en: modelos_ml/historial_entrenamiento.png")

    plt.close()


def main():
    """Función principal de entrenamiento."""
    print("=" * 70)
    print("ENTRENAMIENTO DE CNN PARA CLASIFICACIÓN DE SEVERIDAD MÉDICA")
    print("=" * 70)
    print("\nArquitectura: MobileNetV2 + Transfer Learning")
    print("Clases: crítico, alto, medio, bajo")
    print("=" * 70)

    # 1. Crear arquitectura
    modelo = crear_arquitectura_cnn()

    # 2. Cargar datos
    train_gen, val_gen = cargar_datos(batch_size=32)

    # 3. Entrenar
    history = entrenar_modelo(
        modelo,
        train_gen,
        val_gen,
        epochs=20  # Puedes ajustar según necesidad
    )

    # 4. Evaluar
    evaluar_modelo(modelo, val_gen)

    # 5. Graficar
    graficar_historial(history)

    print("\n" + "=" * 70)
    print("[DONE] ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print("\nModelo guardado en: modelos_ml/modelo_cnn_severidad.h5")
    print("Gráficas en: modelos_ml/historial_entrenamiento.png")
    print("\n[TARGET] Siguiente paso: Integrar con ServicioDecision")
    print("=" * 70)


if __name__ == "__main__":
    main()
