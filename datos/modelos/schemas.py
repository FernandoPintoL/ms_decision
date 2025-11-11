"""
Schemas/modelos de datos para MongoDB.
Capa: DATOS
Responsabilidad: Definir estructura de documentos en colecciones.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class PacienteSchema:
    """Schema para colección de pacientes."""

    @staticmethod
    def crear_documento(
        paciente_id: str,
        nombre: str,
        apellido: str,
        edad: int,
        ci: str,
        sexo: str,
        presion_sistolica: float,
        presion_diastolica: float,
        frecuencia_cardiaca: int,
        frecuencia_respiratoria: int,
        temperatura: float,
        saturacion_oxigeno: float,
        tipo_incidente: str,
        nivel_dolor: int,
        tiene_seguro: bool,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Crea documento de paciente."""
        return {
            "paciente_id": paciente_id,
            "nombre": nombre,
            "apellido": apellido,
            "edad": edad,
            "ci": ci,
            "sexo": sexo,
            "signos_vitales": {
                "presion_sistolica": presion_sistolica,
                "presion_diastolica": presion_diastolica,
                "frecuencia_cardiaca": frecuencia_cardiaca,
                "frecuencia_respiratoria": frecuencia_respiratoria,
                "temperatura": temperatura,
                "saturacion_oxigeno": saturacion_oxigeno
            },
            "incidente": {
                "tipo": tipo_incidente,
                "nivel_dolor": nivel_dolor
            },
            "tiene_seguro": tiene_seguro,
            "timestamp": timestamp or datetime.now()
        }


class HospitalSchema:
    """Schema para colección de hospitales."""

    @staticmethod
    def crear_documento(
        hospital_id: str,
        nombre: str,
        latitud: float,
        longitud: float,
        capacidad_actual: int,
        capacidad_maxima: int,
        tiempo_atencion_promedio: float,
        tasa_exito: float,
        nivel: str,
        especialidades: Dict[str, int],
        cluster: Optional[int] = None
    ) -> Dict[str, Any]:
        """Crea documento de hospital."""
        return {
            "hospital_id": hospital_id,
            "nombre": nombre,
            "ubicacion": {
                "latitud": latitud,
                "longitud": longitud
            },
            "capacidad": {
                "actual": capacidad_actual,
                "maxima": capacidad_maxima
            },
            "metricas": {
                "tiempo_atencion_promedio": tiempo_atencion_promedio,
                "tasa_exito": tasa_exito
            },
            "nivel": nivel,
            "especialidades": especialidades,
            "cluster": cluster
        }


class DecisionSchema:
    """Schema para colección de decisiones."""

    @staticmethod
    def crear_documento(
        paciente_id: str,
        tipo_atencion: str,
        severidad: str,
        hospital_id: Optional[str] = None,
        hospital_nombre: Optional[str] = None,
        distancia_km: Optional[float] = None,
        motivo_decision: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Crea documento de decisión."""
        return {
            "paciente_id": paciente_id,
            "tipo_atencion": tipo_atencion,  # "ambulatoria" o "traslado"
            "severidad": severidad,  # "crítico", "alto", "medio", "bajo"
            "hospital": {
                "id": hospital_id,
                "nombre": hospital_nombre,
                "distancia_km": distancia_km
            } if hospital_id else None,
            "motivo_decision": motivo_decision,
            "timestamp": timestamp or datetime.now()
        }


class EvaluacionMLSchema:
    """Schema para colección de evaluaciones ML."""

    @staticmethod
    def crear_documento(
        paciente_id: str,
        severidad_predicha: str,
        probabilidad_severidad: Dict[str, float],
        cluster_hospital: Optional[int] = None,
        modelo_usado: str = "random_forest",
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Crea documento de evaluación ML."""
        return {
            "paciente_id": paciente_id,
            "prediccion": {
                "severidad": severidad_predicha,
                "probabilidades": probabilidad_severidad,
                "cluster_hospital": cluster_hospital
            },
            "modelo": {
                "nombre": modelo_usado,
                "version": "1.0"
            },
            "timestamp": timestamp or datetime.now()
        }


class HistorialClinicoSchema:
    """Schema para colección de historial clínico."""

    @staticmethod
    def crear_documento(
        paciente_id: str,
        estado_inicial: str,
        diagnostico: str,
        tipo_sangre: str,
        procedimiento: str,
        medicamentos_administrados: List[str],
        estado_final: str,
        fecha_atencion: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Crea documento de historial clínico."""
        return {
            "paciente_id": paciente_id,
            "estado_inicial": estado_inicial,
            "diagnostico": diagnostico,
            "tipo_sangre": tipo_sangre,
            "procedimiento": procedimiento,
            "medicamentos_administrados": medicamentos_administrados,
            "estado_final": estado_final,
            "fecha_atencion": fecha_atencion or datetime.now()
        }
