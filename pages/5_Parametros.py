import streamlit as st
from database import get_params, update_params, get_config, update_config, get_product_params, update_product_params
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
st.markdown("### 🧮 Parámetros de Ingeniería")
st.markdown("Estos factores son utilizados por el motor del Dashboard para los cálculos automáticos.")

params = get_params()

with st.form("params_form"):
    factor_kg = st.number_input("Factor Libras a KG (ej. 0.453592)", value=float(params['factor_kg']), format="%.6f")
    factor_micras = st.number_input("Multiplicador cm a Micras (ej. 10000)", value=float(params['factor_micras']), format="%.1f")
    multiplicador_prod = st.number_input("Multiplicador Producción Teórica (ej. 1000)", value=float(params['multiplicador_prod']), format="%.1f")
    
    if st.form_submit_button("Guardar Parámetros de Ingeniería", type="primary"):
        update_params(factor_kg, factor_micras, multiplicador_prod)
        st.success("Parámetros de ingeniería actualizados exitosamente.")

st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
st.markdown("### 🧪 Parámetros por Producto")
st.markdown("Configura el **Peso Neto Teórico (Líquido)** y el **Peso de Referencia de Bolsa Vacía** para cada producto. Estos valores se utilizarán para la Prueba de Hipótesis Estadística de Llenado.")

df_prod = get_product_params()
if not df_prod.empty:
    with st.form("product_params_form"):
        # We will collect the new values to update them later
        new_values = {}
        for index, row in df_prod.iterrows():
            st.markdown(f"**{row['producto']}**")
            c1, c2 = st.columns(2)
            with c1:
                p_prod = st.number_input(f"Peso Líquido Esperado (g) - {row['producto']}", min_value=0.0, step=0.1, value=float(row['peso_producto_g']), format="%.1f")
            with c2:
                p_bolsa = st.number_input(f"Peso Bolsa Vacía (g) - {row['producto']}", min_value=0.0, step=0.1, value=float(row['peso_bolsa_g']), format="%.1f")
            
            new_values[row['producto']] = (p_prod, p_bolsa)
            st.markdown("<br>", unsafe_allow_html=True)
            
        if st.form_submit_button("Guardar Parámetros de Productos", type="primary"):
            for prod, vals in new_values.items():
                update_product_params(prod, vals[0], vals[1])
            st.success("Parámetros de productos actualizados exitosamente.")
            st.rerun()
else:
    st.info("Aún no hay productos registrados en la base de datos de parámetros.")
