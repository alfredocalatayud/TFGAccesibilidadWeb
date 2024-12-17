# TFGAccesibilidadWeb
Código utilizado durante la elaboración del TFG sobre Estudio y mejora de la Accesibilidad Web en la administración pública

## Requerimientos

**Bibliotecas necesarias**

 - pandas
 - requests
 - tqdm
 - tabulate

## consultaweb.py
Mediante este archivo leeremos un CSV con las URLs de las páginas web de los ayuntamientos, este CSV tendrá la siguiente estructura:
| ComunidadAutonoma | Provincia | NombreAyuntamiento | WebAuntamiento | SedeElectronica
|--|--|--|--|--|--|
| Andalucía | Almería | Ayuntamiento de Abla | https://www.abla.es | https://ayuntamientodeabla.sedelectronica.es
| Andalucía | Almería | Ayuntamiento de Abrucena | http://www.abrucena.es | https://www.abrucena.es/Servicios/cmsdipro/index.nsf/index.xsp?p=SedeAbrucena
| Andalucía | Almería | Ayuntamiento de Adra | http://adra.es | https://sede.adra.es
| ... |  |  |  | 

Se utiliza la biblioteca request para recuperar el código de respuesta HTTP:

**Función para obtener el estado HTTP de una URL**  
```python
def get_http_status(url):  
    try:  
        response = requests.get(url, timeout=5, stream=True)  
        return response.status_code  
    except requests.RequestException as e:  
        return str(e)
```

Estos código de respuesta se dividen entre con código 200 y distinto de 200, en CSVs separados.

Al ejecutar el programa aparecerá el siguiente menú:

```
Menú:
	1. Comprobar el fichero de webs
	2. Ver los resultados
	3. Crear archivos CSV por código de respuesta HTTP
	4. Revisar errores y crear 'revision_errores.csv'
	5. Salir
Selecciona una opción:
```
La comprobación se hará mediante la primera opción, aparte podremos ver resultados, dividir el CSV de salida y revisar errores.
La salida de la ejecución de la primera opción tendrá la siguiente apariencia:
```
Consultando webs: 100%|████████████████████████████████████████████████████████████████| 2/2 [00:01<00:00,  1.35it/s] 
Comprobación completada y guardada en 'ayuntamientos_con_estado_http.csv'
  ComunidadAutonoma Provincia  ...                                    SedeElectronica HttpStatus
0         Andalucía   Almería  ...       https://ayuntamientodeabla.sedelectronica.es        200
1         Andalucía   Almería  ...  https://www.abrucena.es/Servicios/cmsdipro/ind...        200

[2 rows x 6 columns]
Archivo creado: resultados/resultado_200.csv
Archivo creado: resultados/resultado_no_200.csv
```
## llamadalighthouse.py
Mediante este archivo leeremos un CSV con las URLs de las páginas web de los ayuntamientos, este CSV tendrá la siguiente estructura:
| ComunidadAutonoma | Provincia | NombreAyuntamiento | WebAuntamiento | SedeElectronica
|--|--|--|--|--|--|
| Andalucía | Almería | Ayuntamiento de Abla | https://www.abla.es | https://ayuntamientodeabla.sedelectronica.es
| Andalucía | Almería | Ayuntamiento de Abrucena | http://www.abrucena.es | https://www.abrucena.es/Servicios/cmsdipro/index.nsf/index.xsp?p=SedeAbrucena
| Andalucía | Almería | Ayuntamiento de Adra | http://adra.es | https://sede.adra.es

Y llamaremos a la API de Google LightHouse para recuperar la calificación de accesibilidad que esta le pone. 

