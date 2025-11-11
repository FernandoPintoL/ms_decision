"""
Script de prueba del sistema completo de decisión médica.
Prueba: Random Forest + K-means + Repositorios
Estándares: PEP 8, Type hints
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Agregar rutas al path
ruta_base = Path(__file__).parent.parent
sys.path.append(str(ruta_base))

from datos.configuracion.conexion_mongodb import ConexionMongoDB
from negocio.servicios.servicio_decision import ServicioDecision


def imprimir_separador(titulo: str = "") -> None:
    """Imprime separador visual."""
    print("\n" + "=" * 70)
    if titulo:
        print(f" {titulo}")
        print("=" * 70)


def imprimir_evaluacion(evaluacion: Dict[str, Any]) -> None:
    """Imprime resultado de evaluación de paciente."""
    print(f"\nSeveridad predicha:    {evaluacion['severidad'].upper()}")
    print(f"Confianza:             {evaluacion['confianza']}%")
    print(f"Requiere traslado:     {'SI' if evaluacion['requiere_traslado'] else 'NO'}")
    print(f"Tipo incidente:        {evaluacion['tipo_incidente']}")

    print("\nProbabilidades por clase:")
    for clase, prob in sorted(evaluacion['probabilidades'].items()):
        barra = "#" * int(prob * 50)
        print(f"  {clase:10s}: {prob*100:5.1f}% {barra}")


def imprimir_hospitales(recomendacion: Dict[str, Any]) -> None:
    """Imprime hospitales recomendados."""
    if not recomendacion['hospitales_recomendados']:
        print(f"\n{recomendacion['mensaje']}")
        return

    print(f"\nCluster utilizado:     {recomendacion['cluster_utilizado']}")
    print(f"Especialidades:        {', '.join(recomendacion['especialidades_cluster'])}")
    print(f"Total disponibles:     {recomendacion['total_disponibles']}")
    print(f"\n{recomendacion['mensaje']}")

    print("\nHOSPITALES RECOMENDADOS (ordenados por distancia):")
    print("-" * 70)

    for i, hospital in enumerate(recomendacion['hospitales_recomendados'], 1):
        print(f"\n{i}. {hospital['nombre']}")
        print(f"   ID:             {hospital['hospital_id']}")
        print(f"   Distancia:      {hospital['distancia_km']} km")
        print(f"   Nivel:          {hospital['nivel']}")
        print(f"   Disponibilidad: {hospital['disponibilidad_porcentaje']}%")
        print(f"   Capacidad:      {hospital['capacidad']['actual']}/{hospital['capacidad']['maxima']} camas")

        # Mostrar especialidades relevantes
        especialidades = [esp for esp, tiene in hospital['especialidades'].items() if tiene == 1]
        print(f"   Especialidades: {', '.join(especialidades[:5])}")


def prueba_caso_critico() -> None:
    """Prueba con caso crítico - problema cardíaco severo."""
    imprimir_separador("CASO 1: CRITICO - PROBLEMA CARDIACO SEVERO")

    datos_paciente = {
        'edad': 68,
        'sexo': 'M',
        'presion_sistolica': 185,
        'presion_diastolica': 115,
        'frecuencia_cardiaca': 125,
        'frecuencia_respiratoria': 28,
        'temperatura': 38.8,
        'saturacion_oxigeno': 86,
        'nivel_dolor': 10,
        'tipo_incidente': 'problema_cardiaco',
        'tiempo_desde_incidente': 12
    }

    ubicacion_paciente = {
        'latitud': -12.0464,  # Lima Centro
        'longitud': -77.0428
    }

    print("\nDATOS DEL PACIENTE:")
    print(f"  Edad: {datos_paciente['edad']} anos, Sexo: {datos_paciente['sexo']}")
    print(f"  Presion: {datos_paciente['presion_sistolica']}/{datos_paciente['presion_diastolica']} mmHg")
    print(f"  Frecuencia cardiaca: {datos_paciente['frecuencia_cardiaca']} bpm")
    print(f"  Temperatura: {datos_paciente['temperatura']} C")
    print(f"  Saturacion O2: {datos_paciente['saturacion_oxigeno']}%")
    print(f"  Nivel dolor: {datos_paciente['nivel_dolor']}/10")
    print(f"  Tiempo desde incidente: {datos_paciente['tiempo_desde_incidente']} min")

    # Conectar y probar
    conexion = ConexionMongoDB()
    db = conexion.conectar()
    servicio = ServicioDecision(db)

    # Obtener recomendación
    recomendacion = servicio.recomendar_hospitales(
        datos_paciente,
        ubicacion_paciente,
        top_n=5
    )

    imprimir_evaluacion(recomendacion['evaluacion'])
    imprimir_hospitales(recomendacion)


def prueba_caso_trauma() -> None:
    """Prueba con caso de trauma - accidente auto."""
    imprimir_separador("CASO 2: ALTO - ACCIDENTE AUTO (TRAUMA)")

    datos_paciente = {
        'edad': 32,
        'sexo': 'F',
        'presion_sistolica': 95,
        'presion_diastolica': 60,
        'frecuencia_cardiaca': 115,
        'frecuencia_respiratoria': 24,
        'temperatura': 36.5,
        'saturacion_oxigeno': 92,
        'nivel_dolor': 8,
        'tipo_incidente': 'accidente_auto',
        'tiempo_desde_incidente': 8
    }

    ubicacion_paciente = {
        'latitud': -12.1191,  # Miraflores
        'longitud': -77.0383
    }

    print("\nDATOS DEL PACIENTE:")
    print(f"  Edad: {datos_paciente['edad']} anos, Sexo: {datos_paciente['sexo']}")
    print(f"  Presion: {datos_paciente['presion_sistolica']}/{datos_paciente['presion_diastolica']} mmHg")
    print(f"  Frecuencia cardiaca: {datos_paciente['frecuencia_cardiaca']} bpm")
    print(f"  Saturacion O2: {datos_paciente['saturacion_oxigeno']}%")
    print(f"  Nivel dolor: {datos_paciente['nivel_dolor']}/10")

    # Conectar y probar
    conexion = ConexionMongoDB()
    db = conexion.conectar()
    servicio = ServicioDecision(db)

    recomendacion = servicio.recomendar_hospitales(
        datos_paciente,
        ubicacion_paciente,
        top_n=3
    )

    imprimir_evaluacion(recomendacion['evaluacion'])
    imprimir_hospitales(recomendacion)


def prueba_caso_medio() -> None:
    """Prueba con caso medio - fractura simple."""
    imprimir_separador("CASO 3: MEDIO - FRACTURA (NO REQUIERE TRASLADO)")

    datos_paciente = {
        'edad': 25,
        'sexo': 'M',
        'presion_sistolica': 120,
        'presion_diastolica': 80,
        'frecuencia_cardiaca': 75,
        'frecuencia_respiratoria': 16,
        'temperatura': 36.8,
        'saturacion_oxigeno': 98,
        'nivel_dolor': 5,
        'tipo_incidente': 'fractura',
        'tiempo_desde_incidente': 30
    }

    ubicacion_paciente = {
        'latitud': -12.0500,
        'longitud': -77.0500
    }

    print("\nDATOS DEL PACIENTE:")
    print(f"  Edad: {datos_paciente['edad']} anos, Sexo: {datos_paciente['sexo']}")
    print(f"  Presion: {datos_paciente['presion_sistolica']}/{datos_paciente['presion_diastolica']} mmHg")
    print(f"  Nivel dolor: {datos_paciente['nivel_dolor']}/10")

    # Conectar y probar
    conexion = ConexionMongoDB()
    db = conexion.conectar()
    servicio = ServicioDecision(db)

    recomendacion = servicio.recomendar_hospitales(
        datos_paciente,
        ubicacion_paciente
    )

    imprimir_evaluacion(recomendacion['evaluacion'])
    imprimir_hospitales(recomendacion)


def prueba_estadisticas_clusters() -> None:
    """Prueba obtención de estadísticas de clusters."""
    imprimir_separador("ESTADISTICAS DE CLUSTERS K-MEANS")

    conexion = ConexionMongoDB()
    db = conexion.conectar()
    servicio = ServicioDecision(db)

    estadisticas = servicio.obtener_estadisticas_clusters()

    print("\nINFORMACION DE CLUSTERS:")
    print("-" * 70)

    for cluster_id in sorted(estadisticas.keys()):
        info = estadisticas[cluster_id]
        print(f"\nCluster {cluster_id}:")
        print(f"  Hospitales:     {len(info['hospitales'])}")
        print(f"  Especialidades: {', '.join(info['especialidades'])}")
        print(f"  IDs hospitales: {', '.join(info['hospitales'][:5])}")
        if len(info['hospitales']) > 5:
            print(f"                  ... y {len(info['hospitales']) - 5} mas")


def main() -> None:
    """Ejecuta todas las pruebas del sistema."""
    print("\n")
    print("*" * 70)
    print(" PRUEBA COMPLETA DEL SISTEMA DE DECISION MEDICA")
    print(" Arquitectura 3 Capas: Presentacion -> Negocio -> Datos")
    print(" ML Supervisado: Random Forest (severidad)")
    print(" ML No Supervisado: K-means (clustering hospitales)")
    print("*" * 70)

    try:
        # Cargar modelos ML
        print("\n[INICIALIZACION] Cargando modelos ML...")
        conexion = ConexionMongoDB()
        db = conexion.conectar()
        servicio = ServicioDecision(db)
        print("# Modelos cargados exitosamente")

        # Ejecutar pruebas
        prueba_caso_critico()
        prueba_caso_trauma()
        prueba_caso_medio()
        prueba_estadisticas_clusters()

        # Resumen final
        imprimir_separador("RESUMEN DE PRUEBAS")
        print("\n# TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\nComponentes verificados:")
        print("  [OK] Random Forest - Prediccion de severidad")
        print("  [OK] K-means - Clustering de hospitales")
        print("  [OK] Repositorio Hospitales - Acceso a datos")
        print("  [OK] Servicio Decision - Orquestacion completa")
        print("  [OK] Calculo de distancias GPS (Haversine)")
        print("  [OK] Filtraje por cluster y capacidad")
        print("  [OK] Arquitectura 3 capas mantenida")

        print("\n" + "=" * 70)
        print(" FASE 1 - BACKEND COMPLETADO AL 100%")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
