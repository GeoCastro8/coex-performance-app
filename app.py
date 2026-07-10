import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_integrated_data, get_llenado_data, init_db
from ui_helper import apply_premium_theme, render_top_navigation

@st.cache_resource
def setup_database():
    init_db()
    return True

setup_database()

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
        tab_global, tab_diario, tab_bobina = st.tabs(["🌎 Resumen Global", "📅 Análisis Diario", "🧵 Detalle por Bobina"])
        
        with tab_global:
            # Global KPIs
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_prod = filtered_df['produccion_real_estimada_und'].sum()
                st.metric("Total Prod. Real (und)", f"{total_prod:,.0f}")
            with col2:
                total_lbs = filtered_df['peso_neto_etiqueta_lbs'].sum()
                global_bolsas_lb = total_prod / total_lbs if total_lbs > 0 else 0
                st.metric("Rendimiento Global", f"{global_bolsas_lb:,.0f} Bolsas/lb")
            with col3:
                promedio_merma = filtered_df['porcentaje_merma'].mean()
                st.metric("Merma Promedio", f"{promedio_merma:.2f} %")
            with col4:
                total_bobinas = filtered_df['no_bobina'].nunique()
                st.metric("Bobinas Evaluadas", f"{total_bobinas}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Global Charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                fig_prod = px.bar(
                    filtered_df, x="fecha", y="produccion_real_estimada_und", color="producto", 
                    title="Producción Real (und)", color_discrete_sequence=["#0066CC", "#5AC8FA", "#34C759"]
                )
                fig_prod.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_prod, use_container_width=True)
                
            with col_chart2:
                fig_rend = px.scatter(
                    filtered_df, x="fecha", y="bolsas_por_libra", color="producto", size="peso_bruto_kg",
                    title="Rendimiento (Bolsas/lb) por Fecha", color_discrete_sequence=["#FF3B30", "#FF9500", "#FFCC00"]
                )
                fig_rend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_rend, use_container_width=True)
                
            st.subheader("Historial Global")
            display_cols = ['fecha', 'producto', 'no_bobina', 'peso_neto_etiqueta_lbs', 'porcentaje_merma', 'produccion_real_estimada_und', 'bolsas_por_libra']
            st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
            
        with tab_diario:
            st.subheader("Análisis de Producción por Día")
            fechas_disponibles = sorted(filtered_df['fecha'].dt.date.unique(), reverse=True)
            if not fechas_disponibles:
                st.info("No hay fechas en el rango actual.")
            else:
                dia_seleccionado = st.selectbox("Selecciona un día de producción:", fechas_disponibles)
                df_dia = filtered_df[filtered_df['fecha'].dt.date == dia_seleccionado]
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    prod_dia = df_dia['produccion_real_estimada_und'].sum()
                    st.metric(f"Producción del Día", f"{prod_dia:,.0f} und")
                with c2:
                    lbs_dia = df_dia['peso_neto_etiqueta_lbs'].sum()
                    rend_dia = prod_dia / lbs_dia if lbs_dia > 0 else 0
                    st.metric(f"Rendimiento del Día", f"{rend_dia:,.0f} Bolsas/lb")
                with c3:
                    st.metric("Bobinas Procesadas", f"{df_dia['no_bobina'].nunique()}")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                fig_dia = px.bar(
                    df_dia, x="no_bobina", y="bolsas_por_libra", color="producto",
                    title=f"Rendimiento por Bobina - {dia_seleccionado}",
                    color_discrete_sequence=["#0066CC", "#34C759", "#FF9500"]
                )
                fig_dia.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_dia, use_container_width=True)
                
        with tab_bobina:
            st.subheader("Ficha Técnica por Bobina")
            bobinas_disp = sorted(filtered_df['no_bobina'].unique())
            if not bobinas_disp:
                st.info("No hay bobinas en el rango actual.")
            else:
                bob_sel = st.selectbox("Selecciona una bobina:", bobinas_disp)
                df_bob = filtered_df[filtered_df['no_bobina'] == bob_sel].iloc[0]
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Producto", f"{df_bob['producto']}")
                c2.metric("Producción Real", f"{df_bob['produccion_real_estimada_und']:,.0f} und")
                c3.metric("Rendimiento", f"{df_bob['bolsas_por_libra']:,.0f} Bolsas/lb")
                c4.metric("Merma", f"{df_bob['porcentaje_merma']:.2f} %")
                
                st.markdown("##### Especificaciones Técnicas")
                c_t1, c_t2, c_t3 = st.columns(3)
                c_t1.write(f"**Peso Etiqueta:** {df_bob.get('peso_neto_etiqueta_lbs', 0)} lbs")
                c_t1.write(f"**Peso Báscula:** {df_bob.get('peso_bascula_lbs', 0)} lbs")
                
                c_t2.write(f"**Densidad:** {df_bob.get('densidad_g_cm3', 0):.4f} g/cm3")
                c_t2.write(f"**Espesor Promedio:** {df_bob.get('espesor_micras', 0):.2f} micras")
                
                c_t3.write(f"**Dimensiones:** {df_bob.get('ancho_bolsa_mm', 0)} x {df_bob.get('largo_bolsa_mm', 0)} mm")

# Sección de Llenado
df_llenado = get_llenado_data()
if not df_llenado.empty:
    st.markdown("<hr style='border: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
    st.subheader("Control de Muestras de Llenado")
    
    df_llenado['fecha'] = pd.to_datetime(df_llenado['fecha'])
    
    # Crear un filtro de fecha independiente para Llenado
    min_date_l = df_llenado['fecha'].min().date()
    max_date_l = df_llenado['fecha'].max().date()
    
    if min_date_l == max_date_l:
        start_l, end_l = min_date_l, max_date_l
    else:
        col_filtro, _ = st.columns([1, 3])
        with col_filtro:
            date_range_l = st.date_input("Rango de Fechas (Muestras)", [min_date_l, max_date_l], key="date_llenado")
        if len(date_range_l) == 2:
            start_l, end_l = date_range_l
        else:
            start_l, end_l = date_range_l[0], date_range_l[0]
            
    mask_l = (df_llenado['fecha'].dt.date >= start_l) & (df_llenado['fecha'].dt.date <= end_l)
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
