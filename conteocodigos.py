import json
import csv
from collections import defaultdict

# Función para leer los archivos JSON y devolver el contenido
def leer_json(archivos):
    datos = []
    for archivo in archivos:
        with open(archivo, 'r', encoding='utf-8') as f:
            datos.extend(json.load(f))  # Cargar el contenido del archivo
    return datos

# Función para procesar los datos y contar las incidencias de los códigos
def contar_codes(datos):
    # Diccionarios para contar las incidencias totales y únicas
    total_count = defaultdict(int)  # Contador total de incidencias
    unique_count = defaultdict(lambda: defaultdict(int))  # Contador único por URL

    # Iterar sobre los datos
    for pagina in datos:
        # Extraer la URL de la página
        page_url = pagina['result']['pageUrl']
        
        # Procesar cada 'issue' en el registro
        for issue in pagina['result']['issues']:
            # Obtener el código y reducirlo a los primeros 4 segmentos
            code = issue['code']
            # Tomar solo los primeros 5 elementos del código (4 segmentos)
            code_reducido = '.'.join(code.split('.')[:5])  # Primeros 5 elementos (4 segmentos)
            tipo = issue['type']

            # Contar la aparición total del código
            total_count[(code_reducido, tipo)] += 1
            
            # Contar la aparición única del código para esa URL
            unique_count[(code_reducido, tipo)][page_url] += 1

    return total_count, unique_count

# Función para guardar los resultados en un archivo CSV
def guardar_resultados(total_count, unique_count, output_csv):
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Escribir el encabezado
        writer.writerow(['code', 'type', 'total_count', 'unique_count'])

        # Escribir los resultados
        for (code, tipo), count in total_count.items():
            unique_count_value = len(unique_count[(code, tipo)])  # Número de URLs únicas
            writer.writerow([code, tipo, count, unique_count_value])

# Función principal
def main():
    archivos_json = ['salida1.json', 'salida2.json', 'salida3.json']  # Archivos de entrada
    datos = leer_json(archivos_json)  # Leer los datos de los tres archivos

    # Contar las instancias de los códigos
    total_count, unique_count = contar_codes(datos)

    # Guardar los resultados en un archivo CSV
    output_csv = 'conteo_codigos.csv'  # Archivo CSV de salida
    guardar_resultados(total_count, unique_count, output_csv)

# Ejecutar el script
if __name__ == "__main__":
    main()
