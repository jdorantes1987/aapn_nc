from datetime import date, datetime
from time import sleep

import streamlit as st

from helpers.navigation import make_sidebar

st.set_page_config(page_title="Registro de nuevo creyente", layout="wide", page_icon="")

make_sidebar()

st.title("Gestión de Creyentes")


def actualizar_listado():
    st.session_state.lista_creyentes = st.session_state.creyentes_crud.list()


if st.button("Refrescar"):
    actualizar_listado()

if "stage2" not in st.session_state:
    st.session_state.stage2 = 0


def set_stage(i):
    st.session_state.stage2 = i


# Inicializar campos de texto
if st.session_state.stage2 == 0:
    set_stage(1)

# Requiere que la conexión esté disponible en session_state como 'conexion'
if "conexion" not in st.session_state or st.session_state.conexion is None:
    st.error(
        "No hay conexión a la base de datos. Vuelve a la página de inicio para inicializarla."
    )
    st.stop()

# Formulario de creación
if st.session_state.stage2 >= 1:
    with st.expander("Nuevo creyente"):
        with st.form("form_crear", clear_on_submit=True):
            hoy = date.today()
            # Define the allowed date range
            min_allowed_date = date(1950, 1, 1)
            max_allowed_date = hoy
            nacionalidad = st.selectbox(
                "Nacionalidad",
                options=["V", "E"],
                index=0,
                help="Selecciona la nacionalidad del creyente",
            )
            cedula = st.text_input(
                "Cédula",
                placeholder="Sin guiones ni espacios ejemplo: 12345678",
                key="txt_cedula",
            ).upper()
            nombre = st.text_input("Nombre", key="txt_nombre").upper()
            apellido = st.text_input("Apellido", key="txt_apellido").upper()
            telefono = st.text_input(
                "Teléfono Celular",
                key="txt_telefono",
                placeholder="Sin guiones ni espacios ejemplo: 4143456789",
            ).upper()
            sexo = st.selectbox(
                "Sexo",
                options=["M", "F"],
                index=0,
                help="Selecciona el sexo del creyente",
            )

            correo = st.text_input("Correo", key="txt_correo").lower()

            lista_profesiones = st.session_state.get("lista_profesiones", [])
            pares_codigo_nombre = [
                (str(d["IdProfesion"]) + "|" + d["DescripcionProfesion"].strip())
                for d in lista_profesiones
            ]
            profesion = st.selectbox(
                "Elije una profesión:",
                options=pares_codigo_nombre,
                index=0,
            )
            profesion = str(profesion).split("|")[0]  # Obtener solo el IdProfesion

            ocupacion = st.text_input("Ocupación", key="txt_ocupacion").upper()

            lista_redes = st.session_state.get("lista_redes", [])
            pares_codigo_nombre = [
                (d["CodRed"] + "|" + d["NombreRed"].strip()) for d in lista_redes
            ]

            estado_civil = st.selectbox(
                "Estado Civil",
                options=["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)"],
                index=0,
            )

            codred = st.selectbox(
                "Elije una red:",
                options=pares_codigo_nombre,
                index=0,
            )
            codred = str(codred).split("|")[0]  # Obtener solo el código
            fecha_nac = st.date_input(
                "Fecha de nacimiento",
                value=hoy,
                format="DD/MM/YYYY",
                min_value=min_allowed_date,
                max_value=max_allowed_date,
            )
            estatus = st.selectbox(
                "Estatus",
                options=[1, 0],
                format_func=lambda x: "Activo" if x == 1 else "Inactivo",
            )

            submitted = st.form_submit_button("Crear", use_container_width=False)
            if submitted:
                hoy = date.today()
                # Define the allowed date range
                min_allowed_date = date(1950, 1, 1)
                max_allowed_date = hoy
                payload = {
                    "Cedula": cedula,
                    "Nacionalidad": nacionalidad,
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "IdProfesion": profesion,
                    "Ocupacion": ocupacion,
                    "TelefonoCelular": telefono,
                    "Correo": correo,
                    "EstadoCivil": estado_civil[0],  # Solo la primera letra
                    "CodRed": codred,
                    "FechaNac": fecha_nac if fecha_nac else None,
                    "Consolidacion": 0,
                    "Encuentro": 0,
                    "Academia": 0,
                    "Lanzamiento": 0,
                    "Estatus": estatus,
                    "Sexo": sexo,
                    "co_us_in": st.session_state.get("user", 0),
                    "co_us_mo": st.session_state.get("user", 0),
                }
                safe = st.session_state.creyentes_crud.normalize_payload(payload)
                new_id = st.session_state.creyentes_crud.create(safe)
                if new_id:
                    st.success(
                        f"🙋‍♂️ Creyente {nombre} {apellido} creado con Id {new_id}"
                    )
                    actualizar_listado()
                else:
                    st.error("No se pudo crear el nuevo creyente.")

                sleep(1)
                set_stage(2)

if st.session_state.stage2 == 2:
    set_stage(1)
    st.rerun()


def build_creyentes_df(rows):
    from pandas import DataFrame, to_datetime

    df = DataFrame(rows) if rows else DataFrame()
    # Ensure Id column
    if "Id" not in df.columns:
        df["Id"] = df.index
    # Normalize FechaNac to date
    if "FechaNac" in df.columns:
        df["FechaNac"] = to_datetime(df["FechaNac"], errors="coerce").dt.date
    # Add Eliminar flag
    df["Eliminar"] = False
    return df


