import streamlit as st
import pandas as pd
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine

# Helper para obtener URL y crear motor de Pandas
def get_db_url():
    return st.secrets["postgres"]["url"]

def get_connection():
    return psycopg2.connect(get_db_url())

def get_engine():
    return create_engine(get_db_url())

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de Peso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peso (
            id SERIAL PRIMARY KEY,
            fecha TEXT,
            producto TEXT,
            no_bobina TEXT UNIQUE,
            peso_neto_etiqueta_lbs REAL,
            peso_bascula_lbs REAL,
            peso_tubo_carton_kg REAL,
            merma_kg REAL,
            peso_bolsa_vacia_g REAL,
            ancho_bolsa_mm REAL,
            largo_bolsa_mm REAL,
            metros_etiqueta REAL
        )
    ''')
    
    # Tabla de Densidad
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS densidad (
            id SERIAL PRIMARY KEY,
            fecha TEXT,
            no_bobina TEXT UNIQUE,
            peso_g REAL,
            area_cm2 REAL,
            espesor_a REAL,
            espesor_b REAL,
            espesor_c REAL,
            espesor_d REAL,
            espesor_e REAL
        )
    ''')
    
    # Tabla de Llenado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS llenado (
            id SERIAL PRIMARY KEY,
            fecha TEXT,
            producto TEXT,
            no_muestra INTEGER,
            peso_g REAL
        )
    ''')
    
    # Intento añadir la nueva columna 'set_maquina_g' por si no existe
    try:
        cursor.execute('ALTER TABLE llenado ADD COLUMN set_maquina_g REAL')
        conn.commit()
    except Exception:
        conn.rollback()

    # Tabla de Configuración (Auth)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            require_auth INTEGER,
            password TEXT
        )
    ''')
    
    # Tabla de Parámetros Globales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            factor_kg REAL,
            factor_micras REAL,
            multiplicador_prod REAL
        )
    ''')
    
    # Tabla de Parámetros por Producto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_producto (
            id SERIAL PRIMARY KEY,
            producto TEXT UNIQUE,
            peso_producto_g REAL,
            peso_bolsa_g REAL
        )
    ''')
    
    # Seed de configuración
    cursor.execute('SELECT COUNT(*) FROM configuracion')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO configuracion (id, require_auth, password) VALUES (1, 0, 'admin123')")
        
    # Seed de parámetros globales
    cursor.execute('SELECT COUNT(*) FROM parametros')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO parametros (id, factor_kg, factor_micras, multiplicador_prod) VALUES (1, 0.453592, 10000.0, 1000.0)")
        
    # Seed de parámetros por producto
    cursor.execute('SELECT COUNT(*) FROM parametros_producto')
    if cursor.fetchone()[0] == 0:
        productos_iniciales = ["Aguazul", "Montana Manzana", "Montana Naranja"]
        for p in productos_iniciales:
            cursor.execute("INSERT INTO parametros_producto (producto, peso_producto_g, peso_bolsa_g) VALUES (%s, 0.0, 0.0)", (p,))
            
    conn.commit()
    cursor.close()
    conn.close()

def get_config():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT require_auth, password FROM configuracion WHERE id=1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {'require_auth': bool(row[0]), 'password': row[1]}
    return {'require_auth': False, 'password': '123'}

def update_config(require_auth, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE configuracion SET require_auth=%s, password=%s WHERE id=1", (int(require_auth), password))
    conn.commit()
    cursor.close()
    conn.close()

def get_params():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT factor_kg, factor_micras, multiplicador_prod FROM parametros WHERE id=1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {'factor_kg': row[0], 'factor_micras': row[1], 'multiplicador_prod': row[2]}
    return {'factor_kg': 0.453592, 'factor_micras': 10000.0, 'multiplicador_prod': 1000.0}

def update_params(factor_kg, factor_micras, multiplicador_prod):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE parametros SET factor_kg=%s, factor_micras=%s, multiplicador_prod=%s WHERE id=1", 
                   (factor_kg, factor_micras, multiplicador_prod))
    conn.commit()
    cursor.close()
    conn.close()

