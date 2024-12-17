import requests
from lxml import etree
import csv
import re

def comprobar_accesibilidad(url):
    try:
        # Realizar la solicitud a la URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Verificar si hay errores en la respuesta
    except requests.exceptions.RequestException as e:
        print(f"Error al intentar acceder a la URL: {url} - {e}")
        return False, str(e)

    # Parsear el contenido HTML usando lxml
    try:
        tree = etree.HTML(response.content)
    except Exception as e:
        print(f"Error al analizar el HTML: {e}")
        return False, str(e)

    # Definir rutas XPath donde se busca el texto "Accesibilidad"
    xpaths = [
        "/html/body/div[2]/div/footer/div/div[3]/p/span[2]",
        "/html/body/div[1]/div[1]/div/div[1]/ul/li[1]/a/span[2]"
    ]

    # Definir patrones de búsqueda para varios idiomas
    patrones = [
        r'.*Accesibilidad.*',   # Español
        r'.*Accesibilidade.*',  # Gallego
        r'.*Accessibilitat.*',  # Catalán
        r'.*Accesibilitat.*',   # Valenciano
        r'.*Irisgarritasuna.*'   # Euskera
    ]

    # Comprobar si alguna ruta contiene el texto deseado en cualquiera de los patrones
    for path in xpaths:
        # Buscar elementos en la ruta XPath
        elementos = tree.xpath(path)
        if elementos:
            # Verificar si algún elemento contiene el texto con alguno de los patrones
            for el in elementos:
                if any(re.search(patron, el.text, re.IGNORECASE) for patron in patrones):
                    return True, None

    return False, None


def procesar_csv(input_csv, output_csv, error_csv):
    # Abrir el archivo CSV de entrada
    with open(input_csv, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    # Filtrar registros con ContieneAccesibilidad = N
    registros_a_procesar = [row for row in rows if row['ContieneAccesibilidad'] == 'N']

    # Imprimir el número total de URLs leídas
    total_urls = len(registros_a_procesar)
    print(f"Total de URLs a procesar (ContieneAccesibilidad = N): {total_urls}")

    # Crear los archivos CSV de salida
    with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile, \
         open(error_csv, mode='w', newline='', encoding='utf-8') as errorfile:
        
        # Configurar los campos para ambos CSV
        fieldnames = ['ComunidadAutonoma', 'Provincia', 'NombreAyuntamiento', 'WebAyuntamiento', 'ContieneAccesibilidad']
        error_fieldnames = ['ComunidadAutonoma', 'Provincia', 'NombreAyuntamiento', 'WebAyuntamiento', 'Error']

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        error_writer = csv.DictWriter(errorfile, fieldnames=error_fieldnames)
        
        # Escribir encabezados
        writer.writeheader()
        error_writer.writeheader()

        # Procesar registros con ContieneAccesibilidad = N
        for index, row in enumerate(registros_a_procesar, start=1):
            url = row['WebAyuntamiento']
            print(f"({index}/{total_urls}) Procesando {row['NombreAyuntamiento']} - {url}")

            # Comprobar accesibilidad y manejar errores
            contiene_accesibilidad, error = comprobar_accesibilidad(url)

            if error:
                # Guardar la URL con error en el archivo de errores
                error_writer.writerow({
                    'ComunidadAutonoma': row['ComunidadAutonoma'],
                    'Provincia': row['Provincia'],
                    'NombreAyuntamiento': row['NombreAyuntamiento'],
                    'WebAyuntamiento': url,
                    'Error': error
                })
            else:
                # Actualizar el valor de ContieneAccesibilidad basado en la comprobación
                row['ContieneAccesibilidad'] = 'S' if contiene_accesibilidad else 'N'

        # Escribir todos los registros en el archivo de salida
        for row in rows:
            writer.writerow(row)

input_csv = 'ayuntamientos.csv'  
output_csv = 'resultados_accesibilidad_completos.csv'  # Ruta del archivo CSV de salida
error_csv = 'resultados_accesibilidad_errores.csv'  # Archivo de errores
procesar_csv(input_csv, output_csv, error_csv)
