from typing import Optional, List, Dict, Any
from datetime import datetime


class CreyentesCRUD:
    """
    Clase que gestiona operaciones CRUD sobre la tabla `tbl_creyentes`.

    Se espera que `db` sea un objeto con al menos estos métodos:
      - execute(query: str, params: tuple|dict) -> cursor-like
      - fetchone(query: str, params: tuple|dict) -> dict|tuple
      - fetchall(query: str, params: tuple|dict) -> list[dict|tuple]

    Adapta los nombres de métodos si tu `DatabaseConnector` usa otros.
    """

    def __init__(self, db):
        self.db = db
        self.cursor = self.db.get_cursor()

    def create(self, data: Dict[str, Any]) -> int:
        """Inserta un nuevo creyente. Devuelve el Id insertado (si el conector lo soporta)."""
        cols = []
        placeholders = []
        values = []
        for k, v in data.items():
            cols.append(f"`{k}`")
            placeholders.append("%s")
            values.append(v)

        query = f"INSERT INTO tbl_creyentes ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        self.db.connection.autocommit(True)
        try:
            self.cursor.execute(query, tuple(values))
            self.db.connection.autocommit(False)
            return self.cursor.lastrowid()  # si el conector expone esto
        except Exception:
            return 0

    def get_by_id(self, id_value: int) -> Optional[Dict[str, Any]]:
        q = "SELECT * FROM tbl_creyentes WHERE Id = %s"
        self.cursor.execute(q, (id_value,))
        return self.cursor.fetchone()

    def get_by_cedula(self, cedula: str) -> Optional[Dict[str, Any]]:
        q = "SELECT * FROM tbl_creyentes WHERE Cedula = %s"
        self.cursor.execute(q, (cedula,))
        return self.cursor.fetchone()

    def list(self, limit: int = 100) -> List[Dict[str, Any]]:
        q = "SELECT * FROM tbl_creyentes ORDER BY Id DESC LIMIT %s"
        self.cursor.execute(q, (limit,))
        return self.cursor.fetchall()

    def get_list_redes(self, limit: int = 100) -> List[Dict[str, Any]]:
        q = "SELECT CodRed, NombreRed FROM tbl_redes ORDER BY CodRed DESC LIMIT %s"
        self.cursor.execute(q, (limit,))
        return self.cursor.fetchall()

    def update(self, id_value: int, data: Dict[str, Any]) -> int:
        """Actualiza campos para el Id dado. Devuelve número de filas afectadas."""
        sets = []
        vals = []
        for k, v in data.items():
            sets.append(f"`{k}` = %s")
            vals.append(v)
        vals.append(id_value)
        q = f"UPDATE tbl_creyentes SET {', '.join(sets)} WHERE Id = %s"
        self.db.connection.autocommit(True)
        cursor = self.cursor.execute(q, tuple(vals))
        self.db.connection.autocommit(False)
        try:
            return cursor
        except Exception:
            return 0

    def delete(self, id_value: int) -> int:
        q = "DELETE FROM tbl_creyentes WHERE Id = %s"
        self.db.connection.autocommit(True)
        cursor = self.cursor.execute(q, (id_value,))
        self.db.connection.autocommit(False)
        try:
            return cursor
        except Exception:
            return 0

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
