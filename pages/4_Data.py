import streamlit as st
import pandas as pd
from database import get_raw_table, update_raw_table, get_config
from ui_helper import apply_premium_theme, render_top_navigation

st.set_page_config(page_title="Administración de Data", page_icon="🗄️", layout="wide")
apply_premium_theme()
render_top_navigation()

st.title("🗄️ Base de Datos Principal")
st.markdown("Visualiza y edita los registros crudos de la base de datos.")

config = get_config()
acceso_concedido = True

if config['require_auth']:
    if 'auth_ok' not in st.session_state:
        st.session_state['auth_ok'] = False
        
    if not st.session_state['auth_ok']:
        st.warning("🔒 Esta sección está protegida por contraseña.")
        pwd = st.text_input("Ingresa la contraseña:", type="password")
        if st.button("Acceder"):
            if pwd == config['password']:
                st.session_state['auth_ok'] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        acceso_concedido = False

if acceso_concedido:
    st.info("Puedes hacer doble clic en cualquier celda para editarla. Los cambios se guardarán automáticamente en la base de datos al perder el foco de la celda.")
    
    # Selector de tabla
    tabla = st.selectbox("Seleccionar Tabla", ["peso", "densidad", "llenado"])
    
    df = get_raw_table(tabla)
    
    if df.empty:
        st.warning(f"La tabla '{tabla}' está vacía.")
    else:
        # Data Editor
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        # Validar si hubo cambios y actualizar
        if not df.equals(edited_df):
            try:
                update_raw_table(tabla, edited_df)
                st.success("Cambios guardados en la base de datos exitosamente.")
            except Exception as e:
                st.error(f"Error al guardar los datos: {e}")