**Llamada a la API**
```python
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
		round(score, 2)  
    except Exception as e:  
        print(f"Error analizando {url}: {e}")  
        return None
```
Esta función llama a la API de Google PageSpeed Insights para analizar la accesbilidad de una URL. Los resultados se almacenarán en un CSV de salida, se guardará el progreso cada 100 URLs estudiadas.
Un ejemplo de ejecución:
```
$ python llamadaapi.py 
Se detectó progreso previo: 4884 URLs ya procesadas.
Iniciando el análisis de accesibilidad...
Procesando URLs: 0it [00:00, ?it/s]
Análisis completado. Archivo guardado en: ayuntamientos_con_accesibilidad.csv
```
## llamadapa11y.py
Mediante este archivo leeremos un CSV con las URLs de las páginas web de los ayuntamientos, este CSV tendrá la siguiente estructura:
| ComunidadAutonoma | Provincia | NombreAyuntamiento | WebAuntamiento | SedeElectronica
|--|--|--|--|--|--|
| Andalucía | Almería | Ayuntamiento de Abla | https://www.abla.es | https://ayuntamientodeabla.sedelectronica.es
| Andalucía | Almería | Ayuntamiento de Abrucena | http://www.abrucena.es | https://www.abrucena.es/Servicios/cmsdipro/index.nsf/index.xsp?p=SedeAbrucena
| Andalucía | Almería | Ayuntamiento de Adra | http://adra.es | https://sede.adra.es

Llamaremos a pa11y para realizar comprobación del estado de la accesibilidad de la web. 
Configuraremos la llamada a pa11y del siguiente modo:
```javascript
const result = await pa11y(url, {
	standard:  'WCAG2AA',
	timeout:  90000,
	includeNotices:  true,
	includeWarnings:  true
});
```
De este modo comprobaremos es estándar WCAG 2.1 hasta el nivel AA, e incluiremos en la salida notices y wanings.
Los resultados se guardarán en un archivo json con la estructura de la respuesta de pa11y, por ejemplo:
```json
{
    pageUrl: 'The tested URL',
    documentTitle: 'Title of the page under test',
    issues: [
        {
            code: 'WCAG2AA.Principle1.Guideline1_1.1_1_1.H30.2',
            context: '<a href="https://example.com/"><img src="example.jpg" alt=""/></a>',
            message: 'Img element is the only content of the link, but is missing alt text. The alt text should describe the purpose of the link.',
            selector: 'html > body > p:nth-child(1) > a',
            type: 'error',
            typeCode: 1
        }
    ]
}
```
**Salida pa11y**
Debido al volumen de datos devuelto por la llamada a pa11y, dejo un enlace de descarga de los resultados con WeTransfer:
https://we.tl/t-CflluLIZcr
## conteocodigos.py
Lee uno o varios archivos json y genera un CSV contabilizando los tipos de error que aparecen en dicho json. En el CSV guarda el código, el tipo el número total de apariciones, y apariciones únicas por ayuntamiento. 
## conteoayuntamientos.py
Lee uno o varios archivos json y genera un CSV contabilizando los errores, warnings y notices en criterios de éxito por ayuntamiento. En el CSV guarda el código el la URL comprobada, el nombre de la página, cuenta total de errores, warnings y notices, errores, warnings y notices distintos por ayuntamiento, y divide estos últimos errores por nivel (A o AA). Esta clasificación entre A y AA la hace gracias a un diccionario que los clasifica (diccionario_errores.csv).
## existeaccesibilidad.py
Mediante este archivo leeremos un CSV con las URLs de las páginas web de los ayuntamientos, este CSV tendrá la siguiente estructura:
| ComunidadAutonoma | Provincia | NombreAyuntamiento | WebAuntamiento | SedeElectronica
|--|--|--|--|--|--|
| Andalucía | Almería | Ayuntamiento de Abla | https://www.abla.es | https://ayuntamientodeabla.sedelectronica.es
| Andalucía | Almería | Ayuntamiento de Abrucena | http://www.abrucena.es | https://www.abrucena.es/Servicios/cmsdipro/index.nsf/index.xsp?p=SedeAbrucena
| Andalucía | Almería | Ayuntamiento de Adra | http://adra.es | https://sede.adra.es

Y comprobaremos si en dicha URL existe al menos un elemento en el HTML con la etiqueta "Accesbilidad". Consta de dos funciones principales, comprobar_accesibilidad(url), que comprueba si en la web dada existe algún elemento que indique 'Accesibilidad' en rutas específicas del documento HTML, buscando en varios idiomas.
Y procesar_csv(input_csv,  output_csv,  error_csv), que lee un archivo CSV con la información de los ayuntamientos y verifica si cada URL contiene 'Accesibilidad'. Procesa solo registros con ContieneAccesibilidad = N, pero incluye todos los registros en la salida.

