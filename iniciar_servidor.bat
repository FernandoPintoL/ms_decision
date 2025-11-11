@echo off
echo ============================================================
echo INICIANDO MICROSERVICIO DE DECISION MEDICA
echo ============================================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist ".venv" (
    echo ERROR: No se encuentra el entorno virtual .venv
    echo Por favor ejecuta este script desde la carpeta ServicioDecision
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/3] Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Verificar MongoDB
echo.
echo [2/3] Verificando MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo    # MongoDB ya esta corriendo
) else (
    echo    # Iniciando MongoDB...
    start "MongoDB" /MIN "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --dbpath "D:/mongodb_data/db" --port 27017
    timeout /t 3 /nobreak >nul
)

REM Iniciar servidor GraphQL
echo.
echo [3/3] Iniciando servidor GraphQL...
echo.
echo ============================================================
echo SERVIDOR LISTO
echo ============================================================
echo.
echo API GraphQL:     http://localhost:8000/graphql
echo GraphiQL IDE:    http://localhost:8000/graphql (navegador)
echo Health Check:    http://localhost:8000/health
echo.
echo Para detener el servidor presiona CTRL+C
echo ============================================================
echo.

uvicorn presentacion.servidor:app --host 127.0.0.1 --port 8000 --reload
