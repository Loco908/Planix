import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planix.settings')
django.setup()

from app.scrum.models import Ticket
from app.projects.models import Project

print("Starting backfill...")
for project in Project.objects.all():
    tickets = Ticket.objects.filter(user_story__project=project).order_by('id')
    seq = 1
    for t in tickets:
        if t.project_sequence != seq:
            t.project_sequence = seq
            t.save()
        seq += 1

print("Backfill done")
