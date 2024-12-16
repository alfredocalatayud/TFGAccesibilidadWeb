import pandas as pd
import requests
from tqdm import tqdm
from tabulate import tabulate
import os


# Función para leer el archivo CSV
def read_csv(filename):
    return pd.read_csv(filename, delimiter=',')


# Función para obtener el estado HTTP de una URL
def get_http_status(url):
    try:
        response = requests.get(url, timeout=5, stream=True)
        return response.status_code
    except requests.RequestException as e:
        return str(e)


# Función para comprobar el fichero de webs
def comprobar_webs(df):
    tqdm.pandas(desc="Consultando webs")
    df['HttpStatus'] = df['WebAyuntamiento'].progress_apply(get_http_status)
    df.to_csv('ayuntamientos_con_estado_http.csv', index=False)
    print("Comprobación completada y guardada en 'ayuntamientos_con_estado_http.csv'")

    # Crear archivos CSV separados por código de respuesta
    crear_csv_respuesta(df)


# Función para crear archivos CSV separados por código de respuesta
def crear_csv_respuesta(df):
    os.makedirs('resultados', exist_ok=True)  # Crear un directorio para los archivos CSV

    print(df.head())
    # Filtrar y guardar los resultados con código 200
    df['HttpStatus'] = pd.to_numeric(df['HttpStatus'], errors='coerce').fillna(0).astype(int)
    df_200 = df[df['HttpStatus'] == 200]
    filename_200 = 'resultados/resultado_200.csv'
    df_200.to_csv(filename_200, index=False)
    print(f"Archivo creado: {filename_200}")

    # Filtrar y guardar los resultados con códigos distintos de 200
    df_non_200 = df[df['HttpStatus'] != 200]
    filename_non_200 = 'resultados/resultado_no_200.csv'
    df_non_200.to_csv(filename_non_200, index=False)
    print(f"Archivo creado: {filename_non_200}")


# Función para revisar el archivo de errores
def revisar_csv_errores():
    try:
        df_non_200 = pd.read_csv('resultados/revision_errores.csv', delimiter=',')
        print("\nRevisando archivo 'revision_errores.csv':")

        # Consultar el estado HTTP nuevamente
        tqdm.pandas(desc="Revisando estados HTTP")
        df_non_200['HttpStatusReview'] = df_non_200['WebAyuntamiento'].progress_apply(get_http_status)

        # Guardar el nuevo archivo CSV con los resultados de la revisión
        df_non_200.to_csv('resultados/revision_errores2.csv', index=False)
        print(f"Archivo de revisión creado: 'resultados/revision_errores2.csv'")

    except FileNotFoundError:
        print(
            "El archivo 'revision_errores.csv' no se ha encontrado. Asegúrate de haber ejecutado la opción de comprobación primero.")


# Función para ver los resultados en formato de tablas
def ver_resultados(df):
    # Mostrar los primeros 20 registros
    print("\nPrimeros 20 registros:")
    print(tabulate(df.head(20), headers='keys', tablefmt='pretty'))

    # Mostrar el número de cada código de respuesta
    status_counts = df['HttpStatus'].value_counts().reset_index()
    status_counts.columns = ['HTTP Status', 'Count']
    print("\nNúmero de cada código de respuesta HTTP:")
    print(tabulate(status_counts, headers='keys', tablefmt='pretty'))

    # Listar códigos distintos de 200
    non_200_status = status_counts[status_counts['HTTP Status'] != 200]
    print("\nListado de códigos de respuesta distintos de 200:")
    print(tabulate(non_200_status, headers='keys', tablefmt='pretty'))

# Función principal del menú
def main_menu():
    filename = 'ayuntamientos.csv'
    df = read_csv(filename)

    while True:
        print("\nMenú:")
        print("1. Comprobar el fichero de webs")
        print("2. Ver los resultados")
        print("3. Crear archivos CSV por código de respuesta HTTP")
        print("4. Revisar errores y crear 'revision_errores.csv'")
        print("5. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            comprobar_webs(df)
        elif opcion == '2':
            ver_resultados(df)
        elif opcion == '3':
            crear_csv_respuesta(df)
        elif opcion == '4':
            revisar_csv_errores()
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")

if __name__ == "__main__":
    main_menu()
