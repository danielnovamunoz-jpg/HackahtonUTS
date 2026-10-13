import pandas as pd
import numpy as np
import glob
import os


def extraer_geo(region):
    #"Carcasí - Santander, Colombia" extraemos los datos individuales
    if pd.isna(region): 
        return pd.Series(["No especificado", "No especificado"])

    if '-' in region and ',' in region:
        municipio = region.split('-')[0].strip()
        departamento = region.split('-')[1].split(',')[0].strip()
    elif ',' in region:
        municipio = "No especificado"
        departamento = region.split(',')[0].strip()
    else:
        municipio = region.strip()
        departamento = region.strip()
    return pd.Series([municipio, departamento])



def procesar_sismos():
    ruta_archivos = os.path.join('data', 'datos_crudos', '*.csv')
    archivos = glob.glob(ruta_archivos)
    #lista con los archivos CSV que coinciden
    
    if not archivos:
        print("❌ No se encontraron archivos en data/datos_crudos/")
        return

    lista_dfs = []

    #recorremos todos los archivos CSV y los concatenamos en un solo DataFrame
    for archivo in archivos:
        df_temp = pd.read_csv(archivo)
        cols_renombrar = {col: 'fecha_hora_estandar' for col in df_temp.columns if 'Fecha-Hora' in col}
        df_temp = df_temp.rename(columns=cols_renombrar)
        #renombramos columnas de fecha para evitar variaciones
        lista_dfs.append(df_temp)
        
    df = pd.concat(lista_dfs, ignore_index=True)
    df = df.drop_duplicates()


    # --- FILTRO TEMPORAL ESTRICTO ---
    df['fecha_dt'] = pd.to_datetime(df['fecha_hora_estandar'], errors='coerce')
    df = df.dropna(subset=['fecha_dt'])
    
    fecha_inicio = pd.to_datetime("2018-03-01 00:00:00")
    fecha_fin = pd.to_datetime("2026-10-13 23:59:59")
    df = df[(df['fecha_dt'] >= fecha_inicio) & (df['fecha_dt'] <= fecha_fin)]
    # las fechas no convertidas eliminamos, y filtramos el rango de fechas permitido

    # Variables temporales
    df['año'] = df['fecha_dt'].dt.year.astype(int)
    df['mes'] = df['fecha_dt'].dt.month.astype(int)
    df['dia'] = df['fecha_dt'].dt.day.astype(int)
    df['hora'] = df['fecha_dt'].dt.hour.astype(int)
    df['es_noche'] = df['hora'].apply(lambda x: 1 if (x >= 18 or x < 3) else 0)
    #extraemos fecha y convertimos a enteros, y creamos una variable binaria para indicar si es de noche o no

    # Variables espaciales
    df[['municipio', 'departamento']] = df['Region'].apply(extraer_geo)


    # Feature Engineering
    bins_mag = [-1, 2.9, 3.9, 4.9, 10]
    labels_mag = ['micro', 'menor', 'moderado', 'fuerte']
    df['categoria_magnitud'] = pd.cut(df['Mag.'], bins=bins_mag, labels=labels_mag)
    #pandas cut nos permite crear categorías basadas en rangos definidos por los bins y asignarles etiquetas con labels


    bins_prof = [-1, 70, 300, 1000]
    labels_prof = ['superficial', 'intermedio', 'profundo']
    df['categoria_profundidad'] = pd.cut(df['Prof(Km)'], bins=bins_prof, labels=labels_prof)
    # categorizamos la profundidad en rangos de igual manera


    energia_joules = 10 ** (1.5 * df['Mag.'] + 4.8)
    df['log_energia_joules'] = np.log10(energia_joules + 1)
    #calculo de la energia asociada a la magnitud del sismo


    lat_nido, lon_nido = 6.78, -73.13
    df['dist_nido_sismico'] = np.sqrt((df['Lat(°)'] - lat_nido)**2 + (df['Long(°)'] - lon_nido)**2)
    #distancia euclidiana desde el nido sismico que es la mesa de los santos

    # Renombrar y exportar
    mapeo_columnas = {
        'Lat(°)': 'latitud', 'Long(°)': 'longitud', 'Prof(Km)': 'profundidad',
        'Mag.': 'magnitud', 'Tipo Mag.': 'tipo_magnitud', 'Fases': 'fases',
        'Rms(Seg)': 'Rms(Seg)', 'Gap(°)': 'Gap(°)', 
        'Error Lat(Km)': 'Error Lat(Km)', 'Error Long(Km)': 'Error Long(Km)', 'Error Prof(Km)': 'Error Prof(Km)'
    }
    df = df.rename(columns=mapeo_columnas)

    columnas_finales = [
        'departamento', 'municipio', 'año', 'mes', 'dia', 'hora', 'es_noche',
        'latitud', 'longitud', 'profundidad', 'magnitud', 'tipo_magnitud',
        'fases', 'Rms(Seg)', 'Gap(°)', 'log_energia_joules', 
        'categoria_magnitud', 'categoria_profundidad', 'dist_nido_sismico',
        'Error Lat(Km)', 'Error Long(Km)', 'Error Prof(Km)'
    ]
    df_final = df[columnas_finales]



    print("\n" + "="*40)
    print("    HERRAMIENTA DE EXPORTACIÓN SÍSMICA    ")
    print("="*40, "\n")
    print("1. Exportar TODOS los años (Mar 2018 - Oct 2026)")
    print("2. Exportar un AÑO en específico")
    
    opcion = input("\n👉 Selecciona una opción (1 o 2): ").strip()

    if opcion == '2':
        año_input = input("📅 Ingresa el año (2018-2026): ").strip()
        try:
            año_deseado = int(año_input)
            df_final = df_final[df_final['año'] == año_deseado]
            nombre_archivo = f"dataset_maestro_{año_deseado}_22_variables.csv"
            if df_final.empty:
                print(f"\n⚠️  No hay sismos para el año {año_deseado} en el rango permitido.")
                return
        except ValueError:
            print("\n❌ Año inválido. Se exportará todo.")
            nombre_archivo = "dataset_maestro_completo_22_variables.csv"
    else:
        nombre_archivo = "dataset_maestro_completo_22_variables.csv"

    ruta_salida = os.path.join('data', nombre_archivo)
    df_final.to_csv(ruta_salida, index=False)
    print("\n" + "="*40)
    print(f"📊 Total de sismos en el rango: {len(df_final)}")
    print(f"📁 Guardado en: {ruta_salida}")
    print("="*40 + "\n")

if __name__ == "__main__":
    procesar_sismos()