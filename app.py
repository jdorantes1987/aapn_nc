import sys
from time import sleep

import streamlit as st

from data.creyentes_crud import CreyentesCRUD

sys.path.append(r"..\aapn_ur")

from auth import AuthManager

# Configuración de página con fondo personalizado
st.set_page_config(
    page_title="Nuevo creyente",
    layout="centered",
    initial_sidebar_state="expanded",
    page_icon="",
)

MENU_INICIO = "pages/page1.py"

st.title("Inicio de sesión")

# Cargar las claves de session si no existen
for key, default in [
    ("stage", 0),
    ("conexion", None),
    ("auth_manager", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def set_stage(i):
    st.session_state.stage = i


if st.session_state.stage == 0:
    st.session_state.password = ""

    sys.path.append(r"..\conexiones")
    from conn.database_connector import DatabaseConnector
    from conn.mysql_connector import MySQLConnector

    mysql_connector = MySQLConnector(
        host=st.secrets.auth.DB_HOST,
        database=st.secrets.auth.DB_NAME,
        user=st.secrets.auth.DB_USER_ADMIN,
        password=st.secrets.auth.DB_PASSWORD,
    )
    mysql_connector.connect()
    # Almacenar la conexión
    st.session_state.conexion = DatabaseConnector(mysql_connector)
    # Almacenar el gestor de autenticación en session_state
    st.session_state.auth_manager = AuthManager(st.session_state.conexion)
    st.session_state.creyentes_crud = CreyentesCRUD(st.session_state.conexion)
    st.session_state.lista_creyentes = st.session_state.creyentes_crud.list()
    st.session_state.lista_redes = st.session_state.creyentes_crud.get_list_redes()

    set_stage(1)


def existe_user(username):
    return st.session_state.auth_manager.user_existe(username)


def login(user, passw):
    return st.session_state.auth_manager.autenticar(user, passw)


@st.cache_data(show_spinner=False)
def iniciar_sesion(user, password):
    flag, msg = login(user=user, passw=password)

    if not flag:
        st.toast(msg, icon="⚠️")
    else:
        st.toast(msg, icon="✅")
        st.session_state.logged_in = True
        st.session_state.user = user
        st.switch_page(MENU_INICIO)


if st.session_state.stage == 1:
    if "usuario" not in st.session_state:
        # Si el usuario aún no ha sido ingresado
        user = st.text_input("", placeholder="Ingresa tu usuario y presiona Enter")
        if existe_user(user):
            st.session_state.usuario = user
            st.success("Usuario validado!")
            sleep(1)
            st.rerun()
        else:
            if user:
                st.error("El usuario no existe. Inténtalo de nuevo.")
    else:
        # Si el usuario ya ha sido ingresado, se oculta el input y se muestra el usuario ingresado
        st.write(f"### Usuario ingresado: {st.session_state.usuario}")

        # Pedir la contraseña
        pw = st.text_input(
            "",
            type="password",
            key="password",
            placeholder="Ingresa tu contraseña y presiona Enter",
        )
        if st.session_state.password:
            iniciar_sesion(st.session_state.usuario, st.session_state.password)
        else:
            if st.button("Atrás", type="primary"):
                del st.session_state.usuario
                del st.session_state.password
                st.rerun()
