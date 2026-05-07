from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    ROLE_CHOICES = [
        ('PM', 'Project Manager'),
        ('SM', 'Scrum Master'),
        ('PO', 'Product Owner'),
        ('TL', 'Architect/Tech Lead'),
        ('DEV', 'Developer'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=3, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} ({self.project.name})"
