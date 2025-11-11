"""
Script para verificar que Apollo Federation está funcionando en ms_decision
"""

import requests
import json
import time

GRAPHQL_ENDPOINT = "http://localhost:8002/graphql"
MAX_INTENTOS = 5
DELAY = 10

def hacer_query(query, variables=None):
    """
    Ejecuta una query GraphQL y retorna la respuesta
    """
    payload = {
        "query": query,
        "variables": variables or {}
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GRAPHQL_ENDPOINT, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def verificar_conexion():
    """Verifica que el endpoint GraphQL esté disponible"""
    print("=" * 70)
    print("1️⃣  VERIFICANDO CONEXIÓN AL ENDPOINT GRAPHQL")
    print("=" * 70)

    for intento in range(MAX_INTENTOS):
        try:
            response = requests.get(GRAPHQL_ENDPOINT, timeout=5)
            print(f"✅ Endpoint disponible en: {GRAPHQL_ENDPOINT}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"❌ Intento {intento + 1}/{MAX_INTENTOS}: No se pudo conectar")
            if intento < MAX_INTENTOS - 1:
                print(f"   Esperando {DELAY} segundos...")
                time.sleep(DELAY)

    print("❌ No se pudo conectar al endpoint después de varios intentos")
    return False

def verificar_apollo_federation():
    """
    Verifica que Apollo Federation esté habilitado
    La query _service es el indicador más importante
    """
    print("\n" + "=" * 70)
    print("2️⃣  VERIFICANDO APOLLO FEDERATION (_service)")
    print("=" * 70)
    print("Apollo Federation requiere responder a la query '_service'")
    print("Esta query retorna el schema federado en formato SDL\n")

    query = """
    query {
      _service {
        sdl
      }
    }
    """

    respuesta = hacer_query(query)

    if "errors" in respuesta and respuesta["errors"]:
        print(f"❌ Error en query _service:")
        for error in respuesta["errors"]:
            print(f"   - {error.get('message', 'Error desconocido')}")
        return False

    if "data" in respuesta and respuesta["data"] and respuesta["data"].get("_service"):
        sdl = respuesta["data"]["_service"]["sdl"]
        print("✅ Apollo Federation ACTIVO - _service respondió correctamente")
        print(f"\n📋 Schema SDL (primeros 500 caracteres):")
        print(f"{sdl[:500]}...")
        return True

    print("❌ Apollo Federation NO ESTÁ CONFIGURADO - _service no respondió")
    return False

def verificar_schema_introspection():
    """
    Verifica el schema completo mediante introspection
    """
    print("\n" + "=" * 70)
    print("3️⃣  VERIFICANDO SCHEMA (Introspection)")
    print("=" * 70)

    query = """
    query {
      __schema {
        queryType {
          name
          fields {
            name
          }
        }
        types {
          name
        }
      }
    }
    """

    respuesta = hacer_query(query)

    if "errors" in respuesta and respuesta["errors"]:
        print(f"❌ Error en introspection:")
        for error in respuesta["errors"]:
            print(f"   - {error.get('message', 'Error desconocido')}")
        return False

    if "data" in respuesta:
        data = respuesta["data"]
        if data and "__schema" in data:
            schema = data["__schema"]
            query_type = schema.get("queryType", {})
            fields = query_type.get("fields", [])

            print("✅ Schema Introspection funcionando")
            print(f"\n📋 Query Fields disponibles:")
            for field in fields[:10]:  # Mostrar primeros 10
                print(f"   - {field.get('name')}")

            # Verificar que _service existe (indicador de Federation)
            field_names = [f.get("name") for f in fields]
            if "_service" in field_names:
                print(f"\n✅ _service field encontrado (Apollo Federation está ACTIVO)")
                return True
            else:
                print(f"\n⚠️  _service field NO encontrado")
                return False

    return False

def verificar_entidades():
    """
    Verifica que las entidades federadas existan
    """
    print("\n" + "=" * 70)
    print("4️⃣  VERIFICANDO ENTIDADES FEDERADAS")
    print("=" * 70)

    query = """
    query {
      __type(name: "Paciente") {
        name
        kind
        fields {
          name
        }
      }
    }
    """

    respuesta = hacer_query(query)

    if "errors" in respuesta and respuesta["errors"]:
        print(f"⚠️  Tipo 'Paciente' no encontrado (puede estar sin federar)")
        return False

    if "data" in respuesta:
        tipo = respuesta["data"].get("__type")
        if tipo:
            print(f"✅ Tipo '{tipo['name']}' encontrado")
            print(f"   Kind: {tipo.get('kind')}")
            print(f"   Fields: {[f['name'] for f in tipo.get('fields', [])][:5]}")
            return True

    return False

def verificar_queries_personalizadas():
    """
    Verifica que las queries personalizadas del servicio funcionen
    """
    print("\n" + "=" * 70)
    print("5️⃣  VERIFICANDO QUERIES PERSONALIZADAS")
    print("=" * 70)

    query = """
    query {
      estadisticasSistema {
        totalHospitales
        hospitalesDisponibles
        clustersActivos
        modelosCargados
      }
    }
    """

    respuesta = hacer_query(query)

    if "errors" in respuesta and respuesta["errors"]:
        print(f"⚠️  Error en query personalizada:")
        for error in respuesta["errors"]:
            print(f"   - {error.get('message', 'Error desconocido')}")
        return False

    if "data" in respuesta and respuesta["data"].get("estadisticasSistema"):
        stats = respuesta["data"]["estadisticasSistema"]
        print("✅ Query personalizada funcionando")
        print(f"   - Total Hospitales: {stats.get('totalHospitales')}")
        print(f"   - Hospitales Disponibles: {stats.get('hospitalesDisponibles')}")
        print(f"   - Clusters Activos: {stats.get('clustersActivos')}")
        print(f"   - Modelos Cargados: {stats.get('modelosCargados')}")
        return True

    return False

def main():
    """Ejecuta todas las verificaciones"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "VERIFICADOR DE APOLLO FEDERATION" + " " * 21 + "║")
    print("║" + " " * 18 + "MS Decision GraphQL Service" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")

    resultados = {
        "Conexión": verificar_conexion(),
        "Apollo Federation (_service)": False,
        "Schema Introspection": False,
        "Entidades Federadas": False,
        "Queries Personalizadas": False
    }

    if resultados["Conexión"]:
        resultados["Apollo Federation (_service)"] = verificar_apollo_federation()
        resultados["Schema Introspection"] = verificar_schema_introspection()
        resultados["Entidades Federadas"] = verificar_entidades()
        resultados["Queries Personalizadas"] = verificar_queries_personalizadas()

    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)

    for verificacion, resultado in resultados.items():
        status = "✅ ACTIVO" if resultado else "❌ INACTIVO/ERROR"
        print(f"{verificacion:<40} {status}")

    print("=" * 70)

    # Conclusión
    if resultados.get("Apollo Federation (_service)"):
        print("\n🎉 APOLLO FEDERATION ESTÁ FUNCIONANDO CORRECTAMENTE")
        print("\nMs_decision está listo para ser usado como subgraph en Apollo Gateway")
    else:
        print("\n⚠️  APOLLO FEDERATION NO ESTÁ COMPLETAMENTE CONFIGURADO")
        print("Por favor revisa los errores anteriores")

if __name__ == "__main__":
    main()
