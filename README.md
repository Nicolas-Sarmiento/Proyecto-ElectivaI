# Proyecto Editorial

Este proyecto es un sistema editorial desarrollado en Python con Flask y PostgreSQL.

## Autores
- Andres Felipe Luna Becerra
- Nicolas Sarmiento Vargas

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <url-del-repositorio>
   ```

2. Crea un entorno virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicación:
   ```bash
   python run.py
   ```

5. Crea la base de datos (si hay erores utilizar flask de la carpeta venv):
   ```bash
   .venv/bin/flask db init
   .venv/bin/flask db migrate -m "Crear tablas iniciales"
   .venv/bin/flask db upgrade
   ```


## Estructura del proyecto

- `app/`: Contiene la lógica de la aplicación.
  - `__init__.py`: Inicializa la aplicación.
  - `models.py`: Define los modelos de la base de datos.
  - `routes.py`: Define las rutas de la API.
- `config.py`: Contiene la configuración de la aplicación.
- `run.py`: Punto de entrada de la aplicación.
- `requirements.txt`: Dependencias de la aplicación.
