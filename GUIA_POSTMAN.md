# Guía Completa de Postman - Microservicio de Decisión Médica

## 📋 Configuración Inicial de Postman

### 1. Crear una Nueva Colección

1. Abre Postman
2. Click en **"New"** o **"+"**
3. Selecciona **"HTTP Request"**
4. Guarda la request en una nueva colección: **"Microservicio Decisión Médica"**

---

## 🔧 Configuración Base (Aplica a TODAS las requests)

### Headers Requeridos

| Key | Value |
|-----|-------|
| `Content-Type` | `application/json` |

**Cómo configurar:**
1. Ve a la pestaña **Headers**
2. Agrega: Key: `Content-Type`, Value: `application/json`

### Configuración del Request

- **Método:** `POST`
- **URL:** `http://localhost:8000/graphql`
- **Body:** Selecciona **raw** y **JSON**

---

## 📊 Ejemplo 1: Obtener Estadísticas del Sistema (SIMPLE)

### Configuración

- **Método:** `POST`
- **URL:** `http://localhost:8000/graphql`
- **Headers:** `Content-Type: application/json`
- **Body (raw - JSON):**

```json
{
  "query": "query { estadisticasSistema { totalHospitales hospitalesDisponibles clustersActivos modelosCargados } }"
}
```

### Respuesta Esperada

```json
{
  "data": {
    "estadisticasSistema": {
      "totalHospitales": 30,
      "hospitalesDisponibles": 30,
      "clustersActivos": 4,
      "modelosCargados": true
    }
  }
}
```

### Interpretación

- ✅ **30 hospitales** en total en la base de datos
- ✅ **30 hospitales** con capacidad disponible
- ✅ **4 clusters** de K-means activos
- ✅ **Modelos ML cargados** (Random Forest + K-means)

---

## 🏥 Ejemplo 2: Obtener Información de Clusters

### Configuración

- **Método:** `POST`
- **URL:** `http://localhost:8000/graphql`
- **Body (raw - JSON):**

```json
{
  "query": "query { obtenerClusters { clusterId cantidadHospitales especialidades hospitalesIds } }"
}
```

### Respuesta Esperada

```json
{
  "data": {
    "obtenerClusters": [
      {
        "clusterId": 0,
        "cantidadHospitales": 8,
        "especialidades": [
          "cardiologia",
          "trauma",
          "ortopedia",
          "quemados"
        ],
        "hospitalesIds": [
          "HOSP007",
          "HOSP008",
          "HOSP009",
          "HOSP012",
          "HOSP013",
          "HOSP015",
          "HOSP019",
          "HOSP022"
        ]
      },
      {
        "clusterId": 1,
        "cantidadHospitales": 8,
        "especialidades": [
          "pediatria",
          "ortopedia"
        ],
        "hospitalesIds": [
          "HOSP002",
          "HOSP004",
          "HOSP011",
          "HOSP017",
          "HOSP018",
          "HOSP021",
          "HOSP026",
          "HOSP028"
        ]
      },
      {
        "clusterId": 2,
        "cantidadHospitales": 8,
        "especialidades": [
          "quemados",
          "toxicologia"
        ],
        "hospitalesIds": [
          "HOSP001",
          "HOSP006",
          "HOSP010",
          "HOSP014",
          "HOSP016",
          "HOSP023",
          "HOSP025",
          "HOSP027"
        ]
      },
      {
        "clusterId": 3,
        "cantidadHospitales": 6,
        "especialidades": [
          "trauma",
          "pediatria",
          "neurologia"
        ],
        "hospitalesIds": [
          "HOSP003",
          "HOSP005",
          "HOSP020",
          "HOSP024",
          "HOSP029",
          "HOSP030"
        ]
      }
    ]
  }
}
```

### Interpretación

- **Cluster 0:** Especializado en Cardiología, Trauma, Ortopedia (8 hospitales)
- **Cluster 1:** Especializado en Pediatría, Ortopedia (8 hospitales)
- **Cluster 2:** Especializado en Quemados, Toxicología (8 hospitales)
- **Cluster 3:** Especializado en Trauma, Pediatría, Neurología (6 hospitales)

