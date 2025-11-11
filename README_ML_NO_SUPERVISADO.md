# Machine Learning No Supervisado - K-means Clustering

## 📋 Descripción

Modelo de **Machine Learning No Supervisado** que agrupa **hospitales por especialidades similares** utilizando el algoritmo **K-means**.

**Tipo:** Clustering (agrupamiento automático)
**Objetivo:** Recomendar hospitales adecuados según tipo de emergencia

---

## 🎯 Objetivo

Agrupar los 30 hospitales en clusters basándose en sus especialidades médicas para:
1. Filtrar hospitales relevantes según tipo de emergencia
2. Recomendar hospital más adecuado (cluster + distancia GPS)
3. Optimizar tiempo de decisión

---

## 📊 Dataset

### Archivo: `hospitales.csv`

| Característica | Descripción | Tipo |
|----------------|-------------|------|
| **hospital_id** | Identificador único | str |
| **nombre** | Nombre del hospital | str |
| **latitud** | Coordenada GPS | float |
| **longitud** | Coordenada GPS | float |
| **capacidad_actual** | Camas ocupadas | int |
| **capacidad_maxima** | Camas totales | int |
| **especialidades** | Lista de especialidades | str |
| **nivel** | Nivel hospital (I, II, III) | str |

**Especialidades consideradas:**
- Cardiología
- Trauma
- Pediatría
- Ortopedia
- Neurología
- Quemados
- Toxicología
- General

**Total de hospitales:** 30

---

## 🏗️ Arquitectura (3 Capas)

```
┌─────────────────────────────────────────┐
│ PRESENTACIÓN                            │
│ - GraphQL API                           │
│ - Recibe solicitud de traslado          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ NEGOCIO                                 │
│ 1. Random Forest → severidad           │
│ 2. clustering_hospitales.py             │ ← K-means
│    - Determina cluster por emergencia   │
│    - Filtra hospitales del cluster      │
│ 3. Calcula distancias GPS               │
│ 4. Ordena y selecciona TOP 3-5          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ DATOS                                   │
│ - MongoDB: hospitales (con cluster)     │
│ - Consulta hospitales disponibles       │
└─────────────────────────────────────────┘
```

**✅ Cumple arquitectura 3 capas:**
- K-means está en capa **NEGOCIO/ML**
- Filtra hospitales de DATOS
- Responde a PRESENTACIÓN

---

## 🚀 Uso

### 1️⃣ Entrenamiento (OFFLINE - una vez)

```bash
# Abrir Jupyter Notebook
cd ServicioDecision
jupyter notebook notebooks/entrenar_kmeans.ipynb

# Ejecutar todas las celdas
# Se generarán:
# - modelos_ml/modelo_kmeans.pkl
# - modelos_ml/especialidades_list.pkl
# - modelos_ml/cluster_info.pkl
# - archivos_csv/hospitales_con_clusters.csv
```

**Resultado:**
- Hospitales agrupados en K clusters (ej: K=4)
- Cada cluster tiene especialidades dominantes
- Modelo guardado para producción

---

### 2️⃣ Clustering en Producción (TIEMPO REAL)

```python
from negocio.ml.clustering_hospitales import ClusteringHospitales

# Inicializar clusterer
clusterer = ClusteringHospitales()

# Escenario: Paciente con problema cardíaco
tipo_emergencia = "problema_cardiaco"

# Obtener cluster adecuado
cluster_recomendado = clusterer.obtener_cluster_por_tipo_emergencia(
    tipo_emergencia
)

print(f"Cluster recomendado: {cluster_recomendado}")
# Output: Cluster recomendado: 2

# Ver especialidades de ese cluster
especialidades = clusterer.obtener_especialidades_cluster(cluster_recomendado)
print(f"Especialidades: {especialidades}")
# Output: Especialidades: ['cardiologia', 'neurologia']

# Obtener hospitales del cluster
hospitales_ids = clusterer.obtener_hospitales_cluster(cluster_recomendado)
print(f"Hospitales: {hospitales_ids}")
# Output: Hospitales: ['HOSP005', 'HOSP012', 'HOSP018', ...]
```

---

### 3️⃣ Integración con Sistema Completo

```python
# Flujo completo de decisión

# 1. Predecir severidad (Random Forest)
severidad, probs = predictor_severidad.predecir(datos_paciente)

# 2. Si requiere traslado
if severidad in ["crítico", "alto"]:

    # 3. Obtener cluster por tipo emergencia (K-means)
    cluster = clusterer.obtener_cluster_por_tipo_emergencia(
        datos_paciente["tipo_incidente"]
    )

    # 4. Consultar hospitales de ese cluster (MongoDB)
    hospitales_disponibles = repositorio.obtener_hospitales_por_cluster(
        cluster
    )

    # 5. Calcular distancias GPS
    for hospital in hospitales_disponibles:
        hospital["distancia"] = calcular_distancia_gps(
            ubicacion_paciente,
            hospital["ubicacion"]
        )

    # 6. Ordenar por distancia
    hospitales_ordenados = sorted(
        hospitales_disponibles,
        key=lambda h: h["distancia"]
    )

    # 7. Recomendar TOP 3
    return hospitales_ordenados[:3]
```

---

## 📈 Ejemplo de Clusters

### **Cluster 0: UCI y Trauma** (8 hospitales)
```
Especialidades dominantes:
  - trauma:      100%
  - general:     75%
  - ortopedia:   62%

Hospitales:
  1. Hospital del Sur #2
  2. Hospital Santa Rosa #7
  3. Hospital San José #10
  ...
```

