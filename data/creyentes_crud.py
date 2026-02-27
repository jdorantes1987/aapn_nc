import logging
import logging.config
from datetime import datetime
from typing import Any, Dict, List, Optional


class CreyentesCRUD:
    """
    Clase que gestiona operaciones CRUD sobre la tabla `tbl_creyentes`.

    Se espera que `db` sea un objeto con al menos estos métodos:
      - execute(query: str, params: tuple|dict) -> cursor-like
      - fetchone(query: str, params: tuple|dict) -> dict|tuple
      - fetchall(query: str, params: tuple|dict) -> list[dict|tuple]

    Adapta los nombres de métodos si tu `DatabaseConnector` usa otros.
    """

    logging.config.fileConfig("logging.ini")

    def __init__(self, db):
        self.db = db
        self.cursor = self.db.get_cursor()
        self.logger = logging.getLogger(__class__.__name__)

    def create(self, data: Dict[str, Any]) -> int:
        """Inserta un nuevo creyente. Devuelve el Id insertado (si el conector lo soporta)."""
        cols = []
        placeholders = []
        values = []
        self.db.connection.connect()
        for k, v in data.items():
            cols.append(f"`{k}`")
            placeholders.append("%s")
            values.append(v)

        query = f"INSERT INTO tbl_creyentes ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        self.db.connection.autocommit(True)
        try:
            self.logger.info(f"SQL: {query} with values {values}")
            self.cursor.execute(query, tuple(values))
            self.db.connection.autocommit(False)
            return self.cursor.lastrowid()  # si el conector expone esto
        except Exception as e:
            self.logger.error(f"Error creando creyente: {e}")
            return 0
        finally:
            self.db.connection.close()

    def get_by_id(self, id_value: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tbl_creyentes WHERE Id = %s"
        self.cursor.execute(query, (id_value,))
        return self.cursor.fetchone()

    def get_by_cedula(self, cedula: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tbl_creyentes WHERE Cedula = %s"
        self.cursor.execute(query, (cedula,))
        return self.cursor.fetchone()

    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        self.db.connection.connect()
        query = "SELECT * FROM tbl_creyentes ORDER BY Id DESC LIMIT %s"
        self.cursor.execute(query, (limit,))
        fetch = self.cursor.fetchall()
        self.db.connection.close()
        return fetch

    def get_list_redes(self, limit: int = 100) -> List[Dict[str, Any]]:
        self.db.connection.connect()
        query = "SELECT CodRed, NombreRed FROM tbl_redes ORDER BY CodRed ASC LIMIT %s"
        self.cursor.execute(query, (limit,))
        fetch = self.cursor.fetchall()
        return fetch

    def get_list_profesiones(self, limit: int = 100) -> List[Dict[str, Any]]:
        self.db.connection.connect()
        query = "SELECT IdProfesion, DescripcionProfesion FROM tbl_profesiones ORDER BY IdProfesion ASC LIMIT %s"
        self.cursor.execute(query, (limit,))
        fetch = self.cursor.fetchall()
        return fetch

    def update(self, id_value: int, data: Dict[str, Any]) -> int:
        """Actualiza campos para el Id dado. Devuelve número de filas afectadas."""
        sets = []
        vals = []
        self.db.connection.connect()
        for k, v in data.items():
            sets.append(f"`{k}` = %s")
            vals.append(v)
        vals.append(id_value)
        query = f"UPDATE tbl_creyentes SET {', '.join(sets)} WHERE Id = %s"
        self.db.connection.autocommit(True)
        self.logger.info(f"SQL: {query} with values {vals}")
        cursor = self.cursor.execute(query, tuple(vals))
        self.db.connection.autocommit(False)
        try:
            return cursor
        except Exception as e:
            self.logger.error(f"Error actualizando creyente: {e}")
            return 0
        finally:
            self.db.connection.close()

    def delete(self, id_value: int) -> int:
        self.db.connection.connect()
        query = "DELETE FROM tbl_creyentes WHERE Id = %s"
        self.db.connection.autocommit(True)
        cursor = self.cursor.execute(query, (id_value,))
        self.db.connection.autocommit(False)
        self.logger.info(f"SQL: {query} with Id {id_value}")
        try:
            return cursor
        except Exception as e:
            self.logger.error(f"Error eliminando creyente: {e}")
            return 0
        finally:
            self.db.connection.close()

    # Utility to map form fields to DB columns with basic defaults
    @staticmethod
    def normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        mapping = [
            "Id",
            "Cedula",
            "Nombre",
            "Apellido",
            "IdProfesion",
            "Ocupacion",
            "Correo",
            "TelefonoLocal",
            "TelefonoCelular",
            "Sexo",
            "FechaIngreso",
            "Nacionalidad",
            "EstadoCivil",
            "FechaConvivencia",
            "FechaMatrimonio",
            "Encuentro",
            "Consolidacion",
            "Academia",
            "Lanzamiento",
            "FechaNac",
            "CodRed",
            "FechaBautizo",
            "Estatus",
            "Estado",
            "Ciudad",
            "Direccion",
            "fe_us_in",
            "co_us_in",
            "fe_us_mo",
            "co_us_mo",
        ]
        for k in mapping:
            if k in payload and payload[k] not in (None, ""):
                out[k] = payload[k]
        # If fe_us_in / fe_us_mo not provided, set current
        now = datetime.now()
        if "fe_us_in" not in out:
            out["fe_us_in"] = now
        if "fe_us_mo" not in out:
            out["fe_us_mo"] = now
        return out
