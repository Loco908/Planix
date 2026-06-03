# Planix

Planix es una herramienta integral de gestión de proyectos de software centrada en metodologías ágiles (Scrum). Permite administrar proyectos, miembros de equipo y realizar un seguimiento completo del ciclo de vida del desarrollo.

## Características Principales

- **Gestión de Proyectos:** Crea proyectos y asigna roles a los miembros del equipo (Project Manager, Scrum Master, Product Owner, Tech Lead, Developer).
- **Gestión Ágil (Scrum):**
  - **Sprints:** Planifica, activa y cierra iteraciones de trabajo.
  - **Historias de Usuario (User Stories):** Define requerimientos, estima el esfuerzo y documenta criterios de aceptación.
  - **Tickets y Tareas:** Desglosa historias de usuario en tickets accionables (Features, Artefactos, Spikes o Tasks).
  - **Tablero Kanban:** Sigue el estado de los tickets interactuando con una interfaz nativa **Drag & Drop** que restringe movimientos no permitidos y valida dependencias automáticamente.
  - **Dashboards y Analítica:** Paneles de métricas exclusivas para *Project Managers* (evaluación de rendimiento del equipo) y *Scrum Masters* (monitoreo del Sprint con *Burndown Chart*).

## Tecnologías Utilizadas

- **Backend:** Django 4.2 y Python 3.11
- **Base de Datos:** SQLite (para desarrollo local)
- **Despliegue:** Docker y Docker Compose
- **Autenticación:** Django Social Auth

## Documentación del Proyecto

Hemos preparado guías detalladas para ayudarte a conocer más sobre la estructura y configuración del proyecto:

- 📖 **[Guía de Operación](operation_guide.md):** Contiene los pasos necesarios para instalar dependencias, configurar el entorno local (con y sin Docker) y levantar el servidor.
- 🗄️ **[Modelo de Datos](data_model.md):** Explica a profundidad las entidades de la base de datos, sus relaciones y la lógica de negocio detrás de las aplicaciones `projects` y `scrum`.

---

*Desarrollado para facilitar la administración eficiente de proyectos de software.*
