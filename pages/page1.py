import streamlit as st
import time

from helpers.navigation import make_sidebar

st.set_page_config(page_title="Inicio", layout="wide", page_icon="")
TTL = 24 * 60 * 60


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01)


t1, t2 = st.columns((0.5, 5))
make_sidebar()

st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=78)

st.write(
    """
    # Bienvenido al módulo de registro de nuevos creyentes! 👋.
    ¡Comencemos! 🚀
    """
)

st.write(
    """
    ## ¿Cómo realizar un nuevo registro?
    """
)


texto = """
    Para registrar la información de un nuevo creyente, sigue estos pasos:
    1. **Ir a la pestaña de registro**: Selecciona la pestaña :green-badge[:material/chevron_right: Registro] en el menú lateral.
    2. **Completa los campos requeridos**:
        - 🌐 **:blue[Nacionalidad]**: Selecciona **V** o **E**.
        - 🆔 **:blue[Cédula]**: Ingresa la cédula sin guiones ni espacios (ejemplo: 12345678).
        - 📝 **:blue[Nombre]**:
        - 📝 **:blue[Apellido]**:
        - 📞 **:blue[Teléfono Celular]**: Ingresa el número sin guiones ni espacios (ejemplo: 4143456789).
        - ⚧ **:blue[Sexo]**:
        - 📅 **:blue[Fecha de nacimiento]**:
        - 📧 **:blue[Correo]**:
        - 💼 **:blue[Profesión]**:
        - 🏢 **:blue[Ocupación]**:
        - 💍 **:blue[Estado Civil]**:
        - 📅 **:blue[Fecha de convivencia]**:
        - 📅 **:blue[Fecha de matrimonio]**:
        - 🌐 **:blue[Red]**:
        - **:blue[Estatus]**:
    3. **✳️ Crear registro**: Presiona el botón :gray-badge[Crear] para guardar el nuevo creyente.
"""
st.write_stream(stream_data(texto))
