import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_integrated_data, get_llenado_data, get_product_params, init_db
from ui_helper import apply_premium_theme, render_top_navigation
try:
    from scipy import stats
except ImportError:
    stats = None

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
            # Global Charts
            fig_rend = px.scatter(
                filtered_df, x="fecha", y="bolsas_por_libra", color="producto", size="peso_bruto_kg",
                title="Rendimiento (Bolsas/lb) por Fecha", color_discrete_sequence=["#FF3B30", "#FF9500", "#FFCC00"]
            )
            fig_rend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_rend, use_container_width=True)
            
            st.markdown("<hr style='border: 1px dashed #E5E5EA;'>", unsafe_allow_html=True)
            
            # KPIs por producto a la par
            productos_presentes_global = filtered_df['producto'].unique()
            cols_prods_g = st.columns(len(productos_presentes_global))
            
            for idx, prod in enumerate(productos_presentes_global):
                with cols_prods_g[idx]:
                    st.markdown(f"### {prod}")
                    df_prod_g = filtered_df[filtered_df['producto'] == prod]
                    
                    total_prod = df_prod_g['produccion_real_estimada_und'].sum()
                    total_lbs = df_prod_g['peso_neto_etiqueta_lbs'].sum()
                    rend = total_prod / total_lbs if total_lbs > 0 else 0
                    merma = df_prod_g['porcentaje_merma'].mean()
                    bobinas = df_prod_g['no_bobina'].nunique()
                    dens = df_prod_g['densidad_g_cm3'].mean()
                    esp = df_prod_g['espesor_micras'].mean()
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Prod. (und)", f"{total_prod:,.0f}")
                    m2.metric("Rendimiento", f"{rend:,.0f} Bolsas/lb")
                    
                    m3, m4 = st.columns(2)
                    m3.metric("Merma Prom.", f"{merma:.2f} %" if pd.notna(merma) else "N/A")
                    m4.metric("Bobinas", f"{bobinas}")
                    
                    m5, m6 = st.columns(2)
                    m5.metric("Densidad", f"{dens:.4f}" if pd.notna(dens) else "N/A")
                    m6.metric("Espesor", f"{esp:.2f} µ" if pd.notna(esp) else "N/A")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
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
                
                c4, c5, _ = st.columns(3)
                with c4:
                    dens_dia = df_dia['densidad_g_cm3'].mean()
                    st.metric("Densidad Promedio", f"{dens_dia:.4f} g/cm3" if pd.notna(dens_dia) else "N/A")
                with c5:
                    esp_dia = df_dia['espesor_micras'].mean()
                    st.metric("Espesor Promedio", f"{esp_dia:.2f} µ" if pd.notna(esp_dia) else "N/A")
                    
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
    
    if not df_llenado_filtrado.empty:
        # Gráfica de caja (Box Plot) arriba a todo lo ancho
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
        
        # Tarjetas de productos a la par (columnas)
        df_prod_params = get_product_params()
        productos_presentes = df_llenado_filtrado['producto'].unique()
        
        cols_prods = st.columns(len(productos_presentes))
        
        for idx, prod in enumerate(productos_presentes):
            with cols_prods[idx]:
                st.markdown(f"### {prod}")
                df_prod = df_llenado_filtrado[df_llenado_filtrado['producto'] == prod]
                prom = df_prod['peso_g'].mean()
                std_val = df_prod['peso_g'].std()
                std_val = std_val if pd.notna(std_val) else 0.0
                n = len(df_prod)
                
                m1, m2 = st.columns(2)
                m1.metric("Promedio", f"{prom:.2f} g")
                m2.metric("Desv. Estándar", f"{std_val:.3f} g")
                
                if not df_prod_params.empty and stats is not None:
                    row_param = df_prod_params[df_prod_params['producto'] == prod]
                    if not row_param.empty:
                        peso_liq = float(row_param.iloc[0]['peso_producto_g'])
                        peso_bol = float(row_param.iloc[0]['peso_bolsa_g'])
                        mu0 = peso_liq + peso_bol
                        
                        if mu0 > 0:
                            st.caption(f"⚖️ *Objetivo Teórico:* {mu0:.2f} g")
                            if n >= 2:
                                t_stat, p_val = stats.ttest_1samp(df_prod['peso_g'], mu0)
                                alpha = 0.05
                                
                                if pd.notna(p_val) and p_val < alpha:
                                    if prom > mu0:
                                        st.error(f"⚠️ **Sobredosificación Detectada** (p={p_val:.3f})\n\nEl peso es significativamente mayor al esperado. Ajustar máquina.")
                                    else:
                                        st.warning(f"⚠️ **Subdosificación Detectada** (p={p_val:.3f})\n\nEl peso es significativamente menor al esperado. Riesgo de reclamos.")
                                else:
                                    p_val_display = p_val if pd.notna(p_val) else 1.0
                                    st.success(f"✅ **Proceso Estable** (p={p_val_display:.3f})\n\nEl peso estadísticamente es igual al objetivo (95% confianza).")
                                    
                                # Calcular margen aceptable
                                t_crit = stats.t.ppf(0.975, n-1)
                                sem = df_prod['peso_g'].sem()
                                if pd.notna(sem) and sem > 0:
                                    margen_error = t_crit * sem
                                    rango_min = mu0 - margen_error
                                    rango_max = mu0 + margen_error
                                    st.caption(f"📏 *Rango Aceptable (95% de confianza):* **{rango_min:.2f} g** a **{rango_max:.2f} g** (±{margen_error:.2f} g)")
                                    
                                    if std_val > 0:
                                        prob_cumplimiento = (1 - stats.norm.cdf(mu0, loc=prom, scale=std_val)) * 100
                                        st.markdown("---")
                                        st.markdown("**🛠️ Ingeniería de Calidad**")
                                        st.caption(f"El **{prob_cumplimiento:.1f}%** de la producción tiene un peso igual o mayor a **{mu0:.2f}g**.")
                            else:
                                st.info("ℹ️ Se requieren al menos 2 muestras para la prueba estadística.")
                                
                # --- Análisis vs Set-Point Máquina ---
                if 'set_maquina_g' in df_prod.columns:
                    df_setpoint = df_prod[df_prod['set_maquina_g'].notna() & (df_prod['set_maquina_g'] > 0)]
                    if not df_setpoint.empty:
                        st.markdown("**🔍 Análisis vs Set-Point Máquina**")
                        prom_sp = df_setpoint['peso_g'].mean()
                        n_sp = len(df_setpoint)
                        setpoint_mean = df_setpoint['set_maquina_g'].mean()
                        
                        st.caption(f"Evaluando solo {n_sp} muestra(s) que incluyen Set-Point configurado.")
                        
                        if n_sp >= 2 and stats is not None:
                            t_stat_sp, p_val_sp = stats.ttest_1samp(df_setpoint['peso_g'], setpoint_mean)
                            alpha = 0.05
                            
                            if pd.notna(p_val_sp) and p_val_sp < alpha:
                                if prom_sp > setpoint_mean:
                                    st.error(f"⚠️ **Sobredosificación vs Máquina** (p={p_val_sp:.3f})\n\nEl peso promedio ({prom_sp:.2f}g) es mayor al Set-Point promedio de la máquina ({setpoint_mean:.2f}g).")
                                else:
                                    st.warning(f"⚠️ **Subdosificación vs Máquina** (p={p_val_sp:.3f})\n\nEl peso promedio ({prom_sp:.2f}g) es menor al Set-Point promedio de la máquina ({setpoint_mean:.2f}g).")
                            else:
                                p_val_disp_sp = p_val_sp if pd.notna(p_val_sp) else 1.0
                                st.success(f"✅ **Proceso Alineado a Máquina** (p={p_val_disp_sp:.3f})\n\nEstadísticamente el peso coincide con la configuración de la máquina ({setpoint_mean:.2f}g).")
                        else:
                            st.info(f"ℹ️ Set-Point Promedio Máquina: **{setpoint_mean:.2f}g**. Se requieren al menos 2 muestras para la prueba estadística.")
    else:
        st.info("No hay datos de llenado para el rango de fechas seleccionado.")
