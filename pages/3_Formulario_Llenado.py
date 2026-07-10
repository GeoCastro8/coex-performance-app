import streamlit as st
import datetime
from database import insert_llenado, get_next_llenado_muestra, get_last_set_maquina, init_db
from ui_helper import apply_premium_theme, render_top_navigation

@st.cache_resource
def setup_database():
    init_db()
    return True

setup_database()

st.set_page_config(page_title="Ingreso de Llenado", page_icon="💧", layout="wide")
apply_premium_theme()
render_top_navigation()

st.title("Control de Llenado")
st.markdown("Registro de peso de muestras para cada producto de forma independiente.")

st.subheader("Fecha de Registro")
fecha = st.date_input("Fecha de Producción", datetime.date.today())

with st.form("registro_llenado"):
    st.subheader("Datos de la Muestra")
    
    fecha_str = fecha.strftime('%Y-%m-%d')
    next_muestra = get_next_llenado_muestra(fecha_str)
    last_set_maquina = get_last_set_maquina(fecha_str)
    
    col1, col2 = st.columns(2)
    with col1:
        no_muestra = st.number_input("Número de Muestra", min_value=1, step=1, value=next_muestra, key=f"muestra_{fecha}")
    with col2:
        producto = st.selectbox("Producto Evaluado", ["Aguazul", "Montana Manzana", "Montana Naranja"])
        
    col3, col4 = st.columns(2)
    with col3:
        peso_g = st.number_input("Peso de la Muestra (g)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
    with col4:
        set_maquina_g = st.number_input("Set-Point de Máquina (g)", min_value=0.0, step=0.1, value=last_set_maquina, placeholder="0.00")
        
    submit = st.form_submit_button("Registrar Muestra", type="primary")

if submit:
    if peso_g is not None and peso_g > 0:
        data = {
            'fecha': fecha.strftime('%Y-%m-%d'),
            'producto': producto,
            'no_muestra': no_muestra,
            'peso_g': peso_g,
            'set_maquina_g': set_maquina_g
        }
        
        try:
            insert_llenado(data)
            st.success(f"Muestra {no_muestra} de {producto} registrada exitosamente.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.error("Por favor, ingresa un peso válido mayor a 0.")
