from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import UserStory
from .forms import UserStoryForm, UserStoryTaskFormSet, AcceptanceCriterionFormSet
from projects.models import Project

class UserStoryCreateView(LoginRequiredMixin, CreateView):
    model = UserStory
    form_class = UserStoryForm
    template_name = 'scrum/userstory_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        # RBAC: Solo PM y PO pueden crear historias
        if not self.project.members.filter(user=request.user, role__in=['PM', 'PO']).exists():
            messages.error(request, "No tienes permisos para crear esta historia. Solo el PM o PO pueden hacerlo.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        if self.request.POST:
            context['task_formset'] = UserStoryTaskFormSet(self.request.POST)
            context['criterion_formset'] = AcceptanceCriterionFormSet(self.request.POST)
        else:
            context['task_formset'] = UserStoryTaskFormSet()
            context['criterion_formset'] = AcceptanceCriterionFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        task_formset = context['task_formset']
        criterion_formset = context['criterion_formset']
        
        if task_formset.is_valid() and criterion_formset.is_valid():
            form.instance.project = self.project
            self.object = form.save()
            task_formset.instance = self.object
            task_formset.save()
            criterion_formset.instance = self.object
            criterion_formset.save()
            messages.success(self.request, "Historia de Usuario creada y agregada al Backlog.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.project.pk})

from django.views.generic import UpdateView, DeleteView

class UserStoryUpdateView(LoginRequiredMixin, UpdateView):
    model = UserStory
    form_class = UserStoryForm
    template_name = 'scrum/userstory_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.story = self.get_object()
        if not self.story.project.members.filter(user=request.user, role__in=['PM', 'PO']).exists():
            messages.error(request, "No tienes permisos para editar esta historia. Solo el PM o PO pueden hacerlo.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.story.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.story.project
        if self.request.POST:
            context['task_formset'] = UserStoryTaskFormSet(self.request.POST, instance=self.object)
            context['criterion_formset'] = AcceptanceCriterionFormSet(self.request.POST, instance=self.object)
        else:
            context['task_formset'] = UserStoryTaskFormSet(instance=self.object)
            context['criterion_formset'] = AcceptanceCriterionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        task_formset = context['task_formset']
        criterion_formset = context['criterion_formset']
        
        if task_formset.is_valid() and criterion_formset.is_valid():
            self.object = form.save()
            task_formset.instance = self.object
            task_formset.save()
            criterion_formset.instance = self.object
            criterion_formset.save()
            messages.success(self.request, "Historia actualizada.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.story.project.pk})

class UserStoryDeleteView(LoginRequiredMixin, DeleteView):
    model = UserStory
    template_name = 'scrum/userstory_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.story = self.get_object()
        if not self.story.project.members.filter(user=request.user, role__in=['PM', 'PO']).exists():
            messages.error(request, "No tienes permisos para borrar esta historia. Solo el PM o PO pueden hacerlo.")
            from django.shortcuts import redirect
            return redirect('projects:detail', pk=self.story.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Historia eliminada.")
        return reverse('projects:detail', kwargs={'pk': self.story.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.story.project
        return context
