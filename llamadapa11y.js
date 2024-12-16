const fs = require('fs'); // Importa el módulo fs para manejar archivos
const pa11y = require('pa11y'); // Importa pa11y para análisis de accesibilidad
const csv = require('csv-parser'); // Importa csv-parser para leer archivos CSV

// Función para leer URLs desde el archivo CSV
function leerUrlsDesdeCSV(rutaCSV) {
    return new Promise((resolve, reject) => {
        const urls = [];
        fs.createReadStream(rutaCSV)
            .pipe(csv())
            .on('data', (row) => {
                if (row.WebAyuntamiento) {
                    urls.push(row.WebAyuntamiento);
                }
            })
            .on('end', () => {
                console.log('Archivo CSV leído correctamente.');
                resolve(urls);
            })
            .on('error', (err) => {
                reject(err);
            });
    });
}

// Función para evaluar accesibilidad
async function evaluarAccesibilidad(urls) {
    const resultados = [];
    const total = urls.length; // Número total de URLs a analizar
    console.log(`Se van a analizar un total de ${total} URLs.\n`);

    for (let i = 0; i < total; i++) {
        const url = urls[i];
        try {
            console.log(`(${i + 1}/${total}) Evaluando accesibilidad para: ${url}`);
            const result = await pa11y(url, { 
                standard: 'WCAG2AA',
                timeout: 90000,
                includeNotices: true,
                includeWarnings: true
            });

            resultados.push({ url, result });
            console.log(`(${i + 1}/${total}) Accesibilidad evaluada para: ${url}`);
        } catch (error) {
            console.error(`(${i + 1}/${total}) Error al evaluar la accesibilidad para ${url}:`, error);
        }

        // Guarda los resultados cada 100 URLs procesadas o al final
        if ((i + 1) % 100 === 0 || (i + 1) === total) {
            console.log(`Guardando resultados tras procesar ${i + 1} URLs...`);
            fs.writeFileSync('salida.json', JSON.stringify(resultados, null, 2));
        }
    }
    console.log('Evaluación completada. Todos los resultados están guardados en salida.json.');
}

// Función principal
async function main() {
    try {
        const urls = await leerUrlsDesdeCSV('ayuntamientos.csv');
        await evaluarAccesibilidad(urls);
    } catch (error) {
        console.error('Error en el proceso:', error);
    }
}

// Llama a la función principal
main();
