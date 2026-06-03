# Guía de Operación - Planix

Esta guía detalla los pasos y requisitos para ejecutar y mantener la aplicación en funcionamiento.

## Requisitos del Sistema
- **Python**: 3.11
- **Dependencias principales**: Django (>=4.2, <5.0), gunicorn, social-auth-app-django.
- **Estructura del Código**: Las aplicaciones (`projects`, `scrum`, `accounts`) se encuentran encapsuladas en la carpeta `app/`.
- **Base de Datos**: SQLite (para entornos de desarrollo local; se recomienda migrar a PostgreSQL en producción).
- **Contenerización**: Docker y Docker Compose (opcional, pero recomendado).

## Opción 1: Ejecución Local usando Entorno Virtual (venv)

Esta es la forma estándar de desarrollar en local si tienes Python instalado.

1. **Crear y activar un entorno virtual**:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Aplicar migraciones de la base de datos**:
   Como se utiliza SQLite por defecto (`db.sqlite3`), este archivo se creará o actualizará automáticamente al correr el comando:
   ```bash
   python manage.py migrate
   ```

4. **Crear un superusuario** (opcional, para acceder al Django Admin):
   ```bash
   python manage.py createsuperuser
   ```

5. **Iniciar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```
   La aplicación estará disponible en `http://localhost:8000`.

---

## Opción 2: Ejecución Local usando Docker

Si tienes Docker instalado, puedes iniciar toda la infraestructura con un solo comando.

1. **Construir y levantar el contenedor**:
   ```bash
   docker-compose up --build
   ```
   
   > [!NOTE]
   > Docker Compose creará una imagen basada en `python:3.11-slim`, instalará las dependencias y montará tu directorio local como un volumen en `/app`.

2. **Acceder a la aplicación**:
   Una vez que el contenedor esté corriendo, la aplicación estará accesible en `http://localhost:8000`.

3. **Ejecutar comandos en Docker**:
   Si necesitas hacer migraciones o crear superusuarios dentro de Docker:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Detener los servicios**:
   ```bash
   docker-compose down
   ```

---

## Notas Operativas Adicionales

> [!WARNING]
> - **Variables de Entorno**: El proyecto busca un archivo `.env`. Asegúrate de tenerlo configurado correctamente si tienes configuraciones como `SECRET_KEY` o integraciones de social auth, especialmente al prepararlo para un despliegue productivo.
> - **Base de datos**: El archivo actual de la base de datos local es `db.sqlite3`. Si eliminas este archivo perderás todos los registros locales de tickets, usuarios y proyectos. En Docker, el volumen de la base de datos se guarda temporalmente en el volumen mapeado (`.:/app`).
