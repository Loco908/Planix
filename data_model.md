# Modelo de Datos - Planix

El proyecto está construido sobre Django y utiliza el ORM integrado. La base de datos configurada por defecto es SQLite (`db.sqlite3`). El modelo de datos se divide en dos aplicaciones principales: `projects` y `scrum`, además de utilizar el modelo de usuarios integrado en Django (`django.contrib.auth.models.User`).

---

## Aplicación: `projects`

Maneja la información general de los proyectos y los roles de los usuarios dentro de los mismos.

### 1. `Project` (Proyecto)
Representa un proyecto de software a gestionar.
- **`name`** (`CharField`): Nombre del proyecto (único).
- **`description`** (`TextField`): Descripción detallada del proyecto.
- **`created_at`** (`DateTimeField`): Fecha y hora de creación (automático).
- **`created_by`** (`ForeignKey` a `User`): Usuario creador del proyecto.

### 2. `ProjectMember` (Miembro del Proyecto)
Relaciona a los usuarios con los proyectos y asigna un rol dentro del mismo.
- **`project`** (`ForeignKey` a `Project`): Proyecto al que pertenece el usuario.
- **`user`** (`ForeignKey` a `User`): Usuario asignado.
- **`role`** (`CharField`): Rol del usuario en el proyecto. Valores posibles:
  - `PM` (Project Manager)
  - `SM` (Scrum Master)
  - `PO` (Product Owner)
  - `TL` (Architect/Tech Lead)
  - `DEV` (Developer)

---

## Aplicación: `scrum`

Gestiona los elementos ágiles y el ciclo de vida del desarrollo.

### 1. `Sprint`
Periodos de trabajo iterativos dentro de un proyecto.
- **`project`** (`ForeignKey` a `Project`): Proyecto al que pertenece el sprint.
- **`name`** (`CharField`): Nombre o identificador del sprint.
- **`start_date`** (`DateField`): Fecha de inicio.
- **`end_date`** (`DateField`): Fecha de finalización.
- **`status`** (`CharField`): Estado del sprint (`Planeado`, `Activo`, `Cerrado`).

### 2. `UserStory` (Historia de Usuario)
Requerimientos o funcionalidades a desarrollar.
- **`project`** (`ForeignKey` a `Project`): Proyecto al que pertenece.
- **`title`** (`CharField`): Título corto descriptivo.
- **`description`** (`TextField`): Descripción detallada de la funcionalidad.
- **`status`** (`CharField`): Estado (`Pendiente`, `En desarrollo`, `Concluida`).
- **`value`** (`CharField`): Valor de negocio/prioridad (`Alta`, `Media`, `Baja`).
- **`effort`** (`IntegerField`): Esfuerzo estimado en puntos de historia (1, 2, 4, 6, 8, 10, 20).
- **`created_at`** (`DateTimeField`): Fecha de creación.

### 3. `UserStoryTask` y `AcceptanceCriterion`
Sub-elementos de una historia de usuario.
- Ambas entidades tienen relación uno-a-muchos con `UserStory` y un campo `description` (`CharField`).
- **`UserStoryTask`**: Tareas necesarias para completar la historia.
- **`AcceptanceCriterion`**: Criterios de aceptación para validar la historia.

### 4. `Ticket`
Tareas individuales, issues o features que se planifican en Sprints.
- **`user_story`** (`ForeignKey` a `UserStory`): Historia a la que aporta valor.
- **`sprint`** (`ForeignKey` a `Sprint`): Sprint en el que se trabajará (opcional).
- **`title`** (`CharField`): Título del ticket.
- **`description`** (`TextField`): Descripción del ticket.
- **`type`** (`CharField`): Tipo de ticket (`Feature`, `Artefacto`, `Spike [Research]`, `Task`).
- **`value`** (`CharField`): Prioridad del ticket (`Alta`, `Media`, `Baja`).
- **`status`** (`CharField`): Estado actual en el tablero (`Backlog`, `Ready`, `Doing`, `Blocked`, `Review`, `Testing`, `Done`).
- **`effort`** (`IntegerField`): Esfuerzo (Puntos).
- **`assigned_to`** (`ForeignKey` a `User`): Desarrollador asignado.
- **`tester`** (`ForeignKey` a `User`): Persona encargada de probar el ticket.
- **`due_date`** (`DateField`): Fecha límite.
- **`closed_date`** (`DateTimeField`): Fecha en que se completó.
- **`updated_at`** (`DateTimeField`): Fecha de la última modificación (automático).
- **`dependencies`** (`ManyToManyField` a `self`): Relación con otros tickets de los que depende para ser realizado.

### 5. `TicketAcceptanceCriterion`
Criterios de aceptación específicos para un Ticket en particular.
- **`ticket`** (`ForeignKey` a `Ticket`): El ticket asociado.
- **`description`** (`CharField`): Detalle del criterio a cumplir.
