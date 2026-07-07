import streamlit as st
import datetime
from database import insert_densidad, get_available_bobinas
from ui_helper import apply_premium_theme, render_top_navigation

st.set_page_config(page_title="Ingreso de Densidad", page_icon="🔬", layout="wide")
apply_premium_theme()
render_top_navigation()

st.title("Ingreso de Densidad")
st.markdown("Selecciona una bobina pendiente de análisis para ingresar sus datos de densidad. (Una vez ingresados, la bobina se cerrará y dejará de aparecer aquí).")

# Obtener las bobinas disponibles
df_bobinas = get_available_bobinas()

with st.form("registro_densidad"):
    st.subheader("Identificación de Muestra")
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.date.today())
    with col2:
        if not df_bobinas.empty:
            # Crear una lista amigable para el usuario: "No. Bobina - Producto (Fecha)"
            opciones = df_bobinas.apply(lambda r: f"{r['no_bobina']} - {r['producto']} ({r['fecha']})", axis=1).tolist()
            seleccion = st.selectbox("Seleccionar Bobina Pendiente", opciones)
            no_bobina_real = seleccion.split(" - ")[0]
        else:
            # Si no hay bobinas, mostramos un selectbox deshabilitado con un placeholder
            st.selectbox("Seleccionar Bobina Pendiente", ["Sin bobinas pendientes"], disabled=True)
            no_bobina_real = None
            
    if df_bobinas.empty:
        st.warning("⚠️ No hay bobinas pendientes de registro. Debes ingresar primero una bobina en el formulario de Peso.")
        
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Datos de la Muestra")
    
    col3, col4 = st.columns(2)
    with col3:
        peso_g = st.number_input("Peso (g)", min_value=0.0, step=0.01, format="%.4f")
    with col4:
        area_cm2 = st.number_input("Área (cm²)", min_value=0.0, step=1.0)
        
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Mediciones de Espesor (mm)")
    
    e1, e2, e3, e4, e5 = st.columns(5)
    with e1:
        espesor_a = st.number_input("A", min_value=0.0, step=0.01, format="%.3f")
    with e2:
        espesor_b = st.number_input("B", min_value=0.0, step=0.01, format="%.3f")
    with e3:
        espesor_c = st.number_input("C", min_value=0.0, step=0.01, format="%.3f")
    with e4:
        espesor_d = st.number_input("D", min_value=0.0, step=0.01, format="%.3f")
    with e5:
        espesor_e = st.number_input("E", min_value=0.0, step=0.01, format="%.3f")
        
    submit = st.form_submit_button("Guardar Registro de Densidad", type="primary", disabled=df_bobinas.empty)

if submit and not df_bobinas.empty and no_bobina_real:
    data = {
        'fecha': fecha.strftime('%Y-%m-%d'),
        'no_bobina': no_bobina_real,
        'peso_g': peso_g,
        'area_cm2': area_cm2,
        'espesor_a': espesor_a,
        'espesor_b': espesor_b,
        'espesor_c': espesor_c,
        'espesor_d': espesor_d,
        'espesor_e': espesor_e
    }
    
    try:
        insert_densidad(data)
        st.success(f"Densidad guardada exitosamente para la bobina {no_bobina_real}. Esta bobina se ha cerrado y ya no aparecerá en la lista. Revisa el Dashboard.")
        st.rerun() # Refresca la UI para actualizar el selectbox inmediatamente
    except Exception as e:
        st.error(f"Error al guardar: {e}")
