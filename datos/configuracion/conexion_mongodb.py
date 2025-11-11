"""
Configuración de conexión a MongoDB.
Capa: DATOS
Responsabilidad: Establecer y gestionar conexión con base de datos MongoDB.
"""

from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database


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
        host: str = "localhost",
        puerto: int = 27017,
        nombre_bd: str = "servicio_decision"
    ) -> Database:
        """
        Establece conexión con MongoDB.

        Args:
            host: Host de MongoDB (default: localhost)
            puerto: Puerto de MongoDB (default: 27017)
            nombre_bd: Nombre de la base de datos (default: servicio_decision)

        Returns:
            Database: Instancia de base de datos MongoDB
        """
        if self._cliente is None:
            self._cliente = MongoClient(f"mongodb://{host}:{puerto}/")
            self._base_datos = self._cliente[nombre_bd]
            print(f">> Conectado a MongoDB: {nombre_bd}")

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
