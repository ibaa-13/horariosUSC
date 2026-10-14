# horariosUSC

Generador de horarios personalizados a partir de los horarios publicados por la **Universidade de Santiago de Compostela (USC)**.

El proyecto extrae asignaturas, grupos, aulas y franjas horarias de la web de la USC, prepara un formulario de Google Forms para seleccionar grupos y utiliza Google Apps Script para generar un PDF con el horario de cada respuesta.

## Cómo funciona

1. **Extrae los horarios** de las URLs configuradas y los guarda en un CSV.
2. **Agrupa las asignaturas y sus grupos** por curso en un archivo JSON.
3. **Crea un formulario** con Selenium: añade un título por curso y una pregunta de casillas por asignatura.
4. **Procesa las respuestas** con Google Apps Script: rellena una plantilla, genera un PDF en Drive, lo comparte con la persona que respondió y registra su enlace en la hoja de respuestas.

La configuración incluida contiene entradas de primero a cuarto y de primero a quinto de Mates-Física. Las URLs apuntan a vistas concretas del calendario: revísalas antes de generar un nuevo horario.

## Requisitos

- **Python 3.10 o superior**, por la sintaxis de tipos utilizada en el código.
- Conexión a Internet para consultar los horarios.
- Para crear el formulario: **Google Chrome**, un **ChromeDriver compatible** y un perfil de Chrome con una sesión de Google iniciada.
- Para generar los PDF: acceso a **Google Forms, Sheets, Drive, Docs y Apps Script**.

La automatización de Google Forms utiliza textos de la interfaz en **español**.

## Instalación

Clona el repositorio y entra en su carpeta:

```bash
git clone https://github.com/ibaa-13/horariosUSC.git
cd horariosUSC
python -m venv .venv
```

Activa el entorno virtual:

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install requests beautifulsoup4 pandas PyYAML selenium
```

## Configuración

### 1. Ajustar la ruta del archivo de configuración

En `loadconfig.py`, sustituye la ruta original de `CONFIG_PATH` por:

```python
CONFIG_PATH = "config.yaml"
```

Los comandos de este README deben ejecutarse desde la raíz del repositorio; las rutas relativas se resuelven desde el directorio de ejecución.

### 2. Editar `config.yaml`

Conserva o adapta la lista `cursos` y modifica las rutas de salida y del navegador. Por ejemplo:

```yaml
cursos:
  - curso: "Primero"
    url: "https://www.usc.gal/es/course/widget/76/course-detail-controller-week-filter/5060/19627-1/25/42?_wrapper_format=drupal_ajax"

chrome_data_dir: "chrome/selenium"
chromedriver_path: "chrome/chromedriver.exe"

timetable_path: "output/horario.csv"
forms_data_path: "output/forms_data.json"
```

La URL anterior es un ejemplo incluido en el repositorio, no una referencia que se actualice automáticamente al curso académico vigente. Usa las URLs del widget de horarios correspondiente al curso y la semana que quieras consultar.

| Campo | Descripción |
| --- | --- |
| `cursos` | Lista de nombres de curso y URLs del widget de horarios de la USC. |
| `chrome_data_dir` | Directorio de datos de Chrome utilizado por Selenium. Debe contener una sesión de Google iniciada para crear el formulario. |
| `chromedriver_path` | Ruta al ejecutable de ChromeDriver; adapta el nombre en Linux o macOS. |
| `timetable_path` | Ruta del CSV que genera la extracción. |
| `forms_data_path` | Ruta del JSON con cursos, asignaturas y grupos. |

Crea el directorio de salida antes de ejecutar los scripts:

```bash
mkdir output
```

Los scripts no crean las carpetas de salida automáticamente. Para utilizar Selenium, coloca ChromeDriver en la ruta indicada y evita abrir simultáneamente el mismo directorio de datos con otra instancia de Chrome.

## Uso

### Obtener los horarios y preparar los datos

```bash
python getTimetable.py
python createFormsData.py
```

El primer comando genera el CSV; el segundo lee ese CSV y genera el JSON. Esta opción permite preparar los datos sin abrir Google Forms.

### Crear el formulario

Con el JSON generado y el navegador configurado:

```bash
python createForms.py
```

El script abre `https://forms.new` y añade las asignaturas con sus grupos como opciones de casillas. Revisa el formulario resultante, su título y cualquier pregunta inicial antes de compartirlo.

### Ejecutar el flujo de Python completo

```bash
python run.py
```

Ejecuta la extracción, la generación del JSON y la creación del formulario. Para omitir este último paso, cambia en `run.py`:

```python
wantToCreateForms = False
```

`run.py` importa el módulo de creación del formulario al arrancar, por lo que necesita Selenium instalado incluso con esa opción desactivada. La generación de PDF se configura aparte en Apps Script.

## Generar PDF desde las respuestas

### Preparar los archivos en Google Drive

