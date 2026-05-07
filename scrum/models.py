from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

class Sprint(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.project.name})"

class UserStory(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('INPROG', 'In Progress'),
        ('DONE', 'Done'),
    ]
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='tickets')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='TODO')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
