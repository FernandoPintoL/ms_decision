"""
Schema GraphQL principal.
Capa: PRESENTACION
Responsabilidad: Definir Queries y Mutations de la API.
Estándares: PEP 8, Type hints, Docstrings
"""

from typing import List, Optional
import strawberry
from strawberry.types import Info

from .tipos import (
    RecomendacionHospitales,
    EvaluacionPaciente,
    InfoCluster,
    DatosPacienteInput,
    UbicacionInput,
    EstadisticasSistema,
    ProbabilidadSeveridad,
    Hospital,
    Capacidad,
    Ubicacion,
)


def get_servicio_decision(info: Info):
    """Obtiene el servicio de decisión del contexto."""
    return info.context["servicio_decision"]


@strawberry.type
class Query:
    """Queries disponibles en la API GraphQL."""

    @strawberry.field
    def evaluar_paciente(
        self,
        info: Info,
        datos_paciente: DatosPacienteInput
    ) -> EvaluacionPaciente:
        """
        Evalúa la severidad de un paciente usando Random Forest.

        Args:
            datos_paciente: Datos del paciente (signos vitales, etc.)

        Returns:
            EvaluacionPaciente con severidad y probabilidades

        Example (GraphQL):
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
                probabilidades {
                  critico
                  alto
                  medio
                  bajo
                }
              }
            }
        """
        servicio = get_servicio_decision(info)

        # Convertir input a dict
        datos_dict = {
            'edad': datos_paciente.edad,
            'sexo': datos_paciente.sexo,
            'presion_sistolica': datos_paciente.presion_sistolica,
            'presion_diastolica': datos_paciente.presion_diastolica,
            'frecuencia_cardiaca': datos_paciente.frecuencia_cardiaca,
            'frecuencia_respiratoria': datos_paciente.frecuencia_respiratoria,
            'temperatura': datos_paciente.temperatura,
            'saturacion_oxigeno': datos_paciente.saturacion_oxigeno,
            'nivel_dolor': datos_paciente.nivel_dolor,
            'tipo_incidente': datos_paciente.tipo_incidente,
            'tiempo_desde_incidente': datos_paciente.tiempo_desde_incidente,
        }

        # Evaluar con servicio de negocio
        evaluacion = servicio.evaluar_paciente(datos_dict)

        # Convertir a tipo GraphQL
        probs = evaluacion['probabilidades']
        return EvaluacionPaciente(
            severidad=evaluacion['severidad'],
            probabilidades=ProbabilidadSeveridad(
                critico=probs.get('critico', probs.get('crítico', 0.0)),
                alto=probs.get('alto', 0.0),
                medio=probs.get('medio', 0.0),
                bajo=probs.get('bajo', 0.0)
            ),
            confianza=evaluacion['confianza'],
            requiere_traslado=evaluacion['requiere_traslado'],
            tipo_incidente=evaluacion['tipo_incidente']
        )

    @strawberry.field
    def recomendar_hospitales(
        self,
        info: Info,
        datos_paciente: DatosPacienteInput,
        ubicacion_paciente: UbicacionInput,
        top_n: int = 5
    ) -> RecomendacionHospitales:
        """
        Recomienda hospitales usando ML (Random Forest + K-means).

        Args:
            datos_paciente: Datos del paciente
            ubicacion_paciente: Ubicación GPS del paciente
            top_n: Número de hospitales a recomendar (default: 5)

        Returns:
            RecomendacionHospitales con evaluación y hospitales recomendados

        Example (GraphQL):
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
                topN: 5
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
                }
                totalDisponibles
                mensaje
              }
            }
        """
        servicio = get_servicio_decision(info)

        # Convertir inputs a dicts
        datos_dict = {
            'edad': datos_paciente.edad,
            'sexo': datos_paciente.sexo,
            'presion_sistolica': datos_paciente.presion_sistolica,
            'presion_diastolica': datos_paciente.presion_diastolica,
            'frecuencia_cardiaca': datos_paciente.frecuencia_cardiaca,
            'frecuencia_respiratoria': datos_paciente.frecuencia_respiratoria,
            'temperatura': datos_paciente.temperatura,
            'saturacion_oxigeno': datos_paciente.saturacion_oxigeno,
            'nivel_dolor': datos_paciente.nivel_dolor,
            'tipo_incidente': datos_paciente.tipo_incidente,
            'tiempo_desde_incidente': datos_paciente.tiempo_desde_incidente,
        }

        ubicacion_dict = {
            'latitud': ubicacion_paciente.latitud,
            'longitud': ubicacion_paciente.longitud
        }

        # Obtener recomendación del servicio
        recomendacion = servicio.recomendar_hospitales(
            datos_dict,
            ubicacion_dict,
            top_n
        )

        # Convertir evaluación
        probs_rec = recomendacion['evaluacion']['probabilidades']
        evaluacion = EvaluacionPaciente(
            severidad=recomendacion['evaluacion']['severidad'],
            probabilidades=ProbabilidadSeveridad(
                critico=probs_rec.get('critico', probs_rec.get('crítico', 0.0)),
                alto=probs_rec.get('alto', 0.0),
                medio=probs_rec.get('medio', 0.0),
                bajo=probs_rec.get('bajo', 0.0)
            ),
            confianza=recomendacion['evaluacion']['confianza'],
            requiere_traslado=recomendacion['evaluacion']['requiere_traslado'],
            tipo_incidente=recomendacion['evaluacion']['tipo_incidente']
        )

        # Convertir hospitales
        hospitales = []
        for h in recomendacion['hospitales_recomendados']:
            hospital = Hospital(
                hospital_id=h['hospital_id'],
                nombre=h['nombre'],
                ubicacion=Ubicacion(
                    latitud=h['ubicacion']['latitud'],
                    longitud=h['ubicacion']['longitud']
                ),
                capacidad=Capacidad(
                    actual=h['capacidad']['actual'],
                    maxima=h['capacidad']['maxima'],
                    disponibilidad_porcentaje=h.get('disponibilidad_porcentaje', 0.0)
                ),
                nivel=h['nivel'],
                distancia_km=h.get('distancia_km'),
                disponibilidad_porcentaje=h.get('disponibilidad_porcentaje')
            )
            hospitales.append(hospital)

        return RecomendacionHospitales(
            evaluacion=evaluacion,
            cluster_utilizado=recomendacion.get('cluster_utilizado'),
            especialidades_cluster=recomendacion.get('especialidades_cluster', []),
            hospitales_recomendados=hospitales,
            total_disponibles=recomendacion['total_disponibles'],
            mensaje=recomendacion['mensaje']
        )

    @strawberry.field
    def obtener_clusters(self, info: Info) -> List[InfoCluster]:
        """
        Obtiene información de todos los clusters de hospitales.

        Returns:
            Lista de InfoCluster con datos de cada cluster

        Example (GraphQL):
            query {
              obtenerClusters {
                clusterId
                cantidadHospitales
                especialidades
                hospitalesIds
              }
            }
        """
        servicio = get_servicio_decision(info)
        clusters_info = servicio.obtener_estadisticas_clusters()

        resultado = []
        for cluster_id, info_dict in clusters_info.items():
            cluster = InfoCluster(
                cluster_id=cluster_id,
                cantidad_hospitales=len(info_dict['hospitales']),
                especialidades=info_dict['especialidades'],
                hospitales_ids=info_dict['hospitales']
            )
            resultado.append(cluster)

        return resultado

    @strawberry.field
    def estadisticas_sistema(self, info: Info) -> EstadisticasSistema:
        """
        Obtiene estadísticas generales del sistema.

        Returns:
            EstadisticasSistema con métricas del sistema

        Example (GraphQL):
            query {
              estadisticasSistema {
                totalHospitales
                hospitalesDisponibles
                clustersActivos
                modelosCargados
              }
            }
        """
        servicio = get_servicio_decision(info)

        # Obtener todos los hospitales
        repo = servicio.repo_hospitales
        todos_hospitales = repo.obtener_todos()
        disponibles = repo.obtener_disponibles()

        # Obtener clusters
        clusters_info = servicio.obtener_estadisticas_clusters()

        return EstadisticasSistema(
            total_hospitales=len(todos_hospitales),
            hospitales_disponibles=len(disponibles),
            clusters_activos=len(clusters_info),
            modelos_cargados=True
        )


# ============================================================================
# APOLLO FEDERATION SCHEMA
# ============================================================================
# Schema configurado para Apollo Federation v2
# Expone entities (Paciente, Emergencia) para que el Gateway pueda combinar
# datos de múltiples microservicios
# ============================================================================

schema = strawberry.federation.Schema(
    query=Query,
    enable_federation_2=True,
    types=[
        # Importar entities para que Apollo Gateway las descubra
        __import__('presentacion.gql.tipos', fromlist=['Paciente']).Paciente,
        __import__('presentacion.gql.tipos', fromlist=['Emergencia']).Emergencia,
    ]
)
