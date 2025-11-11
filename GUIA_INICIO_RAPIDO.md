# Guía de Inicio Rápido - Microservicio de Decisión Médica

## 🚀 Cómo Iniciar el Backend

### Opción 1: Usando el Script Automatizado (RECOMENDADO)

**Paso 1:** Abre una terminal en la carpeta `ServicioDecision`

**Paso 2:** Ejecuta el script de inicio:

```bash
iniciar_servidor.bat
```

Esto hará automáticamente:
- ✅ Activar el entorno virtual
- ✅ Verificar/iniciar MongoDB
- ✅ Iniciar el servidor GraphQL en puerto 8000

**Resultado esperado:**
```
============================================================
SERVIDOR LISTO
============================================================

API GraphQL:     http://localhost:8000/graphql
GraphiQL IDE:    http://localhost:8000/graphql (navegador)
Health Check:    http://localhost:8000/health

Para detener el servidor presiona CTRL+C
============================================================
```

---

### Opción 2: Inicio Manual (Paso a Paso)

#### 1. Iniciar MongoDB

Abre una terminal y ejecuta:

```bash
"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "D:/mongodb_data/db" --port 27017
```

**Deja esta terminal abierta** (MongoDB debe estar corriendo).

#### 2. Activar Entorno Virtual

Abre **OTRA terminal** en la carpeta `ServicioDecision` y ejecuta:

```bash
# Windows
.venv\Scripts\activate

# Verás que aparece (.venv) al inicio de la línea
```

#### 3. Iniciar Servidor GraphQL

En la misma terminal (con .venv activado):

```bash
uvicorn presentacion.servidor:app --host 127.0.0.1 --port 8000 --reload
```

**Resultado esperado:**
```
============================================================
INICIANDO MICROSERVICIO DE DECISION MEDICA
============================================================

[1/3] Conectando a MongoDB...
>> Conectado a MongoDB: servicio_decision
   # MongoDB conectado

[2/3] Cargando modelos ML...
   # Random Forest cargado
   # K-means cargado

[3/3] Servidor GraphQL listo
============================================================
API GraphQL disponible en: http://localhost:8000/graphql
============================================================

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## ✅ Verificar que Todo Funciona

### Opción A: Desde el Navegador

1. Abre tu navegador
2. Ve a: http://localhost:8000/graphql
3. Deberías ver **GraphiQL IDE** (interfaz interactiva)

### Opción B: Health Check

Abre http://localhost:8000/health

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected",
  "ml_models": "loaded"
}
```

### Opción C: Script de Prueba

En otra terminal (con .venv activado):

```bash
python pruebas/probar_api_graphql.py
```

---

## 🔧 Solución de Problemas

### Error: "MongoDB no está corriendo"

**Solución:**
```bash
"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "D:/mongodb_data/db" --port 27017
```

Verifica con:
```bash
tasklist | findstr mongod
```

### Error: "Puerto 8000 en uso"

**Solución:** Mata el proceso que usa el puerto:
```bash
# Encuentra el proceso
netstat -ano | findstr :8000

# Mata el proceso (reemplaza <PID> con el número que aparece)
taskkill /PID <PID> /F
```

### Error: "No se encuentra uvicorn"

**Solución:** Asegúrate de activar el entorno virtual primero:
```bash
.venv\Scripts\activate
```

Si aún no funciona, reinstala:
```bash
pip install uvicorn
```

---

## 📱 Probar con Postman

### 1. Configurar Postman

**a) Crear nueva Request:**
- Método: **POST**
- URL: `http://localhost:8000/graphql`
- Headers:
  - `Content-Type: application/json`

**b) Configurar Body:**
- Selecciona **raw**
- Selecciona **JSON**

---

### 2. Ejemplos de Queries

#### Ejemplo 1: Evaluar Paciente

```json
{
  "query": "query { evaluarPaciente(datosPaciente: { edad: 68, sexo: \"M\", presionSistolica: 185, presionDiastolica: 115, frecuenciaCardiaca: 125, frecuenciaRespiratoria: 28, temperatura: 38.8, saturacionOxigeno: 86, nivelDolor: 10, tipoIncidente: \"problema_cardiaco\", tiempoDesdeIncidente: 12 }) { severidad confianza requiereTraslado probabilidades { critico alto medio bajo } } }"
}
```

