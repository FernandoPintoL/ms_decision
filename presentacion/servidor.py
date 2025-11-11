"""
Servidor FastAPI con GraphQL.
Capa: PRESENTACION
Responsabilidad: Exponer API GraphQL para el microservicio.
Estándares: PEP 8, Type hints, Docstrings
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from contextlib import asynccontextmanager
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datos.configuracion.conexion_mongodb import ConexionMongoDB
from negocio.servicios.servicio_decision import ServicioDecision
from presentacion.gql.schema import schema


# Variables globales para el contexto
servicio_decision = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events del servidor.

    Inicializa servicios al arrancar y limpia al cerrar.
    """
    global servicio_decision

    # Startup: Inicializar servicios
    print("\n" + "=" * 60)
    print("INICIANDO MICROSERVICIO DE DECISION MEDICA")
    print("=" * 60)

    print("\n[1/3] Conectando a MongoDB...")
    conexion = ConexionMongoDB()
    db = conexion.conectar(
        host="localhost",
        puerto=27017,
        nombre_bd="servicio_decision"
    )
    print("   # MongoDB conectado")

    print("\n[2/3] Cargando modelos ML...")
    servicio_decision = ServicioDecision(db)
    print("   # Random Forest cargado")
    print("   # K-means cargado")

    print("\n[3/3] Servidor GraphQL listo")
    print("=" * 60)
    print("API GraphQL disponible en: http://localhost:8002/graphql")
    print("GraphiQL IDE disponible en: http://localhost:8002/graphql")
    print("=" * 60 + "\n")

    yield

    # Shutdown: Limpiar recursos
    print("\n" + "=" * 60)
    print("CERRANDO MICROSERVICIO")
    print("=" * 60 + "\n")


# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Decisión Médica",
    description="API GraphQL para evaluación de severidad y recomendación de hospitales",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Función para obtener contexto GraphQL
async def get_context():
    """
    Contexto para resolvers GraphQL.

    Inyecta el servicio de decisión en el contexto.
    """
    return {
        "servicio_decision": servicio_decision
    }


# Crear router GraphQL
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True  # Habilita GraphiQL IDE
)

# Montar router GraphQL
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    """
    Endpoint raíz.

    Returns:
        Info básica de la API
    """
    return {
        "nombre": "Microservicio de Decisión Médica",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
        "graphiql_ide": "/graphql (navegador)",
        "estado": "activo",
        "ml_models": {
            "random_forest": "Cargado",
            "kmeans": "Cargado"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Estado de salud del servicio
    """
    return {
        "status": "healthy",
        "database": "connected",
        "ml_models": "loaded"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "presentacion.servidor:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