1. Sube el CSV generado a Drive como archivo CSV, conservando el separador `;`.
2. Sube `Plantilla.docx` y conviértelo a un documento de Google Docs. Apps Script abre la plantilla mediante `DocumentApp`.
3. Comprueba que la plantilla contiene los códigos de las franjas que quieres rellenar, como `L10`, `M11` o `X12`.
4. Crea una carpeta en Drive para guardar los PDF.
5. Copia los identificadores de la plantilla de Google Docs, el CSV y la carpeta desde sus respectivas URLs.

### Configurar el formulario y Apps Script

1. Activa la recopilación de direcciones de correo electrónico en Google Forms.
2. Vincula el formulario a una hoja de cálculo de Google Sheets.
3. Desde esa hoja, abre **Extensiones → Apps Script** y copia el contenido de `codigo.gs`.
4. Completa las constantes del script:

   ```javascript
   const plantillaId = 'ID_DE_LA_PLANTILLA_GOOGLE_DOCS';
   const datasetId = 'ID_DEL_ARCHIVO_CSV';
   const folderId = 'ID_DE_LA_CARPETA_DE_PDF';
   ```

5. Comprueba que la columna del correo se llama exactamente `Dirección de correo electrónico`. Si tiene otro nombre, adapta la clave utilizada en `e.namedValues`.
6. Añade un **activador instalable** para `onFormSubmit`, con origen **Hoja de cálculo** y evento **Al enviar formulario**, y autoriza los permisos que solicite Google.
7. Envía una respuesta de prueba desde el formulario.

El activador debe estar asociado a la hoja de respuestas porque el código utiliza `e.namedValues`. Ejecutar `onFormSubmit` directamente desde el editor no proporciona ese evento.

Con cada respuesta, el script crea un PDF llamado `Horario`, lo guarda en la carpeta configurada, concede acceso de lectura al correo indicado y añade su URL a la columna `Links`. La copia temporal de Google Docs se envía a la papelera.

## Formato de los datos

El extractor genera un CSV en UTF-8 con BOM y separador `;`, con estas columnas:

| Columna | Contenido | Ejemplo |
| --- | --- | --- |
| `Curso` | Nombre del curso configurado | `Primero` |
| `Slot` | Día y hora de inicio de la franja | `L10` |
| `Asignatura` | Nombre de la asignatura | `Introducción al análisis matemático` |
| `Grupo` | Identificador del grupo | `CLE01` |
| `Aula` | Aula publicada, cuando está disponible | `Aula 02` |
| `Hora` | Intervalo de la franja | `10:00-11:00` |

Los días se codifican como `L`, `M`, `X`, `J`, `V`, `S` y `D`. Las clases se dividen en bloques de una hora. El CSV de ejemplo incluido en la raíz contiene además una columna `Codigo`, que el extractor actual no genera.

El JSON organiza los datos como `curso → asignatura → lista de grupos`. Los grupos se ordenan por prefijo (`CLE`, `CLIS`, `CLIL`) y número.

## Estructura del repositorio

```text
horariosUSC/
├── run.py               # Ejecuta el flujo de Python
├── loadconfig.py        # Carga la configuración YAML
├── config.yaml          # Cursos, URLs y rutas locales
├── getTimetable.py      # Extrae los horarios y genera el CSV
├── createFormsData.py   # Convierte el CSV en datos para el formulario
├── createForms.py       # Crea el formulario mediante Selenium
├── codigo.gs            # Genera y comparte PDF desde Apps Script
├── Plantilla.docx       # Plantilla para el horario
├── horario.csv          # Datos de ejemplo incluidos
└── forms_data.json      # Datos de ejemplo incluidos
```

## Limitaciones y resolución de problemas

- **Rutas no encontradas:** revisa `CONFIG_PATH`, las rutas de `config.yaml` y la existencia de los directorios de salida. Las rutas originales usan una estructura local `python/horarios/` que no coincide con la raíz del repositorio.
- **Errores al extraer horarios:** el extractor depende de la respuesta AJAX y de la estructura HTML de la USC. Si cambian, será necesario adaptar las URLs o los selectores.
- **Errores al crear el formulario:** comprueba la compatibilidad entre Chrome y ChromeDriver, la sesión de Google y el idioma español de la interfaz. Los cambios en Google Forms pueden requerir actualizar los selectores de Selenium.
- **Grupos vacíos o sin número:** la ordenación presupone identificadores con una parte numérica; otros formatos pueden provocar errores.
- **Franjas parciales:** el extractor avanza en bloques de una hora y el código `Slot` no incluye minutos. Los intervalos que no encajan en ese esquema requieren adaptar la lógica.
- **Solapamientos y asignaturas repetidas:** el script no resuelve conflictos de horario y filtra las respuestas por nombre de asignatura y grupo, sin distinguir el curso. Revisa los resultados si varias entradas comparten esos valores.
- **Marcadores de la plantilla:** solo se sustituyen los códigos presentes en el CSV; los demás pueden quedar visibles en el PDF.
- **Respuestas simultáneas:** el enlace del PDF se escribe en la última fila de la hoja, por lo que varias respuestas concurrentes pueden asociarlo a una fila incorrecta.

Cuando actualices los horarios, vuelve a generar los datos y actualiza también el CSV de Drive que utiliza Apps Script. Si cambias su identificador, modifica `datasetId`.
