"""
Configuración de conexión a MongoDB.
Capa: DATOS
Responsabilidad: Establecer y gestionar conexión con base de datos MongoDB.
"""

import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class ConexionMongoDB:
    """Gestiona la conexión a MongoDB siguiendo patrón Singleton."""

    _instancia: Optional['ConexionMongoDB'] = None
    _cliente: Optional[MongoClient] = None
    _base_datos: Optional[Database] = None

    def __new__(cls) -> 'ConexionMongoDB':
        """Implementa patrón Singleton para una única instancia de conexión."""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    def conectar(
        self,
        host: str = None,
        puerto: int = None,
        nombre_bd: str = None,
        uri: str = None
    ) -> Database:
        """
        Establece conexión con MongoDB.

        Args:
            host: Host de MongoDB (default: localhost, desde variable de entorno)
            puerto: Puerto de MongoDB (default: 27017, desde variable de entorno)
            nombre_bd: Nombre de la base de datos (default: servicio_decision)
            uri: URI de conexión para MongoDB Atlas o conexión remota

        Returns:
            Database: Instancia de base de datos MongoDB
        """
        if self._cliente is None:
            # Obtener valores de variables de entorno si no se proporcionan
            if uri is None:
                uri = os.getenv('MONGODB_URI')

            if nombre_bd is None:
                nombre_bd = os.getenv('MONGODB_DB', 'servicio_decision')

            if host is None:
                host = os.getenv('MONGODB_HOST', 'localhost')

            if puerto is None:
                puerto = int(os.getenv('MONGODB_PORT', 27017))

            # Si hay URI, usarla (MongoDB Atlas o similar)
            if uri:
                self._cliente = MongoClient(uri)
                print(f">> Conectado a MongoDB Atlas/Remoto: {nombre_bd}")
            else:
                # Usar conexión local
                self._cliente = MongoClient(f"mongodb://{host}:{puerto}/")
                print(f">> Conectado a MongoDB local: {nombre_bd}")

            self._base_datos = self._cliente[nombre_bd]

        return self._base_datos

    def obtener_bd(self) -> Optional[Database]:
        """
        Obtiene la instancia de base de datos.

        Returns:
            Database: Instancia de BD o None si no está conectada
        """
        return self._base_datos

    def cerrar_conexion(self) -> None:
        """Cierra la conexión con MongoDB."""
        if self._cliente:
            self._cliente.close()
            self._cliente = None
            self._base_datos = None
            print(">> Conexion MongoDB cerrada")


# Instancia global
conexion_db = ConexionMongoDB()
