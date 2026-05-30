# Local AI Workbench / Banco IA

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-2fbf9f)
![SQLite](https://img.shields.io/badge/Storage-SQLite-044a64?logo=sqlite&logoColor=white)
![Windows](https://img.shields.io/badge/Desktop-Windows-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## English

Local AI Workbench is a Windows desktop productivity app for storing, searching, reusing, importing, and exporting AI prompts. It runs fully locally with SQLite and does not require an external API.

### Features

- Prompt library with title, category, tags, prompt body, and favorite toggle.
- Search by title, tag, category, or prompt text.
- Category sidebar and favorites filter.
- Notes linked to each prompt for observations, results, and reuse context.
- Export selected prompt as Markdown.
- Export and import the full prompt library as JSON.
- Copy prompt or prompt plus notes to the clipboard.
- English and Spanish launchers with shared backend logic.
- Auto-created local database at `data/workbench.db`.

### Downloads

After building, the Windows executables are created in `dist/`:

- `dist/LocalAIWorkbench_EN.exe`
- `dist/BancoIA_ES.exe`

### Run From Source

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Spanish UI:

```powershell
python main_es.py
```

### Build Windows Executables

```powershell
.\build_exe.ps1
```

The build script removes old `build/`, `dist/`, and `.spec` files, packages CustomTkinter assets, creates both executables, and performs a launch check.

### Project Structure

```text
main.py          English launcher
main_es.py       Spanish launcher
app_ui.py        CustomTkinter interface
database.py      SQLite schema and persistence
models.py        Shared data models
exporter.py      Markdown and JSON export helpers
utils.py         App paths and utility helpers
requirements.txt Python dependencies
README.md        Bilingual documentation
build_exe.ps1    PyInstaller build script
.gitignore       Ignored generated files
data/            Auto-created local database folder
```

## Espanol

Banco IA es una aplicacion de escritorio para Windows que permite guardar, buscar, reutilizar, importar y exportar prompts de IA. Funciona completamente de forma local con SQLite y no requiere una API externa.

### Funciones

- Biblioteca de prompts con titulo, categoria, etiquetas, cuerpo del prompt y marcador de favorito.
- Busqueda por titulo, etiqueta, categoria o texto del prompt.
- Barra lateral de categorias y filtro de favoritos.
- Notas vinculadas a cada prompt para observaciones, resultados y contexto de reutilizacion.
- Exportacion del prompt seleccionado como Markdown.
- Exportacion e importacion de toda la biblioteca como JSON.
- Copia del prompt o del prompt con notas al portapapeles.
- Lanzadores en ingles y espanol con logica compartida.
- Base de datos local creada automaticamente en `data/workbench.db`.

### Descargas

Despues de compilar, los ejecutables de Windows quedan en `dist/`:

- `dist/LocalAIWorkbench_EN.exe`
- `dist/BancoIA_ES.exe`

### Ejecutar Desde Codigo Fuente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Interfaz en espanol:

```powershell
python main_es.py
```

### Crear Ejecutables Para Windows

```powershell
.\build_exe.ps1
```

El script limpia `build/`, `dist/` y archivos `.spec`, incluye los recursos de CustomTkinter, genera ambos ejecutables y verifica que se puedan iniciar.

### Estructura Del Proyecto

```text
main.py          Lanzador en ingles
main_es.py       Lanzador en espanol
app_ui.py        Interfaz con CustomTkinter
database.py      Esquema SQLite y persistencia
models.py        Modelos de datos compartidos
exporter.py      Exportacion Markdown y JSON
utils.py         Rutas de la app y utilidades
requirements.txt Dependencias de Python
README.md        Documentacion bilingue
build_exe.ps1    Script de compilacion con PyInstaller
.gitignore       Archivos generados ignorados
data/            Carpeta de base de datos local auto-creada
```

