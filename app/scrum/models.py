from django.db import models
from django.contrib.auth.models import User
from app.projects.models import Project

class Sprint(models.Model):
    STATUS_CHOICES = [
        ('Planeado', 'Planeado'),
        ('Activo', 'Activo'),
        ('Cerrado', 'Cerrado'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planeado')

    def __str__(self):
        return f"{self.name} ({self.project.name})"

class UserStory(models.Model):
    STATUS_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En desarrollo', 'En desarrollo'),
        ('Concluida', 'Concluida'),
    ]
    VALUE_CHOICES = [
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
    ]
    EFFORT_CHOICES = [
        (1, '1'),
        (2, '2'),
        (4, '4'),
        (6, '6'),
        (8, '8'),
        (10, '10'),
        (20, '20'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pendiente')
    value = models.CharField(max_length=10, choices=VALUE_CHOICES, default='Media')
    effort = models.IntegerField(choices=EFFORT_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_code(self):
        return f"HU-{self.id:02d}" if self.id else ""

    def __str__(self):
        return f"{self.get_code} - {self.title}"

class UserStoryTask(models.Model):
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='tasks')
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

class AcceptanceCriterion(models.Model):
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='criteria')
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

class Ticket(models.Model):
    TYPE_CHOICES = [
        ('Feature', 'Feature'),
        ('Artefacto', 'Artefacto'),
        ('Spike', 'Spike [Research]'),
        ('Task', 'Task'),
    ]
    PRIORITY_CHOICES = [
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
    ]
    STATUS_CHOICES = [
        ('Backlog', 'Backlog'),
        ('Ready', 'Ready'),
        ('Doing', 'Doing'),
        ('Blocked', 'Blocked'),
        ('Review', 'Review'),
        ('Testing', 'Testing'),
        ('Done', 'Done'),
    ]
    EFFORT_CHOICES = [
        (1, '1'),
        (2, '2'),
        (4, '4'),
        (6, '6'),
        (8, '8'),
        (10, '10'),
        (20, '20'),
    ]
    
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='tickets')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Task')
    value = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Media')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Backlog')
    effort = models.IntegerField(choices=EFFORT_CHOICES, default=1)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    tester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tested_tickets')
    due_date = models.DateField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependents')

    @property
    def get_code(self):
        return f"TK-{self.id:02d}" if self.id else ""

    @property
    def remaining_days(self):
        if not self.due_date:
            return None
        import datetime
        return (self.due_date - datetime.date.today()).days

    def __str__(self):
        return f"{self.get_code} - {self.title}"

class TicketAcceptanceCriterion(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='criteria')
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description
