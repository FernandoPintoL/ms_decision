"""
Script para analizar los datasets descargados.
Muestra estadísticas y estructura de ambos datasets.
"""

from pathlib import Path
from collections import Counter

def analizar_skin_burn():
    """Analiza el dataset de quemaduras."""
    print("=" * 60)
    print("SKIN BURN DATASET")
    print("=" * 60)

    skin_burn_path = Path('datos/imagenes_raw/skin_burn')

    # Contar imágenes
    imagenes = list(skin_burn_path.glob('*.jpg'))
    print(f"\nTotal de imágenes: {len(imagenes)}")

    # Leer etiquetas de los archivos .txt
    clases = []
    for img_path in imagenes:
        txt_path = img_path.with_suffix('.txt')
        if txt_path.exists():
            content = txt_path.read_text().strip()
            if content:
                # El primer número es la clase (0=1er grado, 1=2do grado, 2=3er grado)
                clase = int(content.split()[0])
                clases.append(clase)

    # Contar clases
    conteo_clases = Counter(clases)

    print("\nDistribución por grado de quemadura:")
    print(f"  Clase 0 (1er grado): {conteo_clases.get(0, 0)} imágenes")
    print(f"  Clase 1 (2do grado): {conteo_clases.get(1, 0)} imágenes")
    print(f"  Clase 2 (3er grado): {conteo_clases.get(2, 0)} imágenes")

    print("\nMapeo a severidad:")
    print(f"  MEDIO/BAJO:  {conteo_clases.get(0, 0)} (1er grado)")
    print(f"  ALTO:        {conteo_clases.get(1, 0)} (2do grado)")
    print(f"  CRÍTICO:     {conteo_clases.get(2, 0)} (3er grado)")

    return conteo_clases


def analizar_wound_classification():
    """Analiza el dataset de clasificación de heridas."""
    print("\n" + "=" * 60)
    print("WOUND CLASSIFICATION DATASET")
    print("=" * 60)

    wound_path = Path('datos/imagenes_raw/wound_classification/Wound_dataset copy')

    categorias = {}
    total = 0

    for category_dir in sorted(wound_path.iterdir()):
        if category_dir.is_dir():
            imgs = list(category_dir.glob('*.jpg')) + list(category_dir.glob('*.png'))
            cantidad = len(imgs)
            categorias[category_dir.name] = cantidad
            total += cantidad
            print(f"\n  {category_dir.name}: {cantidad} imágenes")

    print(f"\n  TOTAL: {total} imágenes")

    print("\nMapeo sugerido a severidad:")
    print("  CRÍTICO:")
    print(f"    - Burns (graves):        {categorias.get('Burns', 0)}")
    print(f"    - Diabetic Wounds:       {categorias.get('Diabetic Wounds', 0)}")
    print(f"    - Laseration:            {categorias.get('Laseration', 0)}")

    print("  ALTO:")
    print(f"    - Cut:                   {categorias.get('Cut', 0)}")
    print(f"    - Pressure Wounds:       {categorias.get('Pressure Wounds', 0)}")
    print(f"    - Surgical Wounds:       {categorias.get('Surgical Wounds', 0)}")

    print("  MEDIO:")
    print(f"    - Abrasions:             {categorias.get('Abrasions', 0)}")
    print(f"    - Venous Wounds:         {categorias.get('Venous Wounds', 0)}")

    print("  BAJO:")
    print(f"    - Bruises:               {categorias.get('Bruises', 0)}")
    print(f"    - Normal:                {categorias.get('Normal', 0)}")

    return categorias


def resumen_final(skin_burn_clases, wound_categorias):
    """Muestra resumen final combinado."""
    print("\n" + "=" * 60)
    print("RESUMEN FINAL - DATASET COMBINADO")
    print("=" * 60)

    # Calcular totales por severidad
    critico = skin_burn_clases.get(2, 0) + \
              wound_categorias.get('Burns', 0) + \
              wound_categorias.get('Diabetic Wounds', 0) + \
              wound_categorias.get('Laseration', 0)

    alto = skin_burn_clases.get(1, 0) + \
           wound_categorias.get('Cut', 0) + \
           wound_categorias.get('Pressure Wounds', 0) + \
           wound_categorias.get('Surgical Wounds', 0)

    medio = skin_burn_clases.get(0, 0) + \
            wound_categorias.get('Abrasions', 0) + \
            wound_categorias.get('Venous Wounds', 0)

    bajo = wound_categorias.get('Bruises', 0) + \
           wound_categorias.get('Normal', 0)

    total = critico + alto + medio + bajo

    print(f"\nImágenes totales disponibles: {total}")
    print(f"\nDistribución por severidad:")
    print(f"  CRÍTICO: {critico:4d} imágenes ({critico/total*100:5.1f}%)")
    print(f"  ALTO:    {alto:4d} imágenes ({alto/total*100:5.1f}%)")
    print(f"  MEDIO:   {medio:4d} imágenes ({medio/total*100:5.1f}%)")
    print(f"  BAJO:    {bajo:4d} imágenes ({bajo/total*100:5.1f}%)")

    print(f"\nCon Data Augmentation (x5):")
    print(f"  CRÍTICO: {critico*5:5d} imágenes")
    print(f"  ALTO:    {alto*5:5d} imágenes")
    print(f"  MEDIO:   {medio*5:5d} imágenes")
    print(f"  BAJO:    {bajo*5:5d} imágenes")
    print(f"  TOTAL:   {total*5:5d} imágenes")

    print("\n" + "=" * 60)
    print("ANÁLISIS COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    # Analizar ambos datasets
    skin_burn_clases = analizar_skin_burn()
    wound_categorias = analizar_wound_classification()

    # Resumen final
    resumen_final(skin_burn_clases, wound_categorias)
