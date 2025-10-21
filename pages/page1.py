import streamlit as st

from helpers.navigation import make_sidebar

st.set_page_config(page_title="Inicio", layout="wide", page_icon="")

t1, t2 = st.columns((0.5, 5))
make_sidebar()

with st.expander("Instrucciones para registrar un nuevo creyente", expanded=False):
    texto = """
        Para registrar la información de un nuevo creyente, sigue estos pasos:
        1. **Ir a la pestaña de registro**: Selecciona la pestaña **:green["Registro"]** en el menú lateral.
        2. **Completa los campos requeridos**:
            - **:blue[Nombre]**: Ingresa el nombre del nuevo creyente.
            - **:blue[Apellido]**: Ingresa el apellido del nuevo creyente.
            - **:blue[Edad]**: Ingresa la edad del nuevo creyente.
            - **:blue[Teléfono]**: Ingresa el número de teléfono del nuevo creyente.
            - **:blue[Correo electrónico]**: Ingresa el correo electrónico del nuevo creyente.
            - **:blue[Fecha de nacimiento]**: Selecciona la fecha de nacimiento del nuevo creyente.
    """
    st.write(texto)
