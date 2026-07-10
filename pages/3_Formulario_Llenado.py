import streamlit as st
import datetime
from database import insert_llenado, get_next_llenado_muestra
from ui_helper import apply_premium_theme, render_top_navigation

st.set_page_config(page_title="Ingreso de Llenado", page_icon="💧", layout="wide")
apply_premium_theme()
render_top_navigation()

st.title("Control de Llenado")
st.markdown("Registro de peso de muestras para cada producto de forma independiente.")

with st.form("registro_llenado"):
    st.subheader("Datos de la Muestra")
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha de Producción", datetime.date.today())
    with col2:
        next_muestra = get_next_llenado_muestra(fecha.strftime('%Y-%m-%d'))
        no_muestra = st.number_input("Número de Muestra", min_value=1, step=1, value=next_muestra)
        
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Detalles del Producto")
    
    col3, col4 = st.columns(2)
    with col3:
        producto = st.selectbox("Producto Evaluado", ["Aguazul", "Montana Manzana", "Montana Naranja"])
    with col4:
        peso_g = st.number_input("Peso de la Muestra (g)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
        
    submit = st.form_submit_button("Registrar Muestra", type="primary")

if submit:
    peso_g_val = peso_g or 0.0
    if peso_g_val <= 0:
        st.error("Por favor, ingresa un peso válido mayor a 0.")
    else:
        data = {
            'fecha': fecha.strftime('%Y-%m-%d'),
            'producto': producto,
            'no_muestra': no_muestra,
            'peso_g': peso_g_val
        }
        
        try:
            insert_llenado(data)
            st.success(f"Muestra {no_muestra} de {producto} registrada exitosamente.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
