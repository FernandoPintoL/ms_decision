# Verificación de Apollo Federation en MS_DECISION

## ¿Qué es Apollo Federation?

Apollo Federation es un estándar que permite que múltiples microservicios GraphQL se conecten a través de un **Apollo Gateway** que actúa como un proxy inteligente.

## ¿Cómo verificar que Apollo Federation está habilitado?

### Método 1: Query `_service` (Indicador Principal)

La query más importante para verificar Apollo Federation es `_service`. Esta query retorna el **SDL (Schema Definition Language)** del servicio federado.

**Endpoint:** `POST http://localhost:8002/graphql`

**Query:**
```graphql
query {
  _service {
    sdl
  }
}
```

**Respuesta esperada:**
```json
{
  "data": {
    "_service": {
      "sdl": "schema {\n  query: Query\n}\n\ntype Query {\n  evaluarPaciente(...): EvaluacionPaciente\n  recomendarHospitales(...): RecomendacionHospitales\n..."
    }
  }
}
```

**✅ Si recibes esta respuesta, Apollo Federation ESTÁ ACTIVO**

---

### Método 2: Verificar con cURL

```bash
curl -X POST http://localhost:8002/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ _service { sdl } }"
  }'
```

**Respuesta exitosa:**
```json
{"data":{"_service":{"sdl":"..."}}}
```

---

### Método 3: Usar el script Python

He creado un script automático que verifica toda la configuración:

```bash
cd D:\SWII\micro_servicios\ms_decision
python verificar_apollo_federation.py
```

**Este script verifica:**
1. ✅ Conectividad al endpoint GraphQL
2. ✅ Query `_service` (Apollo Federation)
3. ✅ Schema Introspection
4. ✅ Entidades Federadas (Paciente, Emergencia)
5. ✅ Queries Personalizadas del servicio

---

### Método 4: Usar GraphiQL en el navegador

Abre tu navegador en:
```
http://localhost:8002/graphql
```

En la sección de queries, ejecuta:
```graphql
query {
  _service {
    sdl
  }
}
```

Si ves el SDL en la respuesta, **Apollo Federation está funcionando**.

---

## Queries importantes de Apollo Federation

### 1. **_service** (Información del Schema)
```graphql
query {
  _service {
    sdl
  }
}
```

### 2. **_entities** (Resolver de Entidades)
```graphql
query {
  _entities(representations: [
    {
      __typename: "Paciente"
      id: "123"
    }
  ]) {
    ... on Paciente {
      id
      nombre
      edad
    }
  }
}
```

### 3. **Introspection** (Schema completo)
```graphql
query {
  __schema {
    types {
      name
      kind
      fields {
        name
      }
    }
  }
}
```

---

## ¿Cómo se ve ms_decision en el Apollo Gateway?

Cuando registres ms_decision en el Apollo Gateway, verá:

```javascript
// apollo-gateway.js
const { ApolloGateway } = require("@apollo/gateway");

const gateway = new ApolloGateway({
  supergraphSdl: new IntrospectAndCompose({
    subgraphs: [
      {
        name: "ms-decision",
        url: "http://localhost:8002/graphql"  // Apollo Federation aquí
      },
      {
        name: "ms-recepcion",
        url: "http://localhost:8080/api"
      },
      // ... otros servicios
    ],
  }),
});
```

El Apollo Gateway automáticamente:
1. 🔍 Detecta que `ms-decision` soporta Federation (via `_service`)
2. 📋 Descarga el SDL del servicio
3. 🔗 Integra las entidades federadas
4. ⚡ Resuelve referencias entre servicios

---

## Evidencias de que Apollo Federation funciona

**En código:** Ver `presentacion/gql/schema.py` línea 323:

```python
schema = strawberry.federation.Schema(
    query=Query,
    enable_federation_2=True,  # ← Apollo Federation v2 habilitado
    types=[
        Paciente,      # Entity federada
        Emergencia     # Entity federada
    ]
)
```

**En runtime:** Ejecutar la query `_service` y obtener respuesta.

**En Apollo Gateway:** El gateway descubre automáticamente el servicio como subgraph.

---

## Troubleshooting

### ❌ Si la query `_service` falla:

**Error: "Cannot query field _service"**
- Significa que Apollo Federation NO está habilitado
- Solución: Verificar que `strawberry.federation.Schema` está siendo usado

### ❌ Si no se conecta al endpoint:

**Error: "Connection refused"**
- El container de ms_decision no está corriendo
- Solución: Ejecutar `docker-compose up -d` en ms_decision

### ❌ Si obtiene error de importación en Strawberry:

**Error: "ImportError: cannot import name 'is_new_type'"**
- Conflicto de versiones entre pydantic y strawberry
- Solución: Ya fue resuelta en el requirements.txt

---

## Conclusión

**Ms_decision está 100% configurado con Apollo Federation v2** y listo para ser integrado en el Apollo Gateway como subgraph. Solo necesitas confirmar que:

1. ✅ La query `_service` responde correctamente
2. ✅ El container está corriendo (`docker ps`)
3. ✅ El endpoint es accesible (`http://localhost:8002/graphql`)

Una vez confirmado, puedes registrarlo en el Apollo Gateway.
