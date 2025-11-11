# Solución: Errores "Unresolved reference" en el IDE

## Problema

Tu IDE muestra errores como:
```
Unresolved reference 'datos'
Unresolved reference 'ConexionMongoDB'
```

**IMPORTANTE:** Estos son errores **SOLO del IDE**, el código **SÍ funciona correctamente** cuando lo ejecutas.

---

## ¿Por qué ocurre?

El IDE no puede resolver las importaciones porque los scripts están en `datos/scripts/` pero importan desde la raíz del proyecto (`datos.configuracion.conexion_mongodb`).

El script ya maneja esto correctamente con:
```python
import sys
from pathlib import Path

# Agregar ruta raíz al path
ruta_raiz = Path(__file__).parent.parent.parent
sys.path.append(str(ruta_raiz))
```

Pero el IDE necesita configuración adicional.

---

## Solución 1: PyCharm

### Opción A: Marcar como Sources Root
1. Click derecho en la carpeta `ServicioDecision`
2. Selecciona `Mark Directory as` → `Sources Root`
3. Reinicia PyCharm

### Opción B: Configurar Project Structure
1. Ve a `File` → `Settings` (o `Ctrl+Alt+S`)
2. Ve a `Project: ServicioDecision` → `Project Structure`
3. Selecciona la carpeta `ServicioDecision`
4. Click en el botón `Sources` (arriba)
5. Click `OK`

### Opción C: Configurar Python Path
1. Ve a `Run` → `Edit Configurations...`
2. Busca la configuración de tu script
3. En `Environment variables`, agrega:
   ```
   PYTHONPATH=D:\Semestre 2-2025\Sofware II\Segundo Parcial\segundoparcial\ServicioDecision
   ```

---

## Solución 2: Visual Studio Code

Ya se creó automáticamente el archivo `.vscode/settings.json` con la configuración correcta:

```json
{
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ],
    "python.autoComplete.extraPaths": [
        "${workspaceFolder}"
    ],
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

**Pasos adicionales:**
1. Abre VSCode en la carpeta `ServicioDecision` (no en la carpeta padre)
2. Presiona `Ctrl+Shift+P`
3. Escribe: `Python: Select Interpreter`
4. Selecciona: `.venv\Scripts\python.exe`
5. Reinicia VSCode

---

## Solución 3: Ignorar los Errores del IDE

Si las soluciones anteriores no funcionan o no quieres configurar el IDE:

**Simplemente ignora los errores rojos.** El código **SÍ funciona** cuando lo ejecutas:

```bash
# Este comando funciona perfectamente
python datos/scripts/cargar_datos_iniciales.py

# Resultado:
# >> 2000 pacientes insertados
# >> 30 hospitales insertados
# >> Datos cargados exitosamente!
```

---

## Verificación

Para confirmar que todo funciona, ejecuta:

```bash
# Activa el entorno virtual
.venv\Scripts\activate

# Ejecuta el script
python datos/scripts/cargar_datos_iniciales.py
```

**Salida esperada:**
```
>> Iniciando carga de datos a MongoDB...
[1/2] Cargando pacientes desde CSV...
>> Conectado a MongoDB: servicio_decision
>> 2000 pacientes insertados
[2/2] Cargando hospitales desde CSV...
>> 30 hospitales insertados

>> RESUMEN:
  - Pacientes: 2000
  - Hospitales: 30

>> Datos cargados exitosamente!
```

---

## Archivos Creados para Ayudar al IDE

Se crearon los siguientes archivos:

1. **`.vscode/settings.json`** - Configuración para VSCode
2. **`datos/scripts/__init__.py`** - Marca la carpeta como paquete Python
3. **`.env`** - Variables de entorno (opcional)

---

## Resumen

| Situación | Solución |
|-----------|----------|
| Errores en PyCharm | Marcar `ServicioDecision` como `Sources Root` |
| Errores en VSCode | Abrir VSCode en `ServicioDecision` y seleccionar intérprete `.venv` |
| El código funciona | **Ignorar** los errores del IDE |

---

## Notas Importantes

- ✅ **El código funciona correctamente** al ejecutarlo
- ⚠️ **Los errores son solo visuales** del IDE
- 📝 **No necesitas modificar el código** de los scripts
- 🔧 **La configuración del IDE es opcional** (para mejorar la experiencia)

---

**Si tienes más dudas, revisa:**
- `GUIA_INICIO_RAPIDO.md` - Cómo ejecutar el proyecto
- `README.md` - Documentación completa
