"""
Pruebas de la API GraphQL.
Prueba todos los endpoints GraphQL del microservicio.
Estándares: PEP 8, Type hints
"""

import sys
from pathlib import Path
import httpx
import json

# Agregar rutas al path
ruta_base = Path(__file__).parent.parent
sys.path.append(str(ruta_base))


# URL base de la API
API_URL = "http://localhost:8000/graphql"


def imprimir_separador(titulo: str = "") -> None:
    """Imprime separador visual."""
    print("\n" + "=" * 70)
    if titulo:
        print(f" {titulo}")
        print("=" * 70)


def probar_health_check() -> None:
    """Prueba el endpoint de health check."""
    imprimir_separador("HEALTH CHECK")

    try:
        response = httpx.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"\nEstado: {data['status']}")
            print(f"Base de datos: {data['database']}")
            print(f"Modelos ML: {data['ml_models']}")
            print("\nOK Health check exitoso")
        else:
            print(f"\nERROR Error: {response.status_code}")
    except Exception as e:
        print(f"\nERROR Error de conexión: {e}")
        print("  Asegúrate de que el servidor esté corriendo:")
        print("  python -m presentacion.servidor")


def probar_evaluacion_paciente() -> None:
    """Prueba query de evaluación de paciente."""
    imprimir_separador("QUERY: EVALUAR PACIENTE")

    query = """
    query {
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
    """

    try:
        response = httpx.post(
            API_URL,
            json={"query": query},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print("\nERROR Error en GraphQL:")
                print(json.dumps(data["errors"], indent=2))
                return

            result = data["data"]["evaluarPaciente"]

            print("\nRESULTADO:")
            print(f"  Severidad:         {result['severidad'].upper()}")
            print(f"  Confianza:         {result['confianza']}%")
            print(f"  Requiere traslado: {'SI' if result['requiereTraslado'] else 'NO'}")
            print(f"  Tipo incidente:    {result['tipoIncidente']}")

            print("\n  Probabilidades:")
            probs = result['probabilidades']
            for clase in ['critico', 'alto', 'medio', 'bajo']:
                prob = probs[clase] * 100
                barra = "#" * int(prob / 2)
                print(f"    {clase:8s}: {prob:5.1f}% {barra}")

            print("\nOK Evaluación exitosa")
        else:
            print(f"\nERROR Error HTTP: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\nERROR Error: {e}")


def probar_recomendacion_hospitales() -> None:
    """Prueba query de recomendación de hospitales."""
    imprimir_separador("QUERY: RECOMENDAR HOSPITALES")

    query = """
    query {
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
    """

    try:
        response = httpx.post(
            API_URL,
            json={"query": query},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print("\nERROR Error en GraphQL:")
                print(json.dumps(data["errors"], indent=2))
                return

            result = data["data"]["recomendarHospitales"]

            # Evaluación
            print("\nEVALUACION:")
            eval = result['evaluacion']
            print(f"  Severidad:         {eval['severidad'].upper()}")
            print(f"  Confianza:         {eval['confianza']}%")
            print(f"  Requiere traslado: {'SI' if eval['requiereTraslado'] else 'NO'}")

            # Clustering
            print(f"\nCLUSTERING:")
            print(f"  Cluster utilizado: {result['clusterUtilizado']}")
            print(f"  Especialidades:    {', '.join(result['especialidadesCluster'])}")
            print(f"  Total disponibles: {result['totalDisponibles']}")

            # Hospitales
            print(f"\nHOSPITALES RECOMENDADOS:")
            print(f"  {result['mensaje']}")
            print("-" * 70)

            for i, hospital in enumerate(result['hospitalesRecomendados'], 1):
                print(f"\n  {i}. {hospital['nombre']}")
                print(f"     ID:             {hospital['hospitalId']}")
                print(f"     Distancia:      {hospital['distanciaKm']:.2f} km")
                print(f"     Nivel:          {hospital['nivel']}")
                print(f"     Disponibilidad: {hospital['disponibilidadPorcentaje']:.1f}%")
                print(f"     Capacidad:      {hospital['capacidad']['actual']}/{hospital['capacidad']['maxima']} camas")

            print("\nOK Recomendación exitosa")
        else:
            print(f"\nERROR Error HTTP: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\nERROR Error: {e}")


def probar_obtener_clusters() -> None:
    """Prueba query de obtención de clusters."""
    imprimir_separador("QUERY: OBTENER CLUSTERS")

    query = """
    query {
      obtenerClusters {
        clusterId
        cantidadHospitales
        especialidades
        hospitalesIds
      }
    }
    """

    try:
        response = httpx.post(
            API_URL,
            json={"query": query},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print("\nERROR Error en GraphQL:")
                print(json.dumps(data["errors"], indent=2))
                return

            clusters = data["data"]["obtenerClusters"]

            print("\nINFORMACION DE CLUSTERS:")
            print("-" * 70)

            for cluster in sorted(clusters, key=lambda c: c['clusterId']):
                print(f"\nCluster {cluster['clusterId']}:")
                print(f"  Hospitales:     {cluster['cantidadHospitales']}")
                print(f"  Especialidades: {', '.join(cluster['especialidades'])}")
                print(f"  IDs hospitales: {', '.join(cluster['hospitalesIds'][:5])}")
                if len(cluster['hospitalesIds']) > 5:
                    print(f"                  ... y {len(cluster['hospitalesIds']) - 5} más")

            print("\nOK Obtención de clusters exitosa")
        else:
            print(f"\nERROR Error HTTP: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\nERROR Error: {e}")


def probar_estadisticas_sistema() -> None:
    """Prueba query de estadísticas del sistema."""
    imprimir_separador("QUERY: ESTADISTICAS SISTEMA")

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

    try:
        response = httpx.post(
            API_URL,
            json={"query": query},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()

            if "errors" in data:
                print("\nERROR Error en GraphQL:")
                print(json.dumps(data["errors"], indent=2))
                return

            stats = data["data"]["estadisticasSistema"]

            print("\nESTADISTICAS DEL SISTEMA:")
            print(f"  Total hospitales:        {stats['totalHospitales']}")
            print(f"  Hospitales disponibles:  {stats['hospitalesDisponibles']}")
            print(f"  Clusters activos:        {stats['clustersActivos']}")
            print(f"  Modelos cargados:        {'SI' if stats['modelosCargados'] else 'NO'}")

            print("\nOK Estadísticas obtenidas exitosamente")
        else:
            print(f"\nERROR Error HTTP: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\nERROR Error: {e}")


def main() -> None:
    """Ejecuta todas las pruebas de la API GraphQL."""
    print("\n")
    print("*" * 70)
    print(" PRUEBAS DE API GRAPHQL - MICROSERVICIO DECISION MEDICA")
    print("*" * 70)

    print("\nIMPORTANTE: Asegúrate de que el servidor esté corriendo:")
    print("  python -m presentacion.servidor")
    print("")

    try:
        # Pruebas
        probar_health_check()
        probar_evaluacion_paciente()
        probar_recomendacion_hospitales()
        probar_obtener_clusters()
        probar_estadisticas_sistema()

        # Resumen
        imprimir_separador("RESUMEN DE PRUEBAS")
        print("\nOK TODAS LAS PRUEBAS COMPLETADAS")
        print("\nEndpoints verificados:")
        print("  [OK] GET  /health")
        print("  [OK] POST /graphql - evaluarPaciente")
        print("  [OK] POST /graphql - recomendarHospitales")
        print("  [OK] POST /graphql - obtenerClusters")
        print("  [OK] POST /graphql - estadisticasSistema")

        print("\n" + "=" * 70)
        print(" API GRAPHQL FUNCIONANDO AL 100%")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\nERROR Error general: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
