# Reloj — Vector Analog Clock (Proyecto)

## Descripción

`Reloj` es una aplicación de reloj analógico vectorial desarrollada en Python con interfaz gráfica basada en Tkinter. El proyecto renderiza una cara de reloj escalable usando `pycairo` para dibujo vectorial, convierte a imágenes con `Pillow` y muestra desde `ImageTk`. La aplicación incorpora subesferas semicirculares (termómetro e higrómetro), persistencia de configuraciones en SQLite y características de accesibilidad (visual y lectura de la hora en voz en español).

## Características principales

- Renderizado vectorial a doble resolución (2×) y downsampling con `Image.LANCZOS` para suavizar el resultado.
- Agujas separadas para hora, minuto y segundo; el segundero avanza en pasos enteros por segundo según la zona horaria `America/Bogota`.
- Dos subesferas semicirculares:
  - Termómetro (izquierda): rango 0..60, ticks por unidad, etiqueta cada 10; incluye explícitamente el 0.
  - Higrómetro (derecha): rango 30..100, ticks por unidad, etiqueta cada 10; incluye explícitamente el 30.
- Diálogo de `Settings` persistente: permite cambiar `logo_name` y color del segundero; cambios se guardan en SQLite y se aplican al UI en tiempo real.
- Accesibilidad: muestra la hora digital actual (Colombia) actualizada cada segundo y botón `Speak Time` que utiliza `pyttsx3` para leer la hora en español.
- Persistencia: `src/data/clock_data.db` (SQLite) para configuraciones y logs.

## Arquitectura y patrones usados

- Organización modular en `src/` con separación entre `core`, `ui`, `services`, `controllers`, `utils`.
- Patrones de diseño aplicados:
  - Singleton: `DatabaseService` (gestión de DB centralizada) y `ClockStructure` (estructura de tiempo compartida).
  - Factory: `HandFactory` crea instancias de agujas (`HourHand`, `MinuteHand`, `SecondHand`).
  - Abstract Base Class (ABC): `ClockHand` define la interfaz común para agujas.
  - Estructura de datos: lista circular doble (circular/doble) de 60 puntos en `ClockStructure` para modelar posiciones por segundo/minuto.

## Estructura del proyecto (resumen)

- `main.py` — Punto de entrada; inicializa settings, servicios y la ventana principal.
- `src/core/` — Lógica del reloj y fábrica de agujas (`clock_structure.py`, `hand_factory.py`).
- `src/ui/` — Componentes de interfaz y renderizado vectorial (`clock_face.py`, `settings_dialog.py`).
- `src/services/` — Servicios compartidos, p.ej. `database_service.py`.
- `src/controllers/` — Controladores para el ciclo de actualización del reloj (`clock_controller.py`).
- `src/data/clock_data.db` — Base de datos SQLite con tablas `settings` y `logs`.
- `scripts/` — Scripts auxiliares (p. ej. `check_imports.py`).
- `.gitignore` — Ignora `__pycache__`, `*.pyc` y otros artefactos.

## Tecnologías y dependencias

- Python 3.10+ (se probó en 3.13 en el entorno del desarrollador)
- Bibliotecas principales:
  - `pycairo` — dibujo vectorial (cairo ImageSurface)
  - `Pillow` (`PIL`) — conversión y downsampling (`Image.LANCZOS`)
  - `ImageTk` (desde `Pillow`) — integración con Tkinter
  - `pytz` — manejo de zona horaria `America/Bogota`
  - `pyttsx3` — text-to-speech local (Windows SAPI5)
  - `sqlite3` (módulo estándar) — persistencia local

Recomendado para instalar en el entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install pycairo Pillow pytz pyttsx3 pypiwin32
```

Nota: en Windows `pyttsx3` puede requerir `pypiwin32`/`pywin32` para un backend SAPI estable.

## Pipeline de renderizado (detalles técnicos)

- Se dibuja en `pycairo` a 2× resolución en una `cairo.ImageSurface`.
- El buffer de bytes se transforma a una imagen `Pillow`.
- Se redimensiona a la resolución objetivo con `Image.LANCZOS` para anti-aliasing de alta calidad.
- `ImageTk.PhotoImage` se usa como `PhotoImage` de Tkinter; la referencia se mantiene en `self.image_ref` para evitar que el recolector de basura la elimine.

## Ejecución

Desde la raíz del proyecto (usar entorno virtual recomendado):

```powershell
# Activar venv (PowerShell)
.\venv\Scripts\Activate.ps1
# Asegurar PYTHONPATH para importar desde `src`
$env:PYTHONPATH = (Join-Path $PWD 'src')
python main.py
```

O en un solo comando (Windows PowerShell):

```powershell
& .\venv\Scripts\python.exe .\main.py
```

La ventana principal muestra el reloj; el menú `App → Settings` abre el diálogo para editar `logo_name` y el color del segundero. La hora digital y el botón `Speak Time` se encuentran en ese diálogo para accesibilidad.

## Base de datos y configuración

- Archivo: `src/data/clock_data.db`.
- Tabla `settings`: pares `key`/`value` para persistir `logo_name`, `second_hand_color` y otras preferencias.
- Tabla `logs`: almacena registros de eventos (opcionalmente usados por el controlador).

## Buenas prácticas y notas de mantenimiento

- No incluir `__pycache__` ni `*.pyc` en el control de versiones; `.gitignore` ya está configurado.
- Mantener `venv/` fuera del repositorio.
- Al actualizar dependencias, usar un `requirements.txt` o `pyproject.toml` para reproducibilidad.
- No eliminar archivos de la base de datos sin respaldo si contiene configuraciones que se desean conservar.

## Pruebas y verificación rápida

- Ejecuta `main.py` y verifica que la cara del reloj aparece y que las agujas se mueven.
- Abre `App → Settings`: cambia el `logo_name` y el color del segundero; cierra y reabre la app para confirmar persistencia.
- Prueba `Speak Time` (requiere `pyttsx3` instalado); si falla, instala `pyttsx3` y `pypiwin32`.

## Contribuciones

- Para cambios grandes, crea una rama nueva y abre un pull request explicando la motivación y pruebas realizadas.

## Contacto y autoría

Desarrollado por: **Luis Sebastian Diaz**

Facultad de Ingeniería de Software — Universidad Cooperativa de Colombia