def process_editor_changes(edited_df, original_df):
    """
    Procesa cambios del data_editor.
    - Detecta filas con 'Eliminar' == True y llama a delete(id).
    - Detecta filas editadas (comparando por Id) y llama a update(id, payload).
    - Actualiza el listado en session_state y fuerza rerun cuando hay cambios.
    """
    from pandas import isna, Timestamp

    if edited_df is None or edited_df.empty:
        return

    any_deleted = False
    any_updated = False

    # Manejar eliminaciones
    if "Eliminar" in edited_df.columns:
        to_delete = edited_df.loc[edited_df["Eliminar"], "Id"].tolist()
        if to_delete:
            for id_val in to_delete:
                try:
                    id_int = int(id_val)
                except Exception:
                    st.error(f"Id inválido para eliminar: {id_val}")
                    continue
                try:
                    deleted = st.session_state.creyentes_crud.delete(id_int)
                except Exception as e:
                    st.error(f"Error eliminando Id {id_int}: {e}")
                    deleted = False
                if deleted:
                    st.success(f"Registro {id_int} eliminado")
                    any_deleted = True
                else:
                    st.error(f"No se pudo eliminar Id {id_int}")

    # Manejar actualizaciones (comparar fila por Id)
    # Ignorar columnas de control
    ignore_cols = {"Id", "Eliminar"}
    for _, row in edited_df.iterrows():
        id_val = row.get("Id", None)
        if id_val is None:
            continue
        try:
            id_int = int(id_val)
        except Exception:
            st.error(f"Id inválido en edición: {id_val}")
            continue

        orig_rows = original_df[original_df["Id"] == id_int]
        if orig_rows.empty:
            # fila nueva o no encontrada en original; saltar
            continue
        orig = orig_rows.iloc[0]

        payload = {}
        changed = False

        for col in edited_df.columns:
            if col in ignore_cols:
                continue
            # Si columna no está en original, comparar igual (puede ser nueva columna)
            new_val = row[col]
            old_val = orig.get(col, None) if col in orig.index else None

            # Normalizar NaN/NAT
            if isna(old_val):
                old_val = None
            if isna(new_val):
                new_val = None

            # Normalizar datetime-like a date (si la columna FechaNac viene como Timestamp)
            if col == "FechaNac" and new_val is not None:
                if isinstance(new_val, (Timestamp, datetime)):
                    new_val = new_val.date()
                # si old_val es Timestamp, convertir para comparación
                if isinstance(old_val, (Timestamp, datetime)):
                    old_val = old_val.date()

            # Mapear boolean-like (p. ej. Encuentro) a boolean
            if isinstance(new_val, (str,)) and new_val.lower() in {"true", "false"}:
                new_val = True if new_val.lower() == "true" else False

            # Comparar
            if old_val != new_val:
                # Normalizar valores a mayúsculas si es string
                payload[col] = new_val.upper() if isinstance(new_val, str) else new_val
                changed = True

        if changed:
            # Añadir campos requeridos por normalize_payload / update
            payload["co_us_mo"] = st.session_state.get("user", 0)
            # Asegurar FechaNac en payload (puede ser None)
            payload.setdefault("FechaNac", payload.get("FechaNac", None))
            # Mantener fecha de creación original
            payload["fe_us_in"] = row["fe_us_in"]
            # Mantener usuario de creación original
            payload["co_us_in"] = row["co_us_in"]

            try:
                safe = st.session_state.creyentes_crud.normalize_payload(payload)
                updated = st.session_state.creyentes_crud.update(id_int, safe)
            except Exception as e:
                st.error(f"Error actualizando Id {id_int}: {e}")
                updated = False

            if updated:
                st.success(f"Id {id_int} actualizado")
                any_updated = True
            else:
                st.error(f"No se pudo actualizar Id {id_int}")

    # Si hubo cambios (borrados o actualizaciones), refrescar listado y recargar la página
    if any_deleted or any_updated:
        actualizar_listado()
        st.rerun()


def render_creyentes_editor():
    rows = st.session_state.lista_creyentes or []
    if not rows:
        st.warning("No se encontraron registros.")
    df = build_creyentes_df(rows)
    original_df = df.copy(deep=True)

    edited = st.data_editor(
        df,
        column_config={
            "Consolidacion": st.column_config.CheckboxColumn(
                "Consolidación?",
                help="Culminó la consolidación.",
                width="large",
            ),
            "Encuentro": st.column_config.CheckboxColumn(
                "Encuentro?",
                help="Culminó el encuentro.",
                width="large",
            ),
            "Academia": st.column_config.CheckboxColumn(
                "Academia?",
                help="Culminó la academia.",
                width="large",
            ),
            "Lanzamiento": st.column_config.CheckboxColumn(
                "Lanzamiento?",
                help="Culminó el lanzamiento.",
                width="large",
            ),
            "FechaNac": st.column_config.DateColumn(
                "Fecha de Nacimiento",
                help="Fecha de nacimiento del creyente.",
                format="DD/MM/YYYY",
            ),
            "FechaIngreso": st.column_config.DateColumn(
                "Fecha de Nacimiento",
                help="Fecha de nacimiento del creyente.",
                format="DD/MM/YYYY",
            ),
            "Estatus": st.column_config.CheckboxColumn(
                "Estatus?",
                help="Activo/Inactivo",
                width="large",
            ),
        },
        use_container_width=True,
        disabled=["Id", "co_us_in", "fe_us_in"],
        hide_index=True,
    )

    process_editor_changes(edited, original_df)


# Replace the big if-body with a single call
if st.session_state.rol_user.has_permission("Creyentes", "update"):
    with st.expander("Listado de creyentes (editor)"):
        render_creyentes_editor()
