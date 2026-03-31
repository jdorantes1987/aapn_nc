import streamlit as st
import streamlit.components.v1 as components

from helpers.navigation import make_sidebar

st.set_page_config(page_title="Inicio", layout="wide", page_icon="")

make_sidebar()


def mostrar_fase_ganar():
    st.title("Visualización de Estrategia")

    # Código HTML/CSS/JS con el flujo completo pero enfoque en "Ganar"
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
            body { font-family: 'Poppins', sans-serif; background: transparent; margin: 0; overflow: hidden; }

            .river-container {
                position: relative;
                height: 180px;
                background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
                border-radius: 24px;
                display: flex;
                align-items: center;
                justify-content: space-around;
                box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.5);
                margin-bottom: 24px;
                overflow: hidden;
                padding: 0 20px;
            }

            .river-wave {
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 30px;
                background: url('https://raw.githubusercontent.com/front-end-relative/assets/main/wave.png');
                background-size: 1000px 30px;
                animation: move-wave 8s linear infinite;
                opacity: 0.2;
            }

            @keyframes move-wave {
                0% { background-position-x: 0; }
                100% { background-position-x: 1000px; }
            }

            .node {
                display: flex;
                flex-direction: column;
                align-items: center;
                position: relative;
                z-index: 10;
                transition: all 0.3s ease;
            }

            .node-circle {
                width: 50px;
                height: 50px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: rgba(255, 255, 255, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.3);
            }

            /* Estilo específico para el nodo enfocado: GANAR */
            .node.focused .node-circle {
                width: 85px;
                height: 85px;
                background: white;
                color: #1e40af;
                box-shadow: 0 0 25px rgba(251, 191, 36, 0.6);
                border: 4px solid #fbbf24;
                transform: scale(1.1);
            }

            .node.focused .label {
                color: white;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                font-size: 0.85rem;
            }

            .label {
                margin-top: 8px;
                font-size: 0.65rem;
                color: rgba(255, 255, 255, 0.5);
                text-transform: uppercase;
                font-weight: 600;
            }

            .content-card {
                background: white;
                padding: 24px;
                border-radius: 20px;
                border: 1px solid #e2e8f0;
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 20px;
                align-items: center;
            }
        </style>
    </head>
    <body>
        <div class="river-container">
            <div class="river-wave"></div>

            <!-- Nodo Enfocado: GANAR -->
            <div class="node focused">
                <div class="node-circle">
                    <i class="fas fa-hand-holding-heart text-2xl"></i>
                </div>
                <div class="label">Ganar</div>
            </div>

            <!-- Nodos Atenuados (Contexto) -->
            <div class="node">
                <div class="node-circle">
                    <i class="fas fa-users-rays text-lg"></i>
                </div>
                <div class="label">Consolidar</div>
            </div>

            <div class="node">
                <div class="node-circle">
                    <i class="fas fa-book-open text-lg"></i>
                </div>
                <div class="label">Formar</div>
            </div>

            <div class="node">
                <div class="node-circle">
                    <i class="fas fa-user-friends text-lg"></i>
                </div>
                <div class="label">Discipular</div>
            </div>

            <div class="node">
                <div class="node-circle">
                    <i class="fas fa-paper-plane text-lg"></i>
                </div>
                <div class="label">Enviar</div>
            </div>
        </div>

        <div class="content-card">
            <div>
                <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-bold uppercase">Fase 1 de 5</span>
                <h2 class="text-2xl font-bold text-slate-800 mt-2 mb-2">PROCESO: GANAR</h2>
                <p class="text-slate-600 text-sm leading-relaxed">
                    Esta es la puerta de entrada a la visión. Nos enfocamos en la evangelización estratégica para traer nuevas vidas al cauce del Río de Dios.
                </p>
                <div class="mt-4 flex gap-4">
                    <div class="flex items-center text-xs font-semibold text-slate-700">
                        <i class="fas fa-check-circle text-blue-500 mr-2"></i> Evangelismo Personal
                    </div>
                    <div class="flex items-center text-xs font-semibold text-slate-700">
                        <i class="fas fa-check-circle text-blue-500 mr-2"></i> Brigadas de Amor
                    </div>
                </div>
            </div>
            <div class="opacity-10 text-6xl text-blue-600">
                <i class="fas fa-hand-holding-heart"></i>
            </div>
        </div>
    </body>
    </html>
    """

    # Renderizar el componente en Streamlit
    components.html(html_code, height=450)


mostrar_fase_ganar()

with st.expander(
    "Para registrar la información de un nuevo creyente, sigue estos pasos:"
):
    texto = """
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
    st.write(texto)
