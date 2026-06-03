from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import UserStory
from .forms import UserStoryForm, UserStoryTaskFormSet, AcceptanceCriterionFormSet
from app.projects.models import Project

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

# --- SPRINTS ---
from django.views.generic import ListView
from .models import Sprint, Ticket, TicketAcceptanceCriterion
from .forms import SprintForm, TicketForm, TicketStatusForm, TicketAcceptanceCriterionFormSet

class SprintListView(LoginRequiredMixin, ListView):
    model = Sprint
    template_name = 'scrum/sprint_list.html'
    context_object_name = 'sprints'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Sprint.objects.filter(project=self.project).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        context['is_pm'] = self.project.members.filter(user=self.request.user, role='PM').exists()
        return context

class SprintCreateView(LoginRequiredMixin, CreateView):
    model = Sprint
    form_class = SprintForm
    template_name = 'scrum/sprint_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        if not self.project.members.filter(user=request.user, role='PM').exists():
            messages.error(request, "Solo el Project Manager puede administrar sprints.")
            from django.shortcuts import redirect
            return redirect('scrum:sprint_list', project_id=self.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data['status'] == 'Activo':
            if Sprint.objects.filter(project=self.project, status='Activo').exists():
                form.add_error('status', 'Ya existe un Sprint activo en este proyecto.')
                return self.form_invalid(form)
        form.instance.project = self.project
        messages.success(self.request, "Sprint creado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('scrum:sprint_list', kwargs={'project_id': self.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

class SprintUpdateView(LoginRequiredMixin, UpdateView):
    model = Sprint
    form_class = SprintForm
    template_name = 'scrum/sprint_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.sprint = self.get_object()
        self.project = self.sprint.project
        if not self.project.members.filter(user=request.user, role='PM').exists():
            messages.error(request, "Solo el Project Manager puede administrar sprints.")
            from django.shortcuts import redirect
            return redirect('scrum:sprint_list', project_id=self.project.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data['status'] == 'Activo':
            active_sprints = Sprint.objects.filter(project=self.project, status='Activo').exclude(pk=self.sprint.pk)
            if active_sprints.exists():
                form.add_error('status', 'Ya existe un Sprint activo en este proyecto.')
                return self.form_invalid(form)
        messages.success(self.request, "Sprint actualizado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('scrum:sprint_list', kwargs={'project_id': self.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context

# --- TICKETS ---

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'scrum/ticket_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.sprint = get_object_or_404(Sprint, pk=self.kwargs['sprint_id'])
        self.project = self.sprint.project
        if not self.project.members.filter(user=request.user, role='PM').exists():
            messages.error(request, "Solo el PM puede crear tickets.")
            from django.shortcuts import redirect
            return redirect('scrum:kanban', sprint_id=self.sprint.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.project
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sprint'] = self.sprint
        context['project'] = self.project
        if self.request.POST:
            context['criterion_formset'] = TicketAcceptanceCriterionFormSet(self.request.POST)
        else:
            context['criterion_formset'] = TicketAcceptanceCriterionFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        criterion_formset = context['criterion_formset']
        
        if criterion_formset.is_valid():
            form.instance.sprint = self.sprint
            self.object = form.save()
            criterion_formset.instance = self.object
            criterion_formset.save()
            messages.success(self.request, "Ticket creado.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('scrum:kanban', kwargs={'sprint_id': self.sprint.pk})

class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'scrum/ticket_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.ticket = self.get_object()
        self.sprint = self.ticket.sprint
        self.project = self.sprint.project
        if not self.project.members.filter(user=request.user, role='PM').exists():
            messages.error(request, "Solo el PM puede editar tickets completamente.")
            from django.shortcuts import redirect
            return redirect('scrum:kanban', sprint_id=self.sprint.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.project
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sprint'] = self.sprint
        context['project'] = self.project
        if self.request.POST:
            context['criterion_formset'] = TicketAcceptanceCriterionFormSet(self.request.POST, instance=self.object)
        else:
            context['criterion_formset'] = TicketAcceptanceCriterionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        criterion_formset = context['criterion_formset']
        
        if criterion_formset.is_valid():
            if form.cleaned_data['status'] == 'Done' and not self.ticket.closed_date:
                import datetime
                form.instance.closed_date = datetime.datetime.now()
            self.object = form.save()
            criterion_formset.instance = self.object
            criterion_formset.save()
            messages.success(self.request, "Ticket actualizado.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('scrum:kanban', kwargs={'sprint_id': self.sprint.pk})

class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'scrum/ticket_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.ticket = self.get_object()
        self.sprint = self.ticket.sprint
        self.project = self.sprint.project
        if not self.project.members.filter(user=request.user, role='PM').exists():
            messages.error(request, "Solo el PM puede eliminar tickets.")
            from django.shortcuts import redirect
            return redirect('scrum:kanban', sprint_id=self.sprint.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Ticket eliminado.")
        return reverse('scrum:kanban', kwargs={'sprint_id': self.sprint.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sprint'] = self.sprint
        return context

class TicketStatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketStatusForm
    
    def dispatch(self, request, *args, **kwargs):
        self.ticket = self.get_object()
        is_pm = self.ticket.sprint.project.members.filter(user=request.user, role='PM').exists()
        is_owner = self.ticket.assigned_to == request.user
        if not (is_pm or is_owner):
            messages.error(request, "No tienes permiso para actualizar este ticket.")
            from django.shortcuts import redirect
            return redirect('scrum:kanban', sprint_id=self.ticket.sprint.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.cleaned_data['status'] == 'Done' and not self.ticket.closed_date:
            import datetime
            form.instance.closed_date = datetime.datetime.now()
        form.save()
        messages.success(self.request, "Estado actualizado.")
        from django.shortcuts import redirect
        return redirect('scrum:kanban', sprint_id=self.ticket.sprint.pk)

    def form_invalid(self, form):
        messages.error(self.request, "Error actualizando estado.")
        from django.shortcuts import redirect
        return redirect('scrum:kanban', sprint_id=self.ticket.sprint.pk)

# --- KANBAN ---

class KanbanView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'scrum/kanban_board.html'
    context_object_name = 'tickets'

    def dispatch(self, request, *args, **kwargs):
        self.sprint = get_object_or_404(Sprint, pk=self.kwargs['sprint_id'])
        self.project = self.sprint.project
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Ticket.objects.filter(sprint=self.sprint)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sprint'] = self.sprint
        context['project'] = self.project
        context['is_pm'] = self.project.members.filter(user=self.request.user, role='PM').exists()
        
        # Agrupar tickets
        tickets = self.get_queryset()
        context['backlog'] = tickets.filter(status='Backlog')
        context['ready'] = tickets.filter(status='Ready')
        context['doing'] = tickets.filter(status='Doing')
        context['blocked'] = tickets.filter(status='Blocked')
        context['review'] = tickets.filter(status='Review')
        context['testing'] = tickets.filter(status='Testing')
        context['done'] = tickets.filter(status='Done')
        
        context['status_form'] = TicketStatusForm()
        return context

# --- NEW FEATURES: AJAX STATUS UPDATE & DASHBOARDS ---
import json
from django.http import JsonResponse
from django.views.generic import View, DetailView
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
import datetime

class TicketStatusAjaxUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        sprint = ticket.sprint
        project = sprint.project
        
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
        except:
            return JsonResponse({'error': 'Datos inválidos.'}, status=400)
            
        if new_status not in dict(Ticket.STATUS_CHOICES).keys():
            return JsonResponse({'error': 'Estado inválido.'}, status=400)

        member = project.members.filter(user=request.user).first()
        if not member:
            return JsonResponse({'error': 'No eres miembro del proyecto.'}, status=403)
            
        role = member.role
        if role not in ['PM', 'TL']:
            if ticket.assigned_to != request.user:
                return JsonResponse({'error': 'Solo el desarrollador asignado, PM o TL pueden mover este ticket.'}, status=403)

        if new_status in ['Doing', 'Review', 'Testing', 'Done']:
            pending_deps = ticket.dependencies.exclude(status='Done')
            if pending_deps.exists():
                dep_names = ", ".join([d.get_code for d in pending_deps])
                return JsonResponse({'error': f'No se puede mover a {new_status}. Faltan dependencias por completar: {dep_names}.'}, status=400)

        if new_status == 'Done' and not ticket.closed_date:
            ticket.closed_date = datetime.datetime.now()
        ticket.status = new_status
        ticket.save()
        
        return JsonResponse({'success': True, 'message': 'Estado actualizado.'})

class ScrumMasterDashboardView(LoginRequiredMixin, DetailView):
    model = Sprint
    template_name = 'scrum/sm_dashboard.html'
    context_object_name = 'sprint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sprint = self.object
        tickets = sprint.tickets.all()
        
        context['total_tickets'] = tickets.count()
        context['completed_tickets'] = tickets.filter(status='Done').count()
        context['pending_tickets'] = tickets.exclude(status='Done').count()
        context['blocked_tickets'] = tickets.filter(status='Blocked').count()
        
        context['progress_percentage'] = 0
        if context['total_tickets'] > 0:
            context['progress_percentage'] = int((context['completed_tickets'] / context['total_tickets']) * 100)
            
        context['total_effort'] = tickets.aggregate(Sum('effort'))['effort__sum'] or 0
        context['completed_effort'] = tickets.filter(status='Done').aggregate(Sum('effort'))['effort__sum'] or 0
        context['pending_effort'] = context['total_effort'] - context['completed_effort']

        if sprint.start_date and sprint.end_date:
            days = (sprint.end_date - sprint.start_date).days
            labels = []
            planned_data = []
            real_data = []
            
            total = context['total_effort']
            daily_burn = total / max(days, 1)
            current_effort = total
            
            closed_tickets = tickets.filter(status='Done', closed_date__isnull=False).annotate(close_day=TruncDate('closed_date'))
            
            for i in range(days + 1):
                day = sprint.start_date + datetime.timedelta(days=i)
                labels.append(day.strftime('%d %b'))
                
                planned_val = max(0, total - (daily_burn * i))
                planned_data.append(round(planned_val, 1))
                
                if day <= datetime.date.today():
                    day_closed = closed_tickets.filter(close_day=day).aggregate(Sum('effort'))['effort__sum'] or 0
                    current_effort -= day_closed
                    real_data.append(current_effort)
                else:
                    real_data.append(None)
                    
            context['burndown_labels'] = json.dumps(labels)
            context['burndown_planned'] = json.dumps(planned_data)
            context['burndown_real'] = json.dumps(real_data)
            
        return context

class ProjectManagerDashboardView(LoginRequiredMixin, DetailView):
    model = Sprint
    template_name = 'scrum/pm_dashboard.html'
    context_object_name = 'sprint'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sprint = self.object
        tickets = sprint.tickets.all()
        
        context['total_tickets'] = tickets.count()
        context['completed_tickets'] = tickets.filter(status='Done').count()
        context['pending_tickets'] = tickets.exclude(status='Done').count()
        context['blocked_tickets'] = tickets.filter(status='Blocked').count()
        
        context['total_effort'] = tickets.aggregate(Sum('effort'))['effort__sum'] or 0
        context['completed_effort'] = tickets.filter(status='Done').aggregate(Sum('effort'))['effort__sum'] or 0
        context['pending_effort'] = context['total_effort'] - context['completed_effort']

        members_metrics = []
        for member in sprint.project.members.all():
            member_tickets = tickets.filter(assigned_to=member.user)
            if member_tickets.exists():
                assigned = member_tickets.count()
                completed = member_tickets.filter(status='Done').count()
                pending = assigned - completed
                eff_assigned = member_tickets.aggregate(Sum('effort'))['effort__sum'] or 0
                eff_completed = member_tickets.filter(status='Done').aggregate(Sum('effort'))['effort__sum'] or 0
                members_metrics.append({
                    'name': member.user.username,
                    'role': member.get_role_display(),
                    'assigned_tickets': assigned,
                    'completed_tickets': completed,
                    'pending_tickets': pending,
                    'effort_assigned': eff_assigned,
                    'effort_completed': eff_completed,
                    'progress': int((completed/assigned)*100) if assigned > 0 else 0
                })
        
        context['members_metrics'] = members_metrics
        return context
