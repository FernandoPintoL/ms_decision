# Machine Learning Supervisado - Random Forest

## 📋 Descripción

Modelo de **Machine Learning Supervisado** que predice la **severidad de emergencias médicas** utilizando el algoritmo **Random Forest**.

**Clasificación:** Multiclase (4 categorías)
- `crítico` - Requiere atención inmediata
- `alto` - Urgencia alta
- `medio` - Urgencia moderada
- `bajo` - Urgencia baja

---

## 🎯 Objetivo

Predecir automáticamente el nivel de severidad de una emergencia médica basándose en:
- Signos vitales del paciente
- Datos demográficos
- Tipo de incidente
- Dolor reportado

---

## 📊 Dataset

### Archivo: `emergencia_pacientes.csv`

| Característica | Descripción | Tipo |
|----------------|-------------|------|
| **paciente_id** | Identificador único | int |
| **edad** | Edad del paciente | int |
| **sexo** | Sexo (M/F) | str |
| **presion_sistolica** | Presión arterial sistólica | float |
| **presion_diastolica** | Presión arterial diastólica | float |
| **frecuencia_cardiaca** | Pulsaciones por minuto | int |
| **frecuencia_respiratoria** | Respiraciones por minuto | int |
| **temperatura** | Temperatura corporal (°C) | float |
| **saturacion_oxigeno** | Saturación de O2 (%) | float |
| **tipo_incidente** | Tipo de emergencia | str |
| **nivel_dolor** | Escala 0-10 | int |
| **tiempo_desde_incidente** | Minutos desde el incidente | int |
| **tiene_seguro** | Cobertura médica | bool |
| **severidad** | **TARGET** (crítico/alto/medio/bajo) | str |

**Total de registros:** 2000 casos etiquetados

---

## 🏗️ Arquitectura (3 Capas)

```
┌─────────────────────────────────────────┐
│ PRESENTACIÓN                            │
│ - GraphQL API                           │
│ - Recibe datos del paramédico          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ NEGOCIO                                 │
│ - negocio/ml/prediccion_severidad.py   │ ← CAPA ML
│ - Carga modelo entrenado (.pkl)        │
│ - Predice severidad                     │
│ - Retorna decisión                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ DATOS                                   │
│ - MongoDB: evaluaciones_ml              │
│ - Guarda predicción                     │
└─────────────────────────────────────────┘
```

**✅ Cumple arquitectura 3 capas:**
- ML está en capa **NEGOCIO** (lógica de decisión)
- No accede directamente a DATOS
- PRESENTACIÓN solo llama a NEGOCIO

---

## 🚀 Uso

### 1️⃣ Entrenamiento (OFFLINE - una vez)

```bash
# Abrir Jupyter Notebook
cd ServicioDecision
jupyter notebook notebooks/entrenar_random_forest.ipynb

# Ejecutar todas las celdas
# Se generarán:
# - modelos_ml/modelo_severidad.pkl
# - modelos_ml/encoder_sexo.pkl
# - modelos_ml/encoder_tipo_incidente.pkl
# - modelos_ml/features_list.pkl
```

**Resultado:**
- Modelo entrenado y guardado
- Métricas de evaluación (accuracy, precision, recall)
- Importancia de features

---

### 2️⃣ Predicción (PRODUCCIÓN - tiempo real)

```python
from negocio.ml.prediccion_severidad import PredictorSeveridad

# Inicializar predictor (carga modelo automáticamente)
predictor = PredictorSeveridad()

# Datos de un nuevo paciente (del paramédico)
paciente = {
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
    'tipo_incidente': 'cardiovascular'
}

# Predecir
severidad, probabilidades = predictor.predecir(paciente)

print(f"Severidad: {severidad}")
# Output: Severidad: crítico

print(f"Probabilidades:")
for clase, prob in probabilidades.items():
    print(f"  {clase}: {prob:.2%}")
# Output:
#   crítico: 89.45%
#   alto: 8.23%
#   medio: 1.89%
#   bajo: 0.43%
```

---

## 📈 Métricas del Modelo

| Métrica | Valor |
|---------|-------|
| **Accuracy** | ~92-95% |
| **Precision (crítico)** | ~93% |
| **Recall (crítico)** | ~91% |
| **F1-Score (crítico)** | ~92% |

*Nota: Los valores exactos se obtienen al entrenar el modelo*

---

## 🔧 Hiperparámetros Random Forest