**Respuesta esperada:**
```json
{
  "data": {
    "evaluarPaciente": {
      "severidad": "alto",
      "confianza": 51.75,
      "requiereTraslado": true,
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

---

#### Ejemplo 2: Recomendar Hospitales

```json
{
  "query": "query { recomendarHospitales(datosPaciente: { edad: 68, sexo: \"M\", presionSistolica: 185, presionDiastolica: 115, frecuenciaCardiaca: 125, frecuenciaRespiratoria: 28, temperatura: 38.8, saturacionOxigeno: 86, nivelDolor: 10, tipoIncidente: \"problema_cardiaco\", tiempoDesdeIncidente: 12 }, ubicacionPaciente: { latitud: -12.0464, longitud: -77.0428 }, topN: 3) { evaluacion { severidad confianza requiereTraslado } clusterUtilizado especialidadesCluster hospitalesRecomendados { hospitalId nombre distanciaKm nivel disponibilidadPorcentaje } totalDisponibles mensaje } }"
}
```

**Respuesta esperada:**
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
      "especialidadesCluster": ["cardiologia", "trauma", "ortopedia"],
      "hospitalesRecomendados": [
        {
          "hospitalId": "HOSP008",
          "nombre": "Hospital San José #8",
          "distanciaKm": 1613.1,
          "nivel": "II",
          "disponibilidadPorcentaje": 32.0
        }
      ],
      "totalDisponibles": 8,
      "mensaje": "Se encontraron 3 hospitales adecuados."
    }
  }
}
```

---

#### Ejemplo 3: Obtener Clusters

```json
{
  "query": "query { obtenerClusters { clusterId cantidadHospitales especialidades hospitalesIds } }"
}
```

---

#### Ejemplo 4: Estadísticas del Sistema

```json
{
  "query": "query { estadisticasSistema { totalHospitales hospitalesDisponibles clustersActivos modelosCargados } }"
}
```

---

### 3. Query GraphQL Formateado (Para GraphiQL)

Si usas GraphiQL en el navegador (http://localhost:8000/graphql), puedes usar queries formateadas:

```graphql
query EvaluarPaciente {
  evaluarPaciente(datosPaciente: {
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
  }) {
    severidad
    confianza
    requiereTraslado
    tipoIncidente
    probabilidades {
      critico
      alto
      medio
      bajo
    }
  }
}
```

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

## 📊 Tipos de Incidentes Disponibles

Puedes probar con estos tipos de incidente:

- `problema_cardiaco` → Cluster de Cardiología
- `accidente_auto` → Cluster de Trauma
- `fractura` → Cluster de Ortopedia
- `caida` → Cluster de Ortopedia
- `quemadura` → Cluster de Quemados
- `intoxicacion` → Cluster de Toxicología
- `problema_respiratorio` → Cluster General
- `dolor_abdominal` → Cluster General

---

## 🎯 Flujo Completo de Uso

### Escenario: Paciente con Problema Cardíaco

1. **Iniciar servidor:** `iniciar_servidor.bat`

2. **Evaluar severidad:**
   - POST a `/graphql`
   - Query: `evaluarPaciente`
   - Resultado: `severidad: "alto"`, `requiereTraslado: true`

3. **Recomendar hospitales:**
   - POST a `/graphql`
   - Query: `recomendarHospitales`
   - Resultado: TOP 3 hospitales con especialidad en cardiología, ordenados por distancia

4. **El MS Despacho recibe la lista** y asigna ambulancia + calcula ruta

---

## 📁 Estructura de Carpetas Importante

```
ServicioDecision/
├── iniciar_servidor.bat          ← EJECUTAR ESTO PRIMERO
├── presentacion/
│   ├── servidor.py                ← Servidor FastAPI + GraphQL
│   └── graphql/
│       ├── tipos.py               ← Tipos GraphQL
│       └── schema.py              ← Queries disponibles
├── negocio/
│   ├── ml/
│   │   ├── prediccion_severidad.py   ← Random Forest
│   │   └── clustering_hospitales.py  ← K-means
│   └── servicios/
│       └── servicio_decision.py       ← Orquestador
├── datos/
│   └── repositorios/
│       └── repositorio_hospitales.py  ← MongoDB
├── modelos_ml/                    ← Modelos entrenados (.pkl)
└── pruebas/
    └── probar_api_graphql.py      ← Script de pruebas
```

---

## 🎓 Comandos Rápidos

```bash
# Iniciar todo (FÁCIL)
iniciar_servidor.bat

# Detener servidor
CTRL + C

# Probar API
python pruebas/probar_api_graphql.py

# Ver logs de MongoDB
# (en la terminal donde iniciaste mongod.exe)

# Ver health check
curl http://localhost:8000/health
```

---

## ✅ Checklist de Inicio

- [ ] MongoDB corriendo (puerto 27017)
- [ ] Entorno virtual activado (.venv)
- [ ] Servidor GraphQL corriendo (puerto 8000)
- [ ] Health check responde OK
- [ ] GraphiQL abre en navegador
- [ ] Postman puede hacer queries

---

## 🆘 ¿Necesitas Ayuda?

1. Verifica que MongoDB esté corriendo:
   ```bash
   tasklist | findstr mongod
   ```

2. Verifica que el servidor esté corriendo:
   ```bash
   curl http://localhost:8000/health
   ```

3. Revisa los logs en la terminal donde ejecutaste el servidor

4. Si todo falla, reinicia desde cero:
   ```bash
   # Mata todos los procesos
   taskkill /F /IM mongod.exe
   taskkill /F /IM python.exe
   taskkill /F /IM uvicorn.exe

   # Inicia de nuevo
   iniciar_servidor.bat
   ```

---

**¡Listo! Tu backend está funcionando al 100%** 🎉
