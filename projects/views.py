from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
import django.views.generic
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if current user is PM for this project to conditionally render UI elements
        context['is_pm'] = self.object.members.filter(user=self.request.user, role='PM').exists()
        return context

class ProjectMemberCreateView(LoginRequiredMixin, CreateView):
    model = ProjectMember
    form_class = ProjectMemberForm
    template_name = 'projects/member_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Asegurar que el proyecto existe y el usuario es miembro
        self.project = get_object_or_404(Project, pk=self.kwargs['pk'], members__user=request.user)
        # Solo el PM puede invitar
        if not self.project.members.filter(user=request.user, role='PM').exists():
            messages.error(request, "Acceso denegado: Solo el Project Manager puede agregar integrantes al equipo.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.project.pk)
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

class ProjectMemberUpdateView(LoginRequiredMixin, django.views.generic.UpdateView):
    model = ProjectMember
    fields = ['role']
    template_name = 'projects/member_form.html'
    pk_url_kwarg = 'member_id'

    def dispatch(self, request, *args, **kwargs):
        self.member = get_object_or_404(ProjectMember, pk=self.kwargs['member_id'])
        self.project = self.member.project
        # Solo el PM del proyecto puede editar roles
        if not ProjectMember.objects.filter(project=self.project, user=request.user, role='PM').exists():
            messages.error(request, "Acceso denegado: Solo el Project Manager puede modificar los roles del equipo.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f"Rol de {self.member.user.username} actualizado a {self.member.get_role_display()}.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

class ProjectMemberDeleteView(LoginRequiredMixin, django.views.generic.DeleteView):
    model = ProjectMember
    template_name = 'projects/member_confirm_delete.html'
    pk_url_kwarg = 'member_id'

    def dispatch(self, request, *args, **kwargs):
        self.member = get_object_or_404(ProjectMember, pk=self.kwargs['member_id'])
        self.project = self.member.project
        
        # Solo el PM del proyecto puede eliminar roles
        if not ProjectMember.objects.filter(project=self.project, user=request.user, role='PM').exists():
            messages.error(request, "Acceso denegado: Solo el Project Manager puede eliminar integrantes del equipo.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.project.pk)
            
        # Evitar que el PM se elimine a sí mismo si es el único
        if self.member.user == request.user:
            messages.error(request, "No puedes eliminarte a ti mismo del proyecto.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.project.pk)
            
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, f"Integrante {self.member.user.username} eliminado del proyecto.")
        return reverse('projects:detail', kwargs={'pk': self.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context