def get_product_params():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM parametros_producto ORDER BY producto", engine)

def update_product_params(producto, peso_producto_g, peso_bolsa_g):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE parametros_producto 
        SET peso_producto_g = %s, peso_bolsa_g = %s 
        WHERE producto = %s
    ''', (peso_producto_g, peso_bolsa_g, producto))
    conn.commit()
    cursor.close()
    conn.close()

def get_available_bobinas():
    engine = get_engine()
    query = '''
        SELECT p.no_bobina, p.producto, p.fecha 
        FROM peso p
        LEFT JOIN densidad d ON p.no_bobina = d.no_bobina
        WHERE d.no_bobina IS NULL
    '''
    return pd.read_sql_query(query, engine)

def insert_peso(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO peso (
            fecha, producto, no_bobina, peso_neto_etiqueta_lbs, peso_bascula_lbs, 
            peso_tubo_carton_kg, merma_kg, peso_bolsa_vacia_g, 
            ancho_bolsa_mm, largo_bolsa_mm, metros_etiqueta
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (no_bobina) DO UPDATE SET
            fecha = EXCLUDED.fecha,
            producto = EXCLUDED.producto,
            peso_neto_etiqueta_lbs = EXCLUDED.peso_neto_etiqueta_lbs,
            peso_bascula_lbs = EXCLUDED.peso_bascula_lbs,
            peso_tubo_carton_kg = EXCLUDED.peso_tubo_carton_kg,
            merma_kg = EXCLUDED.merma_kg,
            peso_bolsa_vacia_g = EXCLUDED.peso_bolsa_vacia_g,
            ancho_bolsa_mm = EXCLUDED.ancho_bolsa_mm,
            largo_bolsa_mm = EXCLUDED.largo_bolsa_mm,
            metros_etiqueta = EXCLUDED.metros_etiqueta
    ''', (
        data['fecha'], data['producto'], data['no_bobina'], 
        data['peso_neto_etiqueta_lbs'], data['peso_bascula_lbs'], 
        data['peso_tubo_carton_kg'], data['merma_kg'], data['peso_bolsa_vacia_g'],
        data['ancho_bolsa_mm'], data['largo_bolsa_mm'], data['metros_etiqueta']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def insert_densidad(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO densidad (
            fecha, no_bobina, peso_g, area_cm2, 
            espesor_a, espesor_b, espesor_c, espesor_d, espesor_e
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (no_bobina) DO UPDATE SET
            fecha = EXCLUDED.fecha,
            peso_g = EXCLUDED.peso_g,
            area_cm2 = EXCLUDED.area_cm2,
            espesor_a = EXCLUDED.espesor_a,
            espesor_b = EXCLUDED.espesor_b,
            espesor_c = EXCLUDED.espesor_c,
            espesor_d = EXCLUDED.espesor_d,
            espesor_e = EXCLUDED.espesor_e
    ''', (
        data['fecha'], data['no_bobina'], data['peso_g'], data['area_cm2'], 
        data['espesor_a'], data['espesor_b'], data['espesor_c'], data['espesor_d'], data['espesor_e']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def insert_llenado(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO llenado (
            fecha, producto, no_muestra, peso_g, set_maquina_g
        ) VALUES (%s, %s, %s, %s, %s)
    ''', (
        data['fecha'], data['producto'], data['no_muestra'], data['peso_g'], data.get('set_maquina_g', None)
    ))
    conn.commit()
    cursor.close()
    conn.close()

def get_next_llenado_muestra(fecha_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(no_muestra) FROM llenado WHERE fecha = %s", (fecha_str,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row and row[0] is not None:
        return int(row[0]) + 1
    return 1

def get_integrated_data():
    engine = get_engine()
    
    df_peso = pd.read_sql_query("SELECT * FROM peso", engine)
    df_dens = pd.read_sql_query("SELECT * FROM densidad", engine)
    
    if df_peso.empty:
        return pd.DataFrame()
        
    if df_dens.empty:
        df_dens = pd.DataFrame(columns=['no_bobina', 'peso_g', 'area_cm2', 'espesor_a', 'espesor_b', 'espesor_c', 'espesor_d', 'espesor_e'])
        
    df = pd.merge(df_peso, df_dens, on='no_bobina', how='left', suffixes=('', '_dens'))
    
    # Obtener parámetros dinámicos
    params = get_params()
    f_kg = params['factor_kg']
    f_micras = params['factor_micras']
    f_prod = params['multiplicador_prod']
    
    # Fórmulas de Peso
    df['diferencia_lbs'] = df['peso_neto_etiqueta_lbs'] - df['peso_bascula_lbs']
    df['peso_bascula_kg'] = df['peso_bascula_lbs'] * f_kg
    df['peso_bruto_kg'] = df['peso_neto_etiqueta_lbs'] * f_kg
    df['peso_neto_kg'] = df['peso_bruto_kg'] - df['peso_tubo_carton_kg']
    df['porcentaje_merma'] = df.apply(lambda row: (row['merma_kg'] / row['peso_neto_kg'] * 100) if row['peso_neto_kg'] else 0, axis=1)
    
    # Fórmulas de Densidad
    def calc_espesor_cm(row):
        cols = ['espesor_a', 'espesor_b', 'espesor_c', 'espesor_d', 'espesor_e']
        vals = [row[c] for c in cols if pd.notnull(row.get(c))]
        if vals:
            return (sum(vals) / len(vals)) * 0.1
        return None
        
    df['espesor_cm'] = df.apply(calc_espesor_cm, axis=1)
    
    def calc_densidad(row):
        if pd.notnull(row['peso_g']) and pd.notnull(row['area_cm2']) and pd.notnull(row['espesor_cm']) and (row['area_cm2'] * row['espesor_cm']) > 0:
            return row['peso_g'] / (row['area_cm2'] * row['espesor_cm'])
        return None
        
    df['densidad_g_cm3'] = df.apply(calc_densidad, axis=1)
    
    # Fórmulas Integradas (Dashboard)
    df['espesor_micras'] = df['espesor_cm'] * f_micras
    
    def calc_metros_bobina(row):
        try:
            denominador = row['ancho_bolsa_mm'] * row['espesor_micras'] * row['densidad_g_cm3']
            if denominador > 0:
                return (row['peso_bruto_kg'] * 1000000) / denominador
        except:
            pass
        return 0
        
    df['metros_bobina'] = df.apply(calc_metros_bobina, axis=1)
    df['diferencia_mts'] = df['metros_etiqueta'] - df['metros_bobina']
    
    df['produccion_teorica_und'] = df.apply(lambda row: (row['metros_bobina'] * f_prod) / row['largo_bolsa_mm'] if row['largo_bolsa_mm'] else 0, axis=1)
    df['produccion_real_estimada_und'] = df['produccion_teorica_und'] * (1 - (df['porcentaje_merma'] / 100))
    df['peso_utilizado_kg'] = (df['peso_bolsa_vacia_g'] * df['produccion_teorica_und']) / 1000
    
    # Rendimiento Gerencial: Bolsas por libra
    df['bolsas_por_libra'] = df.apply(lambda row: row['produccion_real_estimada_und'] / row['peso_neto_etiqueta_lbs'] if pd.notnull(row.get('peso_neto_etiqueta_lbs')) and row['peso_neto_etiqueta_lbs'] > 0 else 0, axis=1)
    
    return df

def get_llenado_data():
    engine = get_engine()
    return pd.read_sql_query("SELECT * FROM llenado", engine)
    
def get_raw_table(table_name):
    engine = get_engine()
    return pd.read_sql_query(f"SELECT * FROM {table_name}", engine)

def update_raw_table(table_name, df):
    engine = get_engine()
    # Usamos DELETE FROM en lugar de if_exists='replace' para no destruir
    # las restricciones (UNIQUE, PRIMARY KEY) creadas por init_db()
    with engine.begin() as conn:
        from sqlalchemy import text
        conn.execute(text(f"DELETE FROM {table_name}"))
    
    # Insertar los datos de nuevo (sin reemplazar la estructura de la tabla)
    df.to_sql(table_name, engine, if_exists='append', index=False)

if __name__ == "__main__":
    init_db()