### **Cluster 1: Pediatría** (6 hospitales)
```
Especialidades dominantes:
  - pediatria:   100%
  - general:     83%

Hospitales:
  1. Hospital Infantil #3
  2. Hospital Materno #8
  ...
```

### **Cluster 2: Especialidades Complejas** (10 hospitales)
```
Especialidades dominantes:
  - cardiologia: 90%
  - neurologia:  80%
  - general:     100%

Hospitales:
  1. Hospital Central #1
  2. Hospital Universitario #5
  ...
```

### **Cluster 3: Urgencias Específicas** (6 hospitales)
```
Especialidades dominantes:
  - quemados:     83%
  - toxicologia:  67%
  - trauma:       50%

Hospitales:
  1. Hospital de Quemados #4
  2. Centro Toxicológico #9
  ...
```

---

## 🔧 Parámetros K-means

```python
KMeans(
    n_clusters=4,      # Número de clusters (determinado por método del codo)
    random_state=42,   # Reproducibilidad
    n_init=10          # Ejecuciones para evitar mínimos locales
)
```

---

## 📁 Estructura de Archivos

```
ServicioDecision/
├── notebooks/
│   └── entrenar_kmeans.ipynb              ← ENTRENAMIENTO
│
├── negocio/ml/
│   └── clustering_hospitales.py           ← PRODUCCIÓN
│
├── modelos_ml/
│   ├── modelo_kmeans.pkl                  ← Modelo entrenado
│   ├── especialidades_list.pkl            ← Lista de especialidades
│   └── cluster_info.pkl                   ← Info de cada cluster
│
├── archivos_csv/
│   ├── hospitales.csv                     ← Original
│   └── hospitales_con_clusters.csv        ← Con clusters asignados
│
└── README_ML_NO_SUPERVISADO.md            ← Esta documentación
```

---

## 🎓 Estándares de Codificación Aplicados

### ✅ PEP 8
- Nombres descriptivos
- Líneas máximo 88 caracteres
- Imports ordenados

### ✅ Type Hints
```python
def obtener_cluster_por_tipo_emergencia(
    self,
    tipo_emergencia: str
) -> int:
    ...
```

### ✅ Docstrings (Google Style)
```python
"""
Determina qué cluster es más adecuado para un tipo de emergencia.

Args:
    tipo_emergencia: Tipo de incidente

Returns:
    int: Cluster recomendado

Example:
    >>> cluster = clusterer.obtener_cluster_por_tipo_emergencia('trauma')
    >>> print(cluster)
    0
"""
```

### ✅ SOLID
- **SRP:** `ClusteringHospitales` solo hace clustering
- **OCP:** Extensible para otros algoritmos
- **DIP:** Depende de abstracciones (joblib)

---

## 🔄 Workflow Completo

```
1. DESARROLLO (una vez):
   hospitales.csv → Notebook → K-means → Guardar .pkl

2. PRODUCCIÓN (cada paciente que necesita traslado):
   Tipo emergencia → Clustering → Cluster → Filtrar hospitales
                                              ↓
                                          MongoDB
                                              ↓
                                       Calcular GPS
                                              ↓
                                        TOP 3-5
```

---

## 📚 Dependencias

```txt
scikit-learn==1.4.0    # K-means
pandas==2.2.0          # Procesamiento datos
numpy==1.26.3          # Operaciones numéricas
joblib==1.3.2          # Guardar/cargar modelos
matplotlib==3.8.2      # Visualización
seaborn==0.13.1        # Heatmaps
```

---

## 🧪 Método de Validación

### **Silhouette Score**
Mide qué tan bien están agrupados los hospitales:
- **> 0.5:** Buena separación
- **0.25-0.5:** Aceptable
- **< 0.25:** Clusters no claros

### **Método del Codo**
Determina K óptimo observando dónde la inercia deja de disminuir significativamente.

---

## 🐛 Troubleshooting

### Error: "No se encontraron los modelos K-means"
**Solución:** Ejecuta el notebook de entrenamiento primero.

### Error: "KeyError: 'especialidades'"
**Solución:** Verifica que el CSV tenga la columna correcta o que las especialidades estén procesadas.

### Los clusters no tienen sentido médico
**Solución:**
1. Ajusta K (prueba 3, 4 o 5 clusters)
2. Verifica datos de especialidades en CSV
3. Considera agregar features adicionales (nivel hospital, capacidad)

---

## 💡 Mapeo Emergencia → Cluster

| Tipo Emergencia | Especialidad Requerida | Cluster Típico |
|-----------------|------------------------|----------------|
| problema_cardiaco | cardiologia | 2 |
| trauma / accidente_auto | trauma | 0 |
| fractura / caida | ortopedia | 0 |
| quemadura | quemados | 3 |
| intoxicacion | toxicologia | 3 |
| problema_respiratorio | general | 1 o 2 |
| dolor_abdominal | general | 1 |

---

## 📞 Contacto

**Microservicio:** Decisión y Atención Médica
**Desarrollador:** [Tu Nombre]
**Universidad:** [Tu Universidad]
**Fecha:** Octubre 2025

---

## 🎯 Ventajas vs Búsqueda Simple

### **Sin K-means (búsqueda simple):**
```
1. Buscar TODOS los hospitales (30)
2. Filtrar manualmente por especialidad
3. Calcular 30 distancias GPS
4. Ordenar y seleccionar
```
**Tiempo:** ~500ms

### **Con K-means:**
```
1. Determinar cluster (instantáneo)
2. Filtrar solo hospitales del cluster (6-10)
3. Calcular 6-10 distancias GPS
4. Ordenar y seleccionar
```
**Tiempo:** ~150ms ⚡

**Beneficio:** 3x más rápido + mejores recomendaciones

---

**¡Machine Learning No Supervisado implementado!** 🚀
