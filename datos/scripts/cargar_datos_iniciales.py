"""
Script para cargar datos desde CSVs a MongoDB.
Capa: DATOS
Responsabilidad: Poblar base de datos con información inicial.
"""

import sys
from pathlib import Path

# Agregar ruta raíz al path
ruta_raiz = Path(__file__).parent.parent.parent
sys.path.append(str(ruta_raiz))

import pandas as pd
from datos.configuracion.conexion_mongodb import ConexionMongoDB
from datos.modelos.schemas import PacienteSchema, HospitalSchema

def cargar_pacientes(ruta_csv: str) -> int:
    """
    Carga pacientes desde CSV a MongoDB.

    Args:
        ruta_csv: Ruta al archivo emergencia_pacientes.csv

    Returns:
        int: Cantidad de pacientes insertados
    """
    print("[1/2] Cargando pacientes desde CSV...")

    # Leer CSV
    df = pd.read_csv(ruta_csv)

    # Obtener base de datos
    conexion = ConexionMongoDB()
    db = conexion.conectar()
    coleccion = db["pacientes"]

    # Limpiar colección existente
    coleccion.delete_many({})

    # Insertar documentos
    documentos = []
    for _, fila in df.iterrows():
        doc = PacienteSchema.crear_documento(
            paciente_id=str(fila["paciente_id"]),
            nombre="Paciente",  # CSV no tiene nombre
            apellido=str(fila["paciente_id"]),
            edad=int(fila["edad"]),
            ci=str(fila["paciente_id"]),  # Temporal
            sexo=str(fila["sexo"]),
            presion_sistolica=float(fila["presion_sistolica"]),
            presion_diastolica=float(fila["presion_diastolica"]),
            frecuencia_cardiaca=int(fila["frecuencia_cardiaca"]),
            frecuencia_respiratoria=int(fila["frecuencia_respiratoria"]),
            temperatura=float(fila["temperatura"]),
            saturacion_oxigeno=float(fila["saturacion_oxigeno"]),
            tipo_incidente=str(fila["tipo_incidente"]),
            nivel_dolor=int(fila["nivel_dolor"]),
            tiene_seguro=bool(fila["tiene_seguro"])
        )
        documentos.append(doc)

    resultado = coleccion.insert_many(documentos)
    print(f">> {len(resultado.inserted_ids)} pacientes insertados")

    return len(resultado.inserted_ids)


def cargar_hospitales(ruta_csv: str) -> int:
    """
    Carga hospitales desde CSV a MongoDB.

    Args:
        ruta_csv: Ruta al archivo hospitales.csv

    Returns:
        int: Cantidad de hospitales insertados
    """
    print("[2/2] Cargando hospitales desde CSV...")

    # Leer CSV
    df = pd.read_csv(ruta_csv)

    # Obtener base de datos
    conexion = ConexionMongoDB()
    db = conexion.conectar()
    coleccion = db["hospitales"]

    # Limpiar colección existente
    coleccion.delete_many({})

    # Insertar documentos
    documentos = []
    for _, fila in df.iterrows():
        # Procesar especialidades (vienen como string)
        especialidades_str = str(fila["especialidades"])
        lista_especialidades = [e.strip() for e in especialidades_str.split(",")]

        # Crear diccionario con 1 si tiene la especialidad, 0 si no
        todas_especialidades = ["cardiologia", "trauma", "pediatria", "ortopedia",
                                "neurologia", "quemados", "toxicologia", "general"]
        especialidades = {esp: 1 if esp in lista_especialidades else 0
                         for esp in todas_especialidades}

        doc = HospitalSchema.crear_documento(
            hospital_id=str(fila["hospital_id"]),
            nombre=str(fila["nombre"]),
            latitud=float(fila["latitud"]),
            longitud=float(fila["longitud"]),
            capacidad_actual=int(fila["capacidad_actual"]),
            capacidad_maxima=int(fila["capacidad_maxima"]),
            tiempo_atencion_promedio=float(fila["tiempo_atencion_promedio"]),
            tasa_exito=float(fila["tasa_exito"]),
            nivel=str(fila["nivel"]),
            especialidades=especialidades,
            cluster=None  # Se asignará después del K-means
        )
        documentos.append(doc)

    resultado = coleccion.insert_many(documentos)
    print(f">> {len(resultado.inserted_ids)} hospitales insertados")

    return len(resultado.inserted_ids)


def main():
    """Función principal para cargar todos los datos."""
    print(">> Iniciando carga de datos a MongoDB...")

    # Rutas a los CSVs
    ruta_base = ruta_raiz / "archivos_csv"
    ruta_pacientes = ruta_base / "emergencia_pacientes.csv"
    ruta_hospitales = ruta_base / "hospitales.csv"

    try:
        # Cargar pacientes
        total_pacientes = cargar_pacientes(str(ruta_pacientes))

        # Cargar hospitales
        total_hospitales = cargar_hospitales(str(ruta_hospitales))

        print("\n>> RESUMEN:")
        print(f"  - Pacientes: {total_pacientes}")
        print(f"  - Hospitales: {total_hospitales}")
        print("\n>> Datos cargados exitosamente!")

    except Exception as e:
        print(f"\n>> Error al cargar datos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
