import streamlit as st
from database import get_params, update_params, get_config, update_config
from ui_helper import apply_premium_theme, render_top_navigation

st.set_page_config(page_title="Parámetros y Configuración", page_icon="⚙️", layout="wide")
apply_premium_theme()
render_top_navigation()

st.title("⚙️ Configuración del Sistema")

st.markdown("### 🔐 Seguridad")
config = get_config()
require_auth = st.toggle("Proteger Pestaña 'Data' con Contraseña", value=config['require_auth'])
new_password = st.text_input("Contraseña de Acceso", value=config['password'], type="password")

if st.button("Actualizar Configuración de Seguridad", type="primary"):
    update_config(require_auth, new_password)
    st.success("Configuración de seguridad actualizada exitosamente.")

st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
st.markdown("### 🧮 Parámetros de Cálculo")
st.markdown("Estos factores son utilizados por el motor del Dashboard para los cálculos automáticos.")

params = get_params()

with st.form("params_form"):
    factor_kg = st.number_input("Factor Libras a KG (ej. 0.453592)", value=float(params['factor_kg']), format="%.6f")
    factor_micras = st.number_input("Multiplicador cm a Micras (ej. 10000)", value=float(params['factor_micras']), format="%.1f")
    multiplicador_prod = st.number_input("Multiplicador Producción Teórica (ej. 1000)", value=float(params['multiplicador_prod']), format="%.1f")
    
    if st.form_submit_button("Guardar Parámetros de Ingeniería", type="primary"):
        update_params(factor_kg, factor_micras, multiplicador_prod)
        st.success("Parámetros de ingeniería actualizados exitosamente.")
