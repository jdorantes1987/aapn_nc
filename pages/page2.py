from datetime import date, datetime

import streamlit as st

from helpers.navigation import make_sidebar

st.set_page_config(page_title="Registro de nuevo creyente", layout="wide", page_icon="")

make_sidebar()

st.title("Datos del nuevo creyente")


def actualizar_listado():
    st.session_state.lista_creyentes = st.session_state.creyentes_crud.list()


if st.button("Refrescar"):
    actualizar_listado()

if "stage2" not in st.session_state:
    st.session_state.stage2 = 0


def set_stage(i):
    st.session_state.stage2 = i


def get_default_profesion_option():
    lista_profesiones = st.session_state.get("lista_profesiones", [])
    pares_codigo_nombre = [
        f"{d['IdProfesion']}|{d['DescripcionProfesion'].strip()}"
        for d in lista_profesiones
    ]
    for opcion in pares_codigo_nombre:
        if opcion.split("|", 1)[1].upper() == "SIN ASIGNAR":
            return opcion
    return pares_codigo_nombre[0] if pares_codigo_nombre else None


def reset_nuevo_creyente_controles():
    hoy = date.today()

    # Restablecer widgets de valor fijo antes de su instanciación.
    st.session_state.txt_cedula = ""
    st.session_state.txt_nombre = ""
    st.session_state.txt_apellido = ""
    st.session_state.txt_telefono = ""
    st.session_state.txt_correo = ""
    st.session_state.txt_ocupacion = ""
    st.session_state.estado_civil_select = "Soltero(a)"
    st.session_state.fecha_nac_input = hoy
    st.session_state.sel_nacionalidad = "V"
    st.session_state.sel_sexo = "M"
    st.session_state.sel_estatus = 1
    default_profesion = get_default_profesion_option()
    if default_profesion is not None:
        st.session_state.sel_profesion = default_profesion

    # Limpiar widgets de opciones dinámicas.
    st.session_state.pop("sel_codred", None)
    st.session_state.pop("fecha_convivencia_input", None)
    st.session_state.pop("fecha_matrimonio_input", None)

    # Restaurar claves auxiliares (no widgets).
    st.session_state.estado_civil_seleccionado = "Soltero(a)"
    st.session_state.estado_civil_actual = "Soltero(a)"


# Inicializar campos de texto
if st.session_state.stage2 == 0:
    st.session_state.edo_civil = ""
    set_stage(1)

if "estado_civil_seleccionado" not in st.session_state:
    st.session_state.estado_civil_seleccionado = "Soltero(a)"

if "estado_civil_actual" not in st.session_state:
    st.session_state.estado_civil_actual = "Soltero(a)"

if "fecha_nac_input" not in st.session_state:
    st.session_state.fecha_nac_input = date.today()

if "reset_nuevo_creyente_pending" not in st.session_state:
    st.session_state.reset_nuevo_creyente_pending = False

if st.session_state.reset_nuevo_creyente_pending:
    reset_nuevo_creyente_controles()
    st.session_state.reset_nuevo_creyente_pending = False

# Requiere que la conexión esté disponible en session_state como 'conexion'
if "conexion" not in st.session_state or st.session_state.conexion is None:
    st.error(
        "No hay conexión a la base de datos. Vuelve a la página de inicio para inicializarla."
    )
    st.stop()

