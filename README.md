# horariosUSC

Genera horarios personalizados a partir de los horarios publicados por la Universidade de Santiago de Compostela (USC).

El proyecto extrae asignaturas, grupos, aulas y franjas horarias a un CSV, prepara un formulario de Google Forms para elegir grupos y utiliza Google Apps Script para generar y compartir un PDF con cada respuesta.

## Requisitos

- Python 3.10 o superior.
- Conexión a Internet para consultar la USC.
- Para crear formularios: Google Chrome, ChromeDriver compatible y un perfil de Chrome con una sesión de Google iniciada. La interfaz de Google Forms debe estar en español.
- Para generar PDF: Google Forms, Sheets, Drive, Docs y Apps Script.

## Instalación

```bash
git clone https://github.com/ibaa-13/horariosUSC.git
cd horariosUSC
python -m venv .venv
```

Activa el entorno en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Configuración

Edita [`config.yaml`](config.yaml). La lista `cursos` contiene el nombre de cada curso y la URL AJAX de su calendario en la USC. Las URLs incluidas representan vistas concretas del calendario; revisa el curso académico y la semana antes de usarlas.

Las rutas relativas se resuelven desde la raíz del proyecto, independientemente del directorio desde el que ejecutes `run.py`:

```yaml
chrome_data_dir: "chrome/selenium"
chromedriver_path: "chrome/chromedriver.exe"
timetable_path: "output/horario.csv"
forms_data_path: "output/forms_data.json"
```

Las carpetas de salida se crean automáticamente. Puedes utilizar rutas absolutas si lo necesitas. En Linux o macOS, adapta el nombre del ejecutable de ChromeDriver.

Coloca ChromeDriver en la ruta configurada. El directorio de datos de Chrome debe contener una sesión de Google iniciada; no lo uses simultáneamente desde otra instancia de Chrome. Los perfiles del navegador y las salidas están excluidos de Git.

## Uso

Desde la raíz del repositorio, genera el CSV y el JSON sin abrir el navegador:

```bash
python run.py --no-forms
```

Para ejecutar también la creación del formulario:

```bash
python run.py
```

También puedes ejecutar cada etapa por separado, respetando el orden cuando quieras regenerar todos los datos:

```bash
python -m horarios.getTimetable
python -m horarios.createFormsData
python -m horarios.createForms
```

El formulario añade un título por curso y una pregunta de casillas por asignatura. Revisa el resultado antes de compartirlo: el script puede continuar tras un error en una pregunta y dejar el formulario incompleto.

Los archivos de `examples/` son muestras estáticas; no se actualizan al ejecutar el programa. Los resultados nuevos se guardan en `output/`.

## Generar PDF con Google Apps Script

1. Sube `output/horario.csv` a Drive como archivo CSV, conservando el separador `;`.
2. Sube [`templates/Plantilla.docx`](templates/Plantilla.docx) y conviértelo a un documento de Google Docs. Revisa que sus marcadores, como `L10` o `X12`, coincidan con las franjas del CSV.
3. Crea una carpeta en Drive para los PDF.
4. En Google Forms, activa la recopilación de correos y vincula una hoja de respuestas de Google Sheets.
5. Desde esa hoja, abre **Extensiones → Apps Script** y copia [`apps_script/codigo.gs`](apps_script/codigo.gs).
6. En **Configuración del proyecto → Propiedades de la secuencia de comandos**, añade estas propiedades:

| Propiedad | Valor |
| --- | --- |
| `PLANTILLA_ID` | Identificador del documento de Google Docs usado como plantilla. |
| `DATASET_ID` | Identificador del archivo CSV en Drive. |
| `FOLDER_ID` | Identificador de la carpeta de destino. |

Los identificadores se obtienen de las URLs de los archivos y la carpeta. No es necesario incluirlos en el código del repositorio.

7. Comprueba que `nombre_columna_correo` coincide con el encabezado de correo de tu hoja; por defecto es `Dirección de correo electrónico`.
8. Crea un activador instalable para `onFormSubmit`, con origen **Hoja de cálculo** y evento **Al enviar formulario**, y autoriza los permisos solicitados.
9. Envía una respuesta desde el formulario para comprobar el flujo completo.

