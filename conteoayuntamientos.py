import csv
import json
import os
from collections import defaultdict

def procesar_json_a_csv(input_files, diccionario_csv, output_directory):
    # Crear la carpeta "resultados" si no existe
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Archivos de salida
    output_file_general = os.path.join(output_directory, 'conteo_general.csv')

    # Cargar el diccionario de errores
    diccionario_errores = {}
    with open(diccionario_csv, 'r', encoding='utf-8') as diccionario_file:
        lector = csv.DictReader(diccionario_file)
        for fila in lector:
            diccionario_errores[fila['Codigo']] = fila

    # Estructuras para acumular datos
    general_count = defaultdict(lambda: {
        "error": 0, "warning": 0, "notice": 0,
        "criterios_error": set(), "criterios_warning": set(), "criterios_notice": set(),
        "AErrors": set(), "AAErrors": set()
    })

    # Procesar cada archivo JSON
    for input_file in input_files:
        # Leer el archivo JSON
        with open(input_file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        # Procesar cada entrada en el JSON
        for entrada in data:
            url = entrada.get("url", "")
            result = entrada.get("result", {})
            nombre_pagina = result.get("documentTitle", "")
            issues = result.get("issues", [])

            # Iterar sobre los problemas (issues)
            for issue in issues:
                # Obtener solo los primeros 4 segmentos del código
                codigo_completo = issue["code"]
                codigo_4_partes = '.'.join(codigo_completo.split('.')[:4])

                # Contadores por tipo de problema (error, warning, notice)
                tipo = issue.get("type", "")
                if tipo == "error":
                    general_count[url]["error"] += 1
                    general_count[url]["criterios_error"].add(codigo_4_partes)

                    # Determinar el nivel del código y actualizar AErrors o AAErrors
                    nivel = diccionario_errores.get(codigo_4_partes, {}).get('Nivel', '')
                    if nivel == 'A':
                        general_count[url]["AErrors"].add(codigo_4_partes)
                    elif nivel == 'AA':
                        general_count[url]["AAErrors"].add(codigo_4_partes)

                elif tipo == "warning":
                    general_count[url]["warning"] += 1
                    general_count[url]["criterios_warning"].add(codigo_4_partes)

                elif tipo == "notice":
                    general_count[url]["notice"] += 1
                    general_count[url]["criterios_notice"].add(codigo_4_partes)

    # Guardar resultados en conteo_general.csv
    with open(output_file_general, 'w', newline='', encoding='utf-8') as csv_general:
        writer_general = csv.writer(csv_general)
        # Encabezados del archivo general
        writer_general.writerow([
            "URL", 
            "NombrePagina", 
            "NumeroError", 
            "NumeroWarning", 
            "NumeroNotice", 
            "CriteriosError", 
            "CriteriosWarning", 
            "CriteriosNotice", 
            "AErrors", 
            "AAErrors"
        ])
        # Escribir los datos generales por URL
        for url, counts in general_count.items():
            writer_general.writerow([
                url,
                nombre_pagina,  # Asegúrate de que nombre_pagina esté correctamente extraído
                counts["error"],
                counts["warning"],
                counts["notice"],
                len(counts["criterios_error"]),
                len(counts["criterios_warning"]),
                len(counts["criterios_notice"]),
                len(counts["AErrors"]),
                len(counts["AAErrors"])
            ])

    print(f"Archivo CSV generado exitosamente en la carpeta: {output_directory}")

# Lista de archivos JSON de entrada
input_files = ['salida.json', 'salida1.json', 'salida3.json']  # Agrega aquí más archivos si es necesario

# Carpeta donde se almacenarán los archivos CSV
output_directory = 'resultados'  # Carpeta "resultados"

# Diccionario CSV con los códigos de error
diccionario_csv = 'diccionario_errores.csv'

# Ejecutar la función
procesar_json_a_csv(input_files, diccionario_csv, output_directory)