---

## 🩺 Ejemplo 3: Evaluar Paciente (RANDOM FOREST)

### Escenario: Paciente con Problema Cardíaco Severo

**Datos del Paciente:**
- Hombre de 68 años
- Presión: 185/115 mmHg (hipertensión severa)
- Frecuencia cardíaca: 125 bpm (taquicardia)
- Saturación de oxígeno: 86% (baja)
- Nivel de dolor: 10/10
- Temperatura: 38.8°C (fiebre)

### Configuración en Postman

- **Método:** `POST`
- **URL:** `http://localhost:8000/graphql`
- **Body (raw - JSON):**

```json
{
  "query": "query { evaluarPaciente(datosPaciente: { edad: 68, sexo: \"M\", presionSistolica: 185, presionDiastolica: 115, frecuenciaCardiaca: 125, frecuenciaRespiratoria: 28, temperatura: 38.8, saturacionOxigeno: 86, nivelDolor: 10, tipoIncidente: \"problema_cardiaco\", tiempoDesdeIncidente: 12 }) { severidad confianza requiereTraslado tipoIncidente probabilidades { critico alto medio bajo } } }"
}
```

### Respuesta Esperada

```json
{
  "data": {
    "evaluarPaciente": {
      "severidad": "alto",
      "confianza": 51.75,
      "requiereTraslado": true,
      "tipoIncidente": "problema_cardiaco",
      "probabilidades": {
        "critico": 0.115,
        "alto": 0.5175,
        "medio": 0.326,
        "bajo": 0.041
      }
    }
  }
}
```

### Interpretación

- ✅ **Severidad:** ALTO (requiere atención urgente)
- ✅ **Confianza:** 51.75% (modelo tiene confianza media-alta)
- ✅ **Requiere traslado:** SÍ (debe ir a hospital)
- 📊 **Probabilidades:**
  - Crítico: 11.5%
  - **Alto: 51.75%** ← Predicción del modelo
  - Medio: 32.6%
  - Bajo: 4.1%

---

## 🚑 Ejemplo 4: Recomendar Hospitales (SISTEMA COMPLETO)

### Escenario: Mismo Paciente + Ubicación GPS

**Ubicación del Paciente:**
- Latitud: -12.0464 (Lima Centro)
- Longitud: -77.0428

### Configuración en Postman

- **Método:** `POST`
- **URL:** `http://localhost:8000/graphql`
- **Body (raw - JSON):**

```json
{
  "query": "query { recomendarHospitales(datosPaciente: { edad: 68, sexo: \"M\", presionSistolica: 185, presionDiastolica: 115, frecuenciaCardiaca: 125, frecuenciaRespiratoria: 28, temperatura: 38.8, saturacionOxigeno: 86, nivelDolor: 10, tipoIncidente: \"problema_cardiaco\", tiempoDesdeIncidente: 12 }, ubicacionPaciente: { latitud: -12.0464, longitud: -77.0428 }, topN: 3) { evaluacion { severidad confianza requiereTraslado } clusterUtilizado especialidadesCluster hospitalesRecomendados { hospitalId nombre distanciaKm nivel disponibilidadPorcentaje capacidad { actual maxima } } totalDisponibles mensaje } }"
}
```

### Respuesta Esperada

