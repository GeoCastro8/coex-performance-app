import streamlit as st

def apply_premium_theme():
    """
    Aplica una interfaz ultra-premium basada en Soft Light Glassmorphism.
    """
    glass_css = """
    <style>
        /* Importar fuente moderna */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        /* Fondo global de la aplicación (Malla Gradiente Suave) */
        .stApp {
            background: linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%);
            font-family: 'Outfit', sans-serif;
        }

        /* Ocultar menú lateral y cabecera de Streamlit */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}

        /* Tipografía general oscuro para contraste perfecto */
        html, body, [class*="css"] {
            color: #1e293b;
        }

        /* Títulos principales */
        h1, h2, h3 {
            color: #0f172a;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }

        /* --- STYLES PARA LA NAVEGACIÓN (TABS) ALTERNATIVA MINIMALISTA --- */
        .stPageLink {
            width: 100% !important;
            display: flex;
            justify-content: center;
        }
        [data-testid="stPageLink-NavLink"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 12px 5px !important;
            display: flex !important;
            align-items: center;
            justify-content: center;
            width: 100% !important;
            height: 100%;
            transition: all 0.2s ease-in-out !important;
        }
        [data-testid="stPageLink-NavLink"] p {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #64748b !important; /* Color gris suave */
            margin: 0;
            white-space: normal !important;
            line-height: 1.2;
            text-align: center;
            transition: color 0.2s ease;
        }
        [data-testid="stPageLink-NavLink"]:hover {
            background: transparent !important;
            transform: translateY(0px) !important;
            box-shadow: none !important;
        }
        [data-testid="stPageLink-NavLink"]:hover p {
            color: #2563eb !important; /* Texto azul al pasar el ratón */
        }
        
        /* Estado Activo/Seleccionado */
        [data-testid="stPageLink-NavLink"][aria-current] p, 
        [data-testid="stPageLink-NavLink"][data-active="true"] p {
            color: #2563eb !important; /* Texto azul cuando la pestaña está activa */
            font-weight: 700 !important;
        }

        /* --- STYLES PARA FORMULARIOS Y CONTENEDORES (GLASS) --- */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.45) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(255, 255, 255, 0.8) !important;
            border-radius: 24px !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
            padding: 2.5rem !important;
            transition: transform 0.3s ease;
        }
        [data-testid="stForm"]:hover {
            transform: scale(1.005);
        }

        /* Botones de Acción principales */
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
        }
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5) !important;
        }

        /* Inputs de texto y números */
        .stTextInput input, .stNumberInput input {
            background: rgba(255, 255, 255, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            border-radius: 10px !important;
            color: #0f172a !important;
            font-weight: 500 !important;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
        }
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3) !important;
            background: rgba(255, 255, 255, 0.9) !important;
        }

        /* Tarjetas de Métricas en el Dashboard */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            background: -webkit-linear-gradient(135deg, #1e40af, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.7) !important;
            border-radius: 20px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
        }
    </style>
    """
    st.markdown(glass_css, unsafe_allow_html=True)

def render_top_navigation():
    # Usamos 6 columnas exactamente iguales. 
    # Ahora sí, el CSS forzará a que el botón se expanda a todo el ancho de la columna,
    # asegurando que el espacio vacío entre ellos sea idéntico y perfecto.
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        st.page_link("app.py", label="Dashboard", icon="📊")
    with c2:
        st.page_link("pages/1_Formulario_Peso.py", label="Peso", icon="⚖️")
    with c3:
        st.page_link("pages/2_Formulario_Densidad.py", label="Densidad", icon="🔬")
    with c4:
        st.page_link("pages/3_Formulario_Llenado.py", label="Llenado", icon="💧")
    with c5:
        st.page_link("pages/4_Data.py", label="Data", icon="🗄️")
    with c6:
        st.page_link("pages/5_Parametros.py", label="Parámetros", icon="⚙️")
        
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)