No ejecutes `onFormSubmit` directamente desde el editor: necesita el evento de envío de la hoja, incluido `e.namedValues`.

El script crea un PDF con el nombre `Horario` seguido del usuario del correo, lo guarda en la carpeta configurada, concede acceso de lectura al correo indicado y registra el enlace en la columna `Links`. La copia temporal de Google Docs se envía a la papelera.

Cuando regeneres los horarios, actualiza también el CSV de Drive. Si cambia su identificador, actualiza `DATASET_ID`.

## Estructura

```text
horariosUSC/
├── README.md
├── requirements.txt
├── .gitignore
├── .gitattributes
├── config.yaml
├── run.py
├── horarios/
│   ├── __init__.py
│   ├── loadconfig.py
│   ├── getTimetable.py
│   ├── createFormsData.py
│   └── createForms.py
├── apps_script/
│   └── codigo.gs
├── templates/
│   └── Plantilla.docx
├── examples/
│   ├── horario.csv
│   └── forms_data.json
└── output/                  # Generado localmente; excluido de Git
```

`chrome/`, `local/` y `.local-backup/` son directorios locales excluidos de Git. No forman parte de la distribución.

## Actualizar desde la estructura anterior

Los módulos Python ahora están en `horarios/`. Sustituye comandos como `python getTimetable.py` por `python -m horarios.getTimetable`, ejecutados desde la raíz del repositorio. El punto de entrada sigue siendo `python run.py`; la antigua variable `wantToCreateForms` se sustituye por la opción `--no-forms`.

La configuración se carga desde `config.yaml` en la raíz, sin editar `CONFIG_PATH`. Conserva tus URLs de cursos y adapta las rutas si utilizabas ubicaciones personalizadas.

Si ya tienes una instalación de Apps Script, configura las propiedades `PLANTILLA_ID`, `DATASET_ID` y `FOLDER_ID` con los valores de tus antiguas constantes antes de sustituir el código. La reorganización local no actualiza automáticamente tu proyecto de Apps Script.

## Formato de los datos

El CSV generado utiliza UTF-8 con BOM y separador `;`:

| Columna | Contenido | Ejemplo |
| --- | --- | --- |
| `Curso` | Curso configurado | `Primero` |
| `Slot` | Día y hora de inicio | `L10` |
| `Asignatura` | Nombre de la asignatura | `Introducción al análisis matemático` |
| `Grupo` | Grupo | `CLE01` |
| `Aula` | Aula, si está disponible | `Aula 02` |
| `Hora` | Intervalo horario | `10:00-11:00` |

Los días se representan mediante `L`, `M`, `X`, `J`, `V`, `S` y `D`. El extractor divide las clases en bloques de una hora. El JSON organiza los datos como `curso → asignatura → lista de grupos`, ordenados por prefijo (`CLE`, `CLIS`, `CLIL`) y número.

## Limitaciones

- La extracción depende de la estructura HTML y de las respuestas AJAX de la USC; los cambios en la web pueden requerir adaptar el código.
- Selenium depende del idioma y de la estructura de Google Forms. Comprueba la sesión de Google y la compatibilidad de ChromeDriver si falla.
- La ordenación de grupos presupone nombres con una parte numérica; los grupos vacíos o con otro formato pueden provocar errores.
- Las franjas se procesan en bloques de una hora y sus códigos no incluyen minutos.
- No se resuelven solapamientos. Apps Script filtra por asignatura y grupo, sin distinguir el curso.
- Solo se sustituyen los marcadores presentes en el CSV; otros marcadores pueden quedar visibles en la plantilla.
- El enlace del PDF se escribe en la última fila de la hoja; los envíos simultáneos pueden asociarlo a una fila incorrecta.

Las dependencias no están fijadas a versiones concretas. La generación y el uso del formulario requieren comprobar la integración con los servicios externos.
