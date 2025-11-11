"""Script de prueba para el modelo Random Forest entrenado."""

import sys
from pathlib import Path

# Agregar ruta raíz
sys.path.append(str(Path(__file__).parent))

from negocio.ml.prediccion_severidad import PredictorSeveridad


def main():
    """Prueba el modelo con casos de ejemplo."""
    print("=" * 60)
    print("PRUEBA DE MODELO RANDOM FOREST - PREDICCION DE SEVERIDAD")
    print("=" * 60)

    # Inicializar predictor
    print("\n[1] Inicializando predictor...")
    predictor = PredictorSeveridad()
    print(">> Modelo cargado exitosamente!\n")

    # Casos de prueba
    casos = [
        {
            "nombre": "Caso 1: Paciente CRITICO (infarto)",
            "datos": {
                'edad': 65,
                'sexo': 'M',
                'presion_sistolica': 180,
                'presion_diastolica': 100,
                'frecuencia_cardiaca': 110,
                'frecuencia_respiratoria': 25,
                'temperatura': 38.5,
                'saturacion_oxigeno': 88,
                'nivel_dolor': 9,
                'tiempo_desde_incidente': 15,
                'tipo_incidente': 'problema_cardiaco'
            }
        },
        {
            "nombre": "Caso 2: Paciente MEDIO (trauma leve)",
            "datos": {
                'edad': 30,
                'sexo': 'F',
                'presion_sistolica': 120,
                'presion_diastolica': 80,
                'frecuencia_cardiaca': 75,
                'frecuencia_respiratoria': 16,
                'temperatura': 36.8,
                'saturacion_oxigeno': 98,
                'nivel_dolor': 4,
                'tiempo_desde_incidente': 45,
                'tipo_incidente': 'fractura'
            }
        },
        {
            "nombre": "Caso 3: Paciente ALTO (respiratorio)",
            "datos": {
                'edad': 55,
                'sexo': 'M',
                'presion_sistolica': 140,
                'presion_diastolica': 90,
                'frecuencia_cardiaca': 95,
                'frecuencia_respiratoria': 22,
                'temperatura': 38.0,
                'saturacion_oxigeno': 91,
                'nivel_dolor': 7,
                'tiempo_desde_incidente': 20,
                'tipo_incidente': 'problema_respiratorio'
            }
        }
    ]

    # Probar cada caso
    for i, caso in enumerate(casos, 1):
        print(f"\n[{i+1}] {caso['nombre']}")
        print("-" * 60)

        # Predecir
        severidad, probabilidades = predictor.predecir(caso['datos'])

        # Mostrar resultado
        print(f">> SEVERIDAD PREDICHA: {severidad.upper()}")
        print(f"\n>> Probabilidades:")
        for clase, prob in sorted(probabilidades.items(),
                                  key=lambda x: x[1],
                                  reverse=True):
            barra = "#" * int(prob * 50)
            print(f"   {clase:10s} {prob:6.2%} {barra}")

    # Features importantes
    print("\n" + "=" * 60)
    print("IMPORTANCIA DE FEATURES (Top 5)")
    print("=" * 60)
    features_imp = predictor.obtener_features_importantes(top_n=5)
    for feature, importancia in features_imp:
        barra = "#" * int(importancia * 100)
        print(f"{feature:30s} {importancia:6.4f} {barra}")

    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA EXITOSAMENTE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
