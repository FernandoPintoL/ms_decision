"""
Módulo GraphQL para la API.
Capa: PRESENTACION
"""

from .schema import schema
from .tipos import (
    DatosPacienteInput,
    UbicacionInput,
    RecomendacionHospitales,
    EvaluacionPaciente,
    Hospital,
    InfoCluster,
    EstadisticasSistema,
)

__all__ = [
    'schema',
    'DatosPacienteInput',
    'UbicacionInput',
    'RecomendacionHospitales',
    'EvaluacionPaciente',
    'Hospital',
    'InfoCluster',
    'EstadisticasSistema',
]