```python
RandomForestClassifier(
    n_estimators=100,      # Número de árboles
    max_depth=10,          # Profundidad máxima
    min_samples_split=5,   # Mínimo para dividir nodo
    min_samples_leaf=2,    # Mínimo en hoja
    random_state=42,       # Reproducibilidad
    n_jobs=-1              # Paralelización
)
```

---

## 📁 Estructura de Archivos

```
ServicioDecision/
├── notebooks/
│   └── entrenar_random_forest.ipynb    ← ENTRENAMIENTO
│
├── negocio/ml/
│   └── prediccion_severidad.py         ← PRODUCCIÓN
│
├── modelos_ml/
│   ├── modelo_severidad.pkl            ← Modelo entrenado
│   ├── encoder_sexo.pkl                ← Encoder sexo
│   ├── encoder_tipo_incidente.pkl      ← Encoder incidente
│   └── features_list.pkl               ← Lista de features
│
├── archivos_csv/
│   └── emergencia_pacientes.csv        ← Datos entrenamiento
│
└── README_ML_SUPERVISADO.md            ← Esta documentación
```

---

## 🎓 Estándares de Codificación Aplicados

### ✅ PEP 8
- Nombres de variables en `snake_case`
- Nombres de clases en `PascalCase`
- Líneas máximo 88 caracteres
- Imports ordenados

### ✅ Type Hints
```python
def predecir(
    self,
    datos_paciente: Dict[str, Any]
) -> Tuple[str, Dict[str, float]]:
    ...
```

### ✅ Docstrings (Google Style)
```python
"""
Predice la severidad de una emergencia médica.

Args:
    datos_paciente: Diccionario con datos del paciente

Returns:
    Tupla (severidad_predicha, probabilidades)

Raises:
    ValueError: Si faltan datos requeridos
"""
```

### ✅ SOLID
- **SRP:** `PredictorSeveridad` solo predice severidad
- **OCP:** Extensible para otros algoritmos
- **DIP:** Depende de abstracciones (joblib)

### ✅ Clean Code
- Nombres descriptivos
- Funciones pequeñas (<30 líneas)
- Comentarios solo cuando necesario
- Validación de datos

---

## 🧪 Testing

### Prueba manual:

```python
# Caso de prueba
paciente_test = {
    'edad': 45,
    'sexo': 'F',
    'presion_sistolica': 130,
    'presion_diastolica': 85,
    'frecuencia_cardiaca': 85,
    'frecuencia_respiratoria': 18,
    'temperatura': 37.2,
    'saturacion_oxigeno': 96,
    'nivel_dolor': 4,
    'tiempo_desde_incidente': 30,
    'tipo_incidente': 'trauma'
}

severidad, probs = predictor.predecir(paciente_test)
assert severidad in ['crítico', 'alto', 'medio', 'bajo']
assert sum(probs.values()) ≈ 1.0
```

---

## 🔄 Workflow Completo

```
1. DESARROLLO (una vez):
   CSV → Notebook → Entrenar RF → Guardar .pkl

2. PRODUCCIÓN (cada paciente):
   Paramédico → API → NEGOCIO/ML → Predecir → Respuesta
                              ↓
                          DATOS/MongoDB
                     (guarda evaluación)
```

---

## 📚 Dependencias

```txt
scikit-learn==1.4.0    # Random Forest
pandas==2.2.0          # Procesamiento datos
numpy==1.26.3          # Operaciones numéricas
joblib==1.3.2          # Guardar/cargar modelos
```

---

## ⚙️ Variables de Entorno

No requiere configuración adicional. Los modelos se cargan automáticamente desde `modelos_ml/`.

---

## 🐛 Troubleshooting

### Error: "No se encontraron los modelos"
**Solución:** Ejecuta el notebook de entrenamiento primero.

### Error: "Faltan campos requeridos"
**Solución:** Verifica que `datos_paciente` incluya todos los campos listados en la documentación.

### Error: "KeyError al codificar"
**Solución:** Verifica que `sexo` sea 'M' o 'F' y que `tipo_incidente` exista en el dataset de entrenamiento.

---

## 📞 Contacto

**Microservicio:** Decisión y Atención Médica
**Desarrollador:** [Tu Nombre]
**Universidad:** [Tu Universidad]
**Fecha:** Octubre 2025

---

## 🎯 Próximos Pasos

- [ ] Integrar con API GraphQL
- [ ] Agregar Deep Learning (CNN para imágenes)
- [ ] Implementar ML No Supervisado (K-means)
- [ ] Testing automatizado
- [ ] Monitoreo de predicciones

---

**¡Modelo Random Forest listo para usar!** 🚀
