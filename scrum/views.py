from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import UserStory
from .forms import UserStoryForm
from projects.models import Project

class UserStoryCreateView(LoginRequiredMixin, CreateView):
    model = UserStory
    form_class = UserStoryForm
    template_name = 'scrum/userstory_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Asegurar que el proyecto existe y el usuario pertenece a él
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'], members__user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project
        messages.success(self.request, "Historia de Usuario creada y agregada al Backlog.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