# Formulario de creación
if st.session_state.stage2 >= 1:
    # con icono de nuevo registro asterisco verde
    with st.expander("🟢 Nuevo creyente"):
        hoy = date.today()
        # Define the allowed date range
        min_allowed_date = date(1950, 1, 1)
        max_allowed_date = hoy

        col1, col2 = st.columns([0.12, 0.88])
        with col1:
            nacionalidad = st.selectbox(
                "Nacionalidad",
                options=["V", "E"],
                index=0,
                help="Selecciona la nacionalidad del creyente",
                key="sel_nacionalidad",
            )
        with col2:
            cedula = st.text_input(
                "Cédula *",
                placeholder="Ejemplo: 18560791",
                key="txt_cedula",
                max_chars=8,
            ).upper()

        col3, col4 = st.columns([0.50, 0.50])
        with col3:
            nombre = st.text_input(
                "📝 Nombre *", key="txt_nombre", max_chars=25
            ).upper()
        with col4:
            apellido = st.text_input(
                "📝 Apellido *", key="txt_apellido", max_chars=25
            ).upper()

        col5, col6, col7, col8 = st.columns([0.24, 0.10, 0.23, 0.43])

        with col5:
            telefono = st.text_input(
                "📞 Teléfono Celular *",
                key="txt_telefono",
                placeholder="Ejemplo: 4143456789",
                max_chars=14,
            ).upper()
        with col6:
            sexo = st.selectbox(
                "⚧ Sexo",
                options=["M", "F"],
                index=0,
                help="Selecciona el sexo del creyente",
                key="sel_sexo",
            )
        with col7:
            fecha_nac = st.date_input(
                "📅 Fecha de nacimiento",
                format="DD/MM/YYYY",
                min_value=min_allowed_date,
                max_value=max_allowed_date,
                key="fecha_nac_input",
            )

        with col8:
            correo = st.text_input(
                "📧 Correo",
                key="txt_correo",
                placeholder="Ejemplo: mi_direccion@correo.com",
                max_chars=40,
            ).lower()

        lista_profesiones = st.session_state.get("lista_profesiones", [])
        pares_codigo_nombre = [
            (str(d["IdProfesion"]) + "|" + d["DescripcionProfesion"].strip())
            for d in lista_profesiones
        ]
        default_profesion = get_default_profesion_option()
        if (
            default_profesion is not None
            and st.session_state.get("sel_profesion") not in pares_codigo_nombre
        ):
            st.session_state.sel_profesion = default_profesion
        profesion = st.selectbox(
            "Elije una profesión:",
            options=pares_codigo_nombre,
            key="sel_profesion",
        )
        profesion = str(profesion).split("|")[0]  # Obtener solo el IdProfesion

        ocupacion = st.text_input(
            "Ocupación", key="txt_ocupacion", max_chars=20
        ).upper()

        lista_redes = st.session_state.get("lista_redes", [])
        pares_codigo_nombre = [
            (d["CodRed"] + "|" + d["NombreRed"].strip()) for d in lista_redes
        ]

        estado_civil = st.selectbox(
            "Estado Civil",
            options=["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)"],
            index=0,
            key="estado_civil_select",
        )
        st.session_state.estado_civil_seleccionado = estado_civil
        st.session_state.estado_civil_actual = estado_civil

        fecha_convivencia = None
        fecha_matrimonio = None
        if st.session_state.estado_civil_actual == "Casado(a)":
            fecha_convivencia = st.date_input(
                "Fecha de convivencia",
                value=None,
                format="DD/MM/YYYY",
                min_value=min_allowed_date,
                max_value=max_allowed_date,
                key="fecha_convivencia_input",
            )
            fecha_matrimonio = st.date_input(
                "Fecha de matrimonio",
                value=None,
                format="DD/MM/YYYY",
                min_value=min_allowed_date,
                max_value=max_allowed_date,
                key="fecha_matrimonio_input",
            )
        else:
            st.session_state.pop("fecha_convivencia_input", None)
            st.session_state.pop("fecha_matrimonio_input", None)

        codred = st.selectbox(
            "Elije una red:",
            options=pares_codigo_nombre,
            index=0,
            key="sel_codred",
        )
        codred = str(codred).split("|")[0]  # Obtener solo el código
        estatus = st.selectbox(
            "Estatus",
            options=[1, 0],
            format_func=lambda x: "Activo" if x == 1 else "Inactivo",
            key="sel_estatus",
        )

        submitted = st.button("Crear", use_container_width=False)
        if submitted:
            campos_obligatorios = {
                "Cédula": cedula,
                "Nombre": nombre,
                "Apellido": apellido,
                "Teléfono": telefono,
            }
            faltantes = [
                campo
                for campo, valor in campos_obligatorios.items()
                if not str(valor).strip()
            ]
            if faltantes:
                st.error(f"Completa los campos obligatorios: {', '.join(faltantes)}")
                st.stop()

            payload = {
                "Cedula": cedula,
                "Nacionalidad": nacionalidad,
                "Nombre": nombre,
                "Apellido": apellido,
                "IdProfesion": profesion,
                "Ocupacion": ocupacion,
                "TelefonoCelular": telefono,
                "Correo": correo,
                "EstadoCivil": st.session_state.estado_civil_actual[0],
                "FechaConvivencia": (fecha_convivencia if fecha_convivencia else None),
                "FechaMatrimonio": (fecha_matrimonio if fecha_matrimonio else None),
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
                st.success(f"🙋‍♂️ Creyente {nombre} {apellido} creado con Id {new_id}")
                actualizar_listado()
                st.session_state.reset_nuevo_creyente_pending = True
                st.rerun()
            else:
                st.error("No se pudo crear el nuevo creyente.")


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
        return

    # Filtrar sin usar pandas por columna fe_us_in para mostrar solo los registros creados hoy
    hoy = date.today()
    rows = [
        row
        for row in rows
        if "fe_us_in" in row
        and row["fe_us_mo"] is not None
        and row["fe_us_mo"].date() == hoy
    ]

    if not rows:
        st.info("No hay registros creados hoy.")
        return

    df = build_creyentes_df(rows)
    original_df = df.copy(deep=True)

    edited = st.data_editor(
        df,
        column_config={
            "Consolidacion": st.column_config.CheckboxColumn(
                "Consolidación?",
                help="Culminó la consolidación.",
                width="small",
            ),
            "Encuentro": st.column_config.CheckboxColumn(
                "Encuentro?",
                help="Culminó el encuentro.",
                width="small",
            ),
            "Academia": st.column_config.CheckboxColumn(
                "Academia?",
                help="Culminó la academia.",
                width="small",
            ),
            "Lanzamiento": st.column_config.CheckboxColumn(
                "Lanzamiento?",
                help="Culminó el lanzamiento.",
                width="small",
            ),
            "Bautizo": st.column_config.CheckboxColumn(
                "Bautizo?",
                help="Culminó el bautizo.",
                width="small",
            ),
            "FechaNac": st.column_config.DateColumn(
                "Fecha de Nacimiento",
                help="Fecha de nacimiento del creyente.",
                format="DD-MM-YYYY",
            ),
            "Estatus": st.column_config.CheckboxColumn(
                "Estatus?",
                help="Activo/Inactivo",
                width="large",
            ),
        },
        use_container_width=True,
        disabled=[
            "Id",
            "co_us_in",
            "fe_us_in",
            "Bautizo",
            "Consolidacion",
            "Encuentro",
            "Academia",
            "Lanzamiento",
        ],
        hide_index=True,
    )

    process_editor_changes(edited, original_df)


# Replace the big if-body with a single call
if st.session_state.rol_user.has_permission("Creyentes", "update"):
    with st.expander("✏️ Listado de creyentes (editor)"):
        render_creyentes_editor()
