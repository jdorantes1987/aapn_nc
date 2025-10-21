from datetime import date

import streamlit as st
import pandas as pd

from helpers.creyentes_crud import CreyentesCRUD
from helpers.navigation import make_sidebar

st.set_page_config(page_title="Registro de nuevo creyente", layout="wide", page_icon="")

make_sidebar()

st.title("Gestión de Creyentes")

# Requiere que la conexión esté disponible en session_state como 'conexion'
if "conexion" not in st.session_state or st.session_state.conexion is None:
    st.error(
        "No hay conexión a la base de datos. Vuelve a la página de inicio para inicializarla."
    )
    st.stop()

crud = CreyentesCRUD(st.session_state.conexion)

with st.expander("Crear nuevo creyente"):
    with st.form("form_crear"):
        hoy = date.today()
        # Define the allowed date range
        min_allowed_date = date(1950, 1, 1)
        max_allowed_date = hoy
        cedula = st.text_input("Cédula")
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        telefono = st.text_input("Teléfono Celular")
        sexo = st.selectbox(
            "Sexo",
            options=["M", "F"],
            index=0,
            help="Selecciona el sexo del creyente",
        )
        correo = st.text_input("Correo")
        codred = st.text_input("CodRed")
        fecha_nac = st.date_input(
            "Fecha de nacimiento",
            value=hoy,
            format="DD/MM/YYYY",
            min_value=min_allowed_date,
            max_value=max_allowed_date,
        )
        encuentro = st.checkbox("Culminó el encuentro", value=False)
        estatus = st.selectbox(
            "Estatus",
            options=[1, 0],
            format_func=lambda x: "Activo" if x == 1 else "Inactivo",
        )

        submitted = st.form_submit_button("Crear")
        if submitted:
            hoy = date.today()
            # Define the allowed date range
            min_allowed_date = date(1950, 1, 1)
            max_allowed_date = hoy
            payload = {
                "Cedula": cedula,
                "Nombre": nombre,
                "Apellido": apellido,
                "IdProfesion": 17,
                "TelefonoCelular": telefono,
                "Correo": correo,
                "CodRed": codred,
                "FechaNac": fecha_nac if fecha_nac else None,
                "Encuentro": encuentro,
                "Estatus": estatus,
                "Sexo": sexo,
                "co_us_in": st.session_state.get("user", 0),
                "co_us_mo": st.session_state.get("user", 0),
            }
            safe = CreyentesCRUD.normalize_payload(payload)
            new_id = crud.create(safe)
            if new_id:
                st.success(f"Creado con Id {new_id}")
            else:
                st.info("Creado (id no retornado) o hubo un problema")

# Listado y selección (ahora editable)

with st.expander("Listado de creyentes (editor)"):
    rows = crud.list()
    if not rows:
        st.info("No se encontraron registros.")
    else:
        # Construir DataFrame
        df = pd.DataFrame(rows)
        # Asegurar columnas esperadas
        if "Id" not in df.columns:
            df["Id"] = df.index
        # Normalizar FechaNac a date (si viene como string/timestamp)
        if "FechaNac" in df.columns:
            df["FechaNac"] = pd.to_datetime(df["FechaNac"], errors="coerce").dt.date
        # Añadir columna para marcar eliminación
        df["Eliminar"] = False

        original_df = df.copy(deep=True)

        # Mostrar editor editable
        edited = st.data_editor(
            df,
            column_config={
                "Encuentro": st.column_config.CheckboxColumn(
                    "Encuentro?",
                    help="Culminó el encuentro.",
                    width="large",
                ),
            },
            num_rows="dynamic",
            #  Permite ajustar el ancho al tamaño del contenedor
            use_container_width=False,
        )

        # Procesar eliminaciones
        to_delete = edited.loc[edited["Eliminar"], "Id"].tolist()
        if to_delete:
            for id_del in to_delete:
                try:
                    id_int = int(id_del)
                except Exception:
                    st.error(f"Id inválido para eliminar: {id_del}")
                    continue
                count = crud.delete(id_int)
                if count:
                    st.success(f"Registro {id_int} eliminado")
                else:
                    st.error(f"No se pudo eliminar Id {id_int}")
            st.rerun()

        # Procesar actualizaciones: detectar cambios por Id (ignorar columna Eliminar)
        key_cols = [
            "Nombre",
            "Apellido",
            "TelefonoCelular",
            "Correo",
            "IdProfesion",
            "Ocupacion",
            "Sexo",
            "CodRed",
            "FechaNac",
            "Encuentro",
            "Estatus",
        ]
        for _, row in edited.iterrows():
            id_val = row["Id"]
            # Buscar la fila original
            orig_rows = original_df[original_df["Id"] == id_val]
            if orig_rows.empty:
                continue
            orig = orig_rows.iloc[0]
            changed = False
            payload = {}
            for col in key_cols:
                if col in edited.columns:
                    new_val = row[col]
                    old_val = orig.get(col, None)
                    # Normalizar NaT/NaN a None
                    if pd.isna(old_val):
                        old_val = None
                    if pd.isna(new_val):
                        new_val = None
                    if old_val != new_val:
                        payload[col] = new_val
                        changed = True
            if changed:
                # Añadir campos requeridos por normalize_payload / update
                # Ajustar campos que espera el CRUD
                payload.setdefault("FechaNac", payload.get("FechaNac", None))
                payload["co_us_mo"] = st.session_state.get("user", 0)
                safe = CreyentesCRUD.normalize_payload(payload)
                try:
                    updated = crud.update(int(id_val), safe)
                except Exception as e:
                    st.error(f"Error actualizando Id {id_val}: {e}")
                    updated = False
                if updated:
                    st.success(f"Id {id_val} actualizado")
                    st.rerun()
                else:
                    st.error(f"No se pudo actualizar Id {id_val}")
