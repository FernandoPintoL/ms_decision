"""Script temporal para verificar MongoDB."""
from pymongo import MongoClient

# Conectar
cliente = MongoClient('mongodb://localhost:27017/')

print('>> Bases de datos disponibles:')
for nombre in cliente.list_database_names():
    print(f'  - {nombre}')

# Verificar servicio_decision
db = cliente['servicio_decision']
print('\n>> Colecciones en servicio_decision:')
colecciones = db.list_collection_names()

if not colecciones:
    print('  (ninguna - la BD está vacía)')
else:
    for col in colecciones:
        count = db[col].count_documents({})
        print(f'  - {col}: {count} documentos')

cliente.close()
