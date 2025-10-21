from datetime import date

import streamlit as st

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
        cedula = st.text_input("Cédula")
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        telefono = st.text_input("Teléfono Celular")
        correo = st.text_input("Correo")
        codred = st.text_input("CodRed")
        hoy = date.today()
        fecha_nac = st.date_input("Fecha de nacimiento", value=hoy, format="DD/MM/YYYY")
        estatus = st.selectbox(
            "Estatus",
            options=[1, 0],
            format_func=lambda x: "Activo" if x == 1 else "Inactivo",
        )

        submitted = st.form_submit_button("Crear")
        if submitted:
            payload = {
                "Id": 2,
                "Cedula": cedula,
                "Nombre": nombre,
                "Apellido": apellido,
                "IdProfesion": 17,
                "TelefonoCelular": telefono,
                "Correo": correo,
                "CodRed": codred,
                "FechaNac": fecha_nac if fecha_nac else None,
                "Estatus": estatus,
                "co_us_in": st.session_state.get("user", 0),
                "co_us_mo": st.session_state.get("user", 0),
            }
            safe = CreyentesCRUD.normalize_payload(payload)
            new_id = crud.create(safe)
            if new_id:
                st.success(f"Creado con Id {new_id}")
            else:
                st.info("Creado (id no retornado) o hubo un problema")

st.markdown("---")

# Listado y selección
st.header("Listado de creyentes")
rows = crud.list(200)

if not rows:
    st.info("No se encontraron registros.")
else:
    cols = st.columns((3, 1))
    with cols[0]:
        for r in rows:
            with st.expander(f"{r.get('Id')} - {r.get('Nombre')} {r.get('Apellido')}"):
                st.write(r)
                if st.button(f"Editar {r.get('Id')}", key=f"edit_{r.get('Id')}"):
                    st.session_state._editing = r.get("Id")
                    st.rerun()
                if st.button(f"Borrar {r.get('Id')}", key=f"del_{r.get('Id')}"):
                    count = crud.delete(r.get("Id"))
                    if count:
                        st.success("Registro eliminado")
                        st.rerun()
                    else:
                        st.error("No se pudo eliminar")

# Edit form
if st.session_state.get("_editing"):
    id_edit = st.session_state.get("_editing")
    row = crud.get_by_id(id_edit)
    if row:
        st.header(f"Editar Id {id_edit}")
        with st.form("form_editar"):
            nombre = st.text_input("Nombre", value=row.get("Nombre", ""))
            apellido = st.text_input("Apellido", value=row.get("Apellido", ""))
            telefono = st.text_input(
                "Teléfono Celular", value=row.get("TelefonoCelular", "")
            )
            correo = st.text_input("Correo", value=row.get("Correo", ""))
            codred = st.text_input("CodRed", value=row.get("CodRed", ""))
            fecha_nac = st.date_input(
                "Fecha de nacimiento", value=row.get("FechaNac") or date.today()
            )
            estatus = st.selectbox(
                "Estatus", options=[1, 0], index=0 if row.get("Estatus") == 1 else 1
            )

            submitted = st.form_submit_button("Guardar")
            if submitted:
                payload = {
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "TelefonoCelular": telefono,
                    "Correo": correo,
                    "CodRed": codred,
                    "FechaNac": fecha_nac,
                    "Estatus": estatus,
                    "fe_us_mo": None,
                    "co_us_mo": st.session_state.get("user_id", 0),
                }
                safe = CreyentesCRUD.normalize_payload(payload)
                updated = crud.update(id_edit, safe)
                if updated:
                    st.success("Actualizado")
                    st.session_state.pop("_editing", None)
                    st.rerun()
                else:
                    st.error("No se pudo actualizar")
    else:
        st.error("Registro no encontrado")
        st.session_state.pop("_editing", None)
