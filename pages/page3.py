import streamlit as st
from pandas import DataFrame, to_datetime

from helpers.navigation import make_sidebar

st.set_page_config(page_title="Datos del creyente", layout="wide", page_icon="")

make_sidebar()

st.title("Datos de creyentes")


def estatus_a_num(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    value_str = str(value).strip().lower()
    if value_str in {"1", "true", "t", "si", "sí", "activo"}:
        return 1
    if value_str in {"0", "false", "f", "no", "inactivo"}:
        return 0
    return None


def actualizar_listado():
    st.session_state.lista_creyentes = st.session_state.creyentes_crud.list(limit=500)


def build_creyentes_df(rows):
    df = DataFrame(rows) if rows else DataFrame()
    if df.empty:
        return df

    if "FechaNac" in df.columns:
        df["FechaNac"] = to_datetime(df["FechaNac"], errors="coerce").dt.date

    if "fe_us_in" in df.columns:
        df["fe_us_in"] = to_datetime(df["fe_us_in"], errors="coerce")

    if "fe_us_mo" in df.columns:
        df["fe_us_mo"] = to_datetime(df["fe_us_mo"], errors="coerce")

    if "EstadoCivil" in df.columns:
        estado_civil_map = {
            "S": "Soltero(a)",
            "C": "Casado(a)",
            "D": "Divorciado(a)",
            "V": "Viudo(a)",
            "U": "Unión de hecho",
        }
        df["EstadoCivilTexto"] = (
            df["EstadoCivil"].map(estado_civil_map).fillna(df["EstadoCivil"])
        )

    return df


def limpiar_filtros(fecha_rango_default=None):
    st.session_state.filtro_busqueda = ""
    st.session_state.filtro_sexo = "Todos"
    st.session_state.filtro_estatus = "Todos"
    st.session_state.filtro_red = "Todas"
    st.session_state.filtro_estado_civil = []
    if fecha_rango_default is not None:
        st.session_state.filtro_fecha_nac = fecha_rango_default
    else:
        st.session_state.pop("filtro_fecha_nac", None)


if "conexion" not in st.session_state or st.session_state.conexion is None:
    st.error("No hay conexión a la base de datos. Vuelve a Inicio para inicializarla.")
    st.stop()

if "lista_creyentes" not in st.session_state:
    actualizar_listado()

if st.button("Refrescar datos"):
    actualizar_listado()

rows = st.session_state.get("lista_creyentes", [])
df = build_creyentes_df(rows)

if df.empty:
    st.warning("No se encontraron registros de creyentes.")
    st.stop()

lista_redes = st.session_state.get("lista_redes", [])
redes_map = {str(r["CodRed"]): str(r["NombreRed"]).strip() for r in lista_redes}

fecha_rango_default = None
if "FechaNac" in df.columns and df["FechaNac"].notna().any():
    fecha_min = df["FechaNac"].dropna().min()
    fecha_max = df["FechaNac"].dropna().max()
    fecha_rango_default = (fecha_min, fecha_max)
    if "filtro_fecha_nac" not in st.session_state:
        st.session_state.filtro_fecha_nac = fecha_rango_default
    else:
        rango_guardado = st.session_state.filtro_fecha_nac
        rango_valido = (
            isinstance(rango_guardado, tuple)
            and len(rango_guardado) == 2
            and rango_guardado[0] is not None
            and rango_guardado[1] is not None
            and fecha_min <= rango_guardado[0] <= fecha_max
            and fecha_min <= rango_guardado[1] <= fecha_max
            and rango_guardado[0] <= rango_guardado[1]
        )
        if not rango_valido:
            st.session_state.filtro_fecha_nac = fecha_rango_default

if "filtro_busqueda" not in st.session_state:
    st.session_state.filtro_busqueda = ""
if "filtro_sexo" not in st.session_state:
    st.session_state.filtro_sexo = "Todos"
if "filtro_estatus" not in st.session_state:
    st.session_state.filtro_estatus = "Todos"
if "filtro_red" not in st.session_state:
    st.session_state.filtro_red = "Todas"
if "filtro_estado_civil" not in st.session_state:
    st.session_state.filtro_estado_civil = []

with st.expander("Filtros", expanded=True):
    a1, a2 = st.columns([0.8, 0.2])
    with a2:
        st.button(
            "Borrar filtros",
            use_container_width=True,
            on_click=limpiar_filtros,
            kwargs={"fecha_rango_default": fecha_rango_default},
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        texto_busqueda = st.text_input(
            "Buscar por cédula, nombre, apellido, correo o teléfono",
            placeholder="Escribe para filtrar...",
            key="filtro_busqueda",
        ).strip()
    with c2:
        sexo = st.selectbox(
            "Sexo",
            options=["Todos", "M", "F"],
            key="filtro_sexo",
        )
    with c3:
        estatus = st.selectbox(
            "Estatus",
            options=["Todos", "Activo", "Inactivo"],
            key="filtro_estatus",
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        redes_opciones = ["Todas"] + [
            f"{cod} - {nombre}" for cod, nombre in redes_map.items()
        ]
        if st.session_state.filtro_red not in redes_opciones:
            st.session_state.filtro_red = "Todas"
        red_seleccionada = st.selectbox(
            "Red",
            options=redes_opciones,
            key="filtro_red",
        )
    with c5:
        if "EstadoCivilTexto" in df.columns:
            estados_disponibles = sorted(
                df["EstadoCivilTexto"].dropna().unique().tolist()
            )
        else:
            estados_disponibles = []
        st.session_state.filtro_estado_civil = [
            e for e in st.session_state.filtro_estado_civil if e in estados_disponibles
        ]
        estado_civil = st.multiselect(
            "Estado civil",
            options=estados_disponibles,
            key="filtro_estado_civil",
        )
    with c6:
        fecha_nac_rango = None
        if fecha_rango_default is not None:
            fecha_min, fecha_max = fecha_rango_default
            fecha_nac_rango = st.date_input(
                "Rango fecha de nacimiento",
                min_value=fecha_min,
                max_value=fecha_max,
                format="DD/MM/YYYY",
                key="filtro_fecha_nac",
            )
        else:
            st.caption("Sin datos de fecha de nacimiento para filtrar")

df_filtrado = df.copy()

if texto_busqueda:
    texto = texto_busqueda.lower()
    columnas_busqueda = [
        c
        for c in ["Cedula", "Nombre", "Apellido", "Correo", "TelefonoCelular"]
        if c in df_filtrado.columns
    ]
    if columnas_busqueda:
        mask = False
        for col in columnas_busqueda:
            mask = mask | df_filtrado[col].astype(str).str.lower().str.contains(
                texto, na=False
            )
        df_filtrado = df_filtrado[mask]

if sexo != "Todos" and "Sexo" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Sexo"] == sexo]

if estatus != "Todos" and "Estatus" in df_filtrado.columns:
    estatus_objetivo = 1 if estatus == "Activo" else 0
    df_filtrado = df_filtrado[
        df_filtrado["Estatus"].apply(estatus_a_num) == estatus_objetivo
    ]

if red_seleccionada != "Todas" and "CodRed" in df_filtrado.columns:
    cod = red_seleccionada.split(" - ", 1)[0]
    df_filtrado = df_filtrado[df_filtrado["CodRed"].astype(str) == cod]

if estado_civil and "EstadoCivilTexto" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["EstadoCivilTexto"].isin(estado_civil)]

if fecha_nac_rango and "FechaNac" in df_filtrado.columns:
    if isinstance(fecha_nac_rango, tuple) and len(fecha_nac_rango) == 2:
        desde, hasta = fecha_nac_rango
        df_filtrado = df_filtrado[
            (df_filtrado["FechaNac"] >= desde) & (df_filtrado["FechaNac"] <= hasta)
        ]

total = len(df)
filtrados = len(df_filtrado)
activos = (
    int((df_filtrado["Estatus"].apply(estatus_a_num) == 1).sum())
    if "Estatus" in df_filtrado.columns
    else 0
)

m1, m2, m3 = st.columns(3)
m1.metric("Total registros", total)
m2.metric("Resultado filtrado", filtrados)
m3.metric("Activos en resultado", activos)

columnas_mostrar = [
    c
    for c in [
        "Id",
        "Nacionalidad",
        "Cedula",
        "Nombre",
        "Apellido",
        "Sexo",
        "FechaNac",
        "TelefonoCelular",
        "Correo",
        "Ocupacion",
        "CodRed",
        "EstadoCivilTexto",
        "Estatus",
        "fe_us_in",
    ]
    if c in df_filtrado.columns
]

if not df_filtrado.empty:
    st.dataframe(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No hay resultados con los filtros seleccionados.")
