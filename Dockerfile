# ============================================================================
# Dockerfile - Microservicio Decisión
# ============================================================================
# Imagen: Python 3.10 slim (optimizada)
# Contiene: FastAPI + GraphQL + ML Models (Random Forest, K-means, CNN)
# Expone: Puerto 8000 (GraphQL API)
# ============================================================================

FROM python:3.10-slim

# Metadata
LABEL maintainer="Equipo Ambulancias"
LABEL description="Microservicio de Decisión con ML (Random Forest + K-means + CNN)"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para TensorFlow y MongoDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache de Docker layers)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios si no existen
RUN mkdir -p modelos_ml archivos_csv datos/imagenes_entrenamiento

# Exponer puerto (configurable via environment variable)
ARG SERVER_PORT=8002
ENV SERVER_PORT=${SERVER_PORT}
EXPOSE ${SERVER_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${SERVER_PORT}/health')" || exit 1

# Comando de inicio
CMD ["uvicorn", "presentacion.servidor:app", "--host", "0.0.0.0", "--port", "8002"]