```json
{
  "data": {
    "recomendarHospitales": {
      "evaluacion": {
        "severidad": "alto",
        "confianza": 51.75,
        "requiereTraslado": true
      },
      "clusterUtilizado": 0,
      "especialidadesCluster": [
        "cardiologia",
        "trauma",
        "ortopedia",
        "quemados"
      ],
      "hospitalesRecomendados": [
        {
          "hospitalId": "HOSP008",
          "nombre": "Hospital San José #8",
          "distanciaKm": 1613.1,
          "nivel": "II",
          "disponibilidadPorcentaje": 32.0,
          "capacidad": {
            "actual": 34,
            "maxima": 50
          }
        },
        {
          "hospitalId": "HOSP019",
          "nombre": "Hospital San José #19",
          "distanciaKm": 1613.3,
          "nivel": "II",
          "disponibilidadPorcentaje": 38.0,
          "capacidad": {
            "actual": 31,
            "maxima": 50
          }
        },
        {
          "hospitalId": "HOSP015",
          "nombre": "Hospital Del Norte #15",
          "distanciaKm": 1618.35,
          "nivel": "II",
          "disponibilidadPorcentaje": 86.0,
          "capacidad": {
            "actual": 7,
            "maxima": 50
          }
        }
      ],
      "totalDisponibles": 8,
      "mensaje": "Se encontraron 3 hospitales adecuados."
    }
  }
}
```

### Interpretación del Flujo Completo

1. **Evaluación (Random Forest):**
   - Severidad: ALTO
   - Requiere traslado: SÍ

2. **Clustering (K-means):**
   - Tipo incidente: `problema_cardiaco`
   - Cluster seleccionado: **0** (Cardiología)
   - Especialidades del cluster: Cardiología, Trauma, Ortopedia

3. **Filtrado:**
   - Hospitales disponibles en cluster 0: **8 hospitales**
   - Hospitales con capacidad disponible: Todos

4. **Ordenamiento por Distancia GPS:**
   - **1º Hospital San José #8:** 1613.1 km, 32% disponible (16 camas libres)
   - **2º Hospital San José #19:** 1613.3 km, 38% disponible (19 camas libres)
   - **3º Hospital Del Norte #15:** 1618.35 km, 86% disponible (43 camas libres)

5. **Recomendación:**
   - **Hospital Del Norte #15** es la mejor opción (más disponibilidad)
   - Todos tienen especialidad en cardiología
   - Todos son nivel II o superior

---

## 🧪 Ejemplo 5: Otros Tipos de Incidentes

### 5.1 Trauma (Accidente Auto)

```json
{
  "query": "query { evaluarPaciente(datosPaciente: { edad: 32, sexo: \"F\", presionSistolica: 95, presionDiastolica: 60, frecuenciaCardiaca: 115, frecuenciaRespiratoria: 24, temperatura: 36.5, saturacionOxigeno: 92, nivelDolor: 8, tipoIncidente: \"accidente_auto\", tiempoDesdeIncidente: 8 }) { severidad confianza requiereTraslado } }"
}
```

**Resultado esperado:**
- Cluster: **0 o 3** (Trauma)
- Severidad: ALTO o MEDIO

---

### 5.2 Quemadura

```json
{
  "query": "query { evaluarPaciente(datosPaciente: { edad: 45, sexo: \"M\", presionSistolica: 130, presionDiastolica: 85, frecuenciaCardiaca: 95, frecuenciaRespiratoria: 20, temperatura: 37.2, saturacionOxigeno: 96, nivelDolor: 9, tipoIncidente: \"quemadura\", tiempoDesdeIncidente: 15 }) { severidad confianza requiereTraslado } }"
}
```

**Resultado esperado:**
- Cluster: **2** (Quemados, Toxicología)
- Severidad: ALTO

---

### 5.3 Fractura (No Requiere Traslado)

```json
{
  "query": "query { evaluarPaciente(datosPaciente: { edad: 25, sexo: \"M\", presionSistolica: 120, presionDiastolica: 80, frecuenciaCardiaca: 75, frecuenciaRespiratoria: 16, temperatura: 36.8, saturacionOxigeno: 98, nivelDolor: 5, tipoIncidente: \"fractura\", tiempoDesdeIncidente: 30 }) { severidad confianza requiereTraslado } }"
}
```

**Resultado esperado:**
- Severidad: BAJO o MEDIO
- Requiere traslado: NO
- Recomendación: Atención in situ

---

## 📝 Tipos de Incidentes Disponibles

