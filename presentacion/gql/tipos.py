"""
Tipos GraphQL para la API.
Capa: PRESENTACION
Responsabilidad: Definir esquemas de entrada/salida GraphQL.
Estándares: PEP 8, Type hints, Docstrings
Apollo Federation: Entities compartidas con otros microservicios
"""

from typing import List, Optional
import strawberry


@strawberry.type
class ProbabilidadSeveridad:
    """Probabilidades de cada clase de severidad."""

    critico: float
    alto: float
    medio: float
    bajo: float


@strawberry.type
class EvaluacionPaciente:
    """Resultado de evaluación de severidad de un paciente."""

    severidad: str
    probabilidades: ProbabilidadSeveridad
    confianza: float
    requiere_traslado: bool
    tipo_incidente: str


@strawberry.type
class Capacidad:
    """Capacidad de un hospital."""

    actual: int
    maxima: int
    disponibilidad_porcentaje: float


@strawberry.type
class Ubicacion:
    """Ubicación GPS."""

    latitud: float
    longitud: float


@strawberry.type
class Hospital:
    """Información de un hospital."""

    hospital_id: str
    nombre: str
    ubicacion: Ubicacion
    capacidad: Capacidad
    nivel: str
    distancia_km: Optional[float] = None
    disponibilidad_porcentaje: Optional[float] = None


@strawberry.type
class RecomendacionHospitales:
    """Recomendación de hospitales para un paciente."""

    evaluacion: EvaluacionPaciente
    cluster_utilizado: Optional[int] = None
    especialidades_cluster: List[str]
    hospitales_recomendados: List[Hospital]
    total_disponibles: int
    mensaje: str


@strawberry.type
class InfoCluster:
    """Información de un cluster de hospitales."""

    cluster_id: int
    cantidad_hospitales: int
    especialidades: List[str]
    hospitales_ids: List[str]


@strawberry.input
class DatosPacienteInput:
    """Datos de entrada de un paciente para evaluación."""

    edad: int
    sexo: str
    presion_sistolica: float
    presion_diastolica: float
    frecuencia_cardiaca: int
    frecuencia_respiratoria: int
    temperatura: float
    saturacion_oxigeno: float
    nivel_dolor: int
    tipo_incidente: str
    tiempo_desde_incidente: int


@strawberry.input
class UbicacionInput:
    """Ubicación GPS de entrada."""

    latitud: float
    longitud: float


@strawberry.type
class EstadisticasSistema:
    """Estadísticas generales del sistema."""

    total_hospitales: int
    hospitales_disponibles: int
    clusters_activos: int
    modelos_cargados: bool


# ============================================================================
# APOLLO FEDERATION - ENTITY TYPES
# ============================================================================
# Estas entidades son compartidas con otros microservicios (Despacho, Recepción)
# usando Apollo Federation. El campo 'id' es el Entity Key que permite
# al Gateway combinar datos de múltiples microservicios.
# ============================================================================

@strawberry.federation.type(keys=["id"])
class Paciente:
    """
    Entity Type: Paciente

    Entity Key: id (compartido entre MS Decisión, Recepción, Despacho)

    MS Decisión extiende esta entidad agregando:
    - severidad: Nivel de severidad evaluado por ML
    - hospitalesRecomendados: TOP N hospitales según severidad + clustering

    Otros microservicios pueden extender con:
    - MS Recepción: nombre, edad, dni, dirección
    - MS Despacho: ambulanciaAsignada, ubicacionActual
    """

    id: strawberry.ID = strawberry.federation.field(external=True)
    severidad: Optional[str] = None
    hospitales_recomendados: Optional[List[Hospital]] = None
    evaluacion_completa: Optional[EvaluacionPaciente] = None

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """
        Resolver para Apollo Federation.

        Cuando el Gateway necesita datos de este microservicio para un paciente,
        llama a esta función con el 'id'. Aquí podríamos cargar datos de MongoDB
        si tuviéramos persistencia de evaluaciones.

        Por ahora retorna una instancia vacía ya que las evaluaciones son
        stateless (no se persisten).
        """
        return cls(id=id)


@strawberry.federation.type(keys=["id"])
class Emergencia:
    """
    Entity Type: Emergencia

    Entity Key: id (compartido entre MS Decisión, Recepción, Despacho)

    MS Decisión extiende esta entidad agregando:
    - evaluacionRiesgo: Severidad calculada por ML
    - hospitalRecomendado: Hospital principal recomendado
    - hospitalesAlternativos: Lista de hospitales alternativos

    Otros microservicios pueden extender con:
    - MS Recepción: direccion, ubicacion, descripcion, timestamp
    - MS Despacho: ambulanciaAsignada, estadoDespacho, tiempoEstimado
    """

    id: strawberry.ID = strawberry.federation.field(external=True)
    evaluacion_riesgo: Optional[str] = None
    hospital_recomendado: Optional[Hospital] = None
    hospitales_alternativos: Optional[List[Hospital]] = None

    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        """
        Resolver para Apollo Federation.

        Permite al Gateway resolver referencias a Emergencia desde otros
        microservicios.
        """
        return cls(id=id)
