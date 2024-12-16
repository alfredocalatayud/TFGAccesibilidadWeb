import requests
import pandas as pd
from tqdm import tqdm

def analizar_accesibilidad(url, api_key):
    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "category": "accessibility"
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        # Extrae la puntuación de accesibilidad (0-1, convertido a 0-100)
        score = data['lighthouseResult']['categories']['accessibility']['score'] * 100
        return round(score, 2)
    except Exception as e:
        print(f"Error analizando {url}: {e}")
        return None


def procesar_csv(input_csv, output_csv, api_key, intervalo_guardado=100):
    # Cargar el CSV de entrada
    df = pd.read_csv(input_csv)

    # Verificar si existe un archivo de salida previo y cargarlo
    try:
        df_out = pd.read_csv(output_csv)
        processed_urls = set(df_out["WebAyuntamiento"].dropna())
        print(f"Se detectó progreso previo: {len(processed_urls)} URLs ya procesadas.")
    except FileNotFoundError:
        df_out = df.copy()
        df_out["PuntuacionAccesibilidad"] = None
        processed_urls = set()

    # Crear una barra de progreso y filtrar URLs no procesadas
    remaining_rows = df[~df["WebAyuntamiento"].isin(processed_urls)]
    print("Iniciando el análisis de accesibilidad...")
    for i, (index, row) in enumerate(tqdm(remaining_rows.iterrows(), total=len(remaining_rows), desc="Procesando URLs"),
                                     1):
        url = row["WebAyuntamiento"]
        if pd.notna(url):  # Verificar que la URL no sea NaN
            score = analizar_accesibilidad(url, api_key)
            df_out.at[index, "PuntuacionAccesibilidad"] = score

        # Guardar resultados cada `intervalo_guardado` filas procesadas
        if i % intervalo_guardado == 0:
            df_out.to_csv(output_csv, index=False)
            print(f"Progreso guardado: {i} URLs procesadas.")

    # Guardar cualquier fila restante
    df_out.to_csv(output_csv, index=False)
    print(f"Análisis completado. Archivo guardado en: {output_csv}")


if __name__ == "__main__":
    API_KEY = "AIzaSyDRD6dN7dvQM3rQMCo6hz8PwlWZb4s59dw"
    INPUT_CSV = "ayuntamientos.csv"
    OUTPUT_CSV = "ayuntamientos_con_accesibilidad.csv"

    procesar_csv(INPUT_CSV, OUTPUT_CSV, API_KEY)