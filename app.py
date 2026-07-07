import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_integrated_data, get_llenado_data
from ui_helper import apply_premium_theme, render_top_navigation

st.set_page_config(
    page_title="Rendimiento de Coextruido",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_premium_theme()
render_top_navigation()

st.title("Rendimiento de Coextruido")
st.markdown("Dashboard gerencial de desempeño de bobinas.")

# Cargar datos
df = get_integrated_data()

if df.empty:
    st.info("No hay datos suficientes para mostrar el dashboard. Dirígete a los formularios para ingresar la primera bobina.")
else:
    # Preparar df
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    st.sidebar.header("Filtros")
    
    productos = df['producto'].dropna().unique().tolist()
    if '' in productos: productos.remove('')
    selected_products = st.sidebar.multiselect("Producto", options=productos, default=productos)
    
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    if min_date == max_date:
        start_date, end_date = min_date, max_date
    else:
        date_range = st.sidebar.date_input("Fecha", [min_date, max_date])
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = date_range[0], date_range[0]
            
    mask = (df['producto'].isin(selected_products)) & (df['fecha'].dt.date >= start_date) & (df['fecha'].dt.date <= end_date)
    filtered_df = df.loc[mask]
    
    if filtered_df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_prod = filtered_df['produccion_teorica_und'].sum()
            st.metric("Total Producción Teórica", f"{total_prod:,.0f}")
            
        with col2:
            promedio_merma = filtered_df['porcentaje_merma'].mean()
            st.metric("Merma Promedio", f"{promedio_merma:.2f} %")
            
        with col3:
            total_bobinas = filtered_df['no_bobina'].nunique()
            st.metric("Bobinas Evaluadas", f"{total_bobinas}")
            
        with col4:
            prom_rendimiento = filtered_df['produccion_real_estimada_und'].sum() / total_prod if total_prod > 0 else 0
            st.metric("Rendimiento Estimado", f"{prom_rendimiento*100:.1f} %")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_prod = px.bar(
                filtered_df, 
                x="fecha", 
                y="produccion_real_estimada_und", 
                color="producto", 
                title="Producción Estimada (und)",
                color_discrete_sequence=["#0066CC", "#5AC8FA", "#34C759"]
            )
            fig_prod.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif"))
            st.plotly_chart(fig_prod, use_container_width=True)
            
        with col_chart2:
            fig_merma = px.scatter(
                filtered_df, 
                x="fecha", 
                y="porcentaje_merma", 
                color="producto",
                size="peso_bruto_kg",
                title="% Merma por Bobina",
                color_discrete_sequence=["#FF3B30", "#FF9500", "#FFCC00"]
            )
            fig_merma.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif"))
            st.plotly_chart(fig_merma, use_container_width=True)
            
        st.subheader("Análisis de Historial Combinado")
        display_cols = ['fecha', 'producto', 'no_bobina', 'peso_bruto_kg', 'densidad_g_cm3', 'porcentaje_merma', 'metros_bobina', 'produccion_real_estimada_und']
        st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

# Sección de Llenado
df_llenado = get_llenado_data()
if not df_llenado.empty:
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Control de Muestras de Llenado")
    
    df_llenado['fecha'] = pd.to_datetime(df_llenado['fecha'])
    
    # Aplicar filtro de fecha a llenado tambien para consistencia
    mask_l = (df_llenado['fecha'].dt.date >= start_date) & (df_llenado['fecha'].dt.date <= end_date)
    df_llenado_filtrado = df_llenado.loc[mask_l]
    
    col_l1, col_l2 = st.columns([1, 2])
    with col_l1:
        st.dataframe(df_llenado_filtrado.sort_values(by=['fecha', 'producto', 'no_muestra'], ascending=False).head(10), use_container_width=True, hide_index=True)
    with col_l2:
        if not df_llenado_filtrado.empty:
            fig_llenado = px.box(
                df_llenado_filtrado, 
                x="producto", 
                y="peso_g", 
                color="producto",
                title="Distribución de Pesos de Muestras",
                color_discrete_sequence=["#0066CC", "#34C759", "#FF9500"]
            )
            fig_llenado.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_llenado, use_container_width=True)
        else:
            st.info("No hay datos de llenado para el rango de fechas seleccionado.")
