import pandas as pd

file_path = r'C:\Users\Geo_C\OneDrive\Documents\Rendimiento de Coextruido - EMSULA.xlsx'
try:
    df_dict = pd.read_excel(file_path, sheet_name=None)
    for sheet_name, df in df_dict.items():
        print(f"--- Sheet: {sheet_name} ---")
        print(f"Columns: {df.columns.tolist()}")
        print(df.head(3))
        print("\n")
except Exception as e:
    print(f"Error reading Excel: {e}")
