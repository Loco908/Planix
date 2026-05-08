from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Project, ProjectMember
from .forms import ProjectForm, ProjectMemberForm

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Retorna los proyectos donde el usuario es miembro
        return Project.objects.filter(members__user=self.request.user).distinct()

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')

    def form_valid(self, form):
        # Asignar el usuario actual como creador
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Asignarlo automáticamente como Project Manager
        ProjectMember.objects.create(
            project=self.object,
            user=self.request.user,
            role='PM'
        )
        messages.success(self.request, "Proyecto creado exitosamente.")
        return response

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(members__user=self.request.user).distinct()

class ProjectMemberCreateView(LoginRequiredMixin, CreateView):
    model = ProjectMember
    form_class = ProjectMemberForm
    template_name = 'projects/member_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Asegurar que el proyecto existe y el usuario es Project Manager (PM)
        self.project = get_object_or_404(Project, pk=self.kwargs['pk'], members__user=request.user, members__role='PM')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project
        # Verificar que el usuario no sea ya miembro
        if ProjectMember.objects.filter(project=self.project, user=form.instance.user).exists():
            form.add_error('user', 'Este usuario ya es miembro del proyecto.')
            return self.form_invalid(form)
            
        messages.success(self.request, f"Integrante {form.instance.user.username} agregado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
