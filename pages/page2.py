from datetime import date, datetime
from time import sleep
from pandas import DataFrame, to_datetime, isna

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

if st.session_state.stage2 >= 1:
    with st.expander("Crear nuevo creyente"):
        with st.form("form_crear", clear_on_submit=True):
            hoy = date.today()
            # Define the allowed date range
            min_allowed_date = date(1950, 1, 1)
            max_allowed_date = hoy
            cedula = st.text_input(
                "Cédula",
                help="Número de cédula sin guiones ni espacios",
                key="txt_cedula",
            )
            nombre = st.text_input("Nombre", key="txt_nombre")
            apellido = st.text_input("Apellido", key="txt_apellido")
            telefono = st.text_input("Teléfono Celular", key="txt_telefono")
            sexo = st.selectbox(
                "Sexo",
                options=["M", "F"],
                index=0,
                help="Selecciona el sexo del creyente",
            )

            correo = st.text_input("Correo", key="txt_correo")

            lista_redes = st.session_state.get("lista_redes", [])
            pares_codigo_nombre = [
                (d["CodRed"] + "|" + d["NombreRed"].strip()) for d in lista_redes
            ]
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
            encuentro = st.checkbox("Culminó el encuentro", value=False)
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

# Listado y selección (ahora editable)

with st.expander("Listado de creyentes (editor)"):
    rows = st.session_state.lista_creyentes
    if not rows:
        st.warning("No se encontraron registros.")
        # Continue with an empty list so the rest of the code can run without a large nested else
        rows = []

    # Construir DataFrame
    df = DataFrame(rows)
    # Asegurar columnas esperadas
    if "Id" not in df.columns:
        df["Id"] = df.index
    # Normalizar FechaNac a date (si viene como string/timestamp)
    if "FechaNac" in df.columns:
        df["FechaNac"] = to_datetime(df["FechaNac"], errors="coerce").dt.date
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
        use_container_width=True,
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
            count = st.session_state.creyentes_crud.delete(id_int)
            if count:
                actualizar_listado()
                st.success(f"Registro {id_int} eliminado")
                sleep(1)
                set_stage(2)
                st.rerun()
            else:
                st.error(f"No se pudo eliminar Id {id_int}")

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
                if isna(old_val):
                    old_val = None
                if isna(new_val):
                    new_val = None
                if old_val != new_val:
                    payload[col] = new_val
                    changed = True
        if changed:
            # Añadir campos requeridos por normalize_payload / update
            # Ajustar campos que espera el CRUD
            payload.setdefault("FechaNac", payload.get("FechaNac", None))
            payload["co_us_mo"] = st.session_state.get("user", 0)
            payload["fe_us_mo"] = datetime.now()
            # Mantener fe_us_in original
            payload["fe_us_in"] = row["fe_us_in"]
            safe = st.session_state.creyentes_crud.normalize_payload(payload)
            try:
                updated = st.session_state.creyentes_crud.update(int(id_val), safe)
            except Exception as e:
                st.error(f"Error actualizando Id {id_val}: {e}")
                updated = False
            if updated:
                st.success(f"Id {id_val} actualizado")
            else:
                st.error(f"No se pudo actualizar Id {id_val}")
