import streamlit as st
import datetime
from database import insert_peso
from ui_helper import apply_premium_theme, render_top_navigation

st.set_page_config(page_title="Ingreso de Peso", page_icon="⚖️", layout="wide")
apply_premium_theme()
render_top_navigation()

st.title("Ingreso de Peso de Bobina")
st.markdown("Registro de peso neto, bruto y mermas por bobina.")

with st.form("registro_peso"):
    st.subheader("Identificación")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.date.today())
    with col2:
        producto = st.selectbox("Producto", ["Aguazul", "Montana Manzana", "Montana Naranja"])
    with col3:
        no_bobina = st.text_input("No. Bobina / Lote")
        
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Pesos (Lbs) y Mermas")
    
    col4, col5 = st.columns(2)
    with col4:
        peso_neto_eti = st.number_input("Peso Neto Etiqueta (Lbs)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
        peso_bascula = st.number_input("Peso Báscula (Lbs)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
        merma_kg = st.number_input("Merma Total (Kg)", min_value=0.0, step=0.01, value=None, placeholder="0.00")
        
    with col5:
        peso_tubo = st.number_input("Peso Tubo Cartón (Kg)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
        peso_bolsa_v = st.number_input("Peso Bolsa Vacía (g)", min_value=0.0, step=0.01, value=None, placeholder="0.00")
        
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Dimensiones de la Bolsa")
    col6, col7, col8 = st.columns(3)
    
    with col6:
        ancho = st.number_input("Ancho de Bolsa (mm)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
    with col7:
        largo = st.number_input("Largo de Bolsa (mm)", min_value=0.0, step=0.1, value=None, placeholder="0.00")
    with col8:
        mts_eti = st.number_input("Metros en Etiqueta", min_value=0.0, step=10.0, value=None, placeholder="0.00")
        
    submit = st.form_submit_button("Guardar Registro de Peso", type="primary")

if submit:
    if not no_bobina.strip():
        st.error("El número de bobina es obligatorio.")
    else:
        data = {
            'fecha': fecha.strftime('%Y-%m-%d'),
            'producto': producto,
            'no_bobina': no_bobina,
            'peso_neto_etiqueta_lbs': peso_neto_eti or 0.0,
            'peso_bascula_lbs': peso_bascula or 0.0,
            'peso_tubo_carton_kg': peso_tubo or 0.0,
            'merma_kg': merma_kg or 0.0,
            'peso_bolsa_vacia_g': peso_bolsa_v or 0.0,
            'ancho_bolsa_mm': ancho or 0.0,
            'largo_bolsa_mm': largo or 0.0,
            'metros_etiqueta': mts_eti or 0.0
        }
        
        try:
            insert_peso(data)
            st.success("Registro guardado exitosamente.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
