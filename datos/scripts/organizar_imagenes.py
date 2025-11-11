"""
Script para organizar imágenes en carpetas por severidad.
Copia las imágenes de los datasets raw a carpetas de entrenamiento.

NO MODIFICA ARQUITECTURA - Solo organiza datos de entrenamiento.
"""

from pathlib import Path
import shutil
from tqdm import tqdm


def organizar_skin_burn():
    """
    Organiza imágenes del Skin Burn Dataset.

    Mapeo:
    - Clase 0 (1er grado) → medio
    - Clase 1 (2do grado) → alto
    - Clase 2 (3er grado) → critico
    """
    print("\n[1/2] Organizando Skin Burn Dataset...")

    source_path = Path('datos/imagenes_raw/skin_burn')
    dest_base = Path('datos/imagenes_entrenamiento')

    # Mapeo de clases
    mapeo = {
        0: 'medio',
        1: 'alto',
        2: 'critico'
    }

    # Obtener todas las imágenes
    imagenes = list(source_path.glob('*.jpg'))

    copiadas = {'critico': 0, 'alto': 0, 'medio': 0}

    for img_path in tqdm(imagenes, desc="  Copiando"):
        # Leer etiqueta del archivo .txt
        txt_path = img_path.with_suffix('.txt')
        if txt_path.exists():
            content = txt_path.read_text().strip()
            if content:
                clase = int(content.split()[0])
                severidad = mapeo[clase]

                # Copiar imagen
                dest_dir = dest_base / severidad
                dest_file = dest_dir / f"burn_{img_path.name}"
                shutil.copy2(img_path, dest_file)

                copiadas[severidad] += 1

    print(f"  ✓ Crítico: {copiadas['critico']} imágenes")
    print(f"  ✓ Alto:    {copiadas['alto']} imágenes")
    print(f"  ✓ Medio:   {copiadas['medio']} imágenes")

    return copiadas


def organizar_wound_classification():
    """
    Organiza imágenes del Wound Classification Dataset.

    Mapeo:
    - Burns, Diabetic Wounds, Laseration → critico
    - Cut, Pressure Wounds, Surgical Wounds → alto
    - Abrasions, Venous Wounds → medio
    - Bruises, Normal → bajo
    """
    print("\n[2/2] Organizando Wound Classification Dataset...")

    source_base = Path('datos/imagenes_raw/wound_classification/Wound_dataset copy')
    dest_base = Path('datos/imagenes_entrenamiento')

    # Mapeo de categorías a severidad
    mapeo = {
        'Burns': 'critico',
        'Diabetic Wounds': 'critico',
        'Laseration': 'critico',
        'Cut': 'alto',
        'Pressure Wounds': 'alto',
        'Surgical Wounds': 'alto',
        'Abrasions': 'medio',
        'Venous Wounds': 'medio',
        'Bruises': 'bajo',
        'Normal': 'bajo'
    }

    copiadas = {'critico': 0, 'alto': 0, 'medio': 0, 'bajo': 0}

    for categoria, severidad in mapeo.items():
        source_dir = source_base / categoria
        if not source_dir.exists():
            continue

        # Obtener imágenes
        imagenes = list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.png'))

        print(f"\n  Procesando {categoria} → {severidad.upper()}")

        for img_path in tqdm(imagenes, desc=f"    Copiando"):
            # Crear nombre único
            nombre_limpio = categoria.replace(' ', '_').lower()
            dest_file = dest_base / severidad / f"{nombre_limpio}_{img_path.name}"

            # Copiar imagen
            shutil.copy2(img_path, dest_file)
            copiadas[severidad] += 1

    print(f"\n  ✓ Crítico: {copiadas['critico']} imágenes")
    print(f"  ✓ Alto:    {copiadas['alto']} imágenes")
    print(f"  ✓ Medio:   {copiadas['medio']} imágenes")
    print(f"  ✓ Bajo:    {copiadas['bajo']} imágenes")

    return copiadas


def verificar_organizacion():
    """Verifica que las imágenes se organizaron correctamente."""
    print("\n" + "="*60)
    print("VERIFICACIÓN FINAL")
    print("="*60)

    base_path = Path('datos/imagenes_entrenamiento')

    total = 0
    for severidad in ['critico', 'alto', 'medio', 'bajo']:
        dir_path = base_path / severidad
        imagenes = list(dir_path.glob('*.jpg')) + list(dir_path.glob('*.png'))
        cantidad = len(imagenes)
        total += cantidad
        print(f"\n  {severidad.upper():8s}: {cantidad:4d} imágenes")

    print(f"\n  TOTAL:     {total:4d} imágenes")
    print("\n" + "="*60)
    print("✅ ORGANIZACIÓN COMPLETADA EXITOSAMENTE")
    print("="*60)
    print("\n📂 Ruta: datos/imagenes_entrenamiento/")
    print("   ├── critico/")
    print("   ├── alto/")
    print("   ├── medio/")
    print("   └── bajo/")


if __name__ == "__main__":
    print("="*60)
    print("ORGANIZANDO IMÁGENES PARA ENTRENAMIENTO CNN")
    print("="*60)
    print("\nNOTA: Este script NO modifica la arquitectura del proyecto.")
    print("Solo organiza imágenes en carpetas para entrenamiento.\n")

    # Organizar ambos datasets
    skin_burn_stats = organizar_skin_burn()
    wound_stats = organizar_wound_classification()

    # Verificar resultado
    verificar_organizacion()

    print("\n🎯 Siguiente paso: Entrenar CNN con estas imágenes")