| Tipo de Incidente | Cluster Recomendado | Especialidad |
|-------------------|---------------------|--------------|
| `problema_cardiaco` | 0 | Cardiología |
| `problema_respiratorio` | 0 o General | General |
| `accidente_auto` | 0 o 3 | Trauma |
| `fractura` | 0 o 1 | Ortopedia |
| `caida` | 0 o 1 | Ortopedia |
| `quemadura` | 2 | Quemados |
| `intoxicacion` | 2 | Toxicología |
| `dolor_abdominal` | General | General |
| `alergia_severa` | General | General |
| `herida_punzante` | 0 o 3 | Trauma |

---

## 🎯 Query Formateada (Para GraphiQL)

Si usas GraphiQL en el navegador (http://localhost:8000/graphql), puedes usar este formato más legible:

```graphql
query RecomendarHospitales {
  recomendarHospitales(
    datosPaciente: {
      edad: 68
      sexo: "M"
      presionSistolica: 185
      presionDiastolica: 115
      frecuenciaCardiaca: 125
      frecuenciaRespiratoria: 28
      temperatura: 38.8
      saturacionOxigeno: 86
      nivelDolor: 10
      tipoIncidente: "problema_cardiaco"
      tiempoDesdeIncidente: 12
    }
    ubicacionPaciente: {
      latitud: -12.0464
      longitud: -77.0428
    }
    topN: 3
  ) {
    evaluacion {
      severidad
      confianza
      requiereTraslado
      probabilidades {
        critico
        alto
        medio
        bajo
      }
    }
    clusterUtilizado
    especialidadesCluster
    hospitalesRecomendados {
      hospitalId
      nombre
      distanciaKm
      nivel
      disponibilidadPorcentaje
      capacidad {
        actual
        maxima
      }
    }
    totalDisponibles
    mensaje
  }
}
```

---

## 🔍 Troubleshooting en Postman

### Error: "Connection refused"

**Causa:** El servidor no está corriendo

**Solución:**
```bash
python iniciar_servidor.py
```

---

### Error: "Failed to fetch"

**Causa:** URL incorrecta

**Solución:** Verifica que la URL sea exactamente:
```
http://localhost:8000/graphql
```

---

### Error: "Cannot query field..."

**Causa:** Error en la sintaxis de la query

**Solución:** Copia exactamente los ejemplos de esta guía

---

### Error: "Faltan campos requeridos"

**Causa:** No enviaste todos los campos del paciente

**Solución:** Asegúrate de incluir TODOS estos campos:
- edad
- sexo
- presionSistolica
- presionDiastolica
- frecuenciaCardiaca
- **frecuenciaRespiratoria** ← No olvides este
- temperatura
- saturacionOxigeno
- nivelDolor
- tipoIncidente
- tiempoDesdeIncidente

---

## 📊 Colección de Postman Completa

Te recomiendo crear estas 5 requests en tu colección:

1. **Health Check** (GET)
   - URL: `http://localhost:8000/health`

2. **Estadísticas Sistema** (POST)
   - Query: `estadisticasSistema`

3. **Obtener Clusters** (POST)
   - Query: `obtenerClusters`

4. **Evaluar Paciente** (POST)
   - Query: `evaluarPaciente`

5. **Recomendar Hospitales** (POST)
   - Query: `recomendarHospitales`

---

## ✅ Checklist de Prueba

- [ ] Health check responde OK
- [ ] Estadísticas del sistema muestra 30 hospitales
- [ ] Clusters devuelve 4 clusters
- [ ] Evaluación de paciente retorna severidad
- [ ] Recomendación de hospitales retorna TOP 3
- [ ] Todos los hospitales tienen especialidad correcta
- [ ] Hospitales ordenados por distancia

---

**¡Tu API GraphQL está lista para usar!** 🚀

Para más detalles técnicos, revisa:
- `README.md` - Documentación completa
- `GUIA_INICIO_RAPIDO.md` - Cómo iniciar el servidor
